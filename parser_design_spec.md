# 🎨 AI Blueprint Parser Pipeline — Stage 2 Design Specification

> **Framework**: Following **The Builder's Toolkit** (Stage 2: Design — AI Assists).
> **Goal**: Define the exact User Flow, Scoped MVP Feature List, Screen Wireframes, and User Success Criteria for a fully dynamic, parameter-driven AI Blueprint Parser.

> **Scope note:** This document is Stage 2 — its job is the **what** and **why**
> (what the parser must identify, why it matters, what each trade needs and
> why the gap exists). Everything in it is an initial idea, not a locked
> decision. Anywhere a JSON schema, formula, or numeric threshold appears
> (e.g. 2.1.C, the formula sketches in Section 5), treat it as a placeholder
> sketch of "something like this will exist" — not the actual data model or
> computation logic. Those **how's** belong to Stage 3 (Architecture) and are
> only here as a preview so Stage 3 doesn't start from zero.

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
│                                                                              │
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

## 2.1. Robust Element & Sheet Identification System

To guarantee accurate extraction across complex multi-page DPWH and commercial CAD/PDF drawings, the parser implements a multi-tiered **Robust Identification System**. At a glance:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. SHEET CLASSIFIER & TITLE BLOCK IDENTIFIER                                │
│ - Reads Sheet Codes (S-1 to S-7, A-1 to A-10) and Title Box Content         │
│ - Classifies page layout per the Page Type table in 2.1.A                  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. DUAL-PASS HYBRID TEXT & VECTOR OCR IDENTIFICATION                        │
│ - Pass A (Vector Text): Direct extraction of embedded PDF/DXF text fonts    │
│ - Pass B (RapidOCR Fallback): Local ONNX rasterization for exploded CAD     │
│   polylines, stroked glyphs, and non-selectable drawing graphics            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. STRUCTURAL & ARCHITECTURAL ELEMENT PATTERN MATCHING                      │
│ - Per the full Element Taxonomy in 2.1.B (footings, columns, beams, slabs,  │
│   walls, roofing, doors/windows, ceilings, tile, MEP fixtures)             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. UNIFIED RECORD + CROSS-REFERENCE + PROVENANCE TRACKING                   │
│ - Every element (not just schedule rows) is written to ONE record shape,   │
│   defined in 2.1.C, consumed directly by both Outliner and Solver          │
│ - Tags every extracted attribute with provenance + numeric confidence      │
│   (2.1.D): [vector_parsed | rapidocr | vision_enriched | assumed_default]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why the unified record matters:** earlier iterations of this pipeline wrote
schedule data (footings/columns/beams) to one payload field and display data
to a separate `elements` field. The two were populated by different code
paths and drifted out of sync — OCR would successfully recover a footing
schedule, the cost solver would pick it up, but the Blueprint Outliner UI
stayed empty because nothing ever converted the recovered schedule rows into
the shape the outliner reads. Item 4 above exists specifically to make that
class of bug structurally impossible: one array, one schema, read by both
consumers.

### 2.1.A — Page / Sheet Type Classification

Every page is classified *before* any element extraction runs, so the right
extraction strategy is chosen and the wrong one is never attempted (e.g. no
footing-schedule regex run against an elevation sheet).

| Sheet Type | Typical Codes | Extraction Strategy | Feeds |
|---|---|---|---|
| Structural Schedule | S-3, S-4, S-5 (title contains "SCHEDULE OF") | Dual-pass table OCR: vector text → RapidOCR fallback | Element dimensions, rebar specs |
| Structural Framing / Foundation Plan | S-2, S-6 | Grid-node detection + mark-callout OCR | Element **count** and **location** |
| Structural Details/Sections | S-7 | Detail-callout OCR (bend shapes, spacing notes) | Rebar detailing overrides |
| Architectural Floor Plan | A-2, A-3 | Vector wall/room polygon extraction + area calc | Wall length, room floor area, opening list |
| Architectural Elevation | A-4, A-5 | Vertical dimension OCR, roofline detection | Wall height, roof pitch |
| Architectural Roof Plan | A-6 | Vector roof-plane area extraction | Roofing area |
| Door/Window Schedule | A-7 (or inset table on A-2/A-3) | Same dual-pass table OCR pattern as structural schedules | Door/window type, size, count |
| MEP Layout (Electrical/Plumbing) | E-1, P-1 | Symbol detection + legend cross-reference | Fixture/outlet counts by type |
| Title Block / Cover Sheet | — | Metadata only, no takeoff extraction | Project name, scale, sheet index |

