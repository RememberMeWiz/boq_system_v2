# Documentation Authority Index R1

## Purpose

Prevent stale historical documentation from being interpreted as current architecture or milestone state.

## Proposed authority order

1. PM decisions and accepted QA artifacts for the applicable milestone.
2. `docs/product/PRODUCT_VISION_R3.md`.
3. `docs/product/PRODUCT_PLAN_R3.md`.
4. Accepted team-specific contracts/specifications.
5. Current implementation documentation.
6. Historical specifications and progress reports.

## Historical root documents

Preserve but mark as historical/partially superseded where applicable:

```text
tech_spec_v2.md
parser_design_spec.md
tech_spec_parser_v2.md
progress_report_v2.md
formula_exhaustive_handbook.md
sample_solved_cases.md
00_INSTRUCTIONS_FOR_WEB_AI.md
```

## Supersession banner

```text
> STATUS NOTICE — HISTORICAL / PARTIALLY SUPERSEDED
>
> This document records an earlier project design or implementation state.
> It is not sufficient authority for current production behavior.
>
> Current product direction:
> - `docs/product/PRODUCT_VISION_R3.md`
> - `docs/product/PRODUCT_PLAN_R3.md`
>
> Current technical decisions require the applicable Team Leader,
> specialized QA, and PM acceptance.
```

## Known stale themes

Do not use older documents as authority for:

- legacy Solver "complete/high confidence" claims;
- confidence thresholds as automatic Parser validity;
- `assumed_default` as a normal solver-critical route;
- Antigravity as sole project-management authority;
- old schema sketches as locked contracts;
- old progress reports as QA acceptance.
