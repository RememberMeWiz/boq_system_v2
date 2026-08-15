import copy
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.integration.rc_beam_boundary import (
    IntegrationBoundaryError,
    RcBeamIntegrationBoundary,
    SolverAssemblyConfig,
)

SCHEMA_DIR = ROOT / "schemas/integration"
FIXTURE = Path(__file__).with_name("versioned_parser_claims_p0_006.json")
CLAIMS = json.loads(FIXTURE.read_text())
BY_ID = {x["claim_id"]: x for x in CLAIMS}

POLICY = {
    "policy_id": "POLICY.MEASUREMENT.OWNERSHIP",
    "policy_role": "MEASUREMENT_OWNERSHIP",
    "policy_version": "1.0.0",
}
CONFIG = SolverAssemblyConfig(
    element_id="element:beam-B1",
    element_type="RC_BEAM",
    formula_id="FORMULA.RC_BEAM.CONCRETE_VOLUME",
    formula_version="1.0.0",
    policy_refs=(POLICY,),
    solver_version="solver-kernel/0.0.0-readiness",
    requested_output_stage="BILLABLE",
    precision_policy={
        "application": "NO_ROUNDING",
        "policy_id": "POLICY.ROUNDING.EXACT_CAPTURE",
        "policy_version": "1.0.0",
        "rounding_mode": "NONE",
        "scale": 6,
    },
    source_quantity_state="EXPLICIT_INPUT",
    rounding_state="UNROUNDED",
)

def claim(cid):
    return copy.deepcopy(BY_ID[cid])

