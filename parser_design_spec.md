# 🎨 AI Blueprint Parser Pipeline — Stage 2 Design Specification

> **Framework**: Following **The Builder's Toolkit** (Stage 2: Design — AI Assists).  
> **Goal**: Define the exact User Flow, Scoped MVP Feature List, Screen Wireframes, and User Success Criteria for a fully dynamic, parameter-driven AI Blueprint Parser.

---

![The Builder's Toolkit Methodology](C:/Users/louis/.gemini/antigravity/brain/fec2906c-fb81-47b4-a08e-b1ad1a62f2c5/builders_toolkit.jpg)

---

## 1. Stage 1 Recap — The Problem Statement
> **User Pain Point**: *"Civil estimators cannot trust simple OCR regex or black-box AI tools to extract structural CAD/PDF blueprints because complex multi-page drawings have scattered schedule tables, story-level column changes, overlapping text labels, and referenced missing pages. Estimators need a dynamic, parameter-driven extraction pipeline that mirrors how a real civil engineer audits drawing sheets before passing clean payload to the cost solver engine."*

---

## 2. Dynamic, Parameter-Driven User Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: VARIANT & SCOPE DETECTION (DYNAMIC)                                 │
│ - Reads Cover & Key Plans to identify building scope, variants & grid count │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: GRID NODE TALLY & FRAMING PLAN EXTRACTION                           │
│ - Dynamically walks grid intersections, tallying member mark pairs           │
│   (Footing + Column node pairs on Foundation Plan, Beams/Slabs on Framing)  │
│ - Reads dimension chains for centerline spans and wall thickness callouts    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: DYNAMIC SCHEDULE TABLE PARSING                                      │
│ - Parses Schedule Tables for Footings, Columns, Beams, Slabs, and Trusses    │
│ - Supports multi-row schedules split by story level (e.g. Lower vs Upper)  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: GENERAL NOTES, LAP SPLICES & HOOK TABLES                             │
│ - Reads Concrete Cover rules, Lap Splice tables, and Standard Hook tables   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: MISSING SHEET AUDIT & VERIFICATION SCREEN                           │
│ - Table of Contents Audit: Flags referenced but missing pages to estimator  │
│ - Display Modes: Toggle 🔄 Side-by-Side Comparison vs 🔍 Direct Overlay     │
│ - Sidebar: 📜 Collapsible Real-Time Parser Action Log Console (Debug)       │
│                                                                             │
│ Decision Point: [ ✍️ Edit/Override Spec ]  or  [ ✅ Approve Parsed Payload ] │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: HANDOFF CLEAN PAYLOAD TO FAJARDO SOLVER ENGINE                      │
│ ZERO math/calculations in parser — clean structural payload passed to Solver │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Scoped MVP Feature List

| Component | IN MVP Scope (Must Have) | OUT of Scope (Cut for Later) |
| :--- | :--- | :--- |
| **Input Ingestion** | PDF Blueprint Sheets, AutoCAD DXF/DWG Vector Files | 3D IFC / Revit BIM files |
| **Building Scope Detection** | Auto-detects building scope, variants, and grid spans via Key Plans & Title Sheets | Arbitrary non-standard residential custom variants without key plan |
| **Grid Node Tallying** | Dynamically tallies grid node intersections, member pairs, beam spans, purlin spacings | Non-grid freeform curve geometry |
| **Schedule Table Extraction** | **Footing specs** ($L, W, H$), **Column details split by story level** (*Lower Level* vs *Upper Level*), Beam & Slab specs | Complex curved bridge schedules |
| **Structural Details & Notes** | Concrete cover requirements, Lap splice tables, 90°/135°/180° standard hook lengths | Geotechnical soil shear reports |
| **Missing Sheet Audit** | Table of Contents Audit vs present sheets $\rightarrow$ Flags missing pages as warnings | Auto-generating missing architectural pages from scratch |
| **Visual Viewer Modes** | (1) **Side-by-Side Comparison**, (2) **Direct Overlay** (outlines + rebar directly on PDF page), framing & elevation outlines | Photorealistic 3D structural mesh |
| **Parser Debugging Suite** | **Collapsible Real-Time Parser Action Log Sidebar**: Streams live execution steps, sheet classification events, table parsing logs, and debug notices in the app | External heavy APM log tools |
| **Strict Parser Boundary** | **Zero Math / Calculations in Parser** (Volume, weight, cost calculations reserved 100% for Solver Engine) | Calculation formulas inside parser |

---

## 4. Strict Boundary: Parser vs. Solver Engine

```
┌──────────────────────────────────────────┐    ┌──────────────────────────────────────────┐
│             PARSER PIPELINE              │    │              SOLVER ENGINE               │
│  (Extraction, Identification, Data QA)   │    │      (13-Trade Civil Cost Engine)        │
├──────────────────────────────────────────┤    ├──────────────────────────────────────────┤
│ • Identifies Footings, Columns, Beams    │    │ • Computes Concrete Volume (cu.m.)       │
│ • Extracts $L, W, H$, spans, counts      │ ──►│ • Computes PNS 49 Rebar Weights (kg)   │
│ • Flags missing specs & recommendations  │    │ • Applies Fajardo Laying/Mortar Factors  │
│ • Renders Visual Overlay & Action Logs   │    │ • Computes DPWH Material/Labor Costs (₱) │
│ • ZERO MATH / NO CALCULATIONS HERE       │    │ • All Mathematics Lives Here             │
└──────────────────────────────────────────┘    └──────────────────────────────────────────┘
```

---

## 5. Next Stage Readiness
Following **The Builder's Toolkit**:
- **Stage 1 (Empathy)**: Problem statement clear ✅
- **Stage 2 (Design)**: Dynamic extraction user flow, view mode toggles, story-split column details, missing sheet audit & MVP scope defined ✅
- **Stage 3 (Architecture — Next Step)**: Define tech stack boundaries, API schemas, and data models for `vision_parser.py`, `reconciler.py`, and `reconstruction_module.py`.
