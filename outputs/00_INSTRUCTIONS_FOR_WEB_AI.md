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
5. **Web AI Collaboration Protocol**: External Web AIs (such as Claude Web) receive the PM's task specification, fetch the manifest and technical specs over GitHub raw URLs, execute the coding/takeoff work, and deliver the completed code module directly in their chat response text.

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
- **Technical Specs v2.0**    : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/tech_spec_v2.md`
- **Exhaustive Handbook (100%)**: `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/formula_exhaustive_handbook.md`
- **Sample Solved Cases**     : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/sample_solved_cases.md`
- **Web AI Instructions**     : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/00_INSTRUCTIONS_FOR_WEB_AI.md`
- **Current Takeoff Engine**   : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/backend/engine/fajardo.py`
- **Project Log**             : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/log.md`
- **Database Schema**         : `https://raw.githubusercontent.com/RememberMeWiz/boq_system_v2/main/schema/boq_v2_schema.sql`

---

## 🔄 Step 2 — Code Delivery Protocol

External Web AIs (Claude Web) deliver complete code modules directly as downloadable code blocks in chat responses. The Antigravity PM ingests the code file into the local workspace, executes tests, and commits updates to Git.
