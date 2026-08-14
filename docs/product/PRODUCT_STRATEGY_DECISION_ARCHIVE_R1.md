# Product Strategy Decision Archive R1

**Project:** `boq_system_v2`  
**Decision date:** 2026-08-14  
**Status:** PM-noted product/governance direction  
**Scope:** Organizational design, engine boundaries, and global stretch goal

## Decision 1 — Research organization

### Current Wave 3

Do **not** reorganize Research during the active Wave 3 TL/backjob cycle.

Current Wave 3 completes under the existing Research TL structure.

### Wave 4 onward

Split Research into two teams to reduce TL synthesis overload and improve specialization:

```text
Research A — Technical / Evidence
    ↓
Research A TL
        ┐
        ├→ Shared Research QA → PM
        │
Research B — Commercial / Product
    ↓
Research B TL
```

#### Research A — Technical / Evidence

Typical scope:

- construction methodology;
- quantity ontology;
- standards and source authority;
- Parser/Solver boundary;
- drawing + BOQ corpus;
- PDF/DWG benchmark work;
- element semantics;
- extraction evidence;
- technical benchmark design.

#### Research B — Commercial / Product

Typical scope:

- pricing/rate methodology;
- estimate reproducibility and commercial audit;
- competitor study;
- estimator UX;
- workflow efficiency;
- product/process research;
- portfolio/career/market leverage.

### QA organization

Keep one shared Research QA initially.

Only split Research QA later if evidence shows QA itself is a bottleneck.

## Decision 2 — Solver and Pricing architecture

Do not create a separate Pricing Team yet.

Keep one Solver umbrella team, but separate responsibilities architecturally:

```text
ESTIMATE / SOLVER DOMAIN
│
├── Quantity Engine
│   └── deterministic measured/derived quantities
│
├── Fabrication / Procurement Engine
│   └── cut lengths, stock, waste, ordered quantities
│
└── Pricing / Rate Engine
    └── rates, effective dates, escalation, normalization,
        overrides, currencies, regional provenance
```

The conceptual quantity chain is:

```text
DRAWING FACTS
    ↓
MEASURED / DERIVED QUANTITIES
    ↓
FABRICATION / PROCUREMENT QUANTITIES
    ↓
RATES
    ↓
COST
```

Changing a rate must not change the engineering quantity.

Changing procurement policy must not change what the drawing says.

Pricing becomes a separate organizational team only if its future workload justifies independent ownership.

### Guiding organizational rule

> Separate responsibilities in architecture earlier than people in organization.

## Decision 3 — Global product stretch goal

Global use is an explicit **stretch goal**, not a current MVP requirement.

Product strategy:

> **Philippines-first, globally portable.**

The system should be proven deeply against Philippine projects, standards, rates, and workflows first.

However, core architecture must avoid making Philippine rules universal assumptions.

### Global-ready conceptual architecture

```text
Drawing Intelligence
        ↓
Canonical Construction Facts
        ↓
Measurement Policy Pack
        ↓
Quantity Engine
        ↓
Fabrication / Procurement Policy Pack
        ↓
Pricing / Rate Engine
        ↓
Regional Commercial Policy
        ↓
BOQ / Estimate
```

### Country-specific concepts must be replaceable

Examples that must not be permanently hardwired as universal:

- DPWH authority;
- Fajardo methodology;
- PHP currency;
- Philippine rebar stock lengths;
- Philippine BOQ/trade classifications;
- Philippine tax and commercial assumptions;
- Philippine measurement conventions.

These should eventually become configurable profiles or policy packs.

Example:

```text
PHILIPPINES_MEASUREMENT_PROFILE
PHILIPPINES_STANDARDS_PROFILE
PHILIPPINES_PROCUREMENT_PROFILE
PHILIPPINES_RATE_PACK
```

Future jurisdictions can introduce equivalent packs without rewriting the Parser or core canonical ontology.

## Proposed future milestone

### M11 — Internationalization / Global Portability

Potential scope:

1. country-neutral canonical ontology;
2. configurable measurement standards;
3. metric / imperial and other unit-system support;
4. currency and tax abstraction;
5. jurisdictional standards profiles;
6. regional pricing/rate sources;
7. procurement-policy profiles;
8. local BOQ/classification systems;
9. language/localization support;
10. international benchmark corpus.

## Proposed future global research wave

Potential tasks:

```text
R5-GLOBAL-001
International BOQ Measurement & Classification Systems

R5-STANDARDS-001
Jurisdictional Engineering / Construction Authority Matrix

R5-RATES-001
International Rate, Currency, Tax and Escalation Architecture

R5-CORPUS-001
Global Drawing + BOQ Corpus Expansion

R5-LOCALIZATION-001
Drawing Language, Symbols, Abbreviations, Units and Convention Differences
```

These are future tasks only. They are not authorized production scope today.

## Corpus implications

The long-running corpus should eventually support metadata such as:

```text
country
region
language
drawing convention
measurement standard
currency
project type
discipline
unit system
BOQ classification
```

This enables measured claims such as:

```text
Parser accuracy on Philippine structural drawings
vs.
Parser accuracy on Australian structural drawings
```

instead of vague "global support" claims.

## Product positioning

Near term:

```text
Philippine construction
→ prove trustworthy drawing understanding + BOQ pipeline
```

Mid term:

```text
multiple Philippine project types
→ generalize architecture, policy boundaries, and corpus
```

Stretch:

```text
international policy/rate/standards packs
→ globally portable construction drawing intelligence platform
```

## Governance effect

These decisions change roadmap and organizational planning, but do **not**:

- authorize production code;
- authorize Solver Wave 2 implementation;
- authorize Parser P1;
- authorize Integration implementation;
- authorize Research Wave 4 or Wave 5 execution;
- authorize global-market support in the current milestone.

They are archived product-direction decisions for future planning.