Classification signal priority: (1) sheet code prefix in title block, (2)
title text keywords, (3) dominant content heuristic as a fallback only.

### 2.1.B — Element Taxonomy

For every element type, the pipeline resolves the same four things: what it's
called, what geometry/spec it needs, where that data comes from, and which
of the 13 trades (Section 5) consume it.

| Element | Mark Pattern | Required Attributes | Primary Source Page(s) | Feeds Trades |
|---|---|---|---|---|
| Footing | `F-#`, `CF-#` (mat/continuous), `WF-#` (wall footing) | L, W, D, main bar dia + spacing (both ways), count | Schedule + Foundation Plan | Concrete, Formworks, Rebar, Earthworks |
| Column | `C-#`, story-grouped | Section (b×h or Ø), height per story, main bars (qty+dia), ties (dia+spacing), count per story | Schedule + Framing Plan | Concrete, Formworks, Rebar |
| Beam | `B-#`, `RB-#` (roof beam), `FTB-#` (tie beam) | Section (b×h), span length, top/bottom bar (qty+dia), stirrup (dia+spacing), count | Schedule + Framing Plan | Concrete, Formworks, Rebar |
| Slab | `S-#`, `SL-#` | Thickness, area (**from plan, not schedule**), main bar dia/spacing, temp bar dia/spacing | Schedule (thickness/bars) + Framing Plan (area) | Concrete, Formworks, Rebar |
| Wall (CHB) | none — derived | Length, height, thickness/CHB class, opening deductions | Floor Plan + Elevation | Masonry, Painting |
| Roofing | none — derived | Roof area, pitch, material spec | Roof Plan + Elevation | Roofing |
| Door / Window | `D-#`, `W-#` | Type, width × height, count | Door/Window Schedule + Floor Plan (location) | Doors & Windows, Painting (deduction) |
| Ceiling | none — derived | Room floor area (ceiling ≈ floor area) per finish type | Floor Plan | Ceiling Works |
| Floor/Wall Tile | none — derived | Room floor/wall area by finish type | Floor Plan + Finish Schedule | Tile Works |
| Plumbing Fixture | legend symbol | Fixture type + count | Plumbing Layout + Legend | Plumbing |
| Electrical Fixture/Outlet | legend symbol | Type + count | Electrical Layout + Legend | Electrical |

### 2.1.C — Unified Element Record *(placeholder sketch — final shape is a Stage 3 decision)*

One JSON shape, one array (`payload["elements"]`), consumed directly by both
the Blueprint Outliner (`bounding_box` / `location_ref`) and the Solver
(`geometry` / `reinforcement`, filtered by `trades`). Schedule-shaped views
(e.g. "all footings") are read-time filters over this array, not a second
write target:

```json
{
  "element_id": "footing_1",
  "element_type": "footing",
  "mark": "F-1",
  "sheet_source": "S-4",
  "geometry": {
    "length_m": 1.4,
    "width_m": 1.4,
    "depth_m": 0.35
  },
  "reinforcement": {
    "main_bar_dia_mm": 20,
    "main_bar_count_each_way": 7
  },
  "count": 6,
  "location_ref": "Grid A-1, A-2, B-1, B-2, C-1, C-2",
  "bounding_box": [0, 0, 0, 0],
  "provenance": "rapidocr",
  "confidence": 0.82,
  "trades": ["concrete", "formworks", "rebar", "earthworks"]
}
```

`element_type` values are exactly the rows in 2.1.B (`footing`, `column`,
`beam`, `slab`, `wall`, `roofing`, `door_window`, `ceiling`, `tile`,
`plumbing_fixture`, `electrical_fixture`). Non-quantity elements (walls,
roofing, ceiling, tile) use the same envelope with `geometry` fields specific
to them (e.g. `wall_length_m`, `wall_height_m`) instead of `length/width/depth`.

