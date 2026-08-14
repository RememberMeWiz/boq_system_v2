# BOQ System Product Vision R3

**Project:** `boq_system_v2`  
**Date:** 2026-08-14  
**Status:** Proposed authoritative product direction

## What

`boq_system_v2` is an evidence-backed construction drawing intelligence and BOQ system.

It is not merely OCR, automatic takeoff, or a formula calculator. It should understand enough of a PDF/DWG drawing set to form solver-critical construction claims, show where those claims came from, block unresolved facts, calculate deterministic quantities, and produce a BOQ traceable back to source evidence.

```text
PDF / DWG
→ sheet understanding
→ element identification
→ field-level claims
→ source localization / visual provenance
→ verification / conflict / missing state
→ canonical Solver input
→ deterministic quantities
→ fabrication / procurement
→ rate provenance
→ BOQ
→ reproducible audit trace
```

The **Parser is the evidence engine**.  
The **Solver is the deterministic calculation engine**.  
**Integration is the unit/provenance/validation boundary** between them.

## Why

Construction estimating requires more than reading text. An estimator recognizes sheet types, elements, schedules, dimensions, notes, cross-sheet relationships, revisions, omissions, conflicts, measurement rules, and scope.

The product opportunity is therefore not simply "automatic takeoff." The harder and more valuable problem is:

> **trustworthy drawing understanding with visible evidence and reproducible calculation lineage.**

For every important number the system should answer:

```text
What is this number?
Why should I believe it?
```

## Product promise

For every solver-critical fact, the user should eventually be able to inspect:

- its construction element;
- source sheet and revision;
- exact PDF region or DWG entity;
- observed/derived/missing/conflicting/manual state;
- source and canonical unit;
- verification state;
- downstream transformation;
- formula/Solver version;
- rate source and effective date where applicable.

A BOQ line should be navigable backward to its source evidence.

## Strategic differentiator

```text
UNDERSTAND + PROVE + CALCULATE
```

not merely:

```text
MEASURE + EXPORT
```

## Product principles

1. **Parser as evidence engine.** Plausible JSON is not enough.
2. **Missing stays missing.** No hidden sample/default replacement for solver-critical facts.
3. **Visual provenance is first-class.** PDF regions and DWG entity identity are evidence, not decoration.
4. **Native structure before vision guessing.** CAD/vector → spatial/text → OCR → vision → human review.
5. **Confidence is not validity.** High confidence cannot override conflict, missing provenance, units, or review policy.
6. **Unit-safe deterministic Solver boundary.** Solver does not repair Parser omissions silently.
7. **Quantity stages remain explicit.** Observed, measured, gross, net, fabricated, procured, installed, waste/allowance must not collapse.
8. **Reproducibility over appearance.** A believable number is not enough.
9. **Targeted human review.** Humans review genuine judgment, not checksums/Git routine.
10. **No hidden policy.** Engineering, measurement, estimating, fabrication, procurement, company, project, pricing, and software decisions remain distinguishable.

## Strategic assets

- large PDF/DWG + BOQ corpus;
- source-backed formula/methodology reference;
- golden solved cases;
- audit/provenance architecture.

Existing BOQs are **reference answers**, not automatic ground truth.

## First production success criterion

```text
known RC beam drawing evidence
→ beam identified
→ required facts source-localized
→ missing/conflicting facts blocked
→ canonical beam input
→ deterministic concrete/formwork/rebar
→ fabrication/procurement
→ BOQ
→ full source-to-result trace
```

## Product North Star

For every number that matters:

```text
Where did it come from?
Which drawing/revision supplied it?
What element does it belong to?
What was observed, derived, missing, conflicting, or manually confirmed?
Which units were used?
Which verification state allowed it forward?
Which formula/version produced it?
Which procurement/rate policy transformed it?
Can another reviewer reproduce it?
```


## Geographic product strategy

The product is **Philippines-first, globally portable**.

Philippine construction practice is the first deep proving ground, not a permanent hardcoded limit.

Canonical drawing facts and core quantity semantics should remain as jurisdiction-neutral as practical, while measurement, standards, procurement, pricing, currency, tax, classification, and localization concerns are introduced through explicit policies/profiles.

Global use remains a stretch goal until the Philippine evidence-backed pipeline is proven.
