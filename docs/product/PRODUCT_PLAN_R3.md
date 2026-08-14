# BOQ System Product Plan R3

**Date:** 2026-08-14  
**Status:** Proposed authoritative roadmap

## Strategy

Build evidence-backed vertical slices. Do not replace every trade at once.

The first production-grade slice remains **RC beam** because it exercises drawing understanding, cross-sheet linking, geometry, reinforcement, units, provenance, verification, deterministic calculation, fabrication, procurement, and BOQ traceability.

## Roadmap

| Milestone | Goal | Current state |
|---|---|---|
| M0 | Legacy characterization/provenance | Substantially complete |
| M1 | Architecture + contract readiness | **Current project area** |
| M2 | Trusted RC beam vertical slice | Not yet authorized |
| M3 | Parser benchmark + evidence UX | Preparing |
| M4 | Structural expansion: column/footing/slab | Future |
| M5 | Architectural quantity extraction | Future |
| M6 | MEP symbol/legend workflows | Future |
| M7 | Production pricing/rate provenance | Future |
| M8 | Revision/reproducibility/commercial audit | Future |
| M9 | End-to-end + competitor benchmark | Future |
| M10 | Release hardening/failure injection | Future |

## M1 exit requirements

- Solver readiness → Solver QA → PM;
- Parser P0-006 real golden-source materialization;
- Research Wave 3 → Research TL → Research QA → PM;
- PM adoption/defer/reject decisions for implementation-facing research;
- minimum Parser → Integration → Solver contracts stable enough to implement.

### Current Research state

Research Workers 1–6 have returned Wave 3 outputs. **Research TL is ACTIVE**, reviewing and synthesizing them.

Next:

```text
Research TL
→ Research QA
→ PM
```

## M2: trusted RC beam slice

```text
drawing evidence
→ Parser claims
→ verification/conflict state
→ canonical beam input
→ Solver
→ fabrication/procurement
→ rate provenance
→ BOQ
→ audit trace
```

## Parser expansion sequence

After the RC beam slice:

```text
beam
→ column
→ footing
→ slab
→ structural package
→ architectural elements
→ MEP
```

Every added element type inherits the same source-evidence and unit-safety architecture.

## Parallel Research Wave 4 recommendation

After Wave 3 closes:

- `R4-CORPUS-001` Drawing + BOQ Corpus and Benchmark Program;
- `R4-MARKET-001` competitor landscape and hands-on comparison;
- `R4-UX-001` estimator workflow and visual-provenance UX;
- `R4-PROCESS-001` backjob/process efficiency research;
- `R4-CAREER-001` portfolio/freelance/BIM-VDC/digital-construction leverage;
- `R4-DWG-001` focused native DWG/DXF paired-source acquisition.

## Corpus targets

```text
Raw corpus: hundreds of projects
Paired benchmark: 75-100+ projects
Gold corpus: 20-30 initially, then grow carefully
Sealed holdout: never exposed to implementation workers during development
```

## Productization rule

Do not try to become a broad commercial estimating suite immediately.

First prove:

```text
one beam
correctly
with evidence
```

Then scale.


## Organization decision for Wave 4 onward

After Research Wave 3 closes, split Research into:

```text
Research A — Technical / Evidence
Research B — Commercial / Product
```

with separate TLs and a shared Research QA initially.

Keep Solver as one umbrella team for now, while separating the architecture into:

```text
Quantity Engine
Fabrication / Procurement Engine
Pricing / Rate Engine
```

Pricing becomes a separate team only when workload and ownership complexity justify it.

See:

- `docs/product/PRODUCT_STRATEGY_DECISION_ARCHIVE_R1.md`

## Global stretch goal

Long-term product strategy:

> **Philippines-first, globally portable.**

Current implementation remains Philippine-first.

Future architecture should support jurisdiction-configurable:

- measurement policy;
- standards authority;
- procurement policy;
- pricing/rate sources;
- currency/tax;
- units;
- BOQ classifications;
- localization.

Global support is a stretch milestone after the Philippine evidence-backed pipeline is proven.

See:

- `docs/product/PRODUCT_STRATEGY_DECISION_ARCHIVE_R1.md`