### 2.1.D — Confidence & Provenance

The existing four-value provenance legend (`Parsed·Vector`, `Vision·Extracted`,
`Offline·OCR`, `Assumed`) is kept, plus a numeric `confidence` field (0–1) so
the Verification Gate can flag *individual* low-confidence elements, not only
"table not found" at the page level. Placeholder thresholds, to be tuned in
Stage 3: `< 0.5` → hard warning (requires sign-off), `0.5–0.75` → soft flag
(shown, non-blocking), `> 0.75` → no flag.

---

## 3. Scoped MVP Feature List

| Component | IN MVP Scope (Must Have) | OUT of Scope (Cut for Later) |
| :--- | :--- | :--- |
| **Input Ingestion** | PDF Blueprint Sheets, AutoCAD DXF/DWG Vector Files | 3D IFC / Revit BIM files |
| **Robust Identification System** | **Multi-tier Identification**: page-type classification (2.1.A), dual-pass vector + RapidOCR fallback, full element taxonomy (2.1.B) written to one unified record (2.1.C), explicit provenance + confidence tagging (2.1.D) | Manual manual key-in of schedule tables |
| **Building Scope Detection** | Auto-detects building scope, variants, and grid spans via Key Plans & Title Sheets | Arbitrary non-standard residential custom variants without key plan |
| **Grid Node Tallying** | Dynamically tallies grid node intersections, member pairs, beam spans, purlin spacings | Non-grid freeform curve geometry |
| **Schedule Table Extraction** | **Footing specs** ($L, W, H$), **Column details split by story level** (*Lower Level* vs *Upper Level*), Beam & Slab specs, Door/Window schedules | Complex curved bridge schedules |
| **Structural Details & Notes** | Concrete cover requirements, Lap splice tables, 90°/135°/180° standard hook lengths | Geotechnical soil shear reports |
| **Missing Sheet Audit** | Table of Contents Audit vs present sheets → Flags missing pages as warnings | Auto-generating missing architectural pages from scratch |
| **Visual Viewer Modes** | (1) **Side-by-Side Comparison**, (2) **Direct Overlay** (outlines + rebar directly on PDF page), framing & elevation outlines | Photorealistic 3D structural mesh |
| **Parser Debugging Suite** | **Collapsible Real-Time Parser Action Log Sidebar**: Streams live execution steps, sheet classification events, table parsing logs, and debug notices in the app | External heavy APM log tools |
| **Strict Parser Boundary** | **Zero Math / Calculations in Parser** (Volume, weight, cost calculations reserved 100% for Solver Engine) | Calculation formulas inside parser |

---

## 4. Strict Boundary: Parser vs. Solver Engine

```
┌──────────────────────────────────────────┐    ┌──────────────────────────────────────────┐
│             PARSER PIPELINE               │    │              SOLVER ENGINE               │
│  (Extraction, Identification, Data QA)    │    │      (13-Trade Civil Cost Engine)        │
├──────────────────────────────────────────┤    ├──────────────────────────────────────────┤
│ • Identifies all element types (2.1.B)    │    │ • Computes Concrete Volume (cu.m.)       │
│ • Extracts geometry, rebar, spans, counts │ ──►│ • Computes PNS 49 Rebar Weights (kg)     │
│ • Flags missing specs & recommendations   │    │ • Applies Fajardo Laying/Mortar Factors  │
│ • Renders Visual Overlay & Action Logs    │    │ • Computes DPWH Material/Labor Costs (₱) │
│ • ZERO MATH / NO CALCULATIONS HERE        │    │ • All Mathematics Lives Here — full input│
│                                            │    │   requirements per trade in Section 5    │
└──────────────────────────────────────────┘    └──────────────────────────────────────────┘
```

---

## 5. 13-Trade Solver — Required Input Reference

This section is the elaboration of the Solver side of the boundary above:
what each of the 13 trades needs, where it comes from, and what's already
covered by the current pipeline vs. what's net-new. The "Key Inputs" column
sometimes sketches a formula shape (e.g. `L × W × D × count`) purely to show
*what quantity is needed and why it maps to that trade* — these are not the
final computation logic, which is Stage 3's job.

