# INSTRUCTIONS FOR WEB AIs (Claude Web, ChatGPT Web, Gemini Web) — READ THIS FIRST

You are an external Web AI collaborating on **Plan2Takeoff Version 2** (`boq_system_v2`).
Follow this zero-touch protocol exactly to read workspace state and commit updates without requiring the user to copy-paste or upload manually.

---

## 👔 Section 0 — Orchestrator & Project Manager (PM) Governance Framework

The primary AI agent operating inside the user's IDE terminal is **Antigravity AI (Gemini Orchestrator)**, serving strictly as the **Project Manager / Orchestrator**.

### PM Roles, Directives & Rules:
1. **Executive Oversight & Roadmap Management**: Antigravity AI manages task creation, roadmap tracking, technical specifications, progress reports, and overall system architecture.
2. **Task Specification & Delegation**: When the user requests a task to be delegated, Antigravity AI formulates a comprehensive task description mapped to the 13 trade divisions (`UY_Louis.xlsx`).
3. **Public HTTPS Link Rule**: Every task description created by the PM includes **live public HTTPS tunneled URLs** (e.g. `https://plan2takeoff-v2.loca.lt/tech_spec_v2.md`) so that Web AIs (Claude Web) can directly fetch, inspect, and index all workspace files over the internet.
4. **No Hands-on Subagent Handoff without User Approval**: The PM **never** hands off tasks to subagents automatically without explicit user permission.
17. **Web AI Collaboration & Code Delivery Protocol**: External Web AIs (such as Claude Web) receive the PM's task specification, fetch specs over the public HTTPS tunnel, write the complete code module directly in their response text as downloadable code blocks, and the Antigravity Orchestrator (PM) ingests, tests, and commits the code locally.

---

## 📌 CRITICAL RULE 0 — V1 Isolation Policy
⚠️ **DO NOT TOUCH V1 DATABASE OR CLOUD STORAGE**:
- V2 reuses algorithms from V1 (`boq_system`), but is strictly isolated.
- **NEVER** write to V1 Supabase tables or V1 storage buckets (`project-files`).
- All V2 work must use V2 endpoints, V2 local schema (`boq_v2_schema.sql`), and V2 storage locations.

---

## 🌐 Public HTTPS Tunnel Link Accessibility Rule
All file references and task deliverables provided by the Project Manager include **live public HTTPS tunneled URLs** (e.g. `https://plan2takeoff-v2.loca.lt/tech_spec_v2.md` or `https://plan2takeoff-v2.loca.lt/formula_exhaustive_handbook.md`).
You can fetch and read any of these file URLs directly using your web browsing tool!

Before starting any task, fetch the project manifest endpoint to auto-index the entire active workspace:

- **Live Public Manifest Endpoint**: `https://plan2takeoff-v2.loca.lt/api/v1/manifest`
- **Local Manifest Endpoint**: `http://localhost:5001/api/v1/manifest`

The manifest returns a JSON payload listing all active file URLs, sizes, hashes, and project metadata:
```json
{
  "project_name": "Plan2Takeoff V2",
  "version": "2.0.0",
  "v1_isolation_status": "ISOLATED (No write access to V1 tables/buckets)",
  "manifest_files": [
    { "filename": "tech_spec_v2.md", "public_url": "https://plan2takeoff-v2.loca.lt/tech_spec_v2.md" },
    { "filename": "log.md", "public_url": "https://plan2takeoff-v2.loca.lt/log.md" },
    { "filename": "00_INSTRUCTIONS_FOR_WEB_AI.md", "public_url": "https://plan2takeoff-v2.loca.lt/00_INSTRUCTIONS_FOR_WEB_AI.md" }
  ]
}
```

Fetch `tech_spec_v2.md` and `log.md` first to understand current requirements and roadmap status.

---

## 🔄 Step 2 — Code Delivery Protocol

External Web AIs (Claude Web) deliver complete code modules and updates directly as downloadable code blocks in chat responses. The Antigravity PM ingests the code file directly into the local workspace, runs automated tests, and updates project logs.

- **Sync Endpoint**: `https://plan2takeoff-v2.loca.lt/api/v1/agent-sync`
- **Headers**: 
  - `Content-Type: application/json`
  - `X-Agent-Sync-Token: p2t_v2_agent_relay_token_9981`

- **Payload Format**:
```json
{
  "action": "update_file",
  "target_file": "backend/engine/fajardo.py",
  "content": "<FULL_FILE_CONTENT>",
  "commit_message": "Claude Web: Added Division 06 Roofing & Ceiling calculation module"
}
```

The server automatically writes the file locally, commits to Git, and syncs to V2 storage.

---

## 📝 Step 3 — Log Protocol (`log.md`)

Whenever you start or complete a task, update `log.md` via `POST /api/v1/agent-sync`.
* **Reverse Chronological Order**: Prepend new entries at the very top of `log.md`.
* **Model Name Requirement**: Always include your model name in the heading (e.g., `Model: Claude 3.5 Sonnet (Web)`).

### STARTED Entry:
```markdown
## [YYYY-MM-DD HH:MM UTC] STATUS: STARTED (Model: Claude 3.5 Sonnet (Web))
Task: <clear description of task>
Notes: <relevant context>
---
```

### COMPLETED Entry:
```markdown
## [YYYY-MM-DD HH:MM UTC] STATUS: COMPLETED (Model: Claude 3.5 Sonnet (Web))
Task: <same description as STARTED>
Notes: <summary of changes, file locations, test results>
---
```

---

## 🏗️ Step 4 — Trade Scope & Technical Specifications
- **13 Construction Trades Basis**: All takeoff and costing logic must follow the 13 trade divisions defined in [`UY_Louis.xlsx`](file:///E:/Users/Louis/Documents/3rd%20Yr%20college%202025-26/2nd%20sem/QTYSUR/qty%20lab/QtySur%20Estimate/UY_Louis.xlsx) and [`tech_spec_v2.md`](file:///e:/Users/Louis/Documents/boq_system_v2/tech_spec_v2.md).
- **Fajardo Book Knowledge**: Calculations must strictly follow Max Fajardo's *Simplified Construction Estimate* formulas and solved case study methods.
- **DPWH Direct Costs**: Compute Total Direct Cost ($C_{\text{total}} = C_{\text{material}} + C_{\text{labor}} + C_{\text{equipment}}$) using DPWH CMPD rates.

---

## 📐 Step 5 — Native Blueprint Vector Layer & Visual Comparison
- Render original vector paths directly on blueprint sheets (`pdf.js`/Canvas) with translucent color-coded heatmaps:
  - 🟦 **Blue**: Concrete Footings & Columns
  - 🟧 **Orange**: Beams & Slabs
  - 🟩 **Green**: Masonry Walls
  - 🟪 **Purple**: Steel Rebar & Structural Steel
- Compare ingested vector paths against original drawing sheets with $< 1\text{mm}$ spatial variance tolerance.
