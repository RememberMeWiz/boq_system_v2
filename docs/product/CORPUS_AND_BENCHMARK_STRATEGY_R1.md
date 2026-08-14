# Corpus and Benchmark Strategy R1

## Objective

Build a large provenance-controlled collection of construction drawings and associated BOQ/estimate material for Parser, Solver, end-to-end, competitor, regression, and future research benchmarks.

## Core rule

An existing BOQ is a **reference answer**, not automatic ground truth.

Differences may come from revision, scope, measurement method, deductions, allowances, waste, procurement, pricing, or rounding.

## Corpus tiers

### Raw corpus
Large and diverse. Used for robustness/stress testing.

### Paired benchmark corpus
Drawing set + associated BOQ/specification/revision material.

### Gold corpus
Independently annotated, reconciled, and adjudicated.

## Suggested project structure

```text
CORPUS-<ID>/
├── source/
├── provenance/
│   ├── SOURCE_MANIFEST.json
│   ├── SHA256SUMS.txt
│   ├── acquisition.json
│   └── revision_map.json
├── annotations/
│   ├── sheets.json
│   ├── elements.json
│   ├── attributes.json
│   ├── relationships.json
│   └── source_regions.json
├── truth/
│   ├── reference_boq.json
│   ├── candidate_truth.json
│   ├── adjudicated_truth.json
│   └── boq_reconciliation.json
└── benchmark/
    └── expected_results.json
```

## Annotation targets

- sheet type and discipline;
- element type/mark/location;
- schedules and dimensions;
- geometry/material/reinforcement;
- units/counts;
- PDF bounding regions;
- DWG entity handles/layers/blocks where available;
- cross-sheet relationships;
- missing/conflicting fields;
- BOQ mapping;
- quantity stage;
- adjudicated quantities.

## Benchmark split

```text
Development 60%
Validation 20%
Sealed holdout 20%
```

## Benchmark uses

### Parser
Sheet/element/field/unit/localization/cross-sheet/missing/conflict metrics.

### Solver
Gold canonical input → deterministic expected quantity.

### End-to-end
Drawing → Parser → Integration → Solver → BOQ.

### Commercial tools
Use identical frozen projects where access/licensing permits and compare workflow plus results.

## Rights classes

```text
PUBLIC_REDISTRIBUTABLE
PUBLIC_REFERENCE_ONLY
LICENSED
PERMISSION_GRANTED
PRIVATE_RESTRICTED
UNKNOWN_RIGHTS
```

Unknown rights default to restricted handling.

## Storage

Do not make the production code repo the corpus warehouse.

Prefer Git for metadata/manifests/schemas/small redistributable gold artifacts, and controlled external storage or a dedicated dataset repo for large binaries.
