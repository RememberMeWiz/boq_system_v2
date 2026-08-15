"""Frozen Parser -> Integration -> Solver RC-beam boundary.

Authorized I1 projection only:
- beam_schedule.B1.width -> parameters.width
- beam_schedule.B1.depth -> parameters.depth

No parser extraction logic or solver formulas live here.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import copy
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable


PARSER_CLAIM_VERSION = "parser.claim-envelope/1.0"
CANONICAL_FACT_VERSION = "integration.canonical-fact/2.0"
ACCEPTED_CLAIM_REGISTRY_VERSION = "integration.accepted-parser-claim-registry/1.0"
CANONICAL_FIELD_REGISTRY_VERSION = "integration.canonical-field-registry/1.0"
NORMALIZATION_REGISTRY_VERSION = "integration.normalization-registry/1.0"
PROVENANCE_REGISTRY_VERSION = "integration.provenance-registry/1.0"
SOLVER_INPUT_PROFILE_REGISTRY_VERSION = "integration.solver-input-profile-registry/1.0"
SOLVER_CONTRACT_VERSION = "solver-contract/1.1.0"
AUTHORIZED_P0_SHA256 = "02b516066e288b965d917641243333fdb4c3b9ab92bb430c07b8b7f7e5457aac"

AUTHORIZED_FIELDS = frozenset({
    "beam_schedule.B1.width",
    "beam_schedule.B1.depth",
})
AUTHORIZED_SOLVER_KEYS = frozenset({"width", "depth"})

LENGTH_DIMENSION_VECTOR = {
    "bar_diameter": 0,
    "board_foot": 0,
    "crew_day": 0,
    "currency": 0,
    "item": 0,
    "length": 1,
    "mass": 0,
    "time": 0,
    "unit_day": 0,
}


SOLVER_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9-]*:[A-Za-z0-9._/:-]+$")
POLICY_ID_RE = re.compile(r"^POLICY\.[A-Z0-9_.-]+$")
POLICY_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?$")
SOLVER_CODE_RE = re.compile(r"^[A-Z][A-Z0-9_.-]{2,100}$")
SOLVER_FIELD_PATH_RE = re.compile(r"^(/[^/~]*(?:~[01][^/~]*)*)*$")

POLICY_ROLES = frozenset({
    "MEASUREMENT_OWNERSHIP",
    "SLAB_OWNERSHIP",
    "FORMWORK_SURFACE",
    "WASTE",
    "PROCUREMENT_INCREMENT",
    "ROUNDING",
    "ANCHORAGE_LAP",
    "BEND_HOOK",
    "STOCK_KERF_REUSE",
    "OPTIMIZATION_OBJECTIVE",
    "PRICING",
    "GENERAL",
})
SOLVER_ISSUE_CATEGORIES = frozenset({
    "BOUNDARY",
    "SOURCE_EVIDENCE",
    "CONFLICT",
    "CAPABILITY",
    "POLICY",
    "PARSER",
    "VERIFICATION",
    "PROCUREMENT",
    "PRICING",
    "CALCULATION",
    "ROUNDING",
})
SOLVER_ISSUE_SEVERITIES = frozenset({"INFO", "WARNING", "REVIEW", "BLOCKER", "ERROR"})
SOLVER_DISPOSITIONS = frozenset({
    "VALID",
    "WARNING",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "INVALID_INPUT",
    "UNSUPPORTED_CASE",
    "UNSUPPORTED_POLICY",
    "UNRESOLVED",
})
UNSUPPORTED_ITEM_CATEGORIES = frozenset({"CASE", "POLICY", "CAPABILITY", "ELEMENT_TYPE"})


class IntegrationBoundaryError(ValueError):
    """Fail-closed integration boundary error."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class SolverAssemblyConfig:
    element_id: str
    element_type: str
    formula_id: str
    formula_version: str
    policy_refs: tuple[dict[str, Any], ...]
    solver_version: str
    requested_output_stage: str
    precision_policy: dict[str, Any]
    source_quantity_state: str
    rounding_state: str


def _require(mapping: dict[str, Any], key: str, *, code: str) -> Any:
    if key not in mapping:
        raise IntegrationBoundaryError(code, f"missing required field {key!r}")
    return mapping[key]


def _canonicalize_for_hash(value: Any, parent_key: str | None = None) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, dict):
        return {
            unicodedata.normalize("NFC", str(k)): _canonicalize_for_hash(v, str(k))
            for k, v in value.items()
        }
    if isinstance(value, list):
        values = [_canonicalize_for_hash(v) for v in value]
        if parent_key in {"source_refs", "provenance_refs"}:
            return sorted(values)
        if parent_key == "policy_refs":
            return sorted(
                values,
                key=lambda item: (
                    item["policy_role"],
                    item["policy_id"],
                    item["policy_version"],
                ),
            )
        return values
    return value


