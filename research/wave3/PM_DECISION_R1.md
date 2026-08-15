# Independent Research Wave 3 — PM Decision R1

**Project:** `boq_system_v2`  
**Decision date:** 2026-08-14  
**QA package:** `INDEPENDENT_RESEARCH_WAVE3_QA_TO_PM_R1.zip`  
**QA package SHA-256:** `bb24abbd2741a35f6826b4c260438629c73c503d4693ad31e09f8a3f8b431ce3`  
**QA input TL package:** `INDEPENDENT_RESEARCH_WAVE3_TECH_REVIEW_R1.zip`  
**QA-recorded TL package SHA-256:** `4b231c5f3f0d0ab4e7e460663a5e85eee5589773b46f0669f8f0947e7477a263`

## PM verdict

```text
PM_AUTOMATED_DECISION
PM_ACCEPTED_WITH_NOTES
RESEARCH_WAVE3_CLOSED
RESEARCH_WAVE3_FROZEN_AS_REFERENCE_EVIDENCE
NO_REWORK
```

Research Wave 3 is accepted as sufficiently supported research evidence.

This decision does **not** automatically adopt research recommendations as production policy, measurement policy, structural/detailing rules, procurement rules, pricing precedence, storage architecture, standards editions, or parser automatic-acceptance behavior.

## QA result accepted

```text
QA_PASS_WITH_NOTES
```

PM accepts QA's independent hard-gate recount, semantic sampling, clean validator reruns, mutation checks, and independent numerical/logical recalculations.

Notable QA correction retained:

- RCBEAM strict multi-diameter cases: `17`, not TL's `18`;
- minimum required: `15`;
- gate remains passed.

## PM standards-status override

### ASTM C94/C94M current edition

QA records `ASTM C94/C94M-26C` as Active at its 2026-08-14 check time.

PM's independent retrievable first-party check did not reproduce that exact current-edition claim and still exposed `ASTM C94/C94M-26B` as Active.

Therefore the authoritative PM status is:

```text
ASTM_C94_CURRENT_EDITION = UNRESOLVED_AT_PM
```

This is **nonblocking for Research Wave 3 closure** because:

1. Research 6's correction logic already recognized mutable publisher metadata as time-bounded;
2. no specific ASTM edition is being adopted into production by this decision;
3. any future implementation/adoption depending on the current ASTM C94 edition must perform a fresh first-party lookup and preserve the exact observation time/source metadata.

No worker backjob is required solely to force a mutable publisher page into artificial certainty.

### ISO 12006-2 status

PM independently reproduced the correction-sensitive ISO status:

- `ISO 12006-2:2015` remains current after 2026 confirmation;
- the Edition 3 `ISO/DIS 12006-2` project is deleted/cancelled at stage `40.98`.

These remain dated source-status observations rather than universal project adoption decisions.

## Research package dispositions

```text
R3-COST-001       ACCEPTED_WITH_NOTES / FROZEN
R3-ONTOLOGY-001   ACCEPTED_WITH_NOTES / FROZEN
R3-RCBEAM-001     ACCEPTED_WITH_NOTES / FROZEN
R3-BOUNDARY-001   ACCEPTED_WITH_NOTES / FROZEN
R3-AUDIT-001      ACCEPTED_WITH_NOTES / FROZEN
R3-STANDARDS-001  ACCEPTED_WITH_NOTES / FROZEN
```

## Adoption boundary

Research evidence may now be used by PM to make explicit implementation decisions.

The following remain separate decisions:

- measurement regime;
- quantity-stage model;
- structural/detailing assumptions;
- splice/coupler rules;
- fabrication/procurement objective hierarchy;
- rate precedence and commercial overrides;
- VAT/FX/escalation policy;
- parser automatic acceptance;
- storage architecture;
- project-specific standards editions;
- production code authorization;
- Repository Steward actions;
- merges.

## Project effect

Research Wave 3 is no longer a blocker to M1.

Remaining major M1 dependency:

```text
Parser P0-006 source bundle upload
→ Parser Worker C materialization
→ Parser TL
→ Parser QA
→ PM
```

Solver Wave 2 readiness is already PM-accepted and parked pending the remaining cross-team gate(s).

Once Parser P0-006 is cleared, PM can reconcile the accepted Wave 3 findings with Solver readiness and freeze the minimum Parser → Integration → Solver contracts for the first RC-beam production vertical slice.

## Organizational follow-on

The previously recorded organizational decision remains:

- Wave 4+ Research splits into Research A (Technical / Evidence) and Research B (Commercial / Product), with separate TLs and shared Research QA initially.
- Pricing remains architecturally separate from quantity/fabrication/procurement under the Solver umbrella until workload justifies a dedicated team.
- Global use remains a Philippines-first, globally portable stretch direction.