class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.boundary = RcBeamIntegrationBoundary(SCHEMA_DIR, CONFIG)

    def assert_rejects(self, code, fn):
        with self.assertRaises(IntegrationBoundaryError) as ctx:
            fn()
        self.assertEqual(ctx.exception.code, code)

    def valid_rows(self):
        return [claim("claim-001-b1-width"), claim("claim-001-b1-depth")]

    def test_positive_width_normalization(self):
        f=self.boundary.canonicalize(claim("claim-001-b1-width"))
        self.assertEqual((f["source_value"],f["source_unit"],f["canonical_value"],f["canonical_unit"],f["dimension"]),
                         (200,"mm","0.2","m","LENGTH"))

    def test_positive_depth_normalization(self):
        f=self.boundary.canonicalize(claim("claim-001-b1-depth"))
        self.assertEqual(f["canonical_value"],"0.35")

    def test_attempt_first_blocked(self):
        out=self.boundary.assess_request(self.valid_rows(),"request:i1-001")
        a=out["calculation_attempt"]
        self.assertEqual(a["disposition_state"],"BLOCKED")
        self.assertFalse(a["canonical_input_ready"])
        self.assertFalse(a["may_calculate"])
        self.assertIsNone(out["calculation_input"])
        self.assertGreater(len(a["missing_fields"]),0)

    def test_every_request_has_hashed_attempt(self):
        a=self.boundary.assess_request(self.valid_rows(),"request:i1-001")["calculation_attempt"]
        self.assertRegex(a["attempt_hash"],r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(a["attempt_id"],"attempt:"+a["attempt_hash"])

    def test_canonical_fact_schema_validation(self):
        schema=json.loads((SCHEMA_DIR/"canonical_fact_v2.schema.json").read_text())
        validator=Draft202012Validator(schema)
        validator.validate(self.boundary.canonicalize(claim("claim-001-b1-width")))
        validator.validate(self.boundary.canonicalize(claim("claim-001-b1-depth")))

    def test_attempt_schema_validation(self):
        out=self.boundary.assess_request(self.valid_rows(),"request:i1-001")
        names=["calculation_attempt.schema.json","solver_issue.schema.json","policy_ref.schema.json"]
        schemas={n:json.loads(Path(__file__).with_name(n).read_text()) for n in names}
        store={s["$id"]:s for s in schemas.values()}
        sch=schemas["calculation_attempt.schema.json"]
        Draft202012Validator(sch,resolver=RefResolver.from_schema(sch,store=store)).validate(out["calculation_attempt"])

    def test_missing_dependencies_are_explicit(self):
        a=self.boundary.assess_request(self.valid_rows(),"request:i1-001")["calculation_attempt"]
        expected={
            "/parameters/clear_span_between_support_faces",
            "/parameters/left_support.dimension_along_beam",
            "/parameters/right_support.dimension_along_beam",
            "/policies/support_intersection_owner",
            "/policies/support_deduction_scope",
            "/parameters/slab.thickness",
            "/policies/slab.measured_separately_across_clear_span_beam_strip",
            "/policies/slab_intersection_owner",
            "/policies/slab_deduction_length_basis",
            "/policies/concrete_policy.waste_rate",
            "/policies/concrete_policy.waste_basis",
            "/policies/concrete_policy.procurement_increment",
            "/policies/concrete_policy.procurement_rounding",
        }
        self.assertEqual(set(a["missing_fields"]),expected)

    def test_project_direct_is_forbidden(self):
        self.assert_rejects("ATTEMPT_FIRST_REQUIRED",lambda:self.boundary.project(self.valid_rows()))

    def test_observed_claims_map_to_observed_source(self):
        out=self.boundary.assess_request(self.valid_rows(),"request:i1-001")
        self.assertEqual(out["source_quantity_states"],{"width":"OBSERVED_SOURCE","depth":"OBSERVED_SOURCE"})

    def test_global_config_cannot_relabel_observed_claims(self):
        cfg=copy.deepcopy(CONFIG)
        object.__setattr__(cfg,"source_quantity_state","POLICY_VALUE")
        out=RcBeamIntegrationBoundary(SCHEMA_DIR,cfg).assess_request(self.valid_rows(),"request:i1-001")
        self.assertEqual(out["source_quantity_states"]["width"],"OBSERVED_SOURCE")

    def test_parser_schema_extra_top_level_rejected(self):
        x=claim("claim-001-b1-width"); x["undeclared"]=True
        self.assert_rejects("INVALID_PARSER_CLAIM_SCHEMA",lambda:self.boundary.canonicalize(x))

    def test_parser_schema_nested_evidence_extra_rejected(self):
        x=claim("claim-001-b1-width"); x["evidence_ref"]["x"]=1
        self.assert_rejects("INVALID_PARSER_CLAIM_SCHEMA",lambda:self.boundary.canonicalize(x))

    def test_field_registry_empty_accepted_claims_rejected(self):
        self.boundary.field_registry["entries"]["beam_schedule.B1.width"]["accepted_claim_ids"]=[]
        self.assert_rejects("CLAIM_NOT_AUTHORIZED_FOR_FIELD",lambda:self.boundary.canonicalize(claim("claim-001-b1-width")))

    def test_field_registry_wrong_accepted_claim_rejected(self):
        self.boundary.field_registry["entries"]["beam_schedule.B1.width"]["accepted_claim_ids"]=["claim-001-b1-depth"]
        self.assert_rejects("CLAIM_NOT_AUTHORIZED_FOR_FIELD",lambda:self.boundary.canonicalize(claim("claim-001-b1-width")))

    def test_all_18_parser_claims_validate_static_schema(self):
        schema=json.loads((SCHEMA_DIR/"parser_claim_envelope_v1.schema.json").read_text())
        v=Draft202012Validator(schema)
        for row in CLAIMS: v.validate(row)

    def test_p0_18_15_3(self):
        self.assertEqual(len(CLAIMS),18)
        self.assertEqual(sum(x["solver_readiness_state"]=="READY" and x["value"] is not None for x in CLAIMS),15)
        self.assertEqual(sum(x["solver_readiness_state"]=="BLOCKED" and x["value"] is None for x in CLAIMS),3)

    def test_blocked_claim_rejected(self):
        self.assert_rejects("REQUIRED_VALUE_MISSING",lambda:self.boundary.canonicalize(claim("claim-004-subset-s4-missing")))

    def test_unmapped_ready_claim_rejected_for_i1(self):
        self.assert_rejects("FIELD_NOT_AUTHORIZED_FOR_I1",lambda:self.boundary.canonicalize(claim("claim-001-b1-stirrups")))

    def test_frozen_value_drift_rejected(self):
        x=claim("claim-001-b1-width"); x["value"]=201
        self.assert_rejects("FROZEN_CLAIM_BINDING_MISMATCH",lambda:self.boundary.canonicalize(x))

    def test_source_unit_drift_rejected(self):
        x=claim("claim-001-b1-width"); x["unit"]="m"
        self.assert_rejects("FROZEN_CLAIM_BINDING_MISMATCH",lambda:self.boundary.canonicalize(x))

    def test_source_document_drift_rejected(self):
        x=claim("claim-001-b1-width"); x["source_document_hash"]="0"*64
        self.assert_rejects("FROZEN_CLAIM_BINDING_MISMATCH",lambda:self.boundary.canonicalize(x))

    def test_locator_drift_rejected(self):
        x=claim("claim-001-b1-width"); x["source_locator"]["coordinate_space"]="pixels"
        self.assert_rejects("FROZEN_CLAIM_BINDING_MISMATCH",lambda:self.boundary.canonicalize(x))

    def test_evidence_drift_rejected(self):
        x=claim("claim-001-b1-width"); x["evidence_ref"]["crop_hash"]="1"*64
        self.assert_rejects("FROZEN_CLAIM_BINDING_MISMATCH",lambda:self.boundary.canonicalize(x))

    def test_review_drift_rejected(self):
        x=claim("claim-001-b1-width"); x["review_state"]="REVIEW_REQUIRED"
        self.assert_rejects("FROZEN_CLAIM_BINDING_MISMATCH",lambda:self.boundary.canonicalize(x))

    def test_conflict_drift_rejected(self):
        x=claim("claim-001-b1-width"); x["conflict_ids"]=["conf:test"]
        self.assert_rejects("FROZEN_CLAIM_BINDING_MISMATCH",lambda:self.boundary.canonicalize(x))

    def test_provenance_semantic_drift_rejected(self):
        ref="source:claim:claim-001-b1-width"
        self.boundary.provenance_registry["entries"][ref]["sheet_id"]="WRONG"
        self.assert_rejects("PROVENANCE_SEMANTIC_MISMATCH",lambda:self.boundary.canonicalize(claim("claim-001-b1-width")))

    def test_wrong_factor_rejected(self):
        self.boundary.normalization_registry["rules"]["length.mm_to_m"]["factor"]="1"
        self.assert_rejects("NORMALIZATION_FACTOR_DRIFT",lambda:self.boundary.canonicalize(claim("claim-001-b1-width")))

    def test_wrong_rule_id_rejected(self):
        self.boundary.field_registry["entries"]["beam_schedule.B1.width"]["normalization_rule_id"]="length.m_identity"
        self.assert_rejects("NORMALIZATION_RULE_UNSUPPORTED",lambda:self.boundary.canonicalize(claim("claim-001-b1-width")))

    def test_wrong_rule_version_rejected(self):
        self.boundary.normalization_registry["rules"]["length.mm_to_m"]["version"]="9.9"
        self.assert_rejects("NORMALIZATION_RULE_UNSUPPORTED",lambda:self.boundary.canonicalize(claim("claim-001-b1-width")))

    def test_dimension_drift_rejected(self):
        self.boundary.normalization_registry["rules"]["length.mm_to_m"]["dimension"]="MASS"
        self.assert_rejects("NORMALIZATION_DIMENSION_DRIFT",lambda:self.boundary.canonicalize(claim("claim-001-b1-width")))

    def test_unsupported_formula_rejected(self):
        cfg=copy.deepcopy(CONFIG); object.__setattr__(cfg,"formula_id","FORMULA.OTHER")
        b=RcBeamIntegrationBoundary(SCHEMA_DIR,cfg)
        self.assert_rejects("SOLVER_FORMULA_UNSUPPORTED",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_unsupported_formula_version_rejected(self):
        cfg=copy.deepcopy(CONFIG); object.__setattr__(cfg,"formula_version","9.0.0")
        b=RcBeamIntegrationBoundary(SCHEMA_DIR,cfg)
        self.assert_rejects("SOLVER_FORMULA_UNSUPPORTED",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_unsupported_solver_version_rejected(self):
        cfg=copy.deepcopy(CONFIG); object.__setattr__(cfg,"solver_version","solver/9")
        b=RcBeamIntegrationBoundary(SCHEMA_DIR,cfg)
        self.assert_rejects("SOLVER_VERSION_UNSUPPORTED",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_unsupported_output_stage_rejected(self):
        cfg=copy.deepcopy(CONFIG); object.__setattr__(cfg,"requested_output_stage","PROCUREMENT")
        b=RcBeamIntegrationBoundary(SCHEMA_DIR,cfg)
        self.assert_rejects("SOLVER_OUTPUT_STAGE_UNSUPPORTED",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_missing_mandatory_policy_rejected(self):
        cfg=copy.deepcopy(CONFIG); object.__setattr__(cfg,"policy_refs",tuple())
        b=RcBeamIntegrationBoundary(SCHEMA_DIR,cfg)
        self.assert_rejects("MANDATORY_POLICY_REF_MISSING",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_missing_width_rejected(self):
        self.assert_rejects("SOLVER_PARAMETER_KEY_SET_MISMATCH",lambda:self.boundary.assess_request([claim("claim-001-b1-depth")],"request:i1-001"))

    def test_duplicate_field_rejected(self):
        w=claim("claim-001-b1-width")
        self.assert_rejects("DUPLICATE_CANONICAL_FIELD",lambda:self.boundary.assess_request([w,copy.deepcopy(w),claim("claim-001-b1-depth")],"request:i1-001"))

    def test_duplicate_solver_mapping_rejected(self):
        self.boundary.field_registry["entries"]["beam_schedule.B1.depth"]["solver_parameter_key"]="width"
        self.assert_rejects("DUPLICATE_SOLVER_PARAMETER_MAPPING",lambda:self.boundary.assess_request(self.valid_rows(),"request:i1-001"))

    def test_attempt_deterministic_under_claim_order(self):
        a=self.boundary.assess_request(self.valid_rows(),"request:i1-001")["calculation_attempt"]
        b=self.boundary.assess_request(list(reversed(self.valid_rows())),"request:i1-001")["calculation_attempt"]
        self.assertEqual(a["attempt_hash"],b["attempt_hash"])
        self.assertEqual(a["attempt_id"],b["attempt_id"])

    def test_no_hidden_defaults_static(self):
        src=(ROOT/"backend/integration/rc_beam_boundary.py").read_text().lower()
        for token in ["typical_dimension","sample_substitution","fallback_width","fallback_depth","default_width","default_depth"]:
            self.assertNotIn(token,src)


class BoundaryMetadataR3Tests(unittest.TestCase):
    def valid_rows(self):
        return [claim("claim-001-b1-width"), claim("claim-001-b1-depth")]

    def boundary_with(self, **changes):
        cfg = copy.deepcopy(CONFIG)
        for key, value in changes.items():
            object.__setattr__(cfg, key, value)
        return RcBeamIntegrationBoundary(SCHEMA_DIR, cfg)

    def assert_rejects(self, expected_codes, fn):
        if isinstance(expected_codes, str):
            expected_codes = {expected_codes}
        else:
            expected_codes = set(expected_codes)
        with self.assertRaises(IntegrationBoundaryError) as ctx:
            fn()
        self.assertIn(ctx.exception.code, expected_codes)

    # I1-QA-B01 exact 16 escape classes.
    def test_r3_request_id_none_rejected(self):
        b=self.boundary_with()
        self.assert_rejects("INVALID_REQUEST_ID",lambda:b.assess_request(self.valid_rows(),None))

    def test_r3_request_id_int_rejected(self):
        b=self.boundary_with()
        self.assert_rejects("INVALID_REQUEST_ID",lambda:b.assess_request(self.valid_rows(),123))

    def test_r3_request_id_empty_rejected(self):
        b=self.boundary_with()
        self.assert_rejects("INVALID_REQUEST_ID",lambda:b.assess_request(self.valid_rows(),""))

    def test_r3_request_id_bad_pattern_rejected(self):
        b=self.boundary_with()
        self.assert_rejects("INVALID_REQUEST_ID",lambda:b.assess_request(self.valid_rows(),"BAD NO COLON"))

    def test_r3_request_id_leading_digit_rejected(self):
        b=self.boundary_with()
        self.assert_rejects("INVALID_REQUEST_ID",lambda:b.assess_request(self.valid_rows(),"1bad:abc"))

    def test_r3_element_id_bad_pattern_rejected(self):
        b=self.boundary_with(element_id="bad")
        self.assert_rejects("INVALID_ELEMENT_ID",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_element_id_int_rejected(self):
        b=self.boundary_with(element_id=123)
        self.assert_rejects("INVALID_ELEMENT_ID",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_element_type_empty_rejected(self):
        b=self.boundary_with(element_type="")
        self.assert_rejects("INVALID_ELEMENT_TYPE",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_element_type_int_rejected(self):
        b=self.boundary_with(element_type=123)
        self.assert_rejects("INVALID_ELEMENT_TYPE",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_element_type_over_80_rejected(self):
        b=self.boundary_with(element_type="X"*81)
        self.assert_rejects("INVALID_ELEMENT_TYPE",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_policy_id_bad_pattern_rejected(self):
        p=copy.deepcopy(POLICY); p["policy_id"]="BAD"
        b=self.boundary_with(policy_refs=(p,))
        self.assert_rejects("INVALID_POLICY_REF",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_policy_id_int_rejected(self):
        p=copy.deepcopy(POLICY); p["policy_id"]=123
        b=self.boundary_with(policy_refs=(p,))
        self.assert_rejects("INVALID_POLICY_REF",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_policy_version_bad_pattern_rejected(self):
        p=copy.deepcopy(POLICY); p["policy_version"]="bad"
        b=self.boundary_with(policy_refs=(p,))
        self.assert_rejects("INVALID_POLICY_REF",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_policy_version_int_rejected(self):
        p=copy.deepcopy(POLICY); p["policy_version"]=1
        b=self.boundary_with(policy_refs=(p,))
        self.assert_rejects("INVALID_POLICY_REF",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_policy_extra_property_rejected(self):
        p=copy.deepcopy(POLICY); p["extra"]="NO"
        b=self.boundary_with(policy_refs=(p,))
        self.assert_rejects("INVALID_POLICY_REF",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_duplicate_policy_refs_rejected(self):
        p=copy.deepcopy(POLICY)
        b=self.boundary_with(policy_refs=(p,copy.deepcopy(p)))
        self.assert_rejects("DUPLICATE_POLICY_REF",lambda:b.assess_request(self.valid_rows(),"request:i1-001"))

    def test_r3_final_attempt_gate_rejects_internal_schema_drift(self):
        b=self.boundary_with()
        original=b._make_issue
        def invalid_issue(*args,**kwargs):
            issue=original(*args,**kwargs)
            issue["undeclared"]="invalid"
            return issue
        b._make_issue=invalid_issue
        self.assert_rejects(
            "INVALID_CALCULATION_ATTEMPT_SCHEMA",
            lambda:b.assess_request(self.valid_rows(),"request:i1-001"),
        )

    def test_r3_one_shot_iterable_materialized_once(self):
        b=self.boundary_with()
        out=b.assess_request((row for row in self.valid_rows()),"request:i1-001")
        self.assertEqual(out["source_quantity_states"],{"width":"OBSERVED_SOURCE","depth":"OBSERVED_SOURCE"})
        self.assertEqual(out["calculation_attempt"]["disposition_state"],"BLOCKED")


class RegistryHeaderTests(unittest.TestCase):
    def copy_dir(self):
        import tempfile, shutil
        td=tempfile.TemporaryDirectory(); target=Path(td.name)
        for p in SCHEMA_DIR.iterdir(): shutil.copy2(p,target/p.name)
        return td,target

    def mutate(self,target,name,fn):
        p=target/name; o=json.loads(p.read_text()); fn(o); p.write_text(json.dumps(o))

    def assert_ctor_rejects(self,target,code):
        with self.assertRaises(IntegrationBoundaryError) as ctx: RcBeamIntegrationBoundary(target,CONFIG)
        self.assertEqual(ctx.exception.code,code)

    def test_r9_n01_unsupported_registry_version(self):
        td,t=self.copy_dir()
        try:
            self.mutate(t,"accepted_parser_claim_registry_v1.json",lambda o:o.__setitem__("registry_version","integration.accepted-parser-claim-registry/9.0"))
            self.assert_ctor_rejects(t,"ACCEPTED_CLAIM_REGISTRY_VERSION_UNSUPPORTED")
        finally: td.cleanup()

    def test_r9_n01_missing_registry_version(self):
        td,t=self.copy_dir()
        try:
            self.mutate(t,"accepted_parser_claim_registry_v1.json",lambda o:o.pop("registry_version"))
            self.assert_ctor_rejects(t,"ACCEPTED_CLAIM_REGISTRY_VERSION_MISSING")
        finally: td.cleanup()

    def test_r9_n01_wrong_p0_sha(self):
        td,t=self.copy_dir()
        try:
            self.mutate(t,"accepted_parser_claim_registry_v1.json",lambda o:o.__setitem__("source_p0_package_sha256","0"*64))
            self.assert_ctor_rejects(t,"ACCEPTED_P0_SHA_MISMATCH")
        finally: td.cleanup()

    def test_r9_n01_missing_p0_sha(self):
        td,t=self.copy_dir()
        try:
            self.mutate(t,"accepted_parser_claim_registry_v1.json",lambda o:o.pop("source_p0_package_sha256"))
            self.assert_ctor_rejects(t,"ACCEPTED_P0_SHA_MISSING")
        finally: td.cleanup()

    def test_input_profile_registry_version_rejected(self):
        td,t=self.copy_dir()
        try:
            self.mutate(t,"solver_input_profile_registry_v1.json",lambda o:o.__setitem__("registry_version","integration.solver-input-profile-registry/9.0"))
            self.assert_ctor_rejects(t,"SOLVER_INPUT_PROFILE_REGISTRY_VERSION_UNSUPPORTED")
        finally: td.cleanup()

if __name__=="__main__":
    unittest.main()
