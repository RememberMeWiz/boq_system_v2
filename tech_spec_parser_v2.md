# 🏗️ AI Blueprint & CAD Parser Pipeline — Technical Specification v2.0

> **Framework**: Following **The Builder's Toolkit** (Stage 3: Architecture — AI Ramps Up).  
> **Goal**: Define the exact Tech Stack, System Boundaries & APIs, Data Models & Payloads, Beam-to-Grid Linkages, and Programmatic Verification Gate for the Parser Engine.

---

![The Builder's Toolkit Methodology](C:/Users/louis/.gemini/antigravity/brain/fec2906c-fb81-47b4-a08e-b1ad1a62f2c5/builders_toolkit.jpg)

---

## 1. Tech Stack Selection

| Layer | Technology | Version / Tool | Purpose & Architectural Rationale |
| :--- | :--- | :--- | :--- |
| **PDF Page Raster & Vector Geometry** | `PyMuPDF (fitz)` | `>=1.20.0` | High-DPI page rendering (150–200 DPI PNGs), text node bounding box coordinates ($X_1, Y_1, X_2, Y_2$). |
| **CAD Drawing Extraction** | `ezdxf` | `>=1.0.0` | Layer filtering (`S-FOOTING`, `S-COLUMN`, `S-BEAM`), polylines, block references, text insertion points. |
| **PDF Table Schedule Parsing** | `pdfplumber` + `pandas` | `>=0.7.0` | High-precision table cell border detection & structured text grid extraction for PDF schedules. |
| **Multimodal Vision Intelligence** | `google-genai` SDK | Latest Gemini Vision API | Sheet type classification, schedule table cropping, and missing sheet detection. *(Dynamic SDK model string determined at runtime).* |
| **Visual Reconstruction Engine** | `svgwrite` + `Pillow (PIL)` | `>=1.4.0` | Re-rendering CAD/SVG diagrams, side-by-side comparison panels, and direct overlay images on PDF sheets. |
| **Backend REST Services** | Python `Flask` | `>=2.2.0` | Microservice endpoints for file upload, extraction, visual reconstruction, action log streaming, and verification gate checks. |
| **Frontend Verification UI** | React 18 + HTML5 Canvas | `Vite 6` | Dual-mode viewer (Side-by-Side vs Direct Overlay), collapsible real-time debug action log sidebar, Verification Gate Signoff modal. |

---

## 2. System Boundaries & Service Interaction Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ FRONTEND REACT APP (App.jsx & BlueprintViewer.jsx)                          │
│ - Dual Viewer Modes: (1) Side-by-Side Comparison, (2) Direct Overlay        │
│ - Collapsible Parser Action Console Log Sidebar (Debug)                     │
│ - Verification Gate Modal: Resolves BLOCKING issues & Signoff Audit Log     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                        HTTP REST API (JSON + Multipart)
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ BACKEND FLASK PARSER SERVICES (backend/app.py)                              │
│                                                                             │
│ 1. POST /api/v1/parser/ingest                                             │
│    - Accepts PDF / DWG / DXF file upload                                    │
│    - Triggers Stage 1 Sheet Classification & Schedule Extraction            │
│    - Computes verification_gate status (BLOCKED vs READY)                   │
│    - Returns raw payload + provenance badges + verification_gate            │
│                                                                             │
│ 2. POST /api/v1/parser/reconstruct                                         │
│    - Accepts structural payload JSON                                        │
│    - Generates SVG vector string & side-by-side / direct overlay PNGs       │
│    - ZERO math calculations                                                 │
│                                                                             │
│ 3. POST /api/v1/parser/signoff                                           │
│    - Accepts an ARRAY of itemized issue resolutions (see 3.2 below)         │
│    - Marks resolved:true + signed_off_by/at/note on EACH target issue_id    │
│    - Recomputes verification_gate.status (READY only when all resolved)     │
│                                                                             │
│ 4. GET /api/v1/parser/action-logs                                          │
│    - Streams real-time parser execution events to frontend sidebar console │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                        HTTP REST API (JSON) — frontend-initiated
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ FAJARDO SOLVER COST ENGINE (backend/engine/fajardo.py)                      │
│                                                                             │
│ 5. POST /api/v1/solver/process                                            │
│    - Explicit REST endpoint, called by frontend on "Calculate Civil        │
│      Takeoff" click (NOT auto-invoked by /signoff)                          │
│    - Hard guardrail: rejects HTTP 409 Conflict if                           │
│      verification_gate.status != "READY", returning unresolved issues       │
│    - On success: uses static PNS 49 rebar unit weights (d²/162.2) and       │
│      Fajardo formulas; executes all 13-trade civil engineering              │
│      mathematics & DPWH DUPA costs                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.1 Standardized API Namespace

| Method | Endpoint | Service Boundary | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/parser/ingest` | Parser | Upload & Extract raw structural payload |
| `POST` | `/api/v1/parser/reconstruct` | Parser | Generate SVG/PNG visual canvas (zero math) |
| `POST` | `/api/v1/parser/signoff` | Parser | Itemized issue override & audit log (see 3.2) |
| `GET` | `/api/v1/parser/action-logs` | Parser | Real-time debug event stream |
| `POST` | `/api/v1/solver/process` | Solver | Execute Fajardo cost engine — **hard-rejects `HTTP 409 Conflict`** if `verification_gate.status != "READY"` |

`parser/*` and `solver/*` are deliberately separate namespaces reflecting the two-service boundary: the parser never performs math, and the solver never runs without an explicit frontend call gated by `verification_gate.status`. The solver is **not** auto-invoked by `/signoff` — a successful signoff only promotes gate status; the estimator still explicitly triggers the takeoff calculation.

---

## 3. Data Models & Data Payload Schemas

### 3.1 Structural Payload Schema with Beam-to-Grid Linkage & Audit Block

```json
{
  "project_meta": {
    "filename": "<string: filename>",
    "detected_variant": "<string: detected building variant>",
    "grid_scope": { "bays": "<int: total_bays>", "total_length_mm": "<float: total_length>" },
    "toc_missing_sheets": ["S-6", "S-7", "S-8", "S-11"]
  },
  "grid_nodes": [
    {
      "grid_id": "1-A",
      "footing_mark": "F-1",
      "column_mark": "C-1",
      "x": 120.5,
      "y": 450.0
    }
  ],
  "schedules": {
    "footings": [
      {
        "mark": "F-1",
        "length_m": 1.40,
        "width_m": 1.40,
        "thickness_m": 1.50,
        "rebar": { "size_mm": 20, "count": 7, "type": "grid_mat" },
        "provenance": "parsed"
      }
    ],
    "columns": [
      {
        "mark": "C-1",
        "story_level": "Foundation Level to 2nd Floor Level",
        "width_m": 0.40,
        "depth_m": 0.40,
        "clear_height_m": 3.30,
        "main_bars": { "size_mm": 25, "count": 12 },
        "ties": { "size_mm": 10, "spacing_mm": "1@50, 4@100, rest@150" },
        "provenance": "parsed"
      }
    ],
    "beams": [
      {
        "mark": "2B-1",
        "location": {
          "grid_line": "A",
          "grid_start": "1",
          "grid_end": "2",
          "level": "2nd Floor"
        },
        "clear_span_m": 4.10,
        "span_source": {
          "type": "dimension_chain",
          "sheet": "S-3",
          "raw_dim_mm": 4500,
          "centerline_or_clear": "centerline",
          "deduction_applied_mm": 400,
          "deduction_source": "column_schedule.C-1.width_m"
        },
        "width_m": 0.25,
        "depth_m": 0.40,
        "top_bars": { "size_mm": 20, "count": 4 },
        "bottom_bars": { "size_mm": 20, "count": 3 },
        "stirrups": { "size_mm": 10, "spacing_mm": "1@50, 4@100, rest@150" },
        "provenance": "parsed"
      }
    ],
    "slabs": [
      {
        "mark": "S-1",
        "location": {
          "grid_bay": { "x_start": "1", "x_end": "2", "y_start": "A", "y_end": "B" }
        },
        "area_m2": 31.5,
        "area_source": {
          "type": "derived_from_bay",
          "computed_m2": 31.5,
          "matches_stated": true
        },
        "thickness_m": 0.10,
        "provenance": "parsed"
      }
    ],
    "walls": [
      {
        "mark": "W-1",
        "location": { "grid_line": "A", "grid_start": "1", "grid_end": "8" },
        "length_m": 32.0,
        "height_m": 3.30,
        "thickness_mm": 150,
        "provenance": "parsed"
      }
    ]
  },
  "structural_notes": {
    "concrete_cover_earth_mm": 75,
    "concrete_cover_col_beam_mm": 40,
    "lap_splice_multiplier": 40,
    "seismic_hook_deg": 135
  },
  "verification_gate": {
    "status": "BLOCKED",
    "computed_at": "2026-07-23T10:00:00Z",
    "blocking_issues": [
      {
        "id": "sug_1",
        "severity": "BLOCKING",
        "category": "missing_schedule_sheet",
        "message": "Beam Schedule S-6 referenced in TOC but missing from uploaded file",
        "affected_elements": ["2B-1", "2B-2", "2B-3"],
        "resolution_required": ["upload_sheet", "manual_override_with_signoff"],
        "resolved": false
      },
      {
        "id": "sug_2",
        "severity": "BLOCKING",
        "category": "load_bearing_default_used",
        "message": "Truss member schedule S-8 missing — roof truss steel weight cannot be computed without member list",
        "affected_elements": ["T-1"],
        "resolution_required": ["upload_sheet", "manual_override_with_signoff"],
        "resolved": false
      },
      {
        "id": "sug_4",
        "severity": "BLOCKING",
        "category": "missing_connection_details",
        "message": "Truss connection/weld detail sheet S-7 missing — gusset plates, base plate anchors, and weld lengths cannot be quantified for Structural Steel Works",
        "affected_elements": ["T-1"],
        "resolution_required": ["upload_sheet", "manual_override_with_signoff"],
        "resolved": false
      }
    ],
    "warning_issues": [
      {
        "id": "sug_3",
        "severity": "WARNING",
        "category": "low_confidence_ocr",
        "message": "Footing schedule table F-2 row had low OCR confidence (72%) on reinforcement count",
        "affected_elements": ["F-2"],
        "resolution_required": ["manual_confirm"],
        "resolved": false
      }
    ],
    "resolution_log": [
      {
        "issue_id": "sug_1",
        "action": "manual_override_with_signoff",
        "note": "Beam schedule S-6 missing; applied DPWH standard 400x250mm beam depth with 4-20mm bars.",
        "signed_off_by": "Engr. Louis (Lead Estimator)",
        "signed_off_at": "2026-07-23T11:20:00Z",
        "resolved": true
      }
    ]
  }
}
```

> **Note:** `verification_gate.signoff` (single global object) from v2.0-draft is replaced by `verification_gate.resolution_log` (array). Each `blocking_issues[]` / `warning_issues[]` entry's own `resolved` flag is the source of truth for gate status; `resolution_log` is the append-only audit trail explaining *why* each specific `issue_id` was resolved. This is a **breaking schema change** from the previous draft — flagging explicitly for Stage 4 implementers.

### 3.2 `POST /api/v1/parser/signoff` — Request & Response Schema

**Request** — accepts an array of itemized resolutions, one per targeted `issue_id`. A single call may resolve multiple issues, but each requires its own note and signer:

```json
{
  "resolutions": [
    {
      "issue_id": "sug_1",
      "action": "manual_override_with_signoff",
      "note": "Beam schedule S-6 missing; applied DPWH standard 400x250mm beam depth with 4-20mm bars.",
      "signed_off_by": "Engr. Louis (Lead Estimator)"
    },
    {
      "issue_id": "sug_4",
      "action": "manual_override_with_signoff",
      "note": "Truss connection detail S-7 missing; applied DPWH standard 10% connection hardware allowance on truss steel weight.",
      "signed_off_by": "Engr. Louis (Lead Estimator)"
    },
    {
      "issue_id": "sug_3",
      "action": "manual_confirm",
      "note": "Reviewed footing F-2 reinforcement count against original PDF raster; OCR value confirmed correct.",
      "signed_off_by": "Engr. Louis (Lead Estimator)"
    }
  ]
}
```

**Behavior**:
- Each `issue_id` must exist in either `blocking_issues[]` or `warning_issues[]`, and its `action` must be a member of that issue's own `resolution_required[]` list — the backend rejects (`HTTP 400`) any resolution attempting an action not permitted for that issue (e.g. calling `manual_confirm` on an issue that only allows `upload_sheet` / `manual_override_with_signoff`).
- On success, the backend sets `resolved: true` on each targeted issue, appends a matching entry to `resolution_log[]`, and **recomputes** `verification_gate.status` per the rules in Section 4.3 — it does not simply flip status to `READY`.
- `warning_issues[]` require at minimum a `manual_confirm` action with note + signer before `status` can reach `READY` (see Section 4.5 — no silent auto-promotion).

**Response**: returns the full, updated `verification_gate` object so the frontend can re-render gate state without a second round-trip.

---

## 4. Verification Gate Logic Rules & Audit Requirements

1. **Strict Severity Classification**:
   - `BLOCKING` = Any missing load-path schedule sheet ($S-6$ beams, $S-7$ truss connections/welds, $S-8$ truss members), unparsed column story level, or unconfirmed load-bearing dimension.
   - `WARNING` = Cosmetic text mismatch, low-confidence OCR on non-critical metadata, area delta warnings (`matches_stated: false`).
   - **S-7 classification note**: $S-7$ (Truss Connection Details, Gusset Plates, Base Plate Anchors, Weld Lengths) is `BLOCKING`, not `WARNING`, because its absence prevents quantifying Structural Steel Works (Section VI: truss hardware, gusset plates, weld lengths) — a cost-bearing line item, not cosmetic metadata. Missing $S-7$ generates category `missing_connection_details`, resolvable via `upload_sheet` or `manual_override_with_signoff` (e.g., applying the DPWH standard 10% connection hardware allowance on truss steel weight).

2. **Itemized Resolution, Not Blanket Override**:
   - `POST /api/v1/parser/signoff` (see Section 3.2) accepts an **array** of per-`issue_id` resolutions. Each resolution independently sets `resolved: true` on its target issue and appends a dated, signed entry to `verification_gate.resolution_log[]`.
   - A single global signoff note/signer is **not permitted** — every `manual_override_with_signoff` must document, per issue, what was assumed and who approved it, so the audit trail shows which specific assumption applied to which specific structural element.

3. **Derived Gate Status (`BLOCKED` vs `READY`)**:
   - The field `verification_gate.status` is **dynamically computed**, never user-set directly.
   - If `blocking_issues` contains any `resolved: false` entry $\rightarrow$ `status = "BLOCKED"`.
   - If all `blocking_issues` are resolved AND all `warning_issues` have a logged positive review confirmation $\rightarrow$ `status = "READY"`.
   - Status is recomputed on every `/signoff` call — the endpoint never sets `status` directly, it only resolves individual issues and lets the derivation rule apply.

4. **Solver Handoff Hard Guardrail**:
   - The Fajardo Solver endpoint is **`POST /api/v1/solver/process`** (standardized namespace — see Section 2.1), called explicitly by the frontend on user action, not auto-triggered by `/signoff`.
   - It independently verifies `verification_gate.status == "READY"` before executing any calculation.
   - If `status == "BLOCKED"`, the backend returns **`HTTP 409 Conflict`** with the array of unresolved blocking issues — the frontend should route the user back to the Verification Gate Modal rather than retry.

5. **Product Decision on `WARNING`-Only Payloads**:
   - **No Auto-Promotion**: Even payloads with zero `BLOCKING` issues and only `WARNING` cards require a lightweight **"Reviewed & Verified"** 1-click confirmation per warning, submitted through the same itemized `/signoff` array (`action: "manual_confirm"`).
   - This records `signed_off_by`, timestamp, and note per issue into `verification_gate.resolution_log[]`, creating an unbroken, auditable trail for every estimate — never a single unattributed "approved" flag.

---

## 5. Summary & Handoff to Implementation

With this updated architecture:
- Beam-to-grid linkage join keys (`grid_start`, `grid_end`) defined ✅
- Span centerline-to-clear deduction audit block (`span_source`) defined ✅
- Area consistency checker (`area_source.matches_stated`) defined ✅
- Programmatic Verification Gate with itemized, per-issue Audit Signoff Trail (`resolution_log[]`) defined ✅
- Standardized `parser/*` vs `solver/*` API namespace, with `POST /api/v1/solver/process` as the explicit, frontend-triggered, 409-guarded entry point to Fajardo ✅
- Sheet `S-7` (truss connection/weld details) classified `BLOCKING` alongside `S-6`/`S-8` for Structural Steel Works quantification ✅

**Breaking change flagged for Stage 4 implementers**: `verification_gate.signoff` (single global object, v2.0-draft) is replaced by `verification_gate.resolution_log[]` (append-only array, one entry per resolved `issue_id`). Any Stage 4 code or mockups already scaffolded against the old single-object shape need updating before implementation begins.

We are ready for Stage 4 Implementation when approved!