**Basis for the trade list:** matches the standard trade/division breakdown
used in typical Philippine small-building BOQs (DPWH-style), consistent with
the "General Requirements" line already shown in the BOQ Checklist UI.
Reconcile against the actual trade constants in the solver code and rename
here if they differ.

Today's solver computes **3 of the 13** (Concrete, Formworks, Rebar) — the
only ones fully derivable from the structural schedule tables the parser
currently extracts. The remaining 10 need architectural-drawing extraction
not yet built. Legend: ✅ extractable today · ❌ needs new extraction capability.

| # | Trade | Key Inputs | Source | Status |
|---|---|---|---|---|
| 1 | General Requirements | Lump sum or % of direct-cost subtotal (mobilization, permits, temp facilities) | Solver config, not drawing data | ❌ config field |
| 2 | Earthworks | Footing L/W/D/count; excavation clearance allowance; gravel bedding area × thickness | Schedule (have) + config (missing) | ✅ / ❌ |
| 3 | Concrete Works | L × W × D × count per element type | Structural Schedules | ✅ |
| 4 | Formworks | Contact surface area of poured faces (excl. soil-contact faces) | Structural Schedules | ✅ |
| 5 | Reinforcing Steel | Bar length × unit weight (kg/m by dia) × bar count | Structural Schedules | ✅ |
| 6 | Masonry Works | Wall length × height − opening area; CHB class | Floor Plan + Elevation (new) | ❌ |
| 7 | Roofing Works | Roof plan area ÷ cos(pitch); gutter run ≈ roof perimeter | Roof Plan + Elevation (new) | ❌ |
| 8 | Doors & Windows | Type, W×H, count from Door/Window Schedule | Same table-OCR pattern as structural schedules, new table | ❌ (low effort) |
| 9 | Ceiling Works | Room floor area per room, by finish type | Floor Plan room-polygon extraction (new, shared w/ #10) | ❌ |
| 10 | Tile Works | Room floor/wall area by finish type | Floor Plan (shared w/ #9) + Finish Schedule | ❌ |
| 11 | Painting Works | Wall area (from #6) + ceiling area (from #9), by paint system | Reuses #6 + #9, no new extraction | ❌ (depends on #6, #9) |
| 12 | Plumbing Works | Fixture count by type; pipe runs often allowance-based | MEP Layout + legend symbol detection (new, novel) | ❌ |
| 13 | Electrical Works | Outlet/switch/fixture count; wire runs often allowance-based | MEP Layout + legend symbol detection (shares approach w/ #12) | ❌ |

**Shared-quantity note:** Trades 6, 9, 10, 11 all key off the same two
architectural quantities — wall length/height and room floor area. Build
that extraction once (Floor Plan + Elevation), store it as shared data, and
let all four trades read from it rather than re-deriving it four times. This
is the same "one source of truth" principle behind the unified element
record in 2.1.C, applied to solver inputs instead of parser output.

**Suggested build order:**
1. *(Done)* Concrete, Formworks, Rebar — structural schedules.
2. Earthworks (reuses footing dims already extracted) + Doors & Windows
   (reuses the existing table-OCR pattern on a new schedule table) — lowest
   incremental effort.
3. Floor Plan + Elevation wall/room-geometry extraction — one new capability
   that unlocks Masonry, Ceiling, Tile, and Painting together.
4. Roofing (Roof Plan geometry extraction).
5. Plumbing + Electrical — symbol/legend detection, the most different
   extraction approach from everything above; tackle once the table-OCR and
   plan-geometry pipelines are stable.

---

## 6. Next Stage Readiness
Following **The Builder's Toolkit**:
- **Stage 1 (Empathy)**: Problem statement clear ✅
- **Stage 2 (Design)**: Dynamic extraction user flow, view mode toggles, story-split column details, missing sheet audit, unified element/page identification system, full 13-trade input requirements, and MVP scope defined ✅
- **Stage 3 (Architecture — Next Step)**: Define tech stack boundaries, API schemas, and data models for `vision_parser.py`, `reconciler.py`, and `reconstruction_module.py`, implementing the unified element schema from 2.1.C as the single payload shape across parser, outliner, and solver.
