# Research A Wave 4 — PM Decision R1

## PM Verdict

`PM_ACCEPTED_WITH_NOTES`

`RESEARCH_A_WAVE4: CLOSED`

`FROZEN AS REFERENCE EVIDENCE`

`WORKER BACKJOB: NONE`

`ARCHIVE: PENDING`

## Subject

QA package:
`RESEARCH_A_WAVE4_QA_REVIEW_R1.zip`

QA package SHA-256:
`b40b01d35f55f1b013da9727274bd9ab1a190b2ca68df0736a36b1e52bcfaa05`

QA verdict:
`QA_PASS_WITH_NOTES / READY_FOR_PM`

The QA package itself is internally intact. All five files declared in its `SHA256SUMS.txt` independently verify.

## Accepted Research 1 State — R4-CORPUS-001

Accepted as:
- rights-aware corpus/source discovery evidence;
- explicit truth-state classification;
- adjudication-boundary evidence;
- candidate/source inventory for later controlled ingestion.

Accepted QA evidence includes:
- 52 corpus records;
- 52 unique candidate IDs;
- 52 / 52 independently recomputed semantic hashes distinct;
- 256 / 256 validator checks passing;
- all current records remaining `REFERENCE_BOQ`;
- explicit rights classifications retained.

### Binding limitation

The current inventory is **not** accepted as:
- adjudicated gold truth;
- byte-ingested benchmark truth;
- revision-reconciled truth;
- redistribution-cleared by default.

Downstream work must preserve the distinction between:
`REFERENCE_BOQ`, `CANDIDATE_TRUTH`, `ADJUDICATED_GOLD_TRUTH`, and `UNRESOLVED`.

## Accepted Research 2 State — R4-DWG-001

Accepted as bounded native-DWG evidence and source/provenance research.

Accepted QA evidence includes:
- 38 unique candidate repository paths;
- 38 unique Git blob SHAs;
- three successful object-level native walkthrough records;
- exact entity/layer reconciliations for the three accepted walkthroughs;
- preserved AC1021 reader failure rather than fabricated observations;
- package, contract, negative-control, and overall validators passing;
- pinned legacy revision provenance verified by QA.

### Binding limitation

The current Research 2 evidence **does not establish**:
- universal DWG compatibility;
- universal DWG-version support;
- parser accuracy;
- quantity correctness.

QA did not independently rerun the native reader over fresh local copies of all three accepted DWGs in its own runtime. This remains a non-blocking evidence dependency on the worker execution record, strengthened by TL review and QA provenance reconciliation.

Future hardening should:
1. automatically validate walkthrough JSON ↔ dataset/source-register reconciliation;
2. cross-read representative DWGs with a second independent native reader/toolchain when feasible.

## Accepted Research 3 State — R4-PARSERBENCH-001

Accepted as parser benchmark/scoring design reference evidence.

Accepted QA evidence includes:
- 87 cases;
- 87 / 87 semantic hashes independently recomputed and matched;
- 80 families;
- zero family leakage across development / validation / sealed holdout;
- all task IDs 1 through 18 represented;
- 56 adversarial cases;
- 26 conflict/missing cases;
- 30 source-localization cases;
- 20 cross-sheet cases;
- three independently reproduced false-automatic-acceptance events.

### Binding limitation

This package is a **synthetic benchmark design**, not empirical production parser-accuracy evidence.

Production thresholds, review-time assumptions, and acceptance/calibration policy remain unvalidated until tested against a licensed/controlled real-drawing pilot with adjudicated truth.

Future validator hardening should recompute semantic hashes rather than relying on stored hashes for uniqueness checks.

## Cross-Worker PM Synthesis

Wave 4 Research A is accepted as a coherent evidence ladder:

1. Research 1 defines rights-aware corpus discovery and truth/adjudication boundaries.
2. Research 2 defines bounded native-CAD evidence contracts and real-DWG object-level observations.
3. Research 3 defines parser benchmark/scoring structure for evidence support, abstention, conflict, cross-sheet reasoning, and unsafe automatic acceptance.

No package is accepted as end-to-end production Parser accuracy or Solver correctness evidence.

## PM Notes Carried Forward

1. Preserve Research 1 rights and truth-state gates through future byte-ingestion work.
2. Treat Research 2 native-DWG findings as bounded compatibility evidence only.
3. Harden Research 2 validators with exact walkthrough/dataset/source-register reconciliation.
4. Use a second independent DWG reader/toolchain for future cross-validation where feasible.
5. Treat Research 3 as benchmark design, not production calibration.
6. Empirically calibrate parser thresholds and human-review burden only against controlled real drawings with adjudicated truth.
7. Harden Research 3 validator to recompute semantic hashes directly.

None of these notes warrants another Research A TL/QA cycle.

## Governance State

Research A Wave 4:
`CLOSED / FROZEN AS REFERENCE EVIDENCE`

Research 1:
`ACCEPTED WITH NOTES`

Research 2:
`ACCEPTED WITH NOTES`

Research 3:
`ACCEPTED WITH NOTES`

Required worker correction:
`NONE`

Required TL correction:
`NONE`

Archive:
`ARCHIVE_PENDING`

## Downstream Use

These artifacts may inform:
- Parser benchmark design;
- corpus acquisition and adjudication;
- native-CAD ingestion strategy;
- Integration/Parser evidence contracts;
- future production validation planning.

They must not be silently promoted beyond their accepted evidence class.
