# INSTRUCTIONS FOR WEB AIs (Claude Web, ChatGPT Web, Gemini Web) — READ THIS FIRST

You are an external Web AI collaborating on **Plan2Takeoff Version 2** (`boq_system_v2`).
All project specifications, handbooks, schemas, and source files are hosted in our public GitHub repository with 100% open raw HTTPS links.

---

## 👔 Section 0 — Orchestrator & Project Manager (PM) Governance Framework

The primary AI agent operating inside the user's IDE terminal is **Antigravity AI (Gemini Orchestrator)**, serving strictly as the **Project Manager / Orchestrator**.

### PM Roles, Directives & Rules:
1. **Executive Oversight & Roadmap Management**: Antigravity AI manages task creation, roadmap tracking, technical specifications, progress reports, and overall system architecture.
2. **Task Specification & Delegation**: When the user requests a task to be delegated, Antigravity AI formulates a comprehensive task description mapped to the 13 trade divisions (`UY_Louis.xlsx`).
3. **Mandatory Raw GitHub Link & Verification Protocol**: Web AIs (Claude Web) cannot discover unindexed internal file paths on their own via search engines. Therefore, in EVERY response or task summary where code changes, fixes, or test results are mentioned, Antigravity AI (PM) MUST explicitly provide direct, full raw GitHub HTTPS URLs (`https://raw.githubusercontent.com/...`) for ALL modified source files and JSON output artifacts. To bypass Fastly Edge CDN's 5-minute cache (`Cache-Control: max-age=300`), URLs MUST use the immutable commit SHA path (e.g. `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/<commit-sha>/backend/app.py`) or append `?cb=<commit-sha>`. Never rely on prose summaries or asserted claim tables without direct raw links.
4. **No Hands-on Subagent Handoff without User Approval**: The PM **never** hands off tasks to subagents automatically without explicit user permission.
6. **Long-Running Process Governance**: Persistent processes and servers that must run continuously (Flask backend on port 5000, Vite dev server on port 5173, dev watchers, tunnel managers, etc.) MUST NEVER be spawned as background tasks inside Antigravity, AGY CLI, or any agentic AI chat sessions on desktop unless explicitly requested. Spawning servers inside chat sessions causes context clogging, subagent thread contention, and process lockups when chat contexts reset. Agents must provide the exact PowerShell/cmd command or instruct the user to run `start_plan2takeoff.bat` in their own external terminal window.

### PM Builder's Toolkit & Engineering Directives:
7. **Builder's Toolkit 6-Stage Framework**: The PM follows the 6-stage development framework (`Empathy` $\rightarrow$ `Design` $\rightarrow$ `Architecture` $\rightarrow$ `Implementation` $\rightarrow$ `Judgment` $\rightarrow$ `Shipping`).
8. **Zero Hardcoding Policy**: The PM ensures that parser schemas, payload specifications, and engine logic contain zero hardcoded building sizes, grid counts, classroom numbers, or footing dimensions. Everything must be 100% parameter-driven and extracted dynamically.
9. **Strict Parser vs. Solver Separation**: The parser executes ZERO math/calculations (volume, weight, or cost). It only extracts, classifies, structures, and identifies data payload. All mathematics and PNS 49 calculations belong strictly inside `fajardo.py`.
10. **Programmatic Verification Gate & Audit Signoff**: The parser enforces a programmatic `verification_gate` (`BLOCKED` vs `READY`). Missing load-bearing schedule sheets ($S-6, S-7, S-8$) generate `BLOCKING` issues. The solver REST endpoint (`POST /api/v1/solver/process`) hard-rejects unverified payloads with `HTTP 409 Conflict`. Overriding blocking issues or proceeding with warning cards requires an itemized audit signoff (`POST /api/v1/parser/signoff`) passing a `resolutions[]` array, attaching `signed_off_by`, timestamp, and `note` directly to each target `issue_id` in `verification_gate.resolution_log[]`.
11. **No Unrequested File Edits or Git Commits**: The PM strictly refrains from committing to Git or making unrequested file edits without explicit user approval.
12. **GitHub Edge CDN Cache-Busting Rule**: `raw.githubusercontent.com` uses Fastly Edge CDN with a 5-minute TTL cache (`Cache-Control: max-age=300`). Whenever the PM hands raw GitHub HTTPS links to Web AIs (Claude Web) after a Git push, the PM **must append an explicit cache-busting query parameter (`?cb=<commit-sha>`) or use the immutable commit SHA path** (e.g. `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/<commit-sha>/file.md`). This forces Fastly/GitHub Edge CDN to immediately bypass its 5-minute cache and return byte-for-byte live content.



