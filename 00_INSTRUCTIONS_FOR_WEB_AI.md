# INSTRUCTIONS FOR WEB AIs (Claude Web, ChatGPT Web, Gemini Web) — READ THIS FIRST

You are an external Web AI collaborating on **Plan2Takeoff Version 2** (`boq_system_v2`).
All project specifications, handbooks, schemas, and source files are hosted in our public GitHub repository with 100% open raw HTTPS links.

---

## 👔 Section 0 — Orchestrator & Project Manager (PM) Governance Framework

The primary AI agent operating inside the user's IDE terminal is **Antigravity AI (Gemini Orchestrator)**, serving strictly as the **Project Manager / Orchestrator**.

### PM Roles, Directives & Rules:
1. **Executive Oversight & Roadmap Management**: Antigravity AI manages task creation, roadmap tracking, technical specifications, progress reports, and overall system architecture.
2. **Task Specification & Delegation**: When the user requests a task to be delegated, Antigravity AI formulates a comprehensive task description mapped to the 13 trade divisions (`UY_Louis.xlsx`).
3. **Permanent GitHub Raw Link Rule**: Every task description created by the PM includes **stable GitHub raw HTTPS URLs** (e.g. `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/tech_spec_v2.md`) so that Web AIs (Claude Web) can directly fetch, inspect, and index all workspace files over the web with ZERO 403/503 bot errors or landing page blocks.
4. **No Hands-on Subagent Handoff without User Approval**: The PM **never** hands off tasks to subagents automatically without explicit user permission.
6. **Long-Running Process Rule**: Any process that must run continuously (dev servers, watchers, tunnel managers, Flask backend, `npm run dev`, etc.) **must be instructed to run in a separate terminal window by the user** — NOT as a background task spawned inside the chat session — unless the user explicitly says otherwise. The PM must always provide the exact terminal command for the user to run themselves.

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

- **GitHub Repository**       : `https://github.com/RememberMeWiz/boq_system_v2`
- **Parser Technical Spec v2.0**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/tech_spec_parser_v2.md`
- **Parser Design Spec (Stage 2)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/parser_design_spec.md`
- **Overall Technical Specs v2.0**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/tech_spec_v2.md`
- **Exhaustive Handbook (100%)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/formula_exhaustive_handbook.md`
- **Sample Solved Cases**     : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/sample_solved_cases.md`
- **Web AI Instructions**     : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/00_INSTRUCTIONS_FOR_WEB_AI.md`
- **Current Takeoff Engine**   : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/engine/fajardo.py`
- **Project Log**             : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/log.md`
- **Database Schema**         : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/schema/boq_v2_schema.sql`


---

## 🔄 Step 2 — Code Delivery Protocol

External Web AIs (Claude Web) deliver complete code modules directly as downloadable code blocks in chat responses. The Antigravity PM ingests the code file into the local workspace, executes tests, and commits updates to Git.
