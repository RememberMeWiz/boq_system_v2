# PM DIRECTIVE — RESEARCH ORGANIZATION RESTRUCTURE R2

## Decision

```text
PM_AUTOMATED_DECISION
RESEARCH_RESTRUCTURE_R2_APPROVED
EFFECTIVE_WAVE4
```

This directive supersedes `PM_RESEARCH_RESTRUCTURE_DIRECTIVE_R1`.

## Worker naming rule

Do not rename research workers.

The permanent worker identities remain:

```text
Research 1
Research 2
Research 3
Research 4
Research 5
Research 6
```

Do not use worker names such as:
- Research A Worker 1;
- Research B Worker 1;
- Technical Research Worker;
- Commercial Research Worker.

Team ownership is represented by the TL/QA route, not by renaming workers.

## Lane A

```text
Research 1
Research 2
Research 3
    ↓
Research A TL
    ↓
Research A QA
    ↓
PM
```

Research A owns primarily technical/evidence questions:
- PDF/DWG understanding;
- Parser research;
- construction element semantics;
- quantity ontology;
- measurement methodology;
- standards/source authority;
- evidence/provenance;
- drawing + BOQ corpus;
- benchmark truth;
- Parser/Solver technical boundaries.

## Lane B

```text
Research 4
Research 5
Research 6
    ↓
Research B TL
    ↓
Research B QA
    ↓
PM
```

Research B owns primarily commercial/product questions:
- pricing/rate systems;
- commercial provenance;
- estimator workflow;
- UX;
- competitors;
- project/process efficiency;
- product strategy;
- career/freelance leverage;
- commercial/global portability.

## Separate QA rule

Research A QA and Research B QA are independent functions.

Neither QA waits for the other lane.

Allowed:

```text
Research A QA ACTIVE
Research B workers still ACTIVE
```

or:

```text
Research B QA ACTIVE
Research A already PM_ACCEPTED
```

There is no combined Research QA gate from Wave 4 onward.

## Cross-domain work

For a cross-domain task:
1. PM names one lane as primary.
2. A worker remains named Research 1-6.
3. The primary lane TL reviews it.
4. The primary lane QA reviews it.
5. The other lane may be consulted without becoming a mandatory approval gate.
6. PM resolves conflicting recommendations.

## Workload

Default:

```text
Research A TL: Research 1-3
Research B TL: Research 4-6
```

Reassignment between lanes is allowed only by PM when workload or expertise warrants it.

A reassigned worker keeps the same worker name.

## Archival

Each lane archives accepted research after PM acceptance:

```text
PM_ACCEPTED
→ ARCHIVE_PENDING
→ REMOTE_ARCHIVE_VERIFIED
→ CLOSED_AND_ARCHIVED
```

Archive structure may identify lane/task ownership, but historical worker names remain unchanged.
