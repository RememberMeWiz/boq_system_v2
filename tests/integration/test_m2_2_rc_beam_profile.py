import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.integration.m2_2_rc_beam_profile import (
    M2RcBeamNetMeasuredRuntime,
    M2RequestMetadata,
    PROFILE_ID,
    SOLVER_IMPLEMENTATION_VERSION,
    FROZEN_BILLABLE_BLOB_SHA,
)

SCHEMA_DIR = ROOT / "schemas/integration"
M2_DIR = Path(__file__).with_name("m2_2")
BASE = json.loads((M2_DIR / "base_blocked_readiness_snapshot_v1.json").read_text())
MANIFEST = json.loads((M2_DIR / "negative_fixture_manifest_v1.json").read_text())


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


class M2ProfileTests(unittest.TestCase):
    def setUp(self):
        self.runtime = M2RcBeamNetMeasuredRuntime(SCHEMA_DIR)

    def evaluate(self, payload=None):
        return self.runtime.evaluate(copy.deepcopy(payload if payload is not None else BASE))

    def test_current_authoritative_path_is_blocked_for_both_intended_reasons(self):
        result = self.evaluate()
        self.assertEqual(result["outcome"], "BLOCKED")
        self.assertFalse(result["positive_execution_enabled"])
        self.assertFalse(result["solver_called"])
        self.assertIsNone(result["calculation_input"])
        attempt = result["calculation_attempt"]
        self.assertEqual(attempt["disposition_state"], "BLOCKED")
        self.assertFalse(attempt["canonical_input_ready"])
        self.assertFalse(attempt["may_calculate"])
        self.assertIn("/parameters/slab.thickness", attempt["missing_fields"])
        codes = {x["code"] for x in attempt["issues"]}
        self.assertIn("M2.GEOMETRY_NOT_ADMISSIBLE", codes)
        self.assertIn("M2.BEAM_SLAB_MIX_APPLICABILITY", codes)

    def test_current_attempt_validates_against_accepted_solver_schema(self):
        attempt = self.evaluate()["calculation_attempt"]
        names = [
            "calculation_attempt.schema.json",
            "solver_issue.schema.json",
            "policy_ref.schema.json",
        ]
        schemas = {n: json.loads((Path(__file__).parent / n).read_text()) for n in names}
        store = {s["$id"]: s for s in schemas.values()}
        schema = schemas["calculation_attempt.schema.json"]
        Draft202012Validator(
            schema,
            resolver=RefResolver.from_schema(schema, store=store),
        ).validate(attempt)

    def test_five_po_policy_bindings_exact(self):
        bundle = json.loads((SCHEMA_DIR / "m2_2_approved_measurement_policy_bindings_v1.json").read_text())
        self.assertEqual(bundle["binding_count"], 5)
        actual = {
            x["canonical_name"]: (x["policy_id"], x["policy_version"], x["selected_project_value"])
            for x in bundle["bindings"]
        }
        expected = {
            "support_intersection_owner": ("POLICY.RC_BEAM.SUPPORT_INTERSECTION_OWNER", "1.0.0", "support"),
            "support_deduction_scope": ("POLICY.RC_BEAM.SUPPORT_DEDUCTION_SCOPE", "1.0.0", "full_cross_section"),
            "slab.measured_separately_across_clear_span_beam_strip": ("POLICY.RC_BEAM.SLAB_SEPARATE_CLEAR_SPAN_STRIP", "1.0.0", True),
            "slab_intersection_owner": ("POLICY.RC_BEAM.SLAB_INTERSECTION_OWNER", "1.0.0", "slab"),
            "slab_deduction_length_basis": ("POLICY.RC_BEAM.SLAB_DEDUCTION_LENGTH_BASIS", "1.0.0", "clear_span"),
        }
        self.assertEqual(actual, expected)

    def test_support_width_conservation_guard(self):
        self.assertIsNone(self.runtime._support_guard_validation(BASE))
        g = self.runtime.support_guard["conservation"]
        physical = __import__("decimal").Decimal(g["physical_support_overlap_volume_m3"])
        shoulder = __import__("decimal").Decimal(g["shoulder_junction_volume_m3"])
        notional = __import__("decimal").Decimal(g["notional_support_owned_volume_m3"])
        self.assertEqual(physical + shoulder, notional)
        self.assertEqual(shoulder, __import__("decimal").Decimal("0.0105"))

    def test_support_width_guard_fails_on_conservation_drift(self):
        original = self.runtime.support_guard["conservation"]["shoulder_junction_volume_m3"]
        try:
            self.runtime.support_guard["conservation"]["shoulder_junction_volume_m3"] = "0"
            self.assertEqual(self.runtime._support_guard_validation(BASE), "REJECT")
        finally:
            self.runtime.support_guard["conservation"]["shoulder_junction_volume_m3"] = original

    def test_mix_guard_remains_fail_closed(self):
        self.assertEqual(
            self.runtime._mix_guard_validation(BASE),
            "BLOCKED_BEAM_SLAB_MIX_APPLICABILITY",
        )

    def test_transitive_provenance_gate_passes_authoritative_ready_geometry(self):
        self.assertIsNone(self.runtime._transitive_provenance_validation(BASE))

    def test_positive_gate_stays_disabled_even_if_test_data_fills_blockers(self):
        x = copy.deepcopy(BASE)
        x["geometry"]["slab.thickness"] = {
            "value": "0.15", "unit": "m", "dimension": "LENGTH",
            "state": "READY", "source": "TEST_ONLY_NOT_AUTHORIZED",
        }
        x["guards"]["beam_slab_mix_compatibility"] = {
            "state": "READY", "mix_state": "SAME_MIX",
            "beam_mix_id": "MIX.TEST", "slab_mix_id": "MIX.TEST",
        }
        result = self.runtime.evaluate(x)
        self.assertFalse(result["positive_execution_enabled"])
        self.assertIsNone(result["calculation_input"])
        self.assertFalse(result["solver_called"])
        self.assertFalse(result["calculation_attempt"]["may_calculate"])

    def test_all_30_fixtures_hash_match_manifest(self):
        self.assertEqual(MANIFEST["case_count"], 30)
        for item in MANIFEST["fixtures"]:
            p = M2_DIR / item["file"]
            self.assertTrue(p.exists(), item["case_id"])
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), item["sha256"])

    def test_all_30_negative_fixtures_execute_expected_outcomes(self):
        base_digest = self.runtime.engineering_input_digest(BASE)
        self.assertEqual(len(MANIFEST["fixtures"]), 30)
        for item in MANIFEST["fixtures"]:
            fixture = json.loads((M2_DIR / item["file"]).read_text())
            self.assertTrue(fixture["test_mutation_only"], item["case_id"])
            payload = fixture["payload"]
            result = self.runtime.evaluate(payload)
            expected = fixture["expected"]
            if expected == "NET_MEASURED_AND_DIGEST_UNCHANGED":
                self.assertEqual(result["engineering_input_digest"], base_digest, item["case_id"])
                self.assertIsNone(result["calculation_input"], item["case_id"])
            else:
                self.assertEqual(result["outcome"], expected, item["case_id"])

    def test_commercial_mutations_do_not_change_engineering_digest(self):
        baseline = self.runtime.engineering_input_digest(BASE)
        for case_id in ("NEG-20", "NEG-21", "NEG-22", "NEG-23"):
            fixture = json.loads((M2_DIR / f"negative/{case_id}.json").read_text())
            self.assertEqual(self.runtime.engineering_input_digest(fixture["payload"]), baseline)

    def test_frozen_billable_profile_entry_is_semantically_unchanged(self):
        v1 = json.loads((SCHEMA_DIR / "solver_input_profile_registry_v1.json").read_text())
        v11 = json.loads((SCHEMA_DIR / "solver_input_profile_registry_v1_1.json").read_text())
        self.assertEqual(v1["profiles"]["rc_beam.concrete_volume/1.0"], v11["frozen_existing_profile"]["entry"])
        self.assertEqual(
            v11["frozen_existing_profile"]["source_blob_sha"],
            FROZEN_BILLABLE_BLOB_SHA,
        )
        self.assertFalse(v11["frozen_existing_profile"]["mutation_authorized"])

    def test_additive_profile_is_non_production_and_blocked(self):
        reg = json.loads((SCHEMA_DIR / "solver_input_profile_registry_v1_1.json").read_text())
        p = reg["additive_profile"]
        self.assertEqual(p["profile_id"], PROFILE_ID)
        self.assertEqual(p["implementation_state"], "NON_PRODUCTION_BLOCKED")
        self.assertFalse(p["calculation_input_ready"])
        self.assertFalse(p["may_calculate"])
        self.assertFalse(p["solver_invocation_authorized"])
        self.assertFalse(p["production_activation_authorized"])

    def test_solver_reference_provenance_is_pinned_and_legacy_solver_excluded(self):
        ident = json.loads((SCHEMA_DIR / "m2_2_solver_implementation_identity_v1.json").read_text())
        self.assertEqual(ident["repository_base_commit"], "c03cc3b49c9a8ada46221c55296f620b5d8fd844")
        ref = ident["accepted_deterministic_reference"]
        self.assertEqual(ref["generator"]["git_blob_sha"], "f9bffc9d809ae1565da2aeed4bc558694e5b2b47")
        self.assertEqual(ref["independent_audit"]["git_blob_sha"], "31bba2c5feb5656fe96a1aa491503842f84d168b")
        self.assertEqual(ref["golden_input"]["git_blob_sha"], "70704662e4a752debdd5a4cc7a1d9dad70f8e0f8")
        self.assertEqual(ref["golden_expected"]["git_blob_sha"], "476f9a03c2d708b722367148575b0c48d5cec48e")
        self.assertEqual(ref["golden_spec"]["git_blob_sha"], "fea069e642223e494a981f72c5215f5261108449")
        legacy = ident["legacy_production_solver_exclusion"]
        self.assertEqual(legacy["path"], "backend/engine/fajardo.py")
        self.assertEqual(legacy["git_blob_sha"], "3405e8103ac0e890fd05c869345e3967fc55b3c8")
        self.assertFalse(legacy["invoked_by_m2_2"])

    def test_no_hidden_slab_or_same_mix_default_in_runtime(self):
        source = (ROOT / "backend/integration/m2_2_rc_beam_profile.py").read_text().lower()
        forbidden = [
            'slab.thickness": {"value": "0.1"',
            "assume_same_mix",
            "default_slab_thickness",
            "typical_slab_thickness",
            "0.729000",
        ]
        for token in forbidden:
            self.assertNotIn(token, source)

    def test_attempt_hash_is_deterministic(self):
        a = self.evaluate()["calculation_attempt"]
        b = self.evaluate()["calculation_attempt"]
        self.assertEqual(a["attempt_hash"], b["attempt_hash"])
        self.assertEqual(a["attempt_id"], b["attempt_id"])

    def test_metadata_validation_rejects_bad_identifier(self):
        with self.assertRaises(Exception):
            self.runtime.evaluate(BASE, M2RequestMetadata(request_id="BAD"))

    def test_m2_qa_b01_wrong_selected_instance_rejected_before_attempt(self):
        with self.assertRaisesRegex(Exception, "M2_SELECTED_INSTANCE_MISMATCH"):
            self.runtime.evaluate(
                BASE,
                M2RequestMetadata(
                    element_id="element:OTHER-BEAM",
                    element_type="RC_BEAM",
                ),
            )

    def test_m2_qa_b01_wrong_element_type_rejected_before_attempt(self):
        with self.assertRaisesRegex(Exception, "M2_ELEMENT_TYPE_MISMATCH"):
            self.runtime.evaluate(
                BASE,
                M2RequestMetadata(
                    element_id="element:B1-P33-S6-UPPER-LEFT-C4-PC4",
                    element_type="RC_COLUMN",
                ),
            )

    def test_m2_qa_b01_wrong_instance_and_type_rejected_before_attempt(self):
        with self.assertRaisesRegex(Exception, "M2_SELECTED_INSTANCE_MISMATCH"):
            self.runtime.evaluate(
                BASE,
                M2RequestMetadata(
                    element_id="element:OTHER-BEAM",
                    element_type="RC_COLUMN",
                ),
            )


    def test_r2_clear_span_numeric_drift_with_same_labels_is_rejected(self):
        x = copy.deepcopy(BASE)
        x["geometry"]["clear_span_between_support_faces"]["value"] = "9.999"
        result = self.evaluate(x)
        self.assertEqual(result["outcome"], "INVALID/BLOCKED")
        self.assertIsNone(result["calculation_input"])
        self.assertFalse(result["solver_called"])

    def test_r2_left_support_numeric_drift_is_rejected(self):
        x = copy.deepcopy(BASE)
        x["geometry"]["left_support.dimension_along_beam"]["value"] = "0.900"
        self.assertEqual(self.runtime._transitive_provenance_validation(x), "INVALID/BLOCKED")
        result = self.evaluate(x)
        self.assertIn(result["outcome"], {"INVALID/BLOCKED", "REJECT"})
        self.assertEqual(result["support_width_guard"]["status"], "BLOCKED")

    def test_r2_right_support_numeric_drift_is_rejected(self):
        x = copy.deepcopy(BASE)
        x["geometry"]["right_support.dimension_along_beam"]["value"] = "0.900"
        self.assertEqual(self.runtime._transitive_provenance_validation(x), "INVALID/BLOCKED")
        result = self.evaluate(x)
        self.assertIn(result["outcome"], {"INVALID/BLOCKED", "REJECT"})
        self.assertEqual(result["support_width_guard"]["status"], "BLOCKED")

    def test_r2_width_and_depth_drift_rejected_through_i1_binding(self):
        for key, value in (("width", "0.9"), ("depth", "0.9")):
            x = copy.deepcopy(BASE)
            x["geometry"][key]["value"] = value
            with self.subTest(key=key):
                self.assertEqual(self.runtime._transitive_provenance_validation(x), "INVALID/BLOCKED")
                result = self.evaluate(x)
                self.assertIn(result["outcome"], {"INVALID/BLOCKED", "REJECT"})
                self.assertIsNone(result["calculation_input"])

    def test_r2_derived_geometry_identity_drift_is_rejected(self):
        x = copy.deepcopy(BASE)
        x["geometry"]["clear_span_between_support_faces"]["claim_id"] = "claim:test:laundered"
        self.assertEqual(self.evaluate(x)["outcome"], "INVALID/BLOCKED")

    def test_r2_support_guard_consumes_admitted_request_geometry(self):
        x = copy.deepcopy(BASE)
        x["geometry"]["width"]["value"] = "0.25"
        self.assertEqual(self.runtime._support_guard_validation(x), "REJECT")

    def test_r2_support_transverse_width_is_source_evidence_bound(self):
        claim_id = self.runtime.support_guard["authoritative_transverse_support_binding"]["claim_id"]
        original = self.runtime.claim_graph["claims"][claim_id]["value"]
        try:
            self.runtime.claim_graph["claims"][claim_id]["value"] = 0.16
            self.assertEqual(self.runtime._support_guard_validation(BASE), "REJECT")
        finally:
            self.runtime.claim_graph["claims"][claim_id]["value"] = original

    def test_r2_revoked_policy_approval_state_is_rejected(self):
        x = copy.deepcopy(BASE)
        x["policies"]["support_intersection_owner"]["approval_state"] = "REVOKED"
        self.assertEqual(self.evaluate(x)["outcome"], "REJECT")

    def test_r2_missing_policy_approval_state_or_source_is_rejected(self):
        for field in ("approval_state", "approval_source"):
            x = copy.deepcopy(BASE)
            del x["policies"]["support_intersection_owner"][field]
            with self.subTest(field=field):
                self.assertEqual(self.evaluate(x)["outcome"], "REJECT")

    def test_r2_policy_decision_or_package_identity_drift_is_rejected(self):
        x = copy.deepcopy(BASE)
        x["policies"]["support_intersection_owner"]["decision_id"] = "PO-M2-POL-999"
        self.assertEqual(self.evaluate(x)["outcome"], "REJECT")
        y = copy.deepcopy(BASE)
        y["policies"]["support_intersection_owner"]["approval_source"]["package_sha256"] = "0" * 64
        self.assertEqual(self.evaluate(y)["outcome"], "REJECT")

    def test_r2_policy_bundle_must_equal_additive_profile_bindings(self):
        original = self.runtime.policy_bundle["bindings"][0]["selected_project_value"]
        try:
            self.runtime.policy_bundle["bindings"][0]["selected_project_value"] = "beam"
            with self.assertRaises(Exception):
                self.runtime._validate_static_contract()
        finally:
            self.runtime.policy_bundle["bindings"][0]["selected_project_value"] = original

    def test_r2_required_guard_id_version_drift_fails_static_contract(self):
        binding = self.runtime.profile_registry["additive_profile"]["required_guard_bindings"][0]
        original = binding["guard_version"]
        try:
            binding["guard_version"] = "9.9"
            with self.assertRaises(Exception):
                self.runtime._validate_static_contract()
        finally:
            binding["guard_version"] = original

    def test_r2_attempt_source_refs_include_i1_width_depth_and_m2_geometry(self):
        refs = set(self.evaluate()["calculation_attempt"]["source_refs"])
        required = {
            "source:claim:claim-001-b1-width",
            "source:claim:claim-001-b1-depth",
            "source:claim:claim-m2p-clear-span",
            "source:claim:claim-m2p-left-support-dim",
            "source:claim:claim-m2p-right-support-dim",
        }
        self.assertTrue(required.issubset(refs))

    def test_r2_current_authoritative_path_remains_fail_closed(self):
        result = self.evaluate()
        self.assertEqual(result["outcome"], "BLOCKED")
        self.assertIsNone(result["calculation_input"])
        self.assertFalse(result["solver_called"])
        self.assertFalse(result["calculation_attempt"]["canonical_input_ready"])
        self.assertFalse(result["calculation_attempt"]["may_calculate"])

if __name__ == "__main__":
    unittest.main()
