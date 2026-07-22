# Plan2Takeoff V2 — Technical Specification & Architecture Roadmap Baseline

> **Version**: 2.0.0 (Master Production Specification)  
> **Author**: Plan2Takeoff Engineering Team & Antigravity AI Project Manager  
> **Status**: Approved & Active  
> **Target Trade Scope**: 13 Divisions matching [`UY_Louis.xlsx`](file:///E:/Users/Louis/Documents/3rd%20Yr%20college%202025-26/2nd%20sem/QTYSUR/qty%20lab/QtySur%20Estimate/UY_Louis.xlsx)  
> **Fajardo Knowledge Base**: 100% Complete ([`formula_exhaustive_handbook.md`](file:///e:/Users/Louis/Documents/boq_system_v2/formula_exhaustive_handbook.md), Appendices A, B, C)  
> **Vector Alignment Tolerance**: $< 1.0\text{ mm}$ spatial variance (Verified: $0.0509\text{ mm}$ passed in [`test_vector_diff.py`](file:///e:/Users/Louis/Documents/boq_system_v2/backend/engine/test_vector_diff.py))  
> **V1 Isolation Status**: 100% Isolated (Zero write access to V1 Supabase tables or `project-files` bucket)

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