---

## 📌 CRITICAL RULE 0 — V1 Isolation Policy
⚠️ **DO NOT TOUCH V1 DATABASE OR CLOUD STORAGE**:
- V2 reuses algorithms from V1 (`boq_system`), but is strictly isolated.
- **NEVER** write to V1 Supabase tables or V1 storage buckets (`project-files`).
- All V2 work must use V2 endpoints, V2 local schema (`boq_v2_schema.sql`), and V2 storage locations.

---

## 🌐 Permanent GitHub Raw Links Index

All project files are directly fetchable via your web browsing tool:

### 📋 Specifications & Governance:
- **GitHub Repository**       : `https://github.com/RememberMeWiz/boq_system_v2`
- **Web AI Instructions**     : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/00_INSTRUCTIONS_FOR_WEB_AI.md`
- **Parser Technical Spec v2.0**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/tech_spec_parser_v2.md`
- **Parser Design Spec (Stage 2)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/parser_design_spec.md`
- **Overall Technical Specs v2.0**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/tech_spec_v2.md`
- **Exhaustive Formula Handbook**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/formula_exhaustive_handbook.md`
- **Sample Solved Cases**     : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/sample_solved_cases.md`
- **Project Log**             : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/log.md`
- **Database Schema**         : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/schema/boq_v2_schema.sql`

### ⚙️ Core Backend & API App:
- **Flask Backend API Server (`app.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/app.py`

### 🧠 Civil Engineering & Parser Engines (`backend/engine/`):
- **13-Trade Fajardo Takeoff Engine (`fajardo.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/engine/fajardo.py`
- **Deterministic PDF/DXF Parser (`pdf_dxf_parser.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/engine/pdf_dxf_parser.py`
- **AI Vision Blueprint Inspector (`vision_parser.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/engine/vision_parser.py`
- **Visual CAD Reconstruction Engine (`reconstruction_module.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/engine/reconstruction_module.py`
- **1D Bin-Packing Rebar Optimizer (`rebar_optimizer.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/engine/rebar_optimizer.py`
- **DUPA Unit Price QA Loader (`dupa_loader.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/engine/dupa_loader.py`
- **Vision Schedule Crop Engine (`vision_ocr.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/engine/vision_ocr.py`

### 🔌 API Services & Persistence (`backend/api/`):
- **Project Manifest Generator (`api/manifest.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/api/manifest.py`
- **Agent Sync Handler (`api/agent_sync.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/api/agent_sync.py`
- **Supabase Cloud Sync Client (`api/supabase_client.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/api/supabase_client.py`
- **SQLite Local DB Manager (`api/local_db.py`)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/api/local_db.py`

### 📊 Empirical Benchmark Data & Verified Extraction JSON Outputs:
- **Raw Task Terminal Execution Logs**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/outputs/task_execution_logs.md`
- **Raw Local Cropped Region OCR Side-by-Side Comparison JSON**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/outputs/side_by_side_comparison_results.json`
- **Raw Local Full-Page OCR Benchmark JSON**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/outputs/local_ocr_benchmark_results.json`
- **Raw Surgical Live Gemini Vision Payload JSON**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/outputs/surgical_live_extraction_payload.json`
- **Raw Single-Page Vision OCR Output JSON**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/outputs/single_page_vision_extraction.json`
- **Raw Plan Part 1 Benchmark JSON**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/outputs/benchmark_plan%20part%201.json`






---

## 🔄 Step 2 — Code Delivery Protocol

External Web AIs (Claude Web) deliver complete code modules directly as downloadable code blocks in chat responses. The Antigravity PM ingests the code file into the local workspace, executes tests, and commits updates to Git.
