# Current Project State

> PM checkpoint and durable resumability record for `RememberMeWiz/boq_system_v2`.
> Capture date: 2026-08-15, Asia/Manila.
> Verified base commit (`main`): `c55baf67e4e49c1382618293d8e7ee49e2b542ce`.
> This checkpoint does not replace PM decisions, accepted QA artifacts, product plans, or technical contracts.

---

## 1. Product Thesis and Core Architecture

Evidence-backed construction drawing intelligence and Bill of Quantities system with provenance-first parsing and deterministic quantity calculation.

### Core pipeline
```text
drawing
-> evidence-backed Parser claims
-> verification / conflict / missing state
-> Integration canonical facts
-> deterministic Solver input
-> quantities
-> fabrication / procurement
-> rate provenance
-> BOQ
-> reproducible audit trace
```

- **Product thesis:** `UNDERSTAND + PROVE + CALCULATE`
- **First production vertical slice:** `RC beam` (end-to-end, with visible source evidence and reproducible calculation trace).

---

## 2. Current Milestone and Gate State

### Active technical milestone: `M2-RCBEAM-VERTICAL-SLICE-001`
- **Purpose:** Deliver the end-to-end executable RC beam vertical slice across Parser, Integration, and Solver boundaries.
- **Current active gate:** `M2-0 EXECUTION DEPENDENCY CLOSURE`
- **Subsystem & contract status:**
  - Parser P0-006: `CLOSED / ACCEPTED GOLDEN TRUTH` (18 reviewed / 15 READY / 3 BLOCKED-NULL / 0 hidden defaults)
  - PIS Contract Freeze I0: `CLOSED / ACCEPTED / FROZEN`
  - M1 Architecture & Contract Readiness: `COMPLETE`
  - Integration I1 Materialization: `CLOSED / ACCEPTED / MERGED` (`c55baf67e4e49c1382618293d8e7ee49e2b542ce`)
  - Integration I1 Frozen Projection:
    - `beam_schedule.B1.width -> parameters.width`
    - `beam_schedule.B1.depth -> parameters.depth`
  - Request Status: Current I1 request remains intentionally fail-closed `BLOCKED` because execution dependencies (span/length, clear cover, rebar schedules, concrete grade) are not yet projected.
  - Research Lane A Wave 5: `ACTIVE / TL REVIEW`
  - Research Lane B Wave 5: `ACTIVE / TL REVIEW`
  - Antigravity Role: Repository Steward only (not technical approver).

### Current critical path
```text
M2-0 Parser/Solver dependency review
-> Integration TL reconciliation
-> Integration QA
-> PM
-> M2-1 executable implementation authorization
```

---

## 3. Completed and Accepted Milestones

| Milestone / Area | Status | Reference Authority |
|---|---|---|
| Product R3 governance | `CLOSED / MERGED` | `docs/product/PRODUCT_PLAN_R3.md` |
| Parser P0-006 | `CLOSED / ACCEPTED GOLDEN TRUTH` | Parser P0-006 PM Decision |
| Parser PO truth review | `18 / 18 COMPLETE` | Product Owner Acceptance |
| PIS Contract Freeze I0 | `CLOSED / ACCEPTED / FROZEN` | `PIS_CONTRACT_FREEZE_001_PM_FINAL_DECISION_R1.md` |
| M1 Architecture Readiness | `COMPLETE` | Milestone 1 Completion Review |
| Integration I1 Boundary | `CLOSED / ACCEPTED / MERGED` | `INTEGRATION_I1_RCBEAM_001_PM_MERGE_AUTHORIZATION_R1.md` (`c55baf67e4e49c1382618293d8e7ee49e2b542ce`) |
| Solver Phase 0 readiness | `ACCEPTED / PARKED` | Solver Phase 0 Baseline Audit |
| Research Wave 2 | `CLOSED_AND_ARCHIVED` | `research/wave2-evidence` |
| Research Wave 3 | `CLOSED_AND_ARCHIVED` | `research/wave3-evidence` |
| Research A Wave 4 | `CLOSED_AND_ARCHIVED` | `research/wave4-evidence` (`research_a/`) |
| Research B Wave 4 | `CLOSED_AND_ARCHIVED` | `research/wave4-evidence` (`research_b/`) |

---

## 4. Accepted Research Evidence Branch Chain

| Wave / Lane | Verified Remote Branch | Tip Commit SHA | Parent Commit SHA |
|---|---|---|---|
| Wave 2 | `research/wave2-evidence` | `815d44214a2f52dd34fbc05a0c2faab83b1feb95` | `81013b79b0e8051cd3829d515ab7f144af747841` |
| Wave 3 | `research/wave3-evidence` | `0631843aecfbcdbd3e30ac2e7c6a2f2d5794f449` | `815d44214a2f52dd34fbc05a0c2faab83b1feb95` |
| Wave 4 | `research/wave4-evidence` | `e31a88eda52a6ce090209ff0fd0f763b5a12ff0c` | `0631843aecfbcdbd3e30ac2e7c6a2f2d5794f449` |

> [!NOTE]
> These branches are cumulative accepted reference-evidence archives. They are not automatically production authority and are not merged into `main`.

---

## 5. Scope Boundaries and Authorizations

### Currently Authorized
- Active M2-0 execution dependency review and reconciliation.
- Non-destructive repository governance and navigation documentation.

### Explicitly Parked / NOT Authorized
- M2 production implementation / slice expansion: `NOT YET AUTHORIZED`
- Production activation: `NOT AUTHORIZED`
- Solver production implementation: `PARKED / NOT AUTHORIZED`
- Parser production implementation changes: `FROZEN`
- Parser P1: `NOT AUTHORIZED`
- Repository history rewrite, destructive repo cleanup, large dataset migration, or Git LFS conversion: `NOT AUTHORIZED`

---

## 6. Core Contract Invariants

1. **Missing stays missing:** No fabricating or guessing missing dimensions or callouts.
2. **No hidden defaults:** Every assumption must be explicit and reviewable.
3. **Confidence is not validity:** Probabilistic OCR/vision output requires validation before admission.
4. **Explicit units and coordinate systems:** All quantities, lengths, and areas must carry explicit unit metadata.
5. **End-to-end provenance:** Source bounding box, sheet locator, and entity handles survive through to the BOQ line item.
6. **Fail-closed:** Conflicted, blocked, or unverified claims fail closed.
7. **Solver separation:** The Solver is a deterministic calculator consuming canonical facts.

---

## 7. How To Resume Work

1. Read `README.md` for product vision and system architecture.
2. Read `PROJECT_STATE.md` (this file) for current gate state and critical path.
3. Read `docs/INDEX.md` to navigate current vs historical documentation.
4. Read `docs/governance/DOCUMENT_AUTHORITY_INDEX_R1.md` to resolve any document precedence questions.
5. Identify the active milestone (`M2-RCBEAM-VERTICAL-SLICE-001`) and gate (`M2-0 EXECUTION DEPENDENCY CLOSURE`).
6. Execute only within explicitly authorized scope.
7. Always reverify remote `main` before creating any new working branch.
