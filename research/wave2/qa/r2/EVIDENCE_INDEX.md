# Evidence Index — Wave 2 QA R2

## Governing inputs

- Research QA Reviewer Charter.
- `INDEPENDENT_RESEARCH_WAVE2_TECH_REVIEW_R2.zip`
- `references/PM_RESEARCH_WAVE2_QA_RETURN_DIRECTIVE_R1.md`
- Prior QA packet: `INDEPENDENT_RESEARCH_WAVE2_QA_TO_PM_R1.zip`
- Prior TL packet: `INDEPENDENT_RESEARCH_WAVE2_TECH_REVIEW_R1.zip`

## Correction closure evidence

### COST-001

- `workers/RESEARCH_1_R2_COST_001_QA_CORRECTION_R1.zip`
- `deliverables/data/escalation_cases.json`
- `qa_correction/escalation_distinct_recount.json`
- `qa_correction/escalation_semantic_hashes.csv`
- `qa_correction/escalation_manual_diversity_review.md`
- `qa_correction/validator_portability_run.md`

QA result: 60 raw / 60 independent distinct; 33/33 corrected numerical rate fixtures independently recomputed.

### REBAR-001

- `workers/RESEARCH_3_R2_REBAR_001_QA_CORRECTION_R1.zip`
- `deliverables/data/fabrication_expected.json`
- `deliverables/data/cutting_stock_inputs.json`
- `deliverables/data/cutting_stock_optima.json`
- `qa_correction/fabrication_distinct_recount.json`
- `qa_correction/cutting_stock_distinct_recount.json`
- `qa_correction/multi_diameter_distinct_recount.json`
- `qa_correction/clean_reproduction/`

QA result: fabrication 110 distinct; cutting stock 160 distinct; strict multi-diameter 22 distinct. All 134 fabrication lengths independently recomputed. Original 150 cutting-stock inputs and 150 optimum records are unchanged by case ID.

### RISK-001 / RISK-002

- `workers/RESEARCH_4_R2_RISK_QA_CORRECTION_R1.zip`
- `corrected_packages/RISK_001/deliverables/data/uncertainty_classification_cases.json`
- `corrected_packages/RISK_001/deliverables/data/contingency_cases.json`
- `corrected_packages/RISK_001/deliverables/data/parser_uncertainty_cases.json`
- `corrected_packages/RISK_001/deliverables/data/revision_cases.json`
- `corrected_packages/RISK_001/deliverables/data/risk_gate_cases.json`
- `corrected_packages/RISK_002/deliverables/data/boundary_cases.json`
- `qa_correction/*distinct_recount.json`
- `qa_correction/sealed_validator_behavior.md`

QA result: 88 / 46 / 58 / 58 / 84 / 36 distinct using reviewer core-state signatures that exclude IDs and narrative-only fields.

## TL dependency/reconciliation evidence

- `reviews/QA_RETURN_CLOSURE_MATRIX.md`
- `reviews/DISTINCT_CASE_RECOUNT.json`
- `reviews/CORRECTION_DEPENDENCY_REVIEW.md`
- `reviews/UPDATED_CROSS_RESEARCH_RECONCILIATION.md`
- `evidence/validation_runs/TL_CLEAN_EXTRACTION_REPRODUCTION.json`

## Independent QA preservation evidence

- Prior `SOURCE_VERIFICATION.json`: 25 external sources verified, all 25 primary/official/technical for the sampled purpose.
- Corrected source registers are byte-identical to R1 originals.
- R2 frozen reference SHA-256 and byte sizes match the actual packages preserved in the R1 TL packet.
- Prior independent numerical results are retained only where R2 dependency comparison shows their inputs were not changed.

## QA-generated evidence in this packet

- `HARD_GATE_RECOUNT.json`
- `SOURCE_VERIFICATION.json`
- `SEMANTIC_SAMPLING.json`
- `INDEPENDENT_RECALCULATIONS.json`
- `VALIDATOR_INDEPENDENCE.md`
- `CONTRADICTION_REVIEW.md`
- `CHAIN_OF_CUSTODY.json`
