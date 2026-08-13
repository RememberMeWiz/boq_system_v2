# S0-001-R2 Solver Baseline Portable Restoration Report

**Task:** S0-001-R2  
**Worker status:** READY_FOR_TEAM_LEADER_REVIEW  
**Artifact class:** Portable provenance-restoration package  
**Remote Git provenance established by Worker A:** NO

## Purpose

This report accompanies the approved S0-001 baseline artifacts for later restoration by a Repository Steward into a genuine clone of `https://github.com/RememberMeWiz/boq_system_v2`. It freezes legacy solver behavior and historical execution evidence only. It does not claim that a remote worker branch, remote worker commit, or steward-validated Git lineage currently exists.

The Repository Steward must establish authoritative Git provenance later. The future commit must be created on `solver/s0-baseline` from verified base `main` at `97f16aa3fd7b6d8e7cd364b6edc2ac303a5f54e6`, with the new baseline commit directly parented by that verified base.

## Verified repository reference

- Repository: `https://github.com/RememberMeWiz/boq_system_v2`
- Verified base branch: `main`
- Verified base commit: `97f16aa3fd7b6d8e7cd364b6edc2ac303a5f54e6`
- Future steward branch: `solver/s0-baseline`
- Remote worker SHA in this package: **none**
- Remote branch existence claimed by this package: **no**

## Legacy behavior frozen by the approved fixture

Canonical fixture:

`tests/solver/baseline/current_outputs.json`

Approved fixture SHA-256:

`582a7b00e502953764b73156b9a3eedda23e57af0041518b7221288be98fa7c6`

Approved deterministic process payload hash:

`dd20c25f418db388815bb0d2f12e23d6b8ca09bb0676a13ab417f32ae9fad5fc`

The R1 pinned-source rerun produced the same deterministic process payload hash on both independent executions and the same byte-for-byte `current_outputs.json` hash. Those R1 matches are historical local execution evidence, not native-clone Git provenance.

### Frozen representative outputs

- Section III concrete worked case: `3.78 m3` concrete, `35` cement bags, `1.89 m3` sand, `3.78 m3` gravel, total cost `26779.48`.
- Section V documented reinforcement case: `218.94 kg` rebar, `3.28 kg` tie wire, total cost `12763.35`.
- Existing Section V automated-test input: `109.47 kg` rebar, total cost `6381.67`.
- Full 13-trade takeoff: Sections II-XIII subtotal `863905.01`, Section I total `46576.92`, grand total direct cost `910481.93`.
- Rebar optimizer sample: required `170.15 kg`, purchased `177.55 kg`, scrap `7.40 kg` / `4.17%`, with 3 x 12 m, 0 x 9 m, and 6 x 6 m stock bars.

Floating-point values in the fixture are retained exactly as captured. No formula, expected result, or legacy solver behavior was changed for R2.

## Historical R1 test evidence

The R1 execution environment recorded:

- CPython 3.13.5
- Debian GNU/Linux 13 (trixie)
- pytest 9.0.2
- ezdxf 1.4.4
- PyMuPDF 1.26.7
- pdfplumber 0.11.9
- matplotlib 3.10.8
- Pillow 12.3.0

Historical R1 results:

| Command | Historical result |
|---|---|
| `python -m pytest -ra` | collection interrupted by 1 existing parser-related error; exit 2 |
| `python -m pytest -ra test_fajardo_v2.py` | 4 passed, 0 failed, 0 skipped; exit 0 |
| `python -m unittest -v test_fajardo_v2.py` | 4 passed, 0 failed, 0 skipped; exit 0 |
| `python test_dxf_parser.py` | existing import error; exit 1 |
| `python backend/engine/test_extraction_suite.py` | existing constructor error; exit 1 |
| `MPLBACKEND=Agg python backend/engine/test_vector_diff.py` | diagnostic PASS; exit 0 |
| `python tests/solver/baseline/capture_baseline.py` | deterministic capture PASS; exit 0 |

The parser-related failures are part of the frozen historical baseline evidence. They must be preserved during provenance restoration and must not be repaired as part of S0-001-R2.

## Source integrity evidence

`tests/solver/baseline/source_integrity.json` records unchanged hashes across the R1 capture for production solver and existing test files, including:

- `backend/engine/fajardo.py`
- `backend/engine/rebar_optimizer.py`
- `backend/engine/dupa_loader.py`
- `backend/engine/pdf_dxf_parser.py`
- `backend/engine/test_extraction_suite.py`
- `backend/engine/test_vector_diff.py`
- `test_fajardo_v2.py`
- `test_dxf_parser.py`

No production code or pre-existing test file is included in this portable package.

## Known R1 limitations preserved honestly

The historical R1 environment could not create a genuine repository clone because its network environment could not resolve `github.com`. It also lacked the repository binary reference-input directory. Therefore R1 local Git identities and local reconstruction state are not accepted as final provenance.

`tests/solver/baseline/r1_git_evidence.json` is intentionally reclassified in R2 as historical local execution evidence only. It does not establish a remote branch or worker commit.

## Required steward restoration

The authoritative procedure is in `STEWARD_VALIDATION_INSTRUCTIONS.md` at the root of the portable ZIP. The Repository Steward must:

1. start from a genuine clone;
2. verify and checkout `97f16aa3fd7b6d8e7cd364b6edc2ac303a5f54e6`;
3. create/reset `solver/s0-baseline` at that exact base;
4. restore only the authorized repository paths from this package;
5. confirm genuine repository binary fixtures are present;
6. rerun the complete baseline command set without repairing existing failures;
7. verify the solver fixture and deterministic hashes without rewriting outputs merely to force a match;
8. verify only authorized paths differ from the base;
9. create exactly one new baseline commit whose parent is `97f16aa3fd7b6d8e7cd364b6edc2ac303a5f54e6`;
10. generate and preserve authoritative Git evidence itself.

## R2 scope confirmation

- Production formulas changed: **NO**
- Production solver code changed: **NO**
- Pre-existing tests changed: **NO**
- Parser failures repaired: **NO**
- Baseline expected outputs changed: **NO**
- Remote branch claimed: **NO**
- Remote worker commit claimed: **NO**
- Merge performed: **NO**
- Wave 2 work performed: **NO**

This package is ready for Solver Team Leader review, not for Repository Steward queueing until the governing PM/QA gate authorizes it.
