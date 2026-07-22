"""
Plan2Takeoff V2 — Supabase V2 Session Persistence Client
Uses direct Supabase REST API v1 or supabase-py SDK.
Reads credentials from backend/.env or environment.
All operations target V2 tables ONLY (boq_sessions_v2, boq_items_v2).
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

log = logging.getLogger(__name__)

# Load backend/.env if available
try:
    from dotenv import load_dotenv
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
except ImportError:
    pass

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


def _get_config():
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    # Clean /rest/v1 if user passed full rest URL
    if url.endswith("/rest/v1"):
        url = url[:-8]
    key = os.environ.get("SUPABASE_KEY", "").strip()
    return url, key


def is_configured() -> bool:
    url, key = _get_config()
    return bool(url and key and _REQUESTS_AVAILABLE)


def _get_headers(key: str) -> Dict[str, str]:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }


# ---------------------------------------------------------------------------
# Session Operations
# ---------------------------------------------------------------------------

def save_session(session_id: str, drawing_name: str, boq_rows: List[Dict],
                 grand_total: float, sections_subtotal: float) -> Dict:
    """
    Saves a complete BOQ session to Supabase V2 tables via REST API.
    Returns: {"status": "saved"|"skipped"|"error", "session_id": str}
    """
    url, key = _get_config()
    if not url or not key:
        return {"status": "skipped", "reason": "Supabase credentials not configured in backend/.env", "session_id": session_id}

    if not _REQUESTS_AVAILABLE:
        return {"status": "error", "reason": "requests library missing", "session_id": session_id}

    try:
        headers = _get_headers(key)
        now_iso = datetime.utcnow().isoformat()

        # 1. Upsert header into boq_sessions_v2
        session_payload = [{
            "session_id":          session_id,
            "drawing_name":        drawing_name,
            "grand_total":         round(grand_total, 2),
            "sections_subtotal":   round(sections_subtotal, 2),
            "item_count":          len(boq_rows),
            "updated_at":          now_iso,
        }]

        endpoint_sess = f"{url}/rest/v1/boq_sessions_v2"
        res_sess = requests.post(endpoint_sess, headers=headers, json=session_payload, timeout=10)

        if res_sess.status_code not in (200, 201, 204):
            log.error(f"Supabase session upsert failed [{res_sess.status_code}]: {res_sess.text}")
            return {"status": "error", "reason": f"HTTP {res_sess.status_code}: {res_sess.text}", "session_id": session_id}

        # 2. Upsert line items into boq_items_v2
        if boq_rows:
            item_payloads = [
                {
                    "session_id":           session_id,
                    "item_code":            r.get("item_code", ""),
                    "trade":                r.get("trade", ""),
                    "description":          r.get("description", ""),
                    "quantity":             float(r.get("quantity", 0)),
                    "unit":                 r.get("unit", ""),
                    "material_unit_cost":   float(r.get("material_unit_cost", 0)),
                    "labor_unit_cost":      float(r.get("labor_unit_cost", 0)),
                    "equipment_unit_cost":  float(r.get("equipment_unit_cost", 0)),
                    "total_unit_cost":      float(r.get("total_unit_cost", 0)),
                    "total_amount":         float(r.get("total_amount", 0)),
                    "status":               r.get("status", "Confirmed"),
                }
                for r in boq_rows
            ]

            endpoint_items = f"{url}/rest/v1/boq_items_v2"
            res_items = requests.post(endpoint_items, headers=headers, json=item_payloads, timeout=15)

            if res_items.status_code not in (200, 201, 204):
                log.warning(f"Supabase items upsert issue [{res_items.status_code}]: {res_items.text}")

        log.info(f"Session {session_id} successfully saved to Supabase V2 ({len(boq_rows)} items)")
        return {
            "status": "saved",
            "session_id": session_id,
            "item_count": len(boq_rows),
            "grand_total": grand_total,
            "supabase_url": f"{url}/rest/v1/boq_sessions_v2?session_id=eq.{session_id}"
        }

    except Exception as e:
        log.error(f"Supabase save_session failed: {e}")
        return {"status": "error", "reason": str(e), "session_id": session_id}


def load_session(session_id: str) -> Optional[Dict]:
    """
    Loads a session + its BOQ items from Supabase V2.
    Returns: {"session": {...}, "boq": [...]} or None.
    """
    url, key = _get_config()
    if not url or not key or not _REQUESTS_AVAILABLE:
        return None

    try:
        headers = {"apikey": key, "Authorization": f"Bearer {key}"}

        # Get session header
        sess_url = f"{url}/rest/v1/boq_sessions_v2?session_id=eq.{session_id}"
        r_sess = requests.get(sess_url, headers=headers, timeout=10)
        if r_sess.status_code != 200 or not r_sess.json():
            return None
        sess_data = r_sess.json()[0]

        # Get items
        items_url = f"{url}/rest/v1/boq_items_v2?session_id=eq.{session_id}&order=item_code.asc"
        r_items = requests.get(items_url, headers=headers, timeout=10)
        items_data = r_items.json() if r_items.status_code == 200 else []

        return {
            "session": sess_data,
            "boq": items_data,
        }
    except Exception as e:
        log.error(f"Supabase load_session failed: {e}")
        return None


def list_sessions(limit: int = 20) -> List[Dict]:
    """
    Lists the most recent BOQ sessions from Supabase V2.
    Returns: list of session header dicts, or [].
    """
    url, key = _get_config()
    if not url or not key or not _REQUESTS_AVAILABLE:
        return []

    try:
        headers = {"apikey": key, "Authorization": f"Bearer {key}"}
        endpoint = f"{url}/rest/v1/boq_sessions_v2?select=session_id,drawing_name,grand_total,item_count,created_at&order=created_at.desc&limit={limit}"
        r = requests.get(endpoint, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except Exception as e:
        log.error(f"Supabase list_sessions failed: {e}")
        return []
