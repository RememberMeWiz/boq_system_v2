"""
Plan2Takeoff V2 — Public Auto-Indexed Manifest API
Dynamically formats all project file URLs using the caller's public HTTPS tunnel domain.
Includes live session stats and engine version hash.
"""

import os
import time
import hashlib
from typing import Dict, Any, List
from flask import request


def _engine_hash(workspace_dir: str) -> str:
    """Returns sha256[:16] of fajardo.py for AI agent change detection."""
    fp = os.path.join(workspace_dir, "backend", "engine", "fajardo.py")
    if not os.path.exists(fp):
        return "unavailable"
    with open(fp, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def _live_stats(workspace_dir: str) -> Dict:
    """Reads last session summary written by app.py after each takeoff."""
    cache_path = os.path.join(workspace_dir, "outputs", "last_session.json")
    if os.path.exists(cache_path):
        try:
            import json
            with open(cache_path) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_drawing":       None,
        "last_grand_total":   None,
        "last_session_id":    None,
        "last_processed_at":  None,
        "total_sessions":     0,
    }


def generate_project_manifest(workspace_dir: str) -> Dict[str, Any]:
    """Scans workspace and builds a clean JSON manifest with dynamically formatted HTTPS file URLs."""
    host  = request.headers.get("X-Forwarded-Host", request.headers.get("Host", "localhost:5000"))
    proto = request.headers.get("X-Forwarded-Proto",
                                "https" if ("loca.lt" in host or "ngrok" in host) else "http")
    base_url = f"{proto}://{host}".rstrip("/")

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
        "backend/app.py",
        "backend/api/supabase_client.py",
    ]

    files_list = []
    for fname in known_files:
        full_path = os.path.join(workspace_dir, fname)
        exists = os.path.exists(full_path)
        files_list.append({
            "filename":       fname,
            "exists_locally": exists,
            "public_url":     f"{base_url}/{fname}",
            "size_bytes":     os.path.getsize(full_path) if exists else 0,
            "last_modified":  time.ctime(os.path.getmtime(full_path)) if exists else None,
        })

    stats = _live_stats(workspace_dir)

    prompt_instruction = (
        "🤖 WELCOME CLAUDE WEB / AI AGENT! READ THIS FIRST:\n"
        "You are collaborating on Plan2Takeoff Version 2 (boq_system_v2).\n\n"
        "INSTRUCTIONS & PROTOCOL RULES:\n"
        "1. WORKSPACE DISCOVERY: Fetch 00_INSTRUCTIONS_FOR_WEB_AI.md, tech_spec_v2.md, and log.md "
        "using the public HTTPS URLs listed in manifest_files below.\n"
        "2. TRADE SCOPE & ESTIMATING METHODOLOGY: Follow the 13 construction trade divisions defined "
        "in UY_Louis.xlsx and apply DPWH Direct Costs (Material + Labor + Equipment).\n"
        "3. STRICT V1 ISOLATION POLICY: NEVER write to V1 Supabase tables or V1 storage buckets.\n"
        "4. ZERO-TOUCH CODE SYNC: POST to /api/v1/agent-sync with header "
        f"'X-Agent-Sync-Token: p2t_v2_agent_relay_token_9981' at {base_url}.\n"
        "5. LOG PROTOCOL: Prepend STARTED and COMPLETED log entries at the top of log.md."
    )

    return {
        "START_HERE_PROMPT_INSTRUCTION": prompt_instruction,
        "project_name":        "Plan2Takeoff V2",
        "version":             "2.0.0",
        "timestamp_utc":       time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "engine_hash_sha256":  _engine_hash(workspace_dir),
        "manifest_url":        f"{base_url}/api/v1/manifest",
        "agent_sync_url":      f"{base_url}/api/v1/agent-sync",
        "api_routes": {
            "health":          f"{base_url}/api/v1/health",
            "cmpd_rates":      f"{base_url}/api/v1/cmpd-rates",
            "process_drawing": f"{base_url}/api/v1/process-drawing",
            "optimize_rebar":  f"{base_url}/api/v1/optimize-rebar",
            "parse_schedule":  f"{base_url}/api/v1/parse-schedule",
            "sync_supabase":   f"{base_url}/api/v1/sync-supabase",
            "sessions":        f"{base_url}/api/v1/sessions",
            "export_csv":      f"{base_url}/api/v1/export-csv",
            "export_json":     f"{base_url}/api/v1/export-json",
        },
        "live_session_stats":  stats,
        "v1_isolation_status": "ISOLATED (No write access to V1 tables/buckets)",
        "manifest_files":      files_list,
        "active_trades": [
            "Section I General Requirements",    "Section II Earthworks",
            "Section III Concrete & Formworks",   "Section IV Masonry",
            "Section V Metals & Rebar",           "Section VI Roofing",
            "Section VII Doors & Windows",         "Section VIII Tiles",
            "Section IX Painting",                "Section X Plumbing",
            "Section XI Electrical",              "Section XII Mechanical",
            "Section XIII Special Works",
        ],
    }
