# Independent Research Wave 2

## Status

- Research QA verdict: `QA_PASS_WITH_NOTES`
- PM disposition: `PM_ACCEPTED_WITH_NOTES`
- Evidence milestone: closed and frozen as reference evidence
- Production implementation: not authorized by the research acceptance decision
- Methodology/commercial-policy adoption: not authorized by the research acceptance decision

## Contents of this archival commit

`qa/r2/` contains the extracted contents of `INDEPENDENT_RESEARCH_WAVE2_QA_TO_PM_R2.zip` for normal Git diff/review.

`packages/` preserves the exact QA-to-PM ZIP supplied to the PM together with its outer SHA-256 checksum.

## Scope boundary

This archival queue contains the accepted R2 QA packet available to PM at queue time. It does not reconstruct or fabricate absent worker/TL source packages. The QA packet's `CHAIN_OF_CUSTODY.json` and `EVIDENCE_INDEX.md` preserve the names and hashes of the reviewed upstream artifacts.

If the upstream research worker/TL packages are later archived in Git, that should be done through a separate provenance-preserving queue action using the exact original binaries.
