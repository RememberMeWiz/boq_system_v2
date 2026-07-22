# Automated Quantity Takeoff and Bill of Quantities (BOQ) Generation System
## Objectives Statement and Technical Specifications — Version 2.0 (v2.0)

* **Plan2Takeoff V2 — Technical Specification & Architecture Roadmap Baseline

> **Version**: 2.0.0 (Master Production Specification)  
> **Author**: Plan2Takeoff Engineering Team & Antigravity AI Project Manager  
> **Status**: Approved & Active  
> **Target Trade Scope**: 13 Divisions matching [`UY_Louis.xlsx`](file:///E:/Users/Louis/Documents/3rd%20Yr%20college%202025-26/2nd%20sem/QTYSUR/qty%20lab/QtySur%20Estimate/UY_Louis.xlsx)  
> **Fajardo Knowledge Base**: 100% Complete ([`formula_exhaustive_handbook.md`](file:///e:/Users/Louis/Documents/boq_system_v2/formula_exhaustive_handbook.md), Appendices A, B, C)  
> **Vector Alignment Tolerance**: $< 1.0\text{ mm}$ spatial variance (Verified: $0.0509\text{ mm}$ passed in [`test_vector_diff.py`](file:///e:/Users/Louis/Documents/boq_system_v2/backend/engine/test_vector_diff.py))  
> **V1 Isolation Status**: 100% Isolated (Zero write access to V1 Supabase tables or `project-files` bucket)ion — Version 2.0
* **V1 Preservation & Isolation Policy**: V2 builds upon the validated parsing and formula algorithms of V1 (`boq_system`), but maintains **100% isolation** from V1 database tables and cloud storage buckets (`project-files`). V2 uses dedicated V2 database schemas and local/V2 storage.

---

## 1. Objectives Statement

### 1.1 Project Title
**Plan2Takeoff V2 — Automated Multi-Trade Structural Engine, Native Blueprint Vector Overlay & Direct Costing Platform.**

### 1.2 General Objective
To develop a production-grade, offline-capable software system that ingests architectural and structural CAD drawings (DWG/DXF/PDF), parses geometry and text annotations, computes quantity takeoffs across **13 complete construction trade divisions** using Max Fajardo formulas, applies DPWH CMPD Direct Costs (Material + Labor + Equipment), and renders interactive vector heatmaps on native blueprint sheets with visual diff validation.

---

### 1.3 Specific V2 Objectives & Measurable Goal Criteria

#### **Objective 1: 13-Trade Construction Scope Ingestion**
* **Goal Criteria**: Expand takeoff scope from 3 trades to all **13 trade divisions** defined in reference estimate workbook `UY_Louis.xlsx`.
* **Measurable Target**: 100% automated mapping of items across General Requirements, Earthworks, Concrete, Masonry, Metals, Roofing, Doors/Windows, Tiles, Painting, Plumbing, Electrical, Mechanical, and Special Works.

#### **Objective 2: Direct Cost Calculation Engine (Material + Labor + Equipment)**
* **Goal Criteria**: Compute Total Direct Cost ($C_{\text{total}} = C_{\text{material}} + C_{\text{labor}} + C_{\text{equipment}}$) for all structural and architectural line items using DPWH Department Order productivity matrices.
* **Measurable Target**: Zero missing cost components ($₱0.00$) in generated BOQ checklist rows.

#### **Objective 3: Native Blueprint Vector Heatmap & Visual Comparison Layer**
* **Goal Criteria**: Render original PDF/DXF vector paths directly as the base layer (`pdf.js`/Canvas) overlaid with color-coded translucent heatmaps (🟦 Blue for Concrete, 🟧 Orange for Beams/Slabs, 🟩 Green for Masonry).
* **Measurable Target (Visual Comparison Protocol)**: Ingest a vector PDF blueprint, extract geometries, generate an exported vector PDF/SVG overlay file, and display a side-by-side visual diff comparison against the original drawing sheet to verify alignment accuracy ($< 1\text{mm}$ spatial variance).

#### **Objective 4: CSI MasterFormat / DPWH Trade Accordion UX**
* **Goal Criteria**: Group checklist items into collapsible accordions by the 13 trade divisions with live subtotal banners, variance indicators, and inline unit price editing.
* **Measurable Target**: Interactive accordion UI updating total project costs dynamically within $< 50\text{ms}$ of rate edits.

#### **Objective 5: 1D Commercial Rebar Stock Optimization (Bin Packing)**
* **Goal Criteria**: Implement First Fit Decreasing (FFD) 1D Bin Packing mapping cut demands against commercial bar lengths (**6m, 9m, 12m**).
* **Measurable Target**: Achieve total cutting scrap loss **< 3.0%** across all rebar diameters.

#### **Objective 6: Zero-Touch Autonomous Agent Relay Protocol (Claude Web Coordination)**
* **Goal Criteria**: Expose public manifest endpoint `GET /api/v1/manifest` and webhook sync endpoint `POST /api/v1/agent-sync` specifically designed for seamless coordination with external AI agents (e.g. Claude Web).
* **Measurable Target**: External agents can auto-index project state and push code updates without manual human copy-pasting.

#### **Objective 7: Multimodal AI Vision OCR for Schedule Tables**
* **Goal Criteria**: Crop margin schedules (`TKTHEP`, Beam/Column/Footing schedules) and convert scanned image regions into structured tabular JSON data using vision AI models.
* **Measurable Target**: $> 95\%$ accuracy on schedule table cell parsing.

#### **Objective 8: Offline-First Desktop Executable**
* **Goal Criteria**: Package engine and React UI into an offline desktop executable (`PyWebView` / `Tauri`).
* **Measurable Target**: 100% functionality on remote job sites without internet connection.

---

## 2. Comprehensive 13-Trade Takeoff & Direct Costing Specifications

The V2 Takeoff Engine structures calculations into the **13 Trade Sections** matching `UY_Louis.xlsx`:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        13 Trade Divisions (UY_Louis.xlsx Basis)                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Section I:   General Requirements & Site Prep │ Section VIII: Tile & Flooring Works    │
│ Section II:  Earthworks                       │ Section IX:   Painting Works           │
│ Section III: Concrete Works & Formworks       │ Section X:    Plumbing Works           │
│ Section IV:  Masonry Works                    │ Section XI:   Electrical Works         │
│ Section V:   Metals & Steel Reinforcement     │ Section XII:  Sanitary / Mechanical    │
│ Section VI:  Roofing & Ceiling Works          │ Section XIII: Special Works            │
│ Section VII: Doors & Windows                  │                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.1 Deep Fajardo Methodological Foundation & Solved Case Book Knowledge

All calculations reference standard formulas and solved problems from Max Fajardo's *Simplified Construction Estimate*.

#### 2.1.1 Concrete Mix Designs (Fajardo Chapter 1: Concrete)
Per $1.0\text{ m}^3$ of solid concrete volume using standard $40\text{ kg}$ Portland Cement bags:

* **Class AA (1:1.5:3)**: Cement = $12.00\text{ bags}$, Sand = $0.50\text{ m}^3$, Gravel = $1.00\text{ m}^3$ *(For underwater/pre-stressed concrete)*
* **Class A (1:2:4)**: Cement = $9.00\text{ bags}$, Sand = $0.50\text{ m}^3$, Gravel = $1.00\text{ m}^3$ *(For Footings, Columns, Beams, Slabs)*
* **Class B (1:2.5:5)**: Cement = $7.50\text{ bags}$, Sand = $0.50\text{ m}^3$, Gravel = $1.00\text{ m}^3$ *(For Pathways, Slab on Grade)*
* **Class C (1:3:6)**: Cement = $6.00\text{ bags}$, Sand = $0.50\text{ m}^3$, Gravel = $1.00\text{ m}^3$ *(For Plant boxes, Non-structural mass concrete)*

##### Solved Problem Methodology (Fajardo Solved Example — Footing & Column Volume):
1. **Isolated Footing ($F-1$)**: $V_F = L \times W \times H \times N$.
2. **Column Net Clear Height ($C-1$)**: $H_{\text{clear}} = H_{\text{total}} - T_{\text{footing}} - T_{\text{slab}}$.
3. **Beam Net Clear Span ($2B-1$)**: $L_{\text{clear}} = L_{\text{grid}} - \frac{W_{C1}}{2} - \frac{W_{C2}}{2}$.
4. **Concrete Wastage Factor**: Add $5\%$ for site-mixed concrete, $3\%$ for ready-mix.

---

#### 2.1.2 Steel Reinforcement & Rebar Cut Lengths (Fajardo Chapter 2: Reinforcing Steel)
PNS 49 Theoretical Unit Weight Formula: $W_{\text{kg/m}} = \frac{d^2}{162.2}$

##### Rebar Cut Length Derivations:
* **Footing Mat Rebars**: $L_{\text{cut}} = L_{\text{footing}} - 2 \cdot C_{\text{cover}} + 2 \cdot H_{\text{hook}}$ ($C_{\text{cover}} = 75\text{mm}$, $H_{\text{hook}} = 12 \cdot d_b$).
* **Column Main Longitudinal Bars**: $L_{\text{cut}} = H_{\text{story}} + L_{\text{splice}} + L_{\text{dowel}}$ ($L_{\text{splice}} = 40 \cdot d_b$).
* **Beam Stirrups (135° Seismic Hooks)**: 
  $$L_{\text{stirrup}} = 2 \cdot (W_{\text{beam}} - 2 C_{\text{cover}}) + 2 \cdot (D_{\text{beam}} - 2 C_{\text{cover}}) + 2 \cdot (10 \cdot d_b) - \text{Bend Deductions}$$
* **Tie Wire Factor**: $\#16$ G.I. Tie Wire = $0.015\text{ kg}$ per $\text{kg}$ of rebar ($15\text{ kg/metric ton}$).

---

#### 2.1.3 Masonry Works (Fajardo Chapter 3: Masonry & Plastering)
Per $1.0\text{ m}^2$ of net wall surface area:
* **CHB Unit Count**: Constant $12.5\text{ pcs/m}^2$ (for both $100\text{mm}$ and $150\text{mm}$ CHB).
* **Mortar Laying & Cell Fill (Class B Mortar 1:3)**:
  - $100\text{mm } (4")$ CHB Wall: Cement = $0.522\text{ bags/m}^2$, Sand = $0.0435\text{ m}^3/\text{m}^2$.
  - $150\text{mm } (6")$ CHB Wall: Cement = $1.010\text{ bags/m}^2$, Sand = $0.0840\text{ m}^3/\text{m}^2$.
* **Plastering ($16\text{mm}$ Thickness Class B Mortar per face)**:
  - Cement = $0.192\text{ bags/m}^2/\text{face}$, Sand = $0.016\text{ m}^3/\text{m}^2/\text{face}$.
* **Opening Deductions**: Net Area $A_{\text{net}} = (L_{\text{wall}} \times H_{\text{wall}}) - \sum (W_{\text{door/window}} \times H_{\text{door/window}})$.

---

#### 2.1.4 Formwork & Falsework (Fajardo Chapter 4: Formworks)
Contact area calculation per structural element:
* **Footing Forms**: Surface area of perimeter faces = $2 \cdot (L + W) \times H \times N$.
* **Column Forms**: Contact perimeter = $2 \cdot (W + D) \times H_{\text{clear}} \times N$.
* **Beam Forms (Bottom & 2 Sides)**: Area = $(W + 2 D) \times L_{\text{clear}} \times N$.
* **Material Ratios**: Marine Plywood $1/2" = 0.28\text{ sheets/m}^2$, Form Lumber $2\times2 / 2\times3 = 7.0\text{ bdft/m}^2$.

---

### 2.2 Detailed 13-Trade Breakdown & Itemization

```
Section I: General Requirements
├── 1.1 Mobilization / Demobilization (lot)
├── 1.2 Permits, Licenses & Clearances (lot)
├── 1.3 Temporary Facilities & Enclosure (lot)
└── 1.4 Safety & Health Officer / PPE (lot)

Section II: Earthworks
├── 2.1 Structural Excavation (cu.m.)
├── 2.2 Structure Backfill & Compaction (cu.m.)
├── 2.3 Gravel Bedding 50mm/100mm (cu.m.)
└── 2.4 Soil Poisoning & Termite Control (sq.m.)

Section III: Concrete Works & Formworks
├── 3.1 Concrete Works — Footings Class A (cu.m.)
├── 3.2 Concrete Works — Columns Class A (cu.m.)
├── 3.3 Concrete Works — Beams Class A (cu.m.)
├── 3.4 Concrete Works — Slabs Class A (cu.m.)
├── 3.5 Slab-on-Grade Class B (cu.m.)
├── 3.6 Formwork — Plywood 1/2" Marine (sheet)
└── 3.7 Formwork — Frame Lumber (bdft)

Section IV: Masonry Works
├── 4.1 150mm (6") CHB Exterior Walls (sq.m. / pc)
├── 4.2 100mm (4") CHB Interior Partition Walls (sq.m. / pc)
├── 4.3 Laying Mortar Cement & Sand (bags / cu.m.)
└── 4.4 Plastering 16mm Class B Both Faces (sq.m.)

Section V: Metals & Steel Reinforcement
├── 5.1 Deformed Rebar 10mm / 12mm / 16mm / 20mm / 25mm Grade 40 (kg)
├── 5.2 #16 G.I. Tie Wire (kg)
├── 5.3 Structural Steel Shapes & Canopy Frames (kg / lot)
└── 5.4 Stainless Steel Handrails & Railings (lin.m.)

Section VI: Roofing & Ceiling Works
├── 6.1 C-Purlins & Roof Trusses (kg / lin.m.)
├── 6.2 Pre-painted Long-span Roofing Sheets (sq.m.)
├── 6.3 Thermal Roof Insulation Double Sided (sq.m.)
└── 6.4 1/2" Hardiflex Board Ceiling on Metal Furring (sq.m.)

Section VII: Doors & Windows
├── 7.1 Analok Aluminum / Glass Windows (sq.m. / set)
├── 7.2 Tempered Glass Doors (set)
├── 7.3 Solid Wooden Panel Doors (set)
└── 7.4 Flush Hollow Core Doors (set)

Section VIII: Tile & Flooring Works
├── 8.1 600x600mm Ceramic Floor Tiles (sq.m.)
├── 8.2 300x300mm Rustic Walkway / Toilet Tiles (sq.m.)
├── 8.3 300x600mm Toilet Wall Tiles (sq.m.)
└── 8.4 Plain Cement Floor Finish (sq.m.)

Section IX: Painting Works
├── 9.1 Masonry Wall Paint — Concrete Neutralizer, Primer, Semi-gloss Latex (sq.m.)
├── 9.2 Ceiling Paint — Primer & Flat Latex (sq.m.)
└── 9.3 Metal Paint — Red Oxide Primer & Quick Drying Enamel (sq.m.)

Section X: Plumbing Works
├── 10.1 UPVC Sewer Main & Sanitary Pipes 4" / 2" (pc)
├── 10.2 PPR Cold Water Distribution Pipes 3/4" / 1/2" (pc)
├── 10.3 Plumbing Fixtures — Water Closets, Lavatories, Sinks (set)
└── 10.4 Septic Vault & Catch Basins (lot)

Section XI: Electrical Works
├── 11.1 Lighting Fixtures & LED Panel Lights (pc)
├── 11.2 Convenience Outlets & Switches (pc)
├── 11.3 Panelboard & Main Circuit Breakers (set)
└── 11.4 THHN/THW Copper Wires 3.5mm² / 5.5mm² / 8.0mm² (m)

Section XII: Sanitary / Mechanical Works
├── 12.1 Split-type Inverter Air Conditioning Units (unit)
├── 12.2 Refrigerant Copper Piping & Insulation (lot)
└── 12.3 Testing & Commissioning (lot)

Section XIII: Special Works
├── 13.1 Stair Handrails & Balustrades (lin.m.)
├── 13.2 ACP Canopy Cladding (sq.m.)
└── 13.3 Elastomeric Waterproofing (sq.m.)
```

---

### 2.3 DPWH CMPD Master Direct Cost Matrix

| Code | Item Description | Unit | Material Rate (₱) | Labor Rate (₱) | Equipment Rate (₱) | Total Direct Unit Rate (₱) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **MAT-1** | Portland Cement (40kg bag) | bag | 205.36 | — | — | 205.36 |
| **MAT-2** | Fine Aggregate (Sand) | cu.m. | 1,473.21 | — | — | 1,473.21 |
| **MAT-3** | Coarse Aggregate (Gravel 3/4") | cu.m. | 1,517.86 | — | — | 1,517.86 |
| **MAT-4** | Deformed Rebar Grade 40 | kg | 42.68 | 12.00 | 2.50 | 57.18 |
| **MAT-5** | #16 G.I. Tie Wire | kg | 62.50 | 12.00 | — | 74.50 |
| **MAT-6** | 100mm (4") Ordinary CHB | pc | 15.18 | 19.20 | 1.20 | 35.58 |
| **MAT-7** | 150mm (6") Ordinary CHB | pc | 22.32 | 19.20 | 1.20 | 42.72 |
| **EXC-2.1**| Structural Excavation | cu.m. | 0.00 | 350.00 | 0.00 | 350.00 |
| **CON-3.1**| Class A Concrete (Footings/Cols/Beams) | cu.m. | 4,098.81 | 850.00 | 250.00 | 5,198.81 |
| **FRM-3.6**| Marine Plywood 1/2" Formwork | sheet | 750.00 | 210.00 | — | 960.00 |
| **PNT-9.1**| Masonry 3-Coat Paint System | sq.m. | 95.00 | 85.00 | — | 180.00 |
| **PLM-10.1**| 4" Ø UPVC Sanitary Pipe | pc | 420.00 | 150.00 | — | 570.00 |
| **ELC-11.4**| 3.5mm² THHN Wire | m | 32.00 | 18.00 | — | 50.00 |

---

### 2.4 Zero-Touch Agent Relay & Manifest Protocol (Claude Web Coordination)

In coordination with Claude Web, the relay protocol exposes public auto-indexing endpoints:

#### `GET /api/v1/manifest`
Exposes workspace manifest for multi-agent auto-indexing:
```json
{
  "project_name": "Plan2Takeoff V2",
  "version": "2.0.0",
  "timestamp_utc": "2026-07-22 09:22:00",
  "storage_base_url": "https://ickbqcdbyheyqyqfjpzv.supabase.co/storage/v1/object/public/project-files/",
  "v1_isolation_status": "ISOLATED (No write access to V1 tables/buckets)",
  "manifest_files": [
    { "filename": "tech_spec_v2.md", "exists_locally": true, "public_url": "..." },
    { "filename": "log.md", "exists_locally": true, "public_url": "..." }
  ]
}
```

#### `POST /api/v1/agent-sync`
Webhook sync route allowing external AI agents to push code edits and trigger Git/cloud updates automatically:
* Header: `X-Agent-Sync-Token: p2t_v2_agent_relay_token_9981`
* Payload: `{ "action": "update_file", "target_file": "...", "content": "..." }`

---

### 2.5 Offline-First Desktop Execution Specification
* **Launcher**: `desktop_launcher.py` built on `PyWebView`.
* **Execution**: Launches background Flask HTTP server on `http://127.0.0.1:5001` and opens an offline desktop window.
* **Job Site Support**: 100% operational on remote construction sites without internet connectivity.

---

*Plan2Takeoff V2 Technical Specification Baseline Document v2.0 — Approved for Master Implementation.*
