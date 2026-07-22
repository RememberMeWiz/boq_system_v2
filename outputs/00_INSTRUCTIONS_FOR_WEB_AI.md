# INSTRUCTIONS FOR WEB AIs (Claude Web, ChatGPT Web, Gemini Web) — READ THIS FIRST

You are an external Web AI collaborating on **Plan2Takeoff Version 2** (`boq_system_v2`).
Follow this protocol to read workspace state and deliver code updates directly in chat responses.

---

## 👔 Section 0 — Orchestrator & Project Manager (PM) Governance Framework

The primary AI agent operating inside the user's IDE terminal is **Antigravity AI (Gemini Orchestrator)**, serving strictly as the **Project Manager / Orchestrator**.

### PM Roles, Directives & Rules:
1. **Executive Oversight & Roadmap Management**: Antigravity AI manages task creation, roadmap tracking, technical specifications, progress reports, and overall system architecture.
2. **Task Specification & Delegation**: When the user requests a task to be delegated, Antigravity AI formulates a comprehensive task description mapped to the 13 trade divisions (`UY_Louis.xlsx`).
3. **Public HTTPS Link Rule**: Every task description created by the PM includes **live public HTTPS tunneled URLs** (e.g. `https://plan2takeoff-v2.loca.lt/tech_spec_v2.md`) so that Web AIs (Claude Web) can directly fetch, inspect, and index workspace files over the internet.
4. **No Hands-on Subagent Handoff without User Approval**: The PM **never** hands off tasks to subagents automatically without explicit user permission.
5. **Web AI Collaboration & Code Delivery Protocol**: External Web AIs (such as Claude Web) receive the PM's task specification, write complete code modules directly in their response text as downloadable code blocks, and the Antigravity Orchestrator (PM) ingests, tests, and commits the code locally.

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

---

## 🔄 Step 2 — Code Delivery Protocol

External Web AIs (Claude Web) deliver complete code modules and updates directly as downloadable code blocks in chat responses. The Antigravity PM ingests the code file directly into the local workspace, runs automated tests, and updates project logs.
