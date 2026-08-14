# boq_system_v2

Evidence-backed construction drawing intelligence and Bill of Quantities system.

## Product thesis

```text
drawing
-> evidence-backed Parser claims
-> verification/conflict state
-> canonical Solver input
-> deterministic quantities
-> fabrication/procurement
-> rate provenance
-> BOQ
-> reproducible audit trace
```

The key product differentiator is:

```text
UNDERSTAND + PROVE + CALCULATE
```

## Architecture

- **Parser:** drawing understanding and evidence-backed claims.
- **Integration:** contracts, units, provenance, verification/conflict gates.
- **Solver:** deterministic quantity calculation.
- **Research/QA:** independent methodology, benchmark, corpus, and verification (operating under independent Technical and Commercial lanes).

## Authoritative product and governance docs

- `docs/product/PRODUCT_VISION_R3.md`
- `docs/product/PRODUCT_PLAN_R3.md`
- `docs/product/PRODUCT_STRATEGY_DECISION_ARCHIVE_R2.md`
- `docs/product/CORPUS_AND_BENCHMARK_STRATEGY_R1.md`
- `docs/governance/DOCUMENT_AUTHORITY_INDEX_R1.md`
- `docs/governance/REPOSITORY_HYGIENE_PLAN_R1.md`
- `docs/governance/research/`

## Important note

Several root-level specifications/progress reports are historical artifacts. They are useful context but are not current production authority where they conflict with later QA/PM decisions.

## First replacement slice

RC beam, end-to-end, with visible source evidence and reproducible calculation trace.

## Data governance

Large third-party drawings, books, standards, BOQs, and datasets require provenance and redistribution-rights review. Do not add new large binaries casually to the production source repository.
