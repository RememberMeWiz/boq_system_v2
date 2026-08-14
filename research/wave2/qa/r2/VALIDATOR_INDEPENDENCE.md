# Validator Independence Review — Wave 2 QA R2

## Classification

The corrected package validators are reproducibility checks, not independent oracles merely because they pass. QA therefore did not use worker/TL validator success as the semantic-count oracle.

The returned semantic gates were independently recounted using reviewer-written canonicalization rules. Correction-sensitive numeric results were also independently recomputed where the correction changed active numerical fixtures.

## Clean-extraction reruns

QA clean-extracted all three correction ZIPs and ran the documented entry points.

### Research 1 / COST-001

- `python deliverables/support/validate_rate_research.py` → exit 0, PASS, 948 checks, 0 failures.
- `python support/validate_rate_research.py` → exit 0, same PASS summary.
- Pre/post complete file-tree comparison → 44 files before, 44 after, 0 changed/added/removed.

The two validator locations are redundant implementations/packaging entry points, not independent oracles from one another.

### Research 3 / REBAR-001

- `python support/check_handoff_integrity.py` → exit 0, 77 checked, PASS.
- `PYTHONDONTWRITEBYTECODE=1 python deliverables/support/validate_rebar_benchmark.py` → exit 0, PASS.
- Post-run integrity → exit 0, 77 checked, PASS.
- Complete file-tree comparison → 78 files before, 78 after, 0 changed/added/removed.

The previously broken duplicate convenience validator is absent. The retained validator is read-only with respect to sealed evidence.

### Research 4 / RISK correction

- `python support/validate_correction_package.py` → exit 0, 29/29 PASS.
- `python corrected_packages/RISK_001/support/validate_package.py` → exit 0, 57/57 PASS.
- `python corrected_packages/RISK_002/deliverables/support/validate_risk_002.py` → exit 0, 34/34 PASS.
- Complete outer correction tree → 154 files before, 154 after, 0 changed/added/removed.

The RISK validators no longer mutate sealed evidence.

## Independent QA work beyond validator self-consistency

QA independently established:

- COST escalation: 60/60 distinct under chronology/sign/order-sensitive canonicalization that does not rely on exact cosmetic dates/numbers.
- REBAR fabrication: 110 distinct material bodies; 134/134 fabrication lengths independently recomputed, including 24/24 new cases.
- REBAR cutting stock: 160 distinct material problem bodies.
- REBAR multi-diameter: 22 strict distinct cases after excluding four single-diameter rows, still above the required 20.
- RISK returned corpora: 88, 46, 58, 58, 84, and 36 distinct using core state/decision signatures with narrative fields excluded.
- COST corrected numerical fixtures: 33/33 stored normalized rates independently recomputed.

## Preserved R1 oracle classifications

The prior QA-R1 independent numerical work remains applicable because the relevant frozen datasets were not changed by this narrow correction. Worker-authored “independent reproduction” paths remain classified as worker separate paths, not commissioned external oracles.

## Remaining note

The frozen `R2-ONTOLOGY-002` package retains the R1 QA packaging-hygiene note concerning tracked Python bytecode and post-validator checksum mutation in a normal bytecode-writing environment. R2 did not reopen that accepted-with-notes package. This is one reason the Wave 2 verdict is `QA_PASS_WITH_NOTES`, not an unqualified `QA_PASS`.
