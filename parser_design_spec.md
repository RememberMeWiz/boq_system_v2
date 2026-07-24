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

---

## 2.1. Robust Element & Sheet Identification System

To guarantee 100% extraction accuracy across complex multi-page DPWH and commercial CAD/PDF drawings, the parser implements a multi-tiered **Robust Identification System**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. SHEET CLASSIFIER & TITLE BLOCK IDENTIFIER                                │
│ - Reads Sheet Codes (S-1 to S-7, A-1 to A-10) and Title Box Content         │
│ - Classifies page layout: Schedule Sheet | Framing Plan | Detail Elevation  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. DUAL-PASS HYBRID TEXT & VECTOR OCR IDENTIFICATION                        │
│ - Pass A (Vector Text): Direct extraction of embedded PDF/DXF text fonts    │
│ - Pass B (RapidOCR Fallback): Local ONNX rasterization for exploded CAD      │
│   polylines, stroked glyphs, and non-selectable drawing graphics             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. STRUCTURAL MARK & ENTITY PATTERN MATCHING                                │
│ - Footing Marks: F-1, F-2, CF-1 (Mat/Continuous), WF-1 (Wall Footings)       │
│ - Column Marks: Story-grouped C-1, C-2 (Foundation → 2nd Floor → Roof Deck) │
│ - Beam Marks: 2B-1, RB-1, FTB-1 (Spans, Stirrups, Top/Bottom Rebar)         │
│ - Slab Marks: S-1, S-2, SL-1 (Thickness, Temperature Bars, Main Bar Grid)   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. CROSS-REFERENCE & PROVENANCE TRACKING                                    │
│ - Maps schedule table specs (L × W × D) to framing grid node coordinates    │
│ - Tags every extracted attribute with explicit provenance:                  │
│   [vector_parsed | rapidocr | vision_enriched | assumed_default]            │
└─────────────────────────────────────────────────────────────────────────────┘

---

## 3. Scoped MVP Feature List

| Component | IN MVP Scope (Must Have) | OUT of Scope (Cut for Later) |
| :--- | :--- | :--- |
| **Input Ingestion** | PDF Blueprint Sheets, AutoCAD DXF/DWG Vector Files | 3D IFC / Revit BIM files |
| **Robust Identification System** | **Multi-tier Identification**: Title block sheet codes (S-1 to S-7), dual-pass vector + RapidOCR fallback for exploded CAD text, story-grouped column marks, and explicit provenance tagging | Manual manual key-in of schedule tables |
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
