# Research B Wave 4 — PM Decision R1

Project: `boq_system_v2`
Lane: Research B
Date: `2026-08-15`
Input QA package: `RESEARCH_B_WAVE4_QA_REVIEW_R1.zip`
Input QA package SHA-256: `642c0a2e8c0bde4728b752317620254f0dd68049aebcb7fc8629a3d74791da69`

## PM disposition

- QA verdict reviewed: `QA_PASS_WITH_NOTES`
- PM verdict: `PM_ACCEPTED_WITH_NOTES`
- Research B Wave 4 state: `CLOSED / FROZEN AS REFERENCE EVIDENCE`
- Worker backjob: `NONE`
- Production implementation authorization: `NOT IMPLIED`
- Archive state: `ARCHIVE_PENDING`

## Accepted worker packages

- Research 4 — `R4-MARKET-001`: accepted with notes
- Research 5 — `R4-UX-001`: accepted with notes
- Research 6 — `R4-PROCESS-001`: accepted with notes

## PM verification

The received QA archive is structurally valid and its included `SHA256SUMS.txt` verifies in full.

PM independently spot-checked the load-bearing QA notes:

1. STACK pricing currently displays Premium at US$249 and Pro at US$299 per user/month, billed annually. This supports QA note `R4-N1` that the stored billing basis should be tightened on the next market refresh.
2. PlanSwift currently exposes US$2,000 on its checkout page and US$1,749/year/license on its trial FAQ. Research 4 correctly preserved the contradiction rather than silently choosing one value.
3. The Purdue/CIB irregular-area benchmark reports 94.1% automatic area-calculation accuracy and about 99% time reduction for that tested task. The result remains narrow and must not be generalized into broad commercial-product accuracy.
4. `Automation bias and verification complexity: a systematic review` is authored by David Lyell and Enrico Coiera. Research 5 source `S31` therefore has an author-metadata defect.
5. Repository spot checks corroborate the Research 6 process evidence, including the baseline restoration lineage and the low-value trailing-whitespace follow-up commit.

The QA package records hashes for its upstream TL and worker archives, but those upstream archives are not embedded in this QA ZIP. PM therefore does not claim to have independently rehashed those referenced upstream archives from this package alone. This is not a blocker because Research B QA explicitly performed and recorded that chain-of-custody validation; archival storage should preserve the referenced upstream packages or stable receipts when available.

## Notes carried forward

### R4-N1 — Market-source precision
At the next market-source refresh, record STACK displayed pricing basis explicitly as `per user/month, billed annually`, with observation date. No Research 4 rerun is required.

### R5-N1 — S31 metadata correction
Before the Research B Wave 4 archive is treated as archival-final, correct `S31` author metadata to:

`David Lyell and Enrico Coiera`

Synchronize the corresponding source note. This is an archival metadata correction only. It does not reopen Research 5 and does not require fresh UX research.

### R5-N2 — Ambiguous evidence implementation invariant
Carry into Parser/Integration/Solver contract and implementation policy:

Solver-critical `evidence_health=ambiguous` remains fail-closed unless an explicit authorized policy exception exists. Any exception must preserve the evidence state as `ambiguous`; authorization must not relabel evidence as `supported`.

### R6-N1 — Historical-source portability
Future research packages should preserve, for non-embedded internal project sources, at least the source identity, content SHA-256, originating handoff/package ID, and stable repository/archive receipt where available.

## Preserved limitations

Do not promote this research into claims that were not measured:

- no full hands-on commercial competitor accuracy benchmark was demonstrated;
- no measured estimator usability improvement was demonstrated;
- no measured post-restructure process throughput improvement was demonstrated.

## PM synthesis adopted

Research B Wave 4 is accepted as reference evidence supporting the following bounded direction:

- market precedent exists for automatic takeoff and visual linking;
- the defensible product direction is evidence-complete, reviewable, fail-closed, reproducible drawing-to-BOQ reasoning;
- UX should preserve uncertainty and distinguish source evidence from authorized human decisions;
- process improvements must be measured longitudinally before productivity claims are made;
- vendor documentation must not be promoted into independent benchmark evidence.

## Next route

Research B Wave 4 requires no further TL/QA cycle.

`PM_ACCEPTED_WITH_NOTES -> CLOSED / FROZEN -> ARCHIVE_PENDING`

Archive only after applying the S31 metadata correction and preserving this PM decision with the QA/TL/worker provenance chain or stable receipts.
