"""
Plan2Takeoff V2 — Public Auto-Indexed Manifest API
Dynamically formats all project file URLs using the caller's public HTTPS tunnel domain.
"""

import os
import time
from typing import Dict, Any, List
from flask import request


def generate_project_manifest(workspace_dir: str) -> Dict[str, Any]:
    """Scans workspace and builds a clean JSON manifest with dynamically formatted public HTTPS tunneled file URLs."""
    # Determine base public HTTPS URL dynamically from request headers
    host = request.headers.get("X-Forwarded-Host", request.headers.get("Host", "localhost:5001"))
    proto = request.headers.get("X-Forwarded-Proto", "https" if ("loca.lt" in host or "ngrok" in host) else "http")
    base_url = f"{proto}://{host}".rstrip("/")

    files_list = []
    
    # Complete list of priority project files across docs, schemas, outputs, and engines
    known_files = [
        "00_INSTRUCTIONS_FOR_WEB_AI.md",
        "tech_spec_v2.md",
        "log.md",
        "progress_report_v2.md",
        "claude_web_setup_guide.md",
        "sample_solved_cases.md",
        "formula_exhaustive_handbook.md",
        "sample_structural_plan.pdf",
        "outputs/tech_spec_v2.md",
        "outputs/progress_report_v2.md",
        "outputs/sample_solved_cases.md",
        "outputs/formula_exhaustive_handbook.md",
        "outputs/structural_vector_overlay.svg",
        "outputs/vector_diff_comparison.png",
        "outputs/00_INSTRUCTIONS_FOR_WEB_AI.md",
        "outputs/claude_web_setup_guide.md",
        "schema/boq_v2_schema.sql",
        "backend/engine/fajardo.py",
        "backend/engine/rebar_optimizer.py",
        "backend/engine/pdf_dxf_parser.py",
        "backend/engine/vision_ocr.py",
        "backend/engine/test_vector_diff.py",
        "backend/app.py"
    ]

    for fname in known_files:
        full_path = os.path.join(workspace_dir, fname)
        exists = os.path.exists(full_path)
        files_list.append({
            "filename": fname,
            "exists_locally": exists,
            "public_url": f"{base_url}/{fname}",
            "size_bytes": os.path.getsize(full_path) if exists else 0,
            "last_modified": time.ctime(os.path.getmtime(full_path)) if exists else None
        })

    prompt_instruction = (
        "🤖 WELCOME CLAUDE WEB / AI AGENT! READ THIS FIRST:\n"
        "You are collaborating on Plan2Takeoff Version 2 (boq_system_v2).\n\n"
        "INSTRUCTIONS & PROTOCOL RULES:\n"
        "1. WORKSPACE DISCOVERY: Fetch 00_INSTRUCTIONS_FOR_WEB_AI.md, tech_spec_v2.md, and log.md "
        "using the public HTTPS URLs listed in manifest_files below.\n"
        "2. TRADE SCOPE & ESTIMATING METHODOLOGY: Follow the 13 construction trade divisions defined in UY_Louis.xlsx and "
        "apply standard construction estimate formulas with DPWH Direct Costs (Material + Labor + Equipment).\n"
        "3. STRICT V1 ISOLATION POLICY: NEVER write to V1 Supabase tables or V1 storage buckets (project-files). "
        "V2 is 100% isolated and uses dedicated V2 schemas and local endpoints.\n"
        "4. ZERO-TOUCH CODE SYNC: When you complete code edits or file updates, send your payload directly via "
        f"POST {base_url}/api/v1/agent-sync with header 'X-Agent-Sync-Token: p2t_v2_agent_relay_token_9981'.\n"
        "5. LOG PROTOCOL: Always prepend STARTED and COMPLETED log entries at the top of log.md using your model name."
    )

    return {
        "START_HERE_PROMPT_INSTRUCTION": prompt_instruction,
        "project_name": "Plan2Takeoff V2",
        "version": "2.0.0",
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "manifest_url": f"{base_url}/api/v1/manifest",
        "agent_sync_url": f"{base_url}/api/v1/agent-sync",
        "v1_isolation_status": "ISOLATED (No write access to V1 tables/buckets)",
        "manifest_files": files_list,
        "active_trades": [
          "Section I General Requirements", "Section II Earthworks", "Section III Concrete & Formworks", 
          "Section IV Masonry", "Section V Metals & Rebar", "Section VI Roofing", 
          "Section VII Doors & Windows", "Section VIII Tiles", "Section IX Painting", 
          "Section X Plumbing", "Section XI Electrical", "Section XII Mechanical", "Section XIII Special Works"
        ]
    }