def _canonical_json_bytes(value: Any) -> bytes:
    normalized = _canonicalize_for_hash(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _semantic_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _decimal_string(value: Any) -> str:
    try:
        d = Decimal(str(value)).normalize()
    except (InvalidOperation, ValueError):
        raise IntegrationBoundaryError("NORMALIZATION_VALUE_TYPE", "numeric source value required")
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


class RcBeamIntegrationBoundary:
    """Runtime gate for the frozen first RC-beam projection."""

    def __init__(self, schema_dir: Path | str, solver_config: SolverAssemblyConfig):
        self.schema_dir = Path(schema_dir)
        self.solver_config = solver_config
        self.accepted_claim_registry = self._load_json("accepted_parser_claim_registry_v1.json")
        self.field_registry = self._load_json("canonical_field_registry_v1.json")
        self.normalization_registry = self._load_json("normalization_registry_v1.json")
        self.provenance_registry = self._load_json("provenance_registry_p0_006.json")
        self.solver_input_profiles = self._load_json("solver_input_profile_registry_v1.json")
        self._validate_registry_headers()

    def _load_json(self, filename: str) -> dict[str, Any]:
        path = self.schema_dir / filename
        if not path.exists():
            raise IntegrationBoundaryError("REGISTRY_MISSING", f"missing runtime registry {filename}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _validate_registry_headers(self) -> None:
        # Mandatory PIS-PARSER-R9-N01 runtime gates.
        version = _require(
            self.accepted_claim_registry,
            "registry_version",
            code="ACCEPTED_CLAIM_REGISTRY_VERSION_MISSING",
        )
        if version != ACCEPTED_CLAIM_REGISTRY_VERSION:
            raise IntegrationBoundaryError(
                "ACCEPTED_CLAIM_REGISTRY_VERSION_UNSUPPORTED",
                f"expected {ACCEPTED_CLAIM_REGISTRY_VERSION}, got {version!r}",
            )

        p0_sha = _require(
            self.accepted_claim_registry,
            "source_p0_package_sha256",
            code="ACCEPTED_P0_SHA_MISSING",
        )
        if p0_sha != AUTHORIZED_P0_SHA256:
            raise IntegrationBoundaryError(
                "ACCEPTED_P0_SHA_MISMATCH",
                "accepted Parser registry is not bound to the authorized P0 source",
            )

        expected_headers = (
            (self.field_registry, "registry_version", CANONICAL_FIELD_REGISTRY_VERSION, "FIELD_REGISTRY_VERSION_UNSUPPORTED"),
            (self.normalization_registry, "registry_version", NORMALIZATION_REGISTRY_VERSION, "NORMALIZATION_REGISTRY_VERSION_UNSUPPORTED"),
            (self.provenance_registry, "registry_version", PROVENANCE_REGISTRY_VERSION, "PROVENANCE_REGISTRY_VERSION_UNSUPPORTED"),
        )
        for registry, key, expected, code in expected_headers:
            actual = _require(registry, key, code=code)
            if actual != expected:
                raise IntegrationBoundaryError(code, f"expected {expected}, got {actual!r}")

        if _require(self.field_registry, "solver_contract_version", code="SOLVER_CONTRACT_VERSION_MISSING") != SOLVER_CONTRACT_VERSION:
            raise IntegrationBoundaryError("SOLVER_CONTRACT_VERSION_UNSUPPORTED", "field registry solver contract drift")
        if _require(self.field_registry, "canonical_fact_contract_version", code="CANONICAL_FACT_VERSION_MISSING") != CANONICAL_FACT_VERSION:
            raise IntegrationBoundaryError("CANONICAL_FACT_VERSION_UNSUPPORTED", "field registry canonical fact version drift")
        profile_version = _require(self.solver_input_profiles, "registry_version", code="SOLVER_INPUT_PROFILE_REGISTRY_VERSION_MISSING")
        if profile_version != SOLVER_INPUT_PROFILE_REGISTRY_VERSION:
            raise IntegrationBoundaryError("SOLVER_INPUT_PROFILE_REGISTRY_VERSION_UNSUPPORTED", f"expected {SOLVER_INPUT_PROFILE_REGISTRY_VERSION}, got {profile_version!r}")

    def _validate_parser_envelope(self, claim: dict[str, Any]) -> None:
        expected_keys = {
            "contract_version", "claim_id", "case_id", "field_path", "value", "value_type", "unit",
            "field_state", "solver_readiness_state", "review_state", "source_document_hash",
            "page_number", "sheet_id", "source_locator", "evidence_ref", "conflict_ids",
            "review_provenance",
        }
        if set(claim) != expected_keys:
            raise IntegrationBoundaryError("INVALID_PARSER_CLAIM_SCHEMA", "Parser envelope top-level keyset mismatch")
        if not isinstance(claim["source_locator"], dict) or "bounding_box" not in claim["source_locator"] or "coordinate_space" not in claim["source_locator"]:
            raise IntegrationBoundaryError("INVALID_PARSER_CLAIM_SCHEMA", "invalid source_locator")
        if not isinstance(claim["evidence_ref"], dict) or set(claim["evidence_ref"]) != {"crop_path", "crop_hash"}:
            raise IntegrationBoundaryError("INVALID_PARSER_CLAIM_SCHEMA", "invalid evidence_ref")
        if not isinstance(claim["review_provenance"], dict) or set(claim["review_provenance"]) != {"reviewer", "review_timestamp"}:
            raise IntegrationBoundaryError("INVALID_PARSER_CLAIM_SCHEMA", "invalid review_provenance")
        if not isinstance(claim["conflict_ids"], list) or len(claim["conflict_ids"]) != len(set(claim["conflict_ids"])):
            raise IntegrationBoundaryError("INVALID_PARSER_CLAIM_SCHEMA", "invalid conflict_ids")

    def _bind_frozen_claim(self, claim: dict[str, Any]) -> None:
        version = _require(claim, "contract_version", code="PARSER_CLAIM_VERSION_MISSING")
        if version != PARSER_CLAIM_VERSION:
            raise IntegrationBoundaryError("PARSER_CLAIM_VERSION_UNSUPPORTED", f"unsupported Parser claim version {version!r}")

        claim_id = _require(claim, "claim_id", code="CLAIM_ID_MISSING")
        entries = _require(self.accepted_claim_registry, "entries", code="ACCEPTED_CLAIM_ENTRIES_MISSING")
        record = entries.get(claim_id)
        if record is None:
            raise IntegrationBoundaryError("CLAIM_NOT_IN_FROZEN_REGISTRY", claim_id)

        bound_fields = _require(self.accepted_claim_registry, "bound_fields", code="BOUND_FIELDS_MISSING")
        snapshot: dict[str, Any] = {}
        for field in bound_fields:
            snapshot[field] = copy.deepcopy(_require(claim, field, code="FROZEN_CLAIM_BINDING_MISMATCH"))

        if snapshot != record.get("semantic_snapshot"):
            raise IntegrationBoundaryError("FROZEN_CLAIM_BINDING_MISMATCH", claim_id)
        if _semantic_sha256(snapshot) != record.get("semantic_sha256"):
            raise IntegrationBoundaryError("FROZEN_CLAIM_DIGEST_MISMATCH", claim_id)

    def _state_gate(self, claim: dict[str, Any]) -> None:
        field_state = _require(claim, "field_state", code="FIELD_STATE_MISSING")
        readiness = _require(claim, "solver_readiness_state", code="READINESS_STATE_MISSING")
        review_state = _require(claim, "review_state", code="REVIEW_STATE_MISSING")
        conflict_ids = _require(claim, "conflict_ids", code="CONFLICT_IDS_MISSING")

        if field_state == "CONFLICTING" or conflict_ids:
            raise IntegrationBoundaryError("UNRESOLVED_CONFLICT", "conflicting claim cannot project")
        if field_state == "MISSING":
            raise IntegrationBoundaryError("REQUIRED_VALUE_MISSING", "missing claim cannot project")
        if field_state in {"REVIEW_REQUIRED", "NOT_APPLICABLE", "MANUALLY_OVERRIDDEN"}:
            raise IntegrationBoundaryError("CLAIM_NOT_ADMISSIBLE", field_state)
        if field_state not in {"OBSERVED", "DERIVED_FROM_OBSERVATIONS", "MANUALLY_CONFIRMED"}:
            raise IntegrationBoundaryError("STATE_MAPPING_UNSUPPORTED", field_state)
        if readiness != "READY":
            raise IntegrationBoundaryError("STATE_READINESS_INCONSISTENT", readiness)
        if review_state != "MANUALLY_CONFIRMED":
            raise IntegrationBoundaryError("REVIEW_NOT_ADMISSIBLE", review_state)

        review = _require(claim, "review_provenance", code="REVIEW_AUDIT_INCOMPLETE")
        reviewer = _require(review, "reviewer", code="REVIEW_AUDIT_INCOMPLETE")
        timestamp = _require(review, "review_timestamp", code="REVIEW_AUDIT_INCOMPLETE")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise IntegrationBoundaryError("REVIEW_AUDIT_INCOMPLETE", "reviewer is empty")
        if not isinstance(timestamp, str) or ("Z" not in timestamp and "+" not in timestamp[10:] and "-" not in timestamp[10:]):
            raise IntegrationBoundaryError("REVIEW_AUDIT_INCOMPLETE", "timezone-aware review timestamp required")

    def _provenance_ref(self, claim: dict[str, Any]) -> str:
        claim_id = claim["claim_id"]
        ref = f"source:claim:{claim_id}"
        entries = _require(self.provenance_registry, "entries", code="PROVENANCE_ENTRIES_MISSING")
        entry = entries.get(ref)
        if entry is None:
            raise IntegrationBoundaryError("PROVENANCE_UNRESOLVED", ref)

        expected = {
            "claim_id": claim_id,
            "source_document_hash": claim["source_document_hash"],
            "sheet_id": claim["sheet_id"],
            "page_number": claim["page_number"],
            "source_locator": claim["source_locator"],
            "evidence_ref": claim["evidence_ref"],
            "review_state": claim["review_state"],
            "reviewer": claim["review_provenance"]["reviewer"],
            "review_timestamp": claim["review_provenance"]["review_timestamp"],
        }
        if entry != expected:
            raise IntegrationBoundaryError("PROVENANCE_SEMANTIC_MISMATCH", ref)
        return ref

    def _normalize(self, claim: dict[str, Any], field_entry: dict[str, Any]) -> tuple[str, str, str]:
        rule_id = _require(field_entry, "normalization_rule_id", code="NORMALIZATION_RULE_ID_MISSING")
        rules = _require(self.normalization_registry, "rules", code="NORMALIZATION_RULES_MISSING")
        rule = rules.get(rule_id)
        if rule is None:
            raise IntegrationBoundaryError("NORMALIZATION_RULE_UNSUPPORTED", rule_id)

        rule_version = _require(rule, "version", code="NORMALIZATION_RULE_VERSION_MISSING")
        if rule_id != "length.mm_to_m" or rule_version != "1.0":
            raise IntegrationBoundaryError("NORMALIZATION_RULE_UNSUPPORTED", f"{rule_id}/{rule_version}")
        if _require(rule, "source_unit", code="NORMALIZATION_SOURCE_UNIT_MISSING") != "mm":
            raise IntegrationBoundaryError("NORMALIZATION_SOURCE_UNIT_DRIFT", rule_id)
        if _require(rule, "canonical_unit", code="NORMALIZATION_DESTINATION_UNIT_MISSING") != "m":
            raise IntegrationBoundaryError("NORMALIZATION_DESTINATION_UNIT_DRIFT", rule_id)
        if _require(rule, "dimension", code="NORMALIZATION_DIMENSION_MISSING") != "LENGTH":
            raise IntegrationBoundaryError("NORMALIZATION_DIMENSION_DRIFT", rule_id)
        if str(_require(rule, "factor", code="NORMALIZATION_FACTOR_MISSING")) != "0.001":
            raise IntegrationBoundaryError("NORMALIZATION_FACTOR_DRIFT", rule_id)

        if _require(claim, "unit", code="SOURCE_UNIT_MISSING") != "mm":
            raise IntegrationBoundaryError("SOURCE_UNIT_RULE_MISMATCH", claim["field_path"])
        raw = _require(claim, "value", code="SOURCE_VALUE_MISSING")
        try:
            canonical = Decimal(str(raw)) * Decimal("0.001")
        except (InvalidOperation, ValueError):
            raise IntegrationBoundaryError("NORMALIZATION_VALUE_TYPE", claim["field_path"])
        return _decimal_string(canonical), "m", "LENGTH"

    def canonicalize(self, claim: dict[str, Any]) -> dict[str, Any]:
        self._validate_parser_envelope(claim)
        self._bind_frozen_claim(claim)
        self._state_gate(claim)

        field_path = _require(claim, "field_path", code="FIELD_PATH_MISSING")
        if field_path not in AUTHORIZED_FIELDS:
            raise IntegrationBoundaryError("FIELD_NOT_AUTHORIZED_FOR_I1", field_path)

        entries = _require(self.field_registry, "entries", code="FIELD_REGISTRY_ENTRIES_MISSING")
        field_entry = entries.get(field_path)
        if field_entry is None or not field_entry.get("mapped_to_solver"):
            raise IntegrationBoundaryError("FIELD_NOT_MAPPED_TO_SOLVER", field_path)
        accepted_claim_ids = _require(field_entry, "accepted_claim_ids", code="ACCEPTED_CLAIM_IDS_MISSING")
        if claim["claim_id"] not in accepted_claim_ids:
            raise IntegrationBoundaryError("CLAIM_NOT_AUTHORIZED_FOR_FIELD", claim["claim_id"])

        solver_key = _require(field_entry, "solver_parameter_key", code="SOLVER_PARAMETER_KEY_MISSING")
        if solver_key not in AUTHORIZED_SOLVER_KEYS:
            raise IntegrationBoundaryError("SOLVER_PARAMETER_KEY_UNAUTHORIZED", solver_key)

        canonical_value, canonical_unit, dimension = self._normalize(claim, field_entry)
        provenance_ref = self._provenance_ref(claim)
        rule_id = field_entry["normalization_rule_id"]
        rule = self.normalization_registry["rules"][rule_id]

        return {
            "contract_version": CANONICAL_FACT_VERSION,
            "fact_id": f"fact:{claim['claim_id']}",
            "source_claim_contract_version": PARSER_CLAIM_VERSION,
            "source_claim_id": claim["claim_id"],
            "canonical_field_id": field_path,
            "source_value": claim["value"],
            "source_unit": claim["unit"],
            "canonical_value": canonical_value,
            "canonical_unit": canonical_unit,
            "dimension": dimension,
            "normalization_rule_id": rule_id,
            "normalization_rule_version": rule["version"],
            "provenance_ref": provenance_ref,
            "admission_state": "READY",
            "solver_parameter_key": solver_key,
        }

    def source_quantity_state(self, claim: dict[str, Any]) -> str:
        field_state = _require(claim, "field_state", code="FIELD_STATE_MISSING")
        mapping = {
            "OBSERVED": "OBSERVED_SOURCE",
            "DERIVED_FROM_OBSERVATIONS": "DERIVED",
            "MANUALLY_CONFIRMED": "EXPLICIT_INPUT",
        }
        if field_state not in mapping:
            raise IntegrationBoundaryError("SOURCE_QUANTITY_STATE_UNSUPPORTED", field_state)
        return mapping[field_state]

    def _validate_solver_identifier(self, value: Any, *, field: str, code: str) -> str:
        if not isinstance(value, str) or SOLVER_IDENTIFIER_RE.fullmatch(value) is None:
            raise IntegrationBoundaryError(code, f"{field} violates the accepted Solver identifier schema")
        return value

    def _validate_element_type(self, value: Any) -> str:
        if not isinstance(value, str) or not (1 <= len(value) <= 80):
            raise IntegrationBoundaryError(
                "INVALID_ELEMENT_TYPE",
                "element_type must be a string with length 1..80",
            )
        return value

    def _validate_policy_ref(self, policy: Any) -> dict[str, Any]:
        if not isinstance(policy, dict):
            raise IntegrationBoundaryError("INVALID_POLICY_REF", "PolicyRef must be an object")
        required = {"policy_id", "policy_version", "policy_role"}
        if set(policy) != required:
            raise IntegrationBoundaryError(
                "INVALID_POLICY_REF",
                "PolicyRef must contain exactly policy_id, policy_version, policy_role",
            )
        policy_id = policy["policy_id"]
        policy_version = policy["policy_version"]
        policy_role = policy["policy_role"]
        if not isinstance(policy_id, str) or POLICY_ID_RE.fullmatch(policy_id) is None:
            raise IntegrationBoundaryError("INVALID_POLICY_REF", "policy_id violates accepted Solver schema")
        if not isinstance(policy_version, str) or POLICY_VERSION_RE.fullmatch(policy_version) is None:
            raise IntegrationBoundaryError("INVALID_POLICY_REF", "policy_version violates accepted Solver schema")
        if policy_role not in POLICY_ROLES:
            raise IntegrationBoundaryError("INVALID_POLICY_REF", "policy_role violates accepted Solver schema")
        return copy.deepcopy(policy)

    def _validated_policy_refs(self) -> list[dict[str, Any]]:
        policies = self.solver_config.policy_refs
        if not isinstance(policies, (tuple, list)):
            raise IntegrationBoundaryError("INVALID_POLICY_REF", "policy_refs must be a sequence")
        validated = [self._validate_policy_ref(p) for p in policies]
        fingerprints = [_canonical_json_bytes(p) for p in validated]
        if len(fingerprints) != len(set(fingerprints)):
            raise IntegrationBoundaryError("DUPLICATE_POLICY_REF", "policy_refs must be unique")
        return sorted(
            validated,
            key=lambda item: (item["policy_role"], item["policy_id"], item["policy_version"]),
        )

    def _validate_boundary_metadata(self, request_id: Any) -> list[dict[str, Any]]:
        self._validate_solver_identifier(
            request_id,
            field="request_id",
            code="INVALID_REQUEST_ID",
        )
        self._validate_solver_identifier(
            self.solver_config.element_id,
            field="element_id",
            code="INVALID_ELEMENT_ID",
        )
        self._validate_element_type(self.solver_config.element_type)
        return self._validated_policy_refs()

    def _validate_solver_issue(self, issue: Any) -> None:
        if not isinstance(issue, dict):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "SolverIssue must be an object")
        required = {
            "issue_id",
            "code",
            "category",
            "severity",
            "state_effect",
            "message",
            "blocks_boq",
            "provenance_refs",
        }
        allowed = required | {"field_path"}
        if not required.issubset(issue) or not set(issue).issubset(allowed):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "SolverIssue keyset mismatch")
        self._validate_solver_identifier(
            issue["issue_id"],
            field="issue_id",
            code="INVALID_CALCULATION_ATTEMPT_SCHEMA",
        )
        if not isinstance(issue["code"], str) or SOLVER_CODE_RE.fullmatch(issue["code"]) is None:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid SolverIssue code")
        if issue["category"] not in SOLVER_ISSUE_CATEGORIES:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid SolverIssue category")
        if issue["severity"] not in SOLVER_ISSUE_SEVERITIES:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid SolverIssue severity")
        if issue["state_effect"] not in SOLVER_DISPOSITIONS | {"NONE"}:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid SolverIssue state_effect")
        if not isinstance(issue["message"], str) or not (1 <= len(issue["message"]) <= 2000):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid SolverIssue message")
        if not isinstance(issue["blocks_boq"], bool):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid blocks_boq")
        effect = issue["state_effect"]
        expected_blocks = effect not in {"NONE", "WARNING"}
        if issue["blocks_boq"] != expected_blocks:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "SolverIssue blocks_boq mismatch")
        refs = issue["provenance_refs"]
        if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid SolverIssue provenance_refs")
        for ref in refs:
            self._validate_solver_identifier(
                ref,
                field="provenance_ref",
                code="INVALID_CALCULATION_ATTEMPT_SCHEMA",
            )
        if "field_path" in issue:
            field_path = issue["field_path"]
            if not isinstance(field_path, str) or SOLVER_FIELD_PATH_RE.fullmatch(field_path) is None:
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid SolverIssue field_path")

    def _validate_attempt_body(self, attempt: dict[str, Any]) -> None:
        required = {
            "contract_version",
            "request_id",
            "element_id",
            "element_type",
            "source_refs",
            "policy_refs",
            "issues",
            "missing_fields",
            "conflicting_claims",
            "unsupported_items",
            "disposition_state",
            "canonical_input_ready",
            "may_calculate",
        }
        if set(attempt) != required:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "CalculationAttempt body keyset mismatch")
        if attempt["contract_version"] != SOLVER_CONTRACT_VERSION:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "CalculationAttempt contract drift")
        self._validate_solver_identifier(
            attempt["request_id"],
            field="request_id",
            code="INVALID_CALCULATION_ATTEMPT_SCHEMA",
        )
        self._validate_solver_identifier(
            attempt["element_id"],
            field="element_id",
            code="INVALID_CALCULATION_ATTEMPT_SCHEMA",
        )
        self._validate_element_type(attempt["element_type"])

        source_refs = attempt["source_refs"]
        if not isinstance(source_refs, list) or not source_refs or len(source_refs) != len(set(source_refs)):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid source_refs")
        for ref in source_refs:
            self._validate_solver_identifier(
                ref,
                field="source_ref",
                code="INVALID_CALCULATION_ATTEMPT_SCHEMA",
            )

        policies = attempt["policy_refs"]
        if not isinstance(policies, list):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "policy_refs must be an array")
        validated = [self._validate_policy_ref(p) for p in policies]
        fingerprints = [_canonical_json_bytes(p) for p in validated]
        if len(fingerprints) != len(set(fingerprints)):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "duplicate policy_refs")

        issues = attempt["issues"]
        if not isinstance(issues, list):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "issues must be an array")
        for issue in issues:
            self._validate_solver_issue(issue)

        missing_fields = attempt["missing_fields"]
        if not isinstance(missing_fields, list) or len(missing_fields) != len(set(missing_fields)):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid missing_fields")
        if any(not isinstance(x, str) or not x.startswith("/") for x in missing_fields):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid missing_fields path")

        conflicting_claims = attempt["conflicting_claims"]
        if not isinstance(conflicting_claims, list):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "conflicting_claims must be an array")
        for conflict in conflicting_claims:
            if not isinstance(conflict, dict) or set(conflict) != {"field_path", "claim_refs"}:
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid conflicting_claim entry")
            if not isinstance(conflict["field_path"], str) or not conflict["field_path"].startswith("/"):
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid conflicting claim field_path")
            refs = conflict["claim_refs"]
            if not isinstance(refs, list) or len(refs) < 2 or len(refs) != len(set(refs)):
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid conflicting claim refs")
            for ref in refs:
                self._validate_solver_identifier(
                    ref,
                    field="claim_ref",
                    code="INVALID_CALCULATION_ATTEMPT_SCHEMA",
                )

        unsupported_items = attempt["unsupported_items"]
        if not isinstance(unsupported_items, list):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "unsupported_items must be an array")
        for item in unsupported_items:
            if not isinstance(item, dict):
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid unsupported item")
            required_item = {"category", "code"}
            allowed_item = required_item | {"reference"}
            if not required_item.issubset(item) or not set(item).issubset(allowed_item):
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "unsupported item keyset mismatch")
            if item["category"] not in UNSUPPORTED_ITEM_CATEGORIES:
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid unsupported category")
            if not isinstance(item["code"], str) or SOLVER_CODE_RE.fullmatch(item["code"]) is None:
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid unsupported item code")
            if "reference" in item and (not isinstance(item["reference"], str) or not item["reference"]):
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid unsupported item reference")

        disposition = attempt["disposition_state"]
        if disposition not in SOLVER_DISPOSITIONS:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid disposition_state")
        if not isinstance(attempt["canonical_input_ready"], bool) or not isinstance(attempt["may_calculate"], bool):
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "attempt readiness flags must be boolean")

        if disposition in {"VALID", "WARNING", "REVIEW_REQUIRED"}:
            if not attempt["canonical_input_ready"] or not attempt["may_calculate"]:
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "ready disposition flags mismatch")
        else:
            if attempt["canonical_input_ready"] or attempt["may_calculate"]:
                raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "blocked disposition flags mismatch")
        if disposition == "UNRESOLVED" and not conflicting_claims:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "UNRESOLVED requires conflicts")
        if disposition in {"UNSUPPORTED_CASE", "UNSUPPORTED_POLICY"} and not unsupported_items:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "unsupported disposition requires items")

    def _validate_completed_attempt(self, attempt: dict[str, Any]) -> None:
        expected = {
            "attempt_id",
            "attempt_hash",
            "contract_version",
            "request_id",
            "element_id",
            "element_type",
            "source_refs",
            "policy_refs",
            "issues",
            "missing_fields",
            "conflicting_claims",
            "unsupported_items",
            "disposition_state",
            "canonical_input_ready",
            "may_calculate",
        }
        if set(attempt) != expected:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "completed CalculationAttempt keyset mismatch")
        if not isinstance(attempt["attempt_hash"], str) or re.fullmatch(r"sha256:[0-9a-f]{64}", attempt["attempt_hash"]) is None:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid attempt_hash")
        if not isinstance(attempt["attempt_id"], str) or re.fullmatch(r"attempt:sha256:[0-9a-f]{64}", attempt["attempt_id"]) is None:
            raise IntegrationBoundaryError("INVALID_CALCULATION_ATTEMPT_SCHEMA", "invalid attempt_id")
        body = {k: copy.deepcopy(v) for k, v in attempt.items() if k not in {"attempt_id", "attempt_hash"}}
        self._validate_attempt_body(body)

    def _input_profile(self) -> dict[str, Any]:
        profiles = _require(self.solver_input_profiles, "profiles", code="SOLVER_INPUT_PROFILES_MISSING")
        profile = profiles.get("rc_beam.concrete_volume/1.0")
        if profile is None:
            raise IntegrationBoundaryError("SOLVER_INPUT_PROFILE_MISSING", "rc_beam.concrete_volume/1.0")
        cfg = self.solver_config
        if cfg.formula_id != profile["formula_id"] or cfg.formula_version != profile["formula_version"]:
            raise IntegrationBoundaryError("SOLVER_FORMULA_UNSUPPORTED", f"{cfg.formula_id}/{cfg.formula_version}")
        if cfg.solver_version != profile["solver_version"]:
            raise IntegrationBoundaryError("SOLVER_VERSION_UNSUPPORTED", cfg.solver_version)
        if cfg.requested_output_stage not in profile["allowed_output_stages"]:
            raise IntegrationBoundaryError("SOLVER_OUTPUT_STAGE_UNSUPPORTED", cfg.requested_output_stage)
        roles = {x["policy_role"] for x in cfg.policy_refs}
        missing_roles = sorted(set(profile["required_policy_roles"]) - roles)
        if missing_roles:
            raise IntegrationBoundaryError("MANDATORY_POLICY_REF_MISSING", ",".join(missing_roles))
        return profile

    def _make_issue(self, code: str, field_path: str, message: str, provenance_refs: list[str]) -> dict[str, Any]:
        digest = hashlib.sha256(_canonical_json_bytes({
            "code": code, "field_path": field_path, "message": message, "provenance_refs": provenance_refs
        })).hexdigest()
        return {
            "issue_id": f"issue:sha256:{digest}",
            "code": code,
            "category": "BOUNDARY",
            "severity": "BLOCKER",
            "state_effect": "BLOCKED",
            "message": message,
            "blocks_boq": True,
            "field_path": field_path,
            "provenance_refs": provenance_refs,
        }

    def assess_request(self, claims: Iterable[dict[str, Any]], request_id: str) -> dict[str, Any]:
        validated_policy_refs = self._validate_boundary_metadata(request_id)
        profile = self._input_profile()
        claim_rows = list(claims)
        facts = [self.canonicalize(c) for c in claim_rows]
        by_field: dict[str, dict[str, Any]] = {}
        by_key: dict[str, dict[str, Any]] = {}
        source_states: dict[str, str] = {}
        for claim, fact in zip(claim_rows, facts):
            field = fact["canonical_field_id"]
            key = fact["solver_parameter_key"]
            if field in by_field:
                raise IntegrationBoundaryError("DUPLICATE_CANONICAL_FIELD", field)
            if key in by_key:
                raise IntegrationBoundaryError("DUPLICATE_SOLVER_PARAMETER_MAPPING", key)
            by_field[field] = fact
            by_key[key] = fact
            source_states[key] = self.source_quantity_state(claim)

        if set(by_key) != set(profile["authorized_projected_parameter_keys"]):
            raise IntegrationBoundaryError("SOLVER_PARAMETER_KEY_SET_MISMATCH", "width/depth projection incomplete or expanded")

        source_refs = sorted({f["provenance_ref"] for f in facts})
        missing_fields = sorted(profile["required_execution_dependencies"])
        issues = [
            self._make_issue(
                "BOUNDARY.INCOMPLETE_CONCRETE_VOLUME_INPUT",
                "/parameters",
                "Authorized I1 width/depth projection is insufficient for concrete-volume execution.",
                source_refs,
            )
        ]
        attempt = {
            "contract_version": SOLVER_CONTRACT_VERSION,
            "request_id": request_id,
            "element_id": self.solver_config.element_id,
            "element_type": self.solver_config.element_type,
            "source_refs": source_refs,
            "policy_refs": validated_policy_refs,
            "issues": issues,
            "missing_fields": missing_fields,
            "conflicting_claims": [],
            "unsupported_items": [],
            "disposition_state": "BLOCKED",
            "canonical_input_ready": False,
            "may_calculate": False,
        }
        # Full schema-equivalent body validation happens before hashing so invalid
        # external/configured metadata is never turned into a canonical Solver hash.
        self._validate_attempt_body(attempt)
        digest = hashlib.sha256(_canonical_json_bytes(attempt)).hexdigest()
        attempt["attempt_hash"] = f"sha256:{digest}"
        attempt["attempt_id"] = f"attempt:sha256:{digest}"
        # Validate the completed object, including hash/id constraints, before return.
        self._validate_completed_attempt(attempt)
        return {
            "canonical_facts": facts,
            "source_quantity_states": source_states,
            "calculation_attempt": attempt,
            "calculation_input": None,
        }

    def project(self, claims: Iterable[dict[str, Any]]) -> dict[str, Any]:
        raise IntegrationBoundaryError(
            "ATTEMPT_FIRST_REQUIRED",
            "Use assess_request(); width/depth-only I1 does not create a CalculationInput.",
        )

