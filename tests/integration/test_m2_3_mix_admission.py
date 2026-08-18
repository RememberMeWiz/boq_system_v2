from __future__ import annotations

import copy
import json
import unittest
import tempfile
import shutil
from pathlib import Path

from backend.integration.m2_2_rc_beam_profile import (
    IntegrationBoundaryError,
    M2RcBeamNetMeasuredRuntime,
    M2RequestMetadata,
    POSITIVE_EXECUTION_ENABLED,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas/integration"
M23 = ROOT / "tests/integration/m2_3"
M22 = ROOT / "tests/integration/m2_2"

ACCEPTED = json.loads((M23 / "accepted_mix_slab_blocked_snapshot_v1.json").read_text())
M22_BLOCKED = json.loads((M22 / "base_blocked_readiness_snapshot_v1.json").read_text())


class M23MixAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.runtime = M2RcBeamNetMeasuredRuntime(SCHEMA_DIR)

    def snapshot(self):
        return copy.deepcopy(ACCEPTED)

    def binding(self, snap):
        return snap["guards"]["beam_slab_mix_compatibility"]["reviewed_evidence_binding"]

    def evaluate(self, snap=None, meta=None):
        return self.runtime.evaluate(self.snapshot() if snap is None else snap, meta)

    def assert_reject(self, snap):
        result = self.evaluate(snap)
        self.assertEqual(result["outcome"], "REJECT")
        self.assertIsNone(result["calculation_input"])
        self.assertFalse(result["solver_called"])
        return result

    def test_01_exact_reviewed_mix_evidence_admits_guard(self):
        result = self.evaluate()
        self.assertEqual(result["beam_slab_mix_guard"]["status"], "PASS")
        self.assertEqual(
            result["beam_slab_mix_guard"]["reviewed_evidence_binding_id"],
            "M2-3.MIX.B1.SAME_OR_EQUIVALENT/1.0",
        )
        self.assertNotIn("BLOCKED_BEAM_SLAB_MIX_APPLICABILITY", result["all_gate_outcomes"])

    def test_02_exact_reviewed_mix_plus_slab_missing_stays_blocked(self):
        snap = self.snapshot()
        snap["geometry"]["slab.thickness"] = {
            "value": None, "unit": "m", "dimension": "LENGTH", "state": "MISSING_BLOCKED"
        }
        result = self.evaluate(snap)
        self.assertEqual(result["outcome"], "BLOCKED")
        self.assertEqual(result["beam_slab_mix_guard"]["status"], "PASS")
        self.assertIn("/parameters/slab.thickness", result["calculation_attempt"]["missing_fields"])

    def test_03_exact_reviewed_mix_plus_slab_ambiguous_stays_blocked(self):
        result = self.evaluate()
        self.assertEqual(result["outcome"], "BLOCKED")
        self.assertEqual(result["calculation_attempt"]["missing_fields"], ["/parameters/slab.thickness"])
        codes = {x["code"] for x in result["calculation_attempt"]["issues"]}
        self.assertEqual(codes, {"M2.GEOMETRY_NOT_ADMISSIBLE"})

    def test_04_synthetic_same_mix_without_binding_rejects(self):
        snap = self.snapshot()
        g = snap["guards"]["beam_slab_mix_compatibility"]
        g["mix_state"] = "SAME_MIX"
        g.pop("reviewed_evidence_binding")
        self.assert_reject(snap)

    def test_05_synthetic_ready_without_binding_rejects(self):
        snap = self.snapshot()
        g = snap["guards"]["beam_slab_mix_compatibility"]
        g["mix_state"] = "READY"
        g.pop("reviewed_evidence_binding")
        self.assert_reject(snap)

    def test_06_mix_evidence_sha_drift_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["evidence_identity"]["mix_evidence_sha256"] = "0" * 64
        self.assert_reject(snap)

    def test_07_parser_r3_package_sha_drift_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["evidence_identity"]["parser_r3_package_sha256"] = "1" * 64
        self.assert_reject(snap)

    def test_08_source_document_sha_drift_in_binding_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["evidence_identity"]["source_document_sha256"] = "2" * 64
        self.assert_reject(snap)

    def test_09_missing_reviewed_authority_marker_rejects(self):
        snap = self.snapshot()
        self.binding(snap).pop("review_state")
        self.assert_reject(snap)

    def test_10_wrong_selected_instance_in_binding_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["selected_instance_id"] = "OTHER-BEAM"
        self.assert_reject(snap)

    def test_11_wrong_element_id_rejects_before_attempt(self):
        with self.assertRaises(IntegrationBoundaryError) as cm:
            self.evaluate(meta=M2RequestMetadata(element_id="element:OTHER-BEAM"))
        self.assertEqual(cm.exception.code, "M2_SELECTED_INSTANCE_MISMATCH")

    def test_12_wrong_element_type_rejects_before_attempt(self):
        with self.assertRaises(IntegrationBoundaryError) as cm:
            self.evaluate(meta=M2RequestMetadata(element_type="RC_COLUMN"))
        self.assertEqual(cm.exception.code, "M2_ELEMENT_TYPE_MISMATCH")

    def test_13_conflicting_mix_evidence_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["conflict_state"] = "CONFLICTING"
        self.assert_reject(snap)

    def test_14_policy_id_drift_rejects(self):
        snap = self.snapshot()
        snap["policies"]["slab_intersection_owner"]["policy_id"] = "POLICY.RC_BEAM.BAD"
        self.assert_reject(snap)

    def test_15_policy_version_drift_rejects(self):
        snap = self.snapshot()
        snap["policies"]["slab_intersection_owner"]["policy_version"] = "9.9.9"
        self.assert_reject(snap)

    def test_16_support_width_guard_drift_rejects(self):
        snap = self.snapshot()
        snap["guards"]["support_width_conservation"]["mode"] = "OTHER"
        self.assert_reject(snap)

    def test_17_provenance_edge_loss_rejects(self):
        snap = self.snapshot()
        snap["provenance_mutation"] = {
            "claim_id": "claim-m2p-clear-span",
            "remove_input_claim_id": "claim-m2p-p33-local-x-scale",
        }
        result = self.evaluate(snap)
        self.assertEqual(result["outcome"], "INVALID/BLOCKED")
        self.assertIsNone(result["calculation_input"])
        self.assertFalse(result["solver_called"])

    def test_18_stale_parser_qa_evidence_binding_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["reviewed_authority"]["parser_qa"]["package_sha256"] = "3" * 64
        self.assert_reject(snap)

    def test_19_unit_dimension_drift_rejects(self):
        snap = self.snapshot()
        snap["geometry"]["width"]["unit"] = "mm"
        snap["geometry"]["width"]["dimension"] = "MASS"
        result = self.evaluate(snap)
        self.assertEqual(result["outcome"], "INVALID/BLOCKED")

    def test_20_no_hidden_same_mix_default(self):
        result = self.runtime.evaluate(copy.deepcopy(M22_BLOCKED))
        self.assertEqual(result["beam_slab_mix_guard"]["status"], "BLOCKED")
        codes = {x["code"] for x in result["calculation_attempt"]["issues"]}
        self.assertIn("M2.BEAM_SLAB_MIX_APPLICABILITY", codes)

    def test_21_no_hidden_slab_default(self):
        snap = self.snapshot()
        self.assertIsNone(snap["geometry"]["slab.thickness"]["value"])
        result = self.evaluate(snap)
        self.assertIsNone(result["calculation_input"])
        self.assertIn("/parameters/slab.thickness", result["calculation_attempt"]["missing_fields"])

    def test_22_malformed_slab_sentence_never_becomes_exact(self):
        snap = self.snapshot()
        slab = snap["geometry"]["slab.thickness"]
        slab["value"] = "0.10"
        slab["state"] = "READY"
        slab["source"] = "AMBIGUOUS_MALFORMED_SOURCE_STATEMENT"
        result = self.evaluate(snap)
        self.assertEqual(result["outcome"], "BLOCKED")
        self.assertIsNone(result["calculation_input"])
        self.assertFalse(result["solver_called"])

    def test_23_lower_bound_slab_note_never_becomes_exact(self):
        snap = self.snapshot()
        slab = snap["geometry"]["slab.thickness"]
        slab["value"] = "0.10"
        slab["state"] = "READY"
        slab["source"] = "FORBIDDEN_LOWER_BOUND_AS_EXACT"
        result = self.evaluate(snap)
        self.assertEqual(result["outcome"], "REJECT")
        self.assertIsNone(result["calculation_input"])

    def test_24_no_calculation_input_while_slab_unresolved(self):
        self.assertIsNone(self.evaluate()["calculation_input"])

    def test_25_no_solver_call_while_slab_unresolved(self):
        self.assertFalse(self.evaluate()["solver_called"])

    def test_26_mix_guard_id_drift_rejects(self):
        snap = self.snapshot()
        snap["guards"]["beam_slab_mix_compatibility"]["guard_id"] = "GUARD-BAD"
        self.assert_reject(snap)

    def test_27_mix_guard_version_drift_rejects(self):
        snap = self.snapshot()
        snap["guards"]["beam_slab_mix_compatibility"]["guard_version"] = "2.0"
        self.assert_reject(snap)

    def test_28_accepted_disposition_drift_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["accepted_disposition"] = "READY"
        self.assert_reject(snap)

    def test_29_source_git_blob_drift_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["evidence_identity"]["source_document_git_blob_sha1"] = "f" * 40
        self.assert_reject(snap)

    def test_30_superseded_evidence_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["superseded"] = True
        self.binding(snap)["superseded_by"] = "replacement:test"
        self.assert_reject(snap)

    def test_31_replacement_evidence_ref_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["replacement_evidence_ref"] = "replacement:test"
        self.assert_reject(snap)

    def test_32_parser_qa_role_drift_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["reviewed_authority"]["parser_qa"]["role"] = "Parser"
        self.assert_reject(snap)

    def test_33_pm_verdict_drift_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["reviewed_authority"]["project_manager"]["verdict"] = "PENDING"
        self.assert_reject(snap)

    def test_34_provenance_ref_loss_rejects(self):
        snap = self.snapshot()
        self.binding(snap)["provenance_refs"].pop()
        self.assert_reject(snap)

    def test_35_bare_accepted_semantic_without_binding_rejects(self):
        snap = self.snapshot()
        snap["guards"]["beam_slab_mix_compatibility"].pop("reviewed_evidence_binding")
        self.assert_reject(snap)

    def test_36_positive_execution_kill_switch_remains_disabled(self):
        self.assertFalse(POSITIVE_EXECUTION_ENABLED)
        result = self.evaluate()
        self.assertFalse(result["positive_execution_enabled"])
        self.assertFalse(result["calculation_attempt"]["canonical_input_ready"])
        self.assertFalse(result["calculation_attempt"]["may_calculate"])


    def _runtime_with_binding_mutation(self, mutate):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "integration"
            shutil.copytree(SCHEMA_DIR, target)
            path = target / "m2_3_reviewed_mix_evidence_binding_v1.json"
            data = json.loads(path.read_text())
            mutate(data)
            path.write_text(json.dumps(data, indent=2) + "\n")
            with self.assertRaises(IntegrationBoundaryError):
                M2RcBeamNetMeasuredRuntime(target)

    def test_37_static_binding_digest_drift_rejects(self):
        self._runtime_with_binding_mutation(
            lambda data: data.__setitem__("request_binding_digest", "sha256:" + "0" * 64)
        )

    def test_38_static_parser_package_identity_drift_rejects(self):
        self._runtime_with_binding_mutation(
            lambda data: data["request_binding"]["evidence_identity"].__setitem__(
                "parser_r3_package_sha256", "4" * 64
            )
        )

    def test_39_static_review_authority_drift_rejects(self):
        self._runtime_with_binding_mutation(
            lambda data: data["request_binding"]["reviewed_authority"]["project_manager"].__setitem__(
                "role", "Other"
            )
        )

    def test_40_static_provenance_ref_drift_rejects(self):
        self._runtime_with_binding_mutation(
            lambda data: data["request_binding"].__setitem__("provenance_refs", [])
        )



if __name__ == "__main__":
    unittest.main()
