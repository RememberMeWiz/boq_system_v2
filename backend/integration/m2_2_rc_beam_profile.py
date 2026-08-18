"""M2-2 RC-beam NET_MEASURED implementation boundary.

This module implements only the PM-authorized additive engineering profile:
    rc_beam.concrete_engineering_net_volume/1.0

The current authoritative project fixture MUST remain blocked because:
- exact slab thickness is missing; and
- beam/slab mix applicability is unresolved.

No Solver calculation is invoked from this module while those blockers remain.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import copy
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from typing import Any

from .rc_beam_boundary import IntegrationBoundaryError

PROFILE_ID = "rc_beam.concrete_engineering_net_volume/1.0"
PROFILE_REGISTRY_VERSION = "integration.solver-input-profile-registry/1.1"
SOLVER_CONTRACT_VERSION = "solver-contract/1.1.0"
SOLVER_IMPLEMENTATION_VERSION = "solver-kernel/0.0.0-readiness"
FORMULA_ID = "FORMULA.RC_BEAM.CONCRETE_VOLUME"
FORMULA_VERSION = "1.0.0"
OUTPUT_STAGE = "NET_MEASURED"

FROZEN_BILLABLE_PROFILE_ID = "rc_beam.concrete_volume/1.0"
FROZEN_BILLABLE_BLOB_SHA = "21425d726795d338425f58fa3ec05e673b67f90c"

SUPPORT_GUARD_ID = "GUARD-SUPPORT-WIDTH-CONSERVATION"
SUPPORT_GUARD_VERSION = "1.0"
SUPPORT_GUARD_MODE = "NOTIONAL_FULL_BEAM_WIDTH_SUPPORT_ZONE"
MIX_GUARD_ID = "GUARD-BEAM-SLAB-MIX-COMPATIBILITY"
MIX_GUARD_VERSION = "1.0"
MIX_EVIDENCE_BINDING_SCHEMA = "m2.rcbeam.reviewed-mix-evidence-binding/1.0"
MIX_EVIDENCE_BINDING_ID = "M2-3.MIX.B1.SAME_OR_EQUIVALENT/1.0"
MIX_ACCEPTED_DISPOSITION = "CLOSED_SAME_OR_EQUIVALENT_MIX_PROVEN"
MIX_RUNTIME_STATE = "SAME_OR_EQUIVALENT_MIX_PROVEN"
MIX_PARSER_R3_PACKAGE_SHA256 = "c1ffefd4159d6eb7e2ea74dff00e8ca4e13b751e7132cc73d385380b89f73f81"
MIX_EVIDENCE_SHA256 = "8accf6c6013a38d24e35f76bee51f6fe8f4b5ae8aab70b1ab138fee22437a23e"
MIX_SOURCE_DOCUMENT_SHA256 = "2ef1eca18e00f48e82417ca306941c87fb2a8ae03c764561b52d26aa351e4599"
MIX_SOURCE_DOCUMENT_GIT_BLOB_SHA1 = "0c02c66e0d3bd821e4758c3598422624063ce7ba"
MIX_PARSER_QA_PACKAGE_SHA256 = "620a3d5b92bf5c71bdf446b58522c5ec7791d3a1015c73d87c4b26fa478707fd"
MIX_PM_HANDOFF_PACKAGE_SHA256 = "d3c681a238e18c5c40dafe0b505e53908cac6628e79e75dc175e334e9d1f36ec"
PROVENANCE_GATE_ID = "m2.rcbeam.provenance-admission-gate/1.0"

# PM M2-IMPL-G01: this implementation round must never emit a successful
# CalculationInput, even if test data attempts to fill current blockers.
POSITIVE_EXECUTION_ENABLED = False

SOLVER_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9-]*:[A-Za-z0-9._/:-]+$")
POLICY_ID_RE = re.compile(r"^POLICY\.[A-Z0-9_.-]+$")
POLICY_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?$")

REQUIRED_GEOMETRY = (
    "width",
    "depth",
    "clear_span_between_support_faces",
    "left_support.dimension_along_beam",
    "right_support.dimension_along_beam",
    "slab.thickness",
)
READY_GEOMETRY_EXCEPT_SLAB = REQUIRED_GEOMETRY[:-1]
REQUIRED_POLICIES = (
    "support_intersection_owner",
    "support_deduction_scope",
    "slab.measured_separately_across_clear_span_beam_strip",
    "slab_intersection_owner",
    "slab_deduction_length_basis",
)
COMMERCIAL_KEYS = frozenset({
    "concrete_policy.waste_rate",
    "concrete_policy.waste_basis",
    "concrete_policy.procurement_increment",
    "concrete_policy.procurement_rounding",
})

I1_GEOMETRY_BINDINGS = {
    "width": {
        "claim_id": "claim-001-b1-width",
        "source_field_path": "beam_schedule.B1.width",
        "canonical_value_m": "0.2",
    },
    "depth": {
        "claim_id": "claim-001-b1-depth",
        "source_field_path": "beam_schedule.B1.depth",
        "canonical_value_m": "0.35",
    },
}

EXPECTED_POLICY_APPROVALS = {
    "support_intersection_owner": {
        "decision_id": "PO-M2-POL-001",
        "approval_state": "APPROVED",
        "guard_ref": None,
    },
    "support_deduction_scope": {
        "decision_id": "PO-M2-POL-002",
        "approval_state": "APPROVED_WITH_GUARD",
        "guard_ref": SUPPORT_GUARD_ID,
    },
    "slab.measured_separately_across_clear_span_beam_strip": {
        "decision_id": "PO-M2-POL-003",
        "approval_state": "APPROVED_WITH_GUARD",
        "guard_ref": MIX_GUARD_ID,
    },
    "slab_intersection_owner": {
        "decision_id": "PO-M2-POL-004",
        "approval_state": "APPROVED_WITH_GUARD",
        "guard_ref": MIX_GUARD_ID,
    },
    "slab_deduction_length_basis": {
        "decision_id": "PO-M2-POL-005",
        "approval_state": "APPROVED",
        "guard_ref": None,
    },
}
EXPECTED_POLICY_SOURCE_PACKAGE = "M2_RCBEAM_001_PO_FINAL_POLICY_DECISION_R1.zip"
EXPECTED_POLICY_SOURCE_PACKAGE_SHA256 = "2fa3296622f44241de01197d44cc99128e316cdba0cb736c9f1b225483e4c35e"
EXPECTED_POLICY_SOURCE_DOCUMENT = "PO_FINAL_POLICY_DECISION_R1.md"
EXPECTED_POLICY_SOURCE_DOCUMENT_SHA256 = "62680b250c33ead0ba77aa72d0e0eed5886eb590e382a63f343bc9d3ddfd1d8d"
EXPECTED_POLICY_SCOPE = "M2 selected B1 instance / rc_beam.concrete_engineering_net_volume/1.0"

EXPECTED_GUARD_BINDINGS = {
    SUPPORT_GUARD_ID: SUPPORT_GUARD_VERSION,
    MIX_GUARD_ID: MIX_GUARD_VERSION,
}


SELECTED_INSTANCE_ID = "B1-P33-S6-UPPER-LEFT-C4-PC4"
SELECTED_SOLVER_ELEMENT_ID = f"element:{SELECTED_INSTANCE_ID}"
SELECTED_SOLVER_ELEMENT_TYPE = "RC_BEAM"


@dataclass(frozen=True)
class M2RequestMetadata:
    request_id: str = "request:m2-2-b1-readiness"
    element_id: str = SELECTED_SOLVER_ELEMENT_ID
    element_type: str = SELECTED_SOLVER_ELEMENT_TYPE


def _normalize_for_hash(value: Any, parent_key: str | None = None) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, dict):
        return {
            unicodedata.normalize("NFC", str(k)): _normalize_for_hash(v, str(k))
            for k, v in value.items()
        }
    if isinstance(value, list):
        vals = [_normalize_for_hash(v) for v in value]
        if parent_key in {"source_refs", "provenance_refs", "missing_fields"}:
            return sorted(vals)
        if parent_key == "policy_refs":
            return sorted(
                vals,
                key=lambda item: (
                    item["policy_role"],
                    item["policy_id"],
                    item["policy_version"],
                ),
            )
        if parent_key == "issues":
            return sorted(vals, key=lambda item: item["issue_id"])
        if parent_key == "conflicting_claims":
            return sorted(
                vals,
                key=lambda item: (
                    item["field_path"],
                    tuple(sorted(item.get("claim_refs", []))),
                ),
            )
        return vals
    return value


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize_for_hash(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _decimal(value: Any, *, code: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise IntegrationBoundaryError(code, f"invalid decimal value {value!r}")


class M2RcBeamNetMeasuredRuntime:
    """Fail-closed M2-2 implementation for the additive engineering profile."""

    def __init__(self, schema_dir: str | Path):
        self.schema_dir = Path(schema_dir)
        self.profile_registry = self._load("solver_input_profile_registry_v1_1.json")
        self.policy_bundle = self._load("m2_2_approved_measurement_policy_bindings_v1.json")
        self.geometry_records = self._load("m2_2_geometry_records_v1.json")
        self.evidence_index = self._load("m2_2_evidence_reference_index_v1.json")
        self.support_guard = self._load("m2_2_support_width_conservation_guard_v1.json")
        self.mix_guard = self._load("m2_2_beam_slab_mix_compatibility_guard_v1.json")
        self.reviewed_mix_evidence_binding = self._load("m2_3_reviewed_mix_evidence_binding_v1.json")
        self.claim_graph = self._load("m2_2_transitive_claim_graph_v1.json")
        self.provenance_gate = self._load("m2_2_provenance_admission_gate_v1.json")
        self.solver_identity = self._load("m2_2_solver_implementation_identity_v1.json")
        self.accepted_claim_registry = self._load("accepted_parser_claim_registry_v1.json")
        self.i1_provenance_registry = self._load("provenance_registry_p0_006.json")
        self._validate_static_contract()

    def _load(self, filename: str) -> dict[str, Any]:
        return self._load_path(self.schema_dir / filename)

    @staticmethod
    def _load_path(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise IntegrationBoundaryError("M2_REGISTRY_MISSING", str(path))
        return json.loads(path.read_text(encoding="utf-8"))

    def _validate_static_contract(self) -> None:
        reg = self.profile_registry
        if reg.get("registry_version") != PROFILE_REGISTRY_VERSION:
            raise IntegrationBoundaryError("M2_PROFILE_REGISTRY_VERSION_UNSUPPORTED", str(reg.get("registry_version")))
        frozen = reg.get("frozen_existing_profile", {})
        if frozen.get("source_blob_sha") != FROZEN_BILLABLE_BLOB_SHA:
            raise IntegrationBoundaryError("FROZEN_BILLABLE_PROFILE_IDENTITY_DRIFT", str(frozen.get("source_blob_sha")))
        if frozen.get("mutation_authorized") is not False:
            raise IntegrationBoundaryError("FROZEN_BILLABLE_PROFILE_MUTATION_AUTHORIZED", "must remain false")
        if frozen.get("profile_id") != FROZEN_BILLABLE_PROFILE_ID:
            raise IntegrationBoundaryError("FROZEN_BILLABLE_PROFILE_IDENTITY_DRIFT", str(frozen.get("profile_id")))

        profile = reg.get("additive_profile", {})
        required = {
            "profile_id": PROFILE_ID,
            "formula_id": FORMULA_ID,
            "formula_version": FORMULA_VERSION,
            "solver_version": SOLVER_IMPLEMENTATION_VERSION,
            "required_provenance_gate": PROVENANCE_GATE_ID,
        }
        for key, expected in required.items():
            if profile.get(key) != expected:
                raise IntegrationBoundaryError("M2_PROFILE_IDENTITY_DRIFT", f"{key}={profile.get(key)!r}")
        if profile.get("allowed_output_stages") != [OUTPUT_STAGE]:
            raise IntegrationBoundaryError("M2_OUTPUT_STAGE_DRIFT", str(profile.get("allowed_output_stages")))
        if set(profile.get("excluded_downstream_policy_keys", [])) != COMMERCIAL_KEYS:
            raise IntegrationBoundaryError("M2_COMMERCIAL_EXCLUSION_DRIFT", "commercial exclusion set changed")
        if profile.get("engineering_input_digest_excludes_downstream_commercial") is not True:
            raise IntegrationBoundaryError("M2_COMMERCIAL_EXCLUSION_DRIFT", "digest exclusion disabled")

        ident = self.solver_identity
        if ident.get("solver_contract_version") != SOLVER_CONTRACT_VERSION:
            raise IntegrationBoundaryError("M2_SOLVER_CONTRACT_DRIFT", str(ident.get("solver_contract_version")))
        if ident.get("solver_implementation_version") != SOLVER_IMPLEMENTATION_VERSION:
            raise IntegrationBoundaryError("M2_SOLVER_VERSION_DRIFT", str(ident.get("solver_implementation_version")))
        if ident.get("formula_id") != FORMULA_ID or ident.get("formula_version") != FORMULA_VERSION:
            raise IntegrationBoundaryError("M2_SOLVER_FORMULA_DRIFT", "formula identity changed")

        if self.provenance_gate.get("schema") != PROVENANCE_GATE_ID:
            raise IntegrationBoundaryError("M2_PROVENANCE_GATE_IDENTITY_DRIFT", str(self.provenance_gate.get("schema")))

        if self.support_guard.get("guard_id") != SUPPORT_GUARD_ID:
            raise IntegrationBoundaryError("M2_SUPPORT_GUARD_IDENTITY_DRIFT", str(self.support_guard.get("guard_id")))
        support_mode = self.support_guard.get("selected_interpretation", {})
        if support_mode.get("id") != SUPPORT_GUARD_MODE or support_mode.get("version") != SUPPORT_GUARD_VERSION:
            raise IntegrationBoundaryError("M2_SUPPORT_GUARD_IDENTITY_DRIFT", repr(support_mode))
        if self.mix_guard.get("guard_id") != MIX_GUARD_ID or self.mix_guard.get("guard_version") != MIX_GUARD_VERSION:
            raise IntegrationBoundaryError("M2_MIX_GUARD_IDENTITY_DRIFT", repr(self.mix_guard.get("guard_id")))

        mix_binding = self.reviewed_mix_evidence_binding
        if mix_binding.get("schema") != MIX_EVIDENCE_BINDING_SCHEMA:
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_SCHEMA_DRIFT", repr(mix_binding.get("schema")))
        if mix_binding.get("binding_id") != MIX_EVIDENCE_BINDING_ID:
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_ID_DRIFT", repr(mix_binding.get("binding_id")))
        request_binding = mix_binding.get("request_binding")
        if not isinstance(request_binding, dict):
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_MISSING", "request_binding")
        expected_mix_identity = {
            "selected_instance_id": SELECTED_INSTANCE_ID,
            "solver_element_id": SELECTED_SOLVER_ELEMENT_ID,
            "solver_element_type": SELECTED_SOLVER_ELEMENT_TYPE,
            "guard_id": MIX_GUARD_ID,
            "guard_version": MIX_GUARD_VERSION,
            "accepted_disposition": MIX_ACCEPTED_DISPOSITION,
            "mix_state": MIX_RUNTIME_STATE,
            "review_state": "ACCEPTED",
        }
        for field, expected in expected_mix_identity.items():
            if request_binding.get(field) != expected:
                raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_DRIFT", f"{field}={request_binding.get(field)!r}")
        evidence_identity = request_binding.get("evidence_identity")
        if not isinstance(evidence_identity, dict):
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_DRIFT", "evidence_identity")
        expected_evidence_identity = {
            "parser_r3_package_sha256": MIX_PARSER_R3_PACKAGE_SHA256,
            "mix_evidence_sha256": MIX_EVIDENCE_SHA256,
            "source_document_sha256": MIX_SOURCE_DOCUMENT_SHA256,
            "source_document_git_blob_sha1": MIX_SOURCE_DOCUMENT_GIT_BLOB_SHA1,
            "source_assignment": "Class A (1:2:4)",
            "applies_to": ["suspended slabs", "beams"],
            "source_complete_search_page_count": 55,
            "narrower_applicable_override_found": False,
        }
        if evidence_identity != expected_evidence_identity:
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_DRIFT", "evidence identity mismatch")
        authority = request_binding.get("reviewed_authority")
        expected_authority = {
            "parser_qa": {
                "role": "Independent Parser QA Reviewer",
                "verdict": "QA_PASS_WITH_NOTES",
                "package_sha256": MIX_PARSER_QA_PACKAGE_SHA256,
            },
            "project_manager": {
                "role": "Project Manager",
                "verdict": "PM_ACCEPTED_WITH_NOTES",
                "package_sha256": MIX_PM_HANDOFF_PACKAGE_SHA256,
            },
        }
        if authority != expected_authority:
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_DRIFT", "reviewed authority mismatch")
        if request_binding.get("conflict_state") != "NONE":
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_DRIFT", "conflict state")
        if request_binding.get("superseded") is not False or request_binding.get("superseded_by") is not None:
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_DRIFT", "supersession state")
        if request_binding.get("replacement_evidence_ref") is not None:
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_DRIFT", "replacement evidence")
        required_refs = {
            f"parser-package:sha256:{MIX_PARSER_R3_PACKAGE_SHA256}",
            f"mix-evidence:sha256:{MIX_EVIDENCE_SHA256}",
            f"source-document:sha256:{MIX_SOURCE_DOCUMENT_SHA256}",
            f"parser-qa:sha256:{MIX_PARSER_QA_PACKAGE_SHA256}",
            f"pm-handoff:sha256:{MIX_PM_HANDOFF_PACKAGE_SHA256}",
        }
        if set(request_binding.get("provenance_refs", [])) != required_refs:
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_DRIFT", "provenance refs")
        expected_digest = f"sha256:{_sha256(request_binding)}"
        if mix_binding.get("request_binding_digest") != expected_digest:
            raise IntegrationBoundaryError("M2_MIX_EVIDENCE_BINDING_DIGEST_DRIFT", str(mix_binding.get("request_binding_digest")))

        profile_guards = {
            x.get("guard_id"): x.get("guard_version")
            for x in profile.get("required_guard_bindings", [])
            if isinstance(x, dict)
        }
        if profile_guards != EXPECTED_GUARD_BINDINGS:
            raise IntegrationBoundaryError("M2_REQUIRED_GUARD_BINDING_DRIFT", repr(profile_guards))

        if self.policy_bundle.get("binding_count") != 5:
            raise IntegrationBoundaryError("M2_POLICY_BINDING_COUNT", str(self.policy_bundle.get("binding_count")))
        bindings = self.policy_bundle.get("bindings", [])
        by_name = {x.get("canonical_name"): x for x in bindings if isinstance(x, dict)}
        if set(by_name) != set(REQUIRED_POLICIES):
            raise IntegrationBoundaryError("M2_POLICY_BINDING_SET", repr(sorted(by_name)))

        profile_policy = {
            x.get("canonical_name"): {
                "policy_id": x.get("policy_id"),
                "policy_version": x.get("policy_version"),
                "policy_role": x.get("policy_role"),
                "value": x.get("value"),
            }
            for x in profile.get("required_policy_bindings", [])
            if isinstance(x, dict)
        }
        bundle_policy = {
            name: {
                "policy_id": item.get("policy_id"),
                "policy_version": item.get("policy_version"),
                "policy_role": item.get("policy_role"),
                "value": item.get("selected_project_value"),
            }
            for name, item in by_name.items()
        }
        if profile_policy != bundle_policy:
            raise IntegrationBoundaryError("M2_POLICY_PROFILE_BINDING_DRIFT", "additive profile and approved policy bundle differ")

        for name, item in by_name.items():
            approved = EXPECTED_POLICY_APPROVALS[name]
            source = item.get("approval_source")
            if item.get("decision_id") != approved["decision_id"]:
                raise IntegrationBoundaryError("M2_POLICY_DECISION_ID_DRIFT", name)
            if item.get("approval_state") != approved["approval_state"]:
                raise IntegrationBoundaryError("M2_POLICY_APPROVAL_STATE_DRIFT", name)
            if item.get("approving_authority") != "Product Owner":
                raise IntegrationBoundaryError("M2_POLICY_APPROVING_AUTHORITY_DRIFT", name)
            if item.get("guard_ref") != approved["guard_ref"]:
                raise IntegrationBoundaryError("M2_POLICY_GUARD_REF_DRIFT", name)
            if item.get("effective_scope") != EXPECTED_POLICY_SCOPE:
                raise IntegrationBoundaryError("M2_POLICY_SCOPE_DRIFT", name)
            if not isinstance(source, dict):
                raise IntegrationBoundaryError("M2_POLICY_APPROVAL_SOURCE_MISSING", name)
            expected_source = {
                "package": EXPECTED_POLICY_SOURCE_PACKAGE,
                "package_sha256": EXPECTED_POLICY_SOURCE_PACKAGE_SHA256,
                "document": EXPECTED_POLICY_SOURCE_DOCUMENT,
                "document_sha256": EXPECTED_POLICY_SOURCE_DOCUMENT_SHA256,
                "decision_id": approved["decision_id"],
            }
            if source != expected_source:
                raise IntegrationBoundaryError("M2_POLICY_APPROVAL_SOURCE_DRIFT", name)

    @property
    def policy_refs(self) -> list[dict[str, str]]:
        refs = []
        for item in self.policy_bundle["bindings"]:
            refs.append({
                "policy_id": item["policy_id"],
                "policy_version": item["policy_version"],
                "policy_role": item["policy_role"],
            })
        return sorted(refs, key=lambda x: (x["policy_role"], x["policy_id"], x["policy_version"]))

    @staticmethod
    def _validate_metadata(meta: M2RequestMetadata) -> None:
        # First layer: preserve the existing Solver syntax/shape gates.
        for name, value in (("request_id", meta.request_id), ("element_id", meta.element_id)):
            if not isinstance(value, str) or SOLVER_IDENTIFIER_RE.fullmatch(value) is None:
                raise IntegrationBoundaryError("M2_INVALID_SOLVER_IDENTIFIER", f"{name}={value!r}")
        if not isinstance(meta.element_type, str) or not (1 <= len(meta.element_type) <= 80):
            raise IntegrationBoundaryError("M2_INVALID_ELEMENT_TYPE", repr(meta.element_type))

        # M2-QA-B01: this vertical slice is authoritative for exactly one
        # selected physical B1 instance and its RC-beam Solver type.  Reject
        # semantic rebinding before digesting, hashing, or emitting an attempt.
        if meta.element_id != SELECTED_SOLVER_ELEMENT_ID:
            raise IntegrationBoundaryError(
                "M2_SELECTED_INSTANCE_MISMATCH",
                f"expected {SELECTED_SOLVER_ELEMENT_ID!r}, got {meta.element_id!r}",
            )
        if meta.element_type != SELECTED_SOLVER_ELEMENT_TYPE:
            raise IntegrationBoundaryError(
                "M2_ELEMENT_TYPE_MISMATCH",
                f"expected {SELECTED_SOLVER_ELEMENT_TYPE!r}, got {meta.element_type!r}",
            )

    def _policy_validation(self, snapshot: dict[str, Any]) -> tuple[str | None, list[dict[str, Any]]]:
        policies = snapshot.get("policies")
        if not isinstance(policies, dict):
            return "BLOCKED_PENDING_PO_POLICY", []
        refs = []
        by_name = {x["canonical_name"]: x for x in self.policy_bundle["bindings"]}
        for name in REQUIRED_POLICIES:
            actual = policies.get(name)
            expected = by_name[name]
            approved = EXPECTED_POLICY_APPROVALS[name]
            if actual is None:
                return "BLOCKED_PENDING_PO_POLICY", refs
            if isinstance(actual, dict) and actual.get("state") == "CONFLICTING":
                return "UNRESOLVED", refs
            if not isinstance(actual, dict):
                return "REJECT", refs

            expected_source = {
                "package": EXPECTED_POLICY_SOURCE_PACKAGE,
                "package_sha256": EXPECTED_POLICY_SOURCE_PACKAGE_SHA256,
                "document": EXPECTED_POLICY_SOURCE_DOCUMENT,
                "document_sha256": EXPECTED_POLICY_SOURCE_DOCUMENT_SHA256,
                "decision_id": approved["decision_id"],
            }
            exact_checks = (
                (actual.get("authority"), expected["approving_authority"]),
                (actual.get("policy_id"), expected["policy_id"]),
                (actual.get("policy_version"), expected["policy_version"]),
                (actual.get("value"), expected["selected_project_value"]),
                (actual.get("approval_state"), approved["approval_state"]),
                (actual.get("decision_id"), approved["decision_id"]),
                (actual.get("approval_source"), expected_source),
                (actual.get("effective_scope"), EXPECTED_POLICY_SCOPE),
                (actual.get("guard_ref"), approved["guard_ref"]),
            )
            if any(a != b for a, b in exact_checks):
                return "REJECT", refs
            if POLICY_ID_RE.fullmatch(actual["policy_id"]) is None or POLICY_VERSION_RE.fullmatch(actual["policy_version"]) is None:
                return "REJECT", refs
            refs.append({
                "policy_id": actual["policy_id"],
                "policy_version": actual["policy_version"],
                "policy_role": expected["policy_role"],
            })
        if set(policies) != set(REQUIRED_POLICIES):
            return "REJECT", refs
        return None, refs

    def _geometry_validation(self, snapshot: dict[str, Any]) -> tuple[str | None, list[str], list[dict[str, Any]]]:
        geometry = snapshot.get("geometry")
        if not isinstance(geometry, dict):
            return "BLOCKED", [f"/parameters/{k}" for k in REQUIRED_GEOMETRY], []
        missing: list[str] = []
        conflicts: list[dict[str, Any]] = []
        for key in REQUIRED_GEOMETRY:
            field_path = f"/parameters/{key}"
            item = geometry.get(key)
            if item is None:
                missing.append(field_path)
                continue
            if not isinstance(item, dict):
                return "INVALID/BLOCKED", missing, conflicts
            state = item.get("state")
            if state == "CONFLICTING":
                claims = item.get("claims", [])
                conflicts.append({
                    "field_path": field_path,
                    "claim_refs": [
                        f"claim:test:{key.replace('.', '-')}-{i+1}" for i, _ in enumerate(claims[:2])
                    ] or [f"claim:test:{key}-a", f"claim:test:{key}-b"],
                })
                continue
            if key == "slab.thickness":
                if item.get("value") is None or state == "MISSING_BLOCKED":
                    missing.append(field_path)
                    continue
                source = item.get("source")
                if source in {"FORBIDDEN_LOWER_BOUND_AS_EXACT", "TYPICAL_DEFAULT_FORBIDDEN"}:
                    return "REJECT", missing, conflicts
                # No exact slab-thickness claim is currently authorized. Any injected
                # positive value remains blocked until a new reviewed source record exists.
                return "BLOCKED", missing, conflicts

            if state == "REVIEW_REQUIRED":
                return "REVIEW_REQUIRED/BLOCKED", missing, conflicts
            if state != "READY":
                return "BLOCKED", missing, conflicts
            if item.get("unit") != "m":
                return "INVALID/BLOCKED", missing, conflicts
            if item.get("dimension") != "LENGTH":
                return "INVALID/BLOCKED", missing, conflicts
            if key in {"left_support.dimension_along_beam", "right_support.dimension_along_beam"}:
                if item.get("orientation_evidence") != "VERIFIED":
                    return "REVIEW_REQUIRED/BLOCKED", missing, conflicts

        if conflicts:
            return "UNRESOLVED", missing, conflicts
        if missing:
            return "BLOCKED", missing, conflicts
        return None, missing, conflicts

    def _transitive_provenance_validation(self, snapshot: dict[str, Any]) -> str | None:
        if snapshot.get("stale_source"):
            return "BLOCKED_STALE_SOURCE"
        if snapshot.get("source_document_sha256") != self.claim_graph.get("source_document_sha256"):
            return "BLOCKED_STALE_SOURCE"

        graph = copy.deepcopy(self.claim_graph["claims"])
        mutation = snapshot.get("provenance_mutation")
        if mutation:
            node = graph.get(mutation.get("claim_id"))
            if node and mutation.get("remove_input_claim_id") in node.get("input_claim_ids", []):
                node["input_claim_ids"].remove(mutation["remove_input_claim_id"])

        evidence = {x["evidence_id"]: x for x in self.evidence_index["copied_evidence"]}
        geometry = snapshot.get("geometry")
        if not isinstance(geometry, dict):
            return "INVALID/BLOCKED"

        # Rebind the accepted I1 width/depth canonical facts. These values are
        # normalized from the frozen Parser claims and may not be supplied as
        # bare numbers in M2.
        for key, binding in I1_GEOMETRY_BINDINGS.items():
            actual = geometry.get(key)
            if not isinstance(actual, dict) or actual.get("state") != "READY":
                # Missing/conflicting/review states are owned by the geometry gate.
                continue
            claim_id = binding["claim_id"]
            accepted = self.accepted_claim_registry.get("entries", {}).get(claim_id)
            prov_ref = f"source:claim:{claim_id}"
            prov = self.i1_provenance_registry.get("entries", {}).get(prov_ref)
            if not isinstance(accepted, dict) or not isinstance(prov, dict):
                return "INVALID/BLOCKED"
            semantic = accepted.get("semantic_snapshot", {})
            try:
                source_m = _decimal(semantic.get("value"), code="M2_I1_VALUE") / Decimal("1000")
                actual_m = _decimal(actual.get("value"), code="M2_I1_VALUE")
            except IntegrationBoundaryError:
                return "INVALID/BLOCKED"
            expected_i1 = {
                "unit": "m",
                "dimension": "LENGTH",
                "state": "READY",
                "claim_id": claim_id,
                "source_ref": prov_ref,
                "source_field_path": binding["source_field_path"],
                "source_document_sha256": semantic.get("source_document_hash"),
                "accepted_claim_semantic_sha256": accepted.get("semantic_sha256"),
                "accepted_provenance_digest": f"sha256:{_sha256(prov)}",
                "selected_instance_id": self.geometry_records.get("selected_instance_id"),
            }
            if actual_m != _decimal(binding["canonical_value_m"], code="M2_I1_VALUE") or actual_m != source_m:
                return "INVALID/BLOCKED"
            for field, expected in expected_i1.items():
                if actual.get(field) != expected:
                    return "INVALID/BLOCKED"
            if semantic.get("field_path") != binding["source_field_path"]:
                return "INVALID/BLOCKED"
            if semantic.get("unit") != "mm" or semantic.get("review_state") != "MANUALLY_CONFIRMED":
                return "INVALID/BLOCKED"
            if semantic.get("solver_readiness_state") != "READY" or semantic.get("conflict_ids"):
                return "INVALID/BLOCKED"
            if prov.get("claim_id") != claim_id or prov.get("source_document_hash") != semantic.get("source_document_hash"):
                return "INVALID/BLOCKED"
            if prov.get("evidence_ref") != semantic.get("evidence_ref"):
                return "INVALID/BLOCKED"

        record_by_path = {
            r.get("field_path"): r
            for r in self.geometry_records.get("records", [])
            if r.get("solver_readiness") == "READY"
        }
        key_for_path = {
            "/parameters/clear_span_between_support_faces": "clear_span_between_support_faces",
            "/parameters/left_support.dimension_along_beam": "left_support.dimension_along_beam",
            "/parameters/right_support.dimension_along_beam": "right_support.dimension_along_beam",
        }

        def record_evidence_ids(record: dict[str, Any]) -> list[str]:
            provenance = record.get("provenance", {})
            ids = list(provenance.get("evidence_ids", []))
            for page in provenance.get("source_pages", []):
                if isinstance(page, dict) and page.get("evidence_id"):
                    ids.append(page["evidence_id"])
            return sorted(set(ids))

        # The incoming request must identify the exact reviewed derived record,
        # not merely repeat provenance labels around a different numeric value.
        for path, key in key_for_path.items():
            record = record_by_path.get(path)
            actual = geometry.get(key)
            if not isinstance(record, dict):
                return "INVALID/BLOCKED"
            if not isinstance(actual, dict) or actual.get("state") != "READY":
                # Missing/conflicting/review states are owned by the geometry gate.
                continue
            graph_node = graph.get(record.get("claim_id"))
            original_graph_node = self.claim_graph.get("claims", {}).get(record.get("claim_id"))
            if not isinstance(graph_node, dict) or not isinstance(original_graph_node, dict):
                return "INVALID/BLOCKED"
            try:
                actual_value = _decimal(actual.get("value"), code="M2_DERIVED_VALUE")
                expected_value = _decimal(record.get("value"), code="M2_DERIVED_VALUE")
            except IntegrationBoundaryError:
                return "INVALID/BLOCKED"
            expected_meta = {
                "unit": record.get("unit"),
                "dimension": record.get("dimension"),
                "state": "READY",
                "claim_id": record.get("claim_id"),
                "selected_instance_id": self.geometry_records.get("selected_instance_id"),
                "derivation_rule": record.get("derivation_rule"),
                "input_claim_ids": record.get("input_claim_ids"),
                "source_document_sha256": record.get("provenance", {}).get("source_document_sha256"),
                "evidence_ids": record_evidence_ids(record),
                "authoritative_record_digest": f"sha256:{_sha256(record)}",
                "claim_graph_digest": f"sha256:{_sha256(original_graph_node)}",
            }
            if actual_value != expected_value:
                return "INVALID/BLOCKED"
            for field, expected in expected_meta.items():
                observed = actual.get(field)
                if field in {"input_claim_ids", "evidence_ids"}:
                    if sorted(observed or []) != sorted(expected or []):
                        return "INVALID/BLOCKED"
                elif observed != expected:
                    return "INVALID/BLOCKED"
            if graph_node.get("field_path") != path:
                return "INVALID/BLOCKED"
            if _decimal(graph_node.get("value"), code="M2_DERIVED_GRAPH_VALUE") != expected_value:
                return "INVALID/BLOCKED"
            if graph_node.get("unit") != record.get("unit") or graph_node.get("dimension") != record.get("dimension"):
                return "INVALID/BLOCKED"
            if graph_node.get("derivation_rule") != record.get("derivation_rule"):
                return "INVALID/BLOCKED"
            if sorted(graph_node.get("input_claim_ids", [])) != sorted(record.get("input_claim_ids", [])):
                return "INVALID/BLOCKED"

        def walk(claim_id: str, seen: frozenset[str] = frozenset()) -> None:
            if claim_id in seen:
                raise IntegrationBoundaryError("M2_PROVENANCE_CYCLE", claim_id)
            node = graph.get(claim_id)
            if node is None:
                raise IntegrationBoundaryError("M2_PROVENANCE_EDGE_MISSING", claim_id)
            next_seen = seen | {claim_id}
            children = node.get("input_claim_ids", [])
            if children:
                if not node.get("derivation_rule"):
                    raise IntegrationBoundaryError("M2_DERIVATION_RULE_MISSING", claim_id)
                if "derivation_parameters" not in node:
                    raise IntegrationBoundaryError("M2_DERIVATION_PARAMETERS_MISSING", claim_id)
                for child in children:
                    walk(child, next_seen)
            else:
                for field in (
                    "source_document_sha256", "source_page_sha256", "source_page_number",
                    "sheet_id", "bbox_pdf_pt", "evidence_id"
                ):
                    if field not in node:
                        raise IntegrationBoundaryError("M2_PROVENANCE_LEAF_INCOMPLETE", f"{claim_id}:{field}")
                if node["source_document_sha256"] != self.claim_graph["source_document_sha256"]:
                    raise IntegrationBoundaryError("M2_PROVENANCE_DOCUMENT_MISMATCH", claim_id)
                ev = evidence.get(node["evidence_id"])
                if ev is None:
                    raise IntegrationBoundaryError("M2_PROVENANCE_EVIDENCE_UNRESOLVED", claim_id)
                if ev["source_page_sha256"] != node["source_page_sha256"]:
                    raise IntegrationBoundaryError("M2_PROVENANCE_PAGE_MISMATCH", claim_id)

        try:
            for record in record_by_path.values():
                for cid in record.get("input_claim_ids", []):
                    walk(cid)
        except (IntegrationBoundaryError, KeyError, TypeError):
            return "INVALID/BLOCKED"
        return None

    def _support_guard_validation(self, snapshot: dict[str, Any]) -> str | None:
        guard = self.support_guard
        request_guard = snapshot.get("guards", {}).get("support_width_conservation", {})
        if guard.get("guard_id") != SUPPORT_GUARD_ID:
            return "REJECT"
        mode = guard.get("selected_interpretation", {})
        if mode.get("id") != SUPPORT_GUARD_MODE or mode.get("version") != SUPPORT_GUARD_VERSION:
            return "REJECT"
        if request_guard.get("state") != "READY":
            return "REJECT"
        if request_guard.get("mode") != SUPPORT_GUARD_MODE:
            return "REJECT"
        if request_guard.get("guard_id") != SUPPORT_GUARD_ID or request_guard.get("guard_version") != SUPPORT_GUARD_VERSION:
            return "REJECT"

        geometry = snapshot.get("geometry", {})
        try:
            beam_w = _decimal(geometry["width"]["value"], code="M2_SUPPORT_GUARD_DECIMAL")
            depth = _decimal(geometry["depth"]["value"], code="M2_SUPPORT_GUARD_DECIMAL")
            left = _decimal(geometry["left_support.dimension_along_beam"]["value"], code="M2_SUPPORT_GUARD_DECIMAL")
            right = _decimal(geometry["right_support.dimension_along_beam"]["value"], code="M2_SUPPORT_GUARD_DECIMAL")
        except (KeyError, TypeError, IntegrationBoundaryError):
            return "REJECT"

        # Physical support transverse width is not a second runtime geometry
        # source. It is a pinned source-evidence binding used by this guard.
        binding = guard.get("authoritative_transverse_support_binding", {})
        claim_id = binding.get("claim_id")
        node = self.claim_graph.get("claims", {}).get(claim_id)
        if not isinstance(node, dict):
            return "REJECT"
        expected_binding = {
            "claim_id": claim_id,
            "field_path": node.get("field_path"),
            "value": str(node.get("value")),
            "unit": node.get("unit"),
            "dimension": node.get("dimension"),
            "source_document_sha256": node.get("source_document_sha256"),
            "source_page_sha256": node.get("source_page_sha256"),
            "source_page_number": node.get("source_page_number"),
            "sheet_id": node.get("sheet_id"),
            "evidence_id": node.get("evidence_id"),
            "claim_graph_digest": f"sha256:{_sha256(node)}",
        }
        if binding != expected_binding:
            return "REJECT"
        evidence = {
            x["evidence_id"]: x
            for x in self.evidence_index.get("copied_evidence", [])
            if isinstance(x, dict) and x.get("evidence_id")
        }.get(binding.get("evidence_id"))
        if not isinstance(evidence, dict) or evidence.get("source_page_sha256") != binding.get("source_page_sha256"):
            return "REJECT"
        support_w = _decimal(binding.get("value"), code="M2_SUPPORT_GUARD_DECIMAL")

        # Reference values prove that the admitted request remains bound to the
        # PO-approved selected instance. Computation itself uses the request.
        reference = guard.get("reference_case", {})
        expected_request = {
            "beam_width_m": beam_w,
            "beam_depth_m": depth,
            "left_support_dimension_along_beam_m": left,
            "right_support_dimension_along_beam_m": right,
        }
        for field, observed in expected_request.items():
            try:
                reference_value = _decimal(reference.get(field), code="M2_SUPPORT_GUARD_DECIMAL")
            except IntegrationBoundaryError:
                return "REJECT"
            if observed != reference_value:
                return "REJECT"

        length = left + right
        notional = beam_w * depth * length
        physical = min(beam_w, support_w) * depth * length
        shoulder = (beam_w - min(beam_w, support_w)) * depth * length
        if physical + shoulder != notional:
            return "REJECT"
        c = guard.get("conservation", {})
        try:
            if _decimal(c["notional_support_owned_volume_m3"], code="M2_SUPPORT_GUARD_DECIMAL") != notional:
                return "REJECT"
            if _decimal(c["physical_support_overlap_volume_m3"], code="M2_SUPPORT_GUARD_DECIMAL") != physical:
                return "REJECT"
            if _decimal(c["shoulder_junction_volume_m3"], code="M2_SUPPORT_GUARD_DECIMAL") != shoulder:
                return "REJECT"
        except (KeyError, IntegrationBoundaryError):
            return "REJECT"
        if c.get("identity") != "physical_support_overlap + shoulder_junction == notional_support_owned":
            return "REJECT"
        if c.get("identity_holds") is not True:
            return "REJECT"
        if c.get("residual_explicitly_owned_by") != "support notional BOQ zone":
            return "REJECT"
        return None

    def _mix_guard_validation(self, snapshot: dict[str, Any]) -> str | None:
        mix = snapshot.get("guards", {}).get("beam_slab_mix_compatibility", {})
        if not isinstance(mix, dict):
            return "BLOCKED_BEAM_SLAB_MIX_APPLICABILITY"
        if mix.get("guard_id") != MIX_GUARD_ID or mix.get("guard_version") != MIX_GUARD_VERSION:
            return "REJECT"

        state = mix.get("state")
        mix_state = mix.get("mix_state")
        if state == "BLOCKED" or mix_state in {None, "UNKNOWN"}:
            return "BLOCKED_BEAM_SLAB_MIX_APPLICABILITY"

        # M2-3 reviewed-evidence admission. A semantic state is never authority:
        # READY/SAME_MIX/SAME_OR_EQUIVALENT without the exact accepted evidence
        # identity, review chain, provenance refs, and no-supersession state rejects.
        if state != "READY" or mix_state != MIX_RUNTIME_STATE:
            return "REJECT"
        actual_binding = mix.get("reviewed_evidence_binding")
        expected_binding = self.reviewed_mix_evidence_binding.get("request_binding")
        if not isinstance(actual_binding, dict) or not isinstance(expected_binding, dict):
            return "REJECT"
        if _sha256(actual_binding) != _sha256(expected_binding):
            return "REJECT"
        if snapshot.get("source_document_sha256") != MIX_SOURCE_DOCUMENT_SHA256:
            return "REJECT"
        if actual_binding.get("selected_instance_id") != SELECTED_INSTANCE_ID:
            return "REJECT"
        if actual_binding.get("solver_element_id") != SELECTED_SOLVER_ELEMENT_ID:
            return "REJECT"
        if actual_binding.get("solver_element_type") != SELECTED_SOLVER_ELEMENT_TYPE:
            return "REJECT"
        if actual_binding.get("review_state") != "ACCEPTED":
            return "REJECT"
        if actual_binding.get("conflict_state") != "NONE":
            return "REJECT"
        if actual_binding.get("superseded") is not False:
            return "REJECT"
        if actual_binding.get("superseded_by") is not None:
            return "REJECT"
        if actual_binding.get("replacement_evidence_ref") is not None:
            return "REJECT"
        return None


    def engineering_input_digest(self, snapshot: dict[str, Any]) -> str:
        domain = {
            "profile_id": snapshot.get("profile_id"),
            "solver_version": snapshot.get("solver_version"),
            "geometry": snapshot.get("geometry"),
            "policies": snapshot.get("policies"),
            "guards": snapshot.get("guards"),
            "source_document_sha256": snapshot.get("source_document_sha256"),
        }
        return f"sha256:{_sha256(domain)}"

    def _issue(
        self,
        code: str,
        message: str,
        *,
        field_path: str = "",
        provenance_refs: list[str],
        state_effect: str = "BLOCKED",
        category: str = "BOUNDARY",
    ) -> dict[str, Any]:
        digest = _sha256({
            "code": code,
            "message": message,
            "field_path": field_path,
            "provenance_refs": provenance_refs,
            "state_effect": state_effect,
        })
        severity = "REVIEW" if state_effect == "REVIEW_REQUIRED" else "BLOCKER"
        return {
            "issue_id": f"issue:sha256:{digest}",
            "code": code,
            "category": category,
            "severity": severity,
            "state_effect": state_effect,
            "message": message,
            "blocks_boq": state_effect not in {"NONE", "WARNING"},
            "field_path": field_path,
            "provenance_refs": provenance_refs,
        }

    def _source_refs(self) -> list[str]:
        refs = [
            f"source:claim:{r['claim_id']}"
            for r in self.geometry_records["records"]
            if r.get("solver_readiness") == "READY"
        ]
        refs.extend(
            f"source:claim:{binding['claim_id']}"
            for binding in I1_GEOMETRY_BINDINGS.values()
        )
        refs.append(f"source:document:{self.evidence_index['source_document_sha256']}")
        return sorted(set(refs))

    def _build_attempt(
        self,
        meta: M2RequestMetadata,
        *,
        outcome: str,
        missing_fields: list[str],
        conflicts: list[dict[str, Any]],
        issues: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if outcome == "UNRESOLVED":
            disposition = "UNRESOLVED"
        elif outcome == "REVIEW_REQUIRED/BLOCKED":
            # Current M2 implementation never authorizes a calculation-ready
            # REVIEW_REQUIRED attempt; keep the attempt itself fail-closed.
            disposition = "BLOCKED"
        elif outcome in {"INVALID/BLOCKED", "REJECT", "REJECT_CONTRACT_IMMUTABILITY"}:
            disposition = "INVALID_INPUT"
        elif outcome == "UNSUPPORTED_CONTRACT_VERSION":
            disposition = "UNSUPPORTED_CASE"
        else:
            disposition = "BLOCKED"

        attempt = {
            "contract_version": SOLVER_CONTRACT_VERSION,
            "request_id": meta.request_id,
            "element_id": meta.element_id,
            "element_type": meta.element_type,
            "source_refs": self._source_refs(),
            "policy_refs": self.policy_refs,
            "issues": issues,
            "missing_fields": sorted(set(missing_fields)),
            "conflicting_claims": conflicts,
            "unsupported_items": (
                [{"category": "CASE", "code": "M2.UNSUPPORTED_PROFILE_VERSION", "reference": PROFILE_ID}]
                if outcome == "UNSUPPORTED_CONTRACT_VERSION" else []
            ),
            "disposition_state": disposition,
            "canonical_input_ready": False,
            "may_calculate": False,
        }
        digest = _sha256(attempt)
        attempt["attempt_hash"] = f"sha256:{digest}"
        attempt["attempt_id"] = f"attempt:sha256:{digest}"
        return attempt

    def evaluate(
        self,
        snapshot: dict[str, Any],
        metadata: M2RequestMetadata | None = None,
    ) -> dict[str, Any]:
        meta = metadata or M2RequestMetadata()
        self._validate_metadata(meta)
        engineering_digest = self.engineering_input_digest(snapshot)

        findings: list[tuple[str, dict[str, Any]]] = []
        missing: list[str] = []
        conflicts: list[dict[str, Any]] = []

        def add(outcome: str, issue: dict[str, Any]) -> None:
            findings.append((outcome, issue))

        # Contract/version and authority failures have highest priority.
        if snapshot.get("frozen_billable_profile_mutated"):
            add("REJECT_CONTRACT_IMMUTABILITY", self._issue(
                "M2.FROZEN_PROFILE_MUTATION",
                "Frozen BILLABLE profile mutation is forbidden.",
                provenance_refs=self._source_refs(),
            ))

        if snapshot.get("profile_id") != PROFILE_ID or snapshot.get("solver_version") != SOLVER_IMPLEMENTATION_VERSION:
            add("UNSUPPORTED_CONTRACT_VERSION", self._issue(
                "M2.UNSUPPORTED_PROFILE_VERSION",
                "Unsupported M2 engineering profile or Solver identity.",
                provenance_refs=self._source_refs(),
                state_effect="UNSUPPORTED_CASE",
                category="CAPABILITY",
            ))

        if snapshot.get("parser_claim_injection"):
            add("REJECT", self._issue(
                "M2.AUTHORITY_LAUNDERING",
                "Measurement policy cannot be supplied as Parser evidence.",
                provenance_refs=self._source_refs(),
                category="POLICY",
            ))

        if snapshot.get("duplicate_canonical_facts"):
            fields = snapshot["duplicate_canonical_facts"]
            path = "/parameters/" + str(fields[0].get("field", "unknown"))
            conflicts.append({
                "field_path": path,
                "claim_refs": ["claim:test:duplicate-a", "claim:test:duplicate-b"],
            })
            add("UNRESOLVED", self._issue(
                "M2.DUPLICATE_CANONICAL_FACT",
                "Duplicate or conflicting canonical facts require resolution.",
                field_path=path,
                provenance_refs=self._source_refs(),
                state_effect="UNRESOLVED",
                category="CONFLICT",
            ))

        # Policy gate is intentionally evaluated even while slab/mix remain blocked,
        # so policy defects cannot hide behind an unrelated geometry blocker.
        policy_outcome, _ = self._policy_validation(snapshot)
        if policy_outcome:
            add(policy_outcome, self._issue(
                "M2.POLICY_NOT_ADMISSIBLE",
                f"Measurement-policy gate outcome: {policy_outcome}.",
                field_path="/policies",
                provenance_refs=self._source_refs(),
                state_effect="UNRESOLVED" if policy_outcome == "UNRESOLVED" else "BLOCKED",
                category="POLICY",
            ))

        # Stale/malformed provenance likewise takes precedence over ordinary
        # missing-geometry blocking.
        provenance_outcome = self._transitive_provenance_validation(snapshot)
        if provenance_outcome:
            add(provenance_outcome, self._issue(
                "M2.PROVENANCE_NOT_ADMISSIBLE",
                f"Transitive provenance gate outcome: {provenance_outcome}.",
                provenance_refs=self._source_refs(),
                category="SOURCE_EVIDENCE",
            ))

        geometry_outcome, geometry_missing, geometry_conflicts = self._geometry_validation(snapshot)
        missing.extend(geometry_missing)
        conflicts.extend(geometry_conflicts)
        if geometry_outcome:
            effect = "UNRESOLVED" if geometry_outcome == "UNRESOLVED" else (
                "REVIEW_REQUIRED" if geometry_outcome == "REVIEW_REQUIRED/BLOCKED" else "BLOCKED"
            )
            add(geometry_outcome, self._issue(
                "M2.GEOMETRY_NOT_ADMISSIBLE",
                f"Geometry gate outcome: {geometry_outcome}.",
                field_path=geometry_missing[0] if geometry_missing else "/parameters",
                provenance_refs=self._source_refs(),
                state_effect=effect,
                category="SOURCE_EVIDENCE",
            ))

        # Support conservation can be tested only when its required geometry is
        # present and ready; otherwise the geometry gate owns the failure.
        g = snapshot.get("geometry", {})
        support_ready = all(
            isinstance(g.get(k), dict)
            and g[k].get("state") == "READY"
            and g[k].get("value") is not None
            for k in READY_GEOMETRY_EXCEPT_SLAB
        )
        support_outcome = None
        if support_ready:
            support_outcome = self._support_guard_validation(snapshot)
            if support_outcome:
                add(support_outcome, self._issue(
                    "M2.SUPPORT_WIDTH_CONSERVATION",
                    "Support-width conservation guard failed.",
                    field_path="/guards/support_width_conservation",
                    provenance_refs=self._source_refs(),
                ))

        mix_outcome = self._mix_guard_validation(snapshot)
        if mix_outcome:
            add(mix_outcome, self._issue(
                "M2.BEAM_SLAB_MIX_APPLICABILITY",
                "Beam/slab mix applicability remains unresolved.",
                field_path="/guards/beam_slab_mix_compatibility",
                provenance_refs=self._source_refs(),
                category="POLICY",
            ))

        # Choose a deterministic primary outcome while retaining all issues.
        priority = [
            "REJECT_CONTRACT_IMMUTABILITY",
            "UNSUPPORTED_CONTRACT_VERSION",
            "REJECT",
            "UNRESOLVED",
            "BLOCKED_STALE_SOURCE",
            "INVALID/BLOCKED",
            "REVIEW_REQUIRED/BLOCKED",
            "BLOCKED_PENDING_PO_POLICY",
            "BLOCKED",
            "BLOCKED_BEAM_SLAB_MIX_APPLICABILITY",
        ]
        outcomes = [o for o, _ in findings]
        outcome = next((x for x in priority if x in outcomes), None)
        if outcome is None:
            outcome = "BLOCKED_PENDING_M2_2_POSITIVE_GATE"
            add(outcome, self._issue(
                "M2.POSITIVE_EXECUTION_NOT_AUTHORIZED",
                "M2-IMPL-G01 forbids successful CalculationInput emission in this implementation round.",
                provenance_refs=self._source_refs(),
            ))

        attempt = self._build_attempt(
            meta,
            outcome=outcome,
            missing_fields=missing,
            conflicts=conflicts,
            issues=[issue for _, issue in findings],
        )
        return {
            "profile_id": PROFILE_ID,
            "profile_registry_version": PROFILE_REGISTRY_VERSION,
            "solver_contract_version": SOLVER_CONTRACT_VERSION,
            "solver_implementation_version": SOLVER_IMPLEMENTATION_VERSION,
            "formula_id": FORMULA_ID,
            "formula_version": FORMULA_VERSION,
            "output_stage": OUTPUT_STAGE,
            "engineering_input_digest": engineering_digest,
            "outcome": outcome,
            "all_gate_outcomes": outcomes,
            "support_width_guard": {
                "guard_id": SUPPORT_GUARD_ID,
                "guard_version": SUPPORT_GUARD_VERSION,
                "mode": SUPPORT_GUARD_MODE,
                "status": "PASS" if support_outcome is None and support_ready else "BLOCKED",
            },
            "beam_slab_mix_guard": {
                "guard_id": MIX_GUARD_ID,
                "guard_version": MIX_GUARD_VERSION,
                "status": "PASS" if mix_outcome is None else "BLOCKED",
                "reviewed_evidence_binding_id": (
                    MIX_EVIDENCE_BINDING_ID if mix_outcome is None else None
                ),
            },
            "calculation_attempt": attempt,
            "calculation_input": None,
            "solver_called": False,
            "positive_execution_enabled": POSITIVE_EXECUTION_ENABLED,
        }
