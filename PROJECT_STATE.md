# Current Project State

> PM checkpoint and durable resumability record for `RememberMeWiz/boq_system_v2`.  
> Capture date: 2026-08-15, Asia/Manila.  
> Verified base commit (`main`): `70b3d06f0bc28686bec44b01a087cc9dcbf78e63`.  
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

### Active technical milestone: `PIS-CONTRACT-FREEZE-001: NOT CLOSED`
- **Purpose:** Freeze the minimum Parser -> Integration -> Solver evidence contract before production implementation.
- **Current active owner & gate:** `Integration TL` (`ACTIVE / EVIDENCE RESUBMISSION`)
  - Integration QA R1 review disposition: `QA_BLOCKED` (`EVIDENCE_COMPLETENESS`).
  - PM review disposition: `PM_RETURN_TO_INTEGRATION_TL` (evidence custody resubmission; contract architecture remains intact).
- **Subsystem compatibility status:**
  - Parser TL compatibility: `CLEARED`
  - Solver TL compatibility: `CLEARED`
  - Integration TL reconciliation: `ACTIVE / RESUBMITTING EVIDENCE`
- **Next gate:**
  `Integration TL evidence-complete resubmission -> Integration QA independent replay -> PM contract-freeze decision`

### Current critical path
```text
Integration TL evidence-complete resubmission
-> Integration QA independent replay
-> PM contract-freeze decision
-> Integration implementation authorization
-> RC Beam production vertical slice
```

---

## 3. Completed and Accepted Milestones

| Milestone / Area | Status | Reference Authority |
|---|---|---|
| Product R3 governance | `CLOSED / MERGED` | `docs/product/PRODUCT_PLAN_R3.md` |
| Parser P0-006 | `CLOSED / ACCEPTED GOLDEN TRUTH` | Parser P0-006 PM Decision |
| Parser PO truth review | `18 / 18 COMPLETE` | Product Owner Acceptance |
| Solver readiness | `ACCEPTED / PARKED` | Solver Phase 0 Baseline Audit |
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
- Active evidence resubmission and review on `PIS-CONTRACT-FREEZE-001`.
- Non-destructive repository governance and navigation documentation.

### Explicitly Parked / NOT Authorized
- Solver production implementation: `PARKED / NOT AUTHORIZED`
- Integration production implementation: `NOT AUTHORIZED`
- Parser production implementation changes: `FROZEN`
- Parser P1: `NOT AUTHORIZED`
- RC Beam production vertical slice implementation: `NOT YET AUTHORIZED`
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
5. Identify the active milestone (`PIS-CONTRACT-FREEZE-001`) and gate (`Integration TL ACTIVE / EVIDENCE RESUBMISSION`).
6. Execute only within explicitly authorized scope.
7. Always reverify remote `main` before creating any new working branch.
