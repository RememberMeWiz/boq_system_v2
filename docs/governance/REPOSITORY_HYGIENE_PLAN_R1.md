# Repository Hygiene and Data Governance Plan R1

## Current problem

The repository mixes production code, specifications, generated outputs, local state, solver evidence, large drawing/reference binaries, books/PDFs, and future research/corpus material.

Cleanup must be controlled and non-destructive first.

## Phase A — documentation/governance

- add root README;
- add `docs/product/` and `docs/governance/`;
- mark stale root specs as historical;
- establish document authority.

No production logic changes.

## Phase B — runtime/generated-file audit

Classify tracked `outputs/` files:

```text
RUNTIME_GENERATED
TEST_FIXTURE
HISTORICAL_EVIDENCE
GOLDEN_ARTIFACT
UNKNOWN
```

Do not blanket-delete before classification.

`backend/boq_v2.db` is already ignored but remains tracked. Remove it from tracking in a later authorized cleanup without deleting developers' local DB copies.

## Phase C — large reference-data rights and size audit

Audit `backend/reference_data/` binaries for:

- provenance;
- purpose/current usage;
- redistribution rights;
- hash;
- size;
- public/private status;
- Git/LFS/external-storage destination.

The repository is public. Books, standards, private plans, third-party drawings, and commercial data require rights review.

## Phase D — storage migration

Use a controlled model:

```text
Git:
metadata + manifests + schemas + small public evidence

Dataset/object/private storage:
large drawings/BOQs/books where appropriate

Hashes:
link metadata to immutable bytes
```

## Phase E — optional history cleanup

No `git filter-repo`, BFG, force-push, or history rewrite while active team work is running unless there is a dedicated freeze/migration authorization.

## Corpus rule

Do not put the new large drawing/BOQ corpus directly into the production code repository by default.
