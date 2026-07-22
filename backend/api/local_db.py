"""
Plan2Takeoff V2 — Local SQLite Database Client
Zero-config local database storing project sessions and BOQ items in backend/boq_v2.db.
100% offline, built into Python's standard library.
"""

import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

log = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "boq_v2.db")


def get_connection():
    """Returns a SQLite connection configured for dict rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates local SQLite tables for V2 sessions and BOQ line items."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS boq_sessions_v2 (
                session_id TEXT PRIMARY KEY,
                drawing_name TEXT NOT NULL,
                grand_total REAL DEFAULT 0.0,
                sections_subtotal REAL DEFAULT 0.0,
                item_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS boq_items_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT REFERENCES boq_sessions_v2(session_id) ON DELETE CASCADE,
                item_code TEXT NOT NULL,
                trade TEXT NOT NULL,
                description TEXT NOT NULL,
                quantity REAL DEFAULT 0.0,
                unit TEXT NOT NULL,
                material_unit_cost REAL DEFAULT 0.0,
                labor_unit_cost REAL DEFAULT 0.0,
                equipment_unit_cost REAL DEFAULT 0.0,
                total_unit_cost REAL DEFAULT 0.0,
                total_amount REAL DEFAULT 0.0,
                status TEXT DEFAULT 'Confirmed',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    log.info(f"Local SQLite database initialized at {DB_PATH}")


def save_session(session_id: str, drawing_name: str, boq_rows: List[Dict],
                 grand_total: float, sections_subtotal: float) -> Dict:
    """Saves a complete BOQ session and its line items to local SQLite DB."""
    try:
        now_iso = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            cursor = conn.cursor()

            # Upsert session header
            cursor.execute("""
                INSERT INTO boq_sessions_v2 (session_id, drawing_name, grand_total, sections_subtotal, item_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    drawing_name=excluded.drawing_name,
                    grand_total=excluded.grand_total,
                    sections_subtotal=excluded.sections_subtotal,
                    item_count=excluded.item_count,
                    updated_at=excluded.updated_at
            """, (session_id, drawing_name, round(grand_total, 2), round(sections_subtotal, 2), len(boq_rows), now_iso))

            # Remove previous items for this session if re-saving
            cursor.execute("DELETE FROM boq_items_v2 WHERE session_id = ?", (session_id,))

            # Insert line items
            for r in boq_rows:
                cursor.execute("""
                    INSERT INTO boq_items_v2 (
                        session_id, item_code, trade, description, quantity, unit,
                        material_unit_cost, labor_unit_cost, equipment_unit_cost,
                        total_unit_cost, total_amount, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    r.get("item_code", ""),
                    r.get("trade", ""),
                    r.get("description", ""),
                    float(r.get("quantity", 0)),
                    r.get("unit", ""),
                    float(r.get("material_unit_cost", 0)),
                    float(r.get("labor_unit_cost", 0)),
                    float(r.get("equipment_unit_cost", 0)),
                    float(r.get("total_unit_cost", 0)),
                    float(r.get("total_amount", 0)),
                    r.get("status", "Confirmed"),
                ))
            conn.commit()

        log.info(f"Saved session {session_id} to local SQLite ({len(boq_rows)} items)")
        return {
            "status": "saved",
            "storage": "local_sqlite",
            "db_path": DB_PATH,
            "session_id": session_id,
            "item_count": len(boq_rows),
            "grand_total": grand_total,
        }

    except Exception as e:
        log.error(f"Local SQLite save_session failed: {e}")
        return {"status": "error", "reason": str(e), "session_id": session_id}


def load_session(session_id: str) -> Optional[Dict]:
    """Loads a session + its BOQ items from local SQLite DB."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM boq_sessions_v2 WHERE session_id = ?", (session_id,))
            sess_row = cursor.fetchone()
            if not sess_row:
                return None

            cursor.execute("SELECT * FROM boq_items_v2 WHERE session_id = ? ORDER BY item_code ASC", (session_id,))
            item_rows = cursor.fetchall()

            return {
                "session": dict(sess_row),
                "boq": [dict(r) for r in item_rows],
            }
    except Exception as e:
        log.error(f"Local SQLite load_session failed: {e}")
        return None


def list_sessions(limit: int = 20) -> List[Dict]:
    """Lists the most recent BOQ sessions from local SQLite DB."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, drawing_name, grand_total, item_count, created_at
                FROM boq_sessions_v2
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(r) for r in cursor.fetchall()]
    except Exception as e:
        log.error(f"Local SQLite list_sessions failed: {e}")
        return []


def delete_session_by_drawing(drawing_name: str) -> bool:
    """Deletes all sessions and BOQ items associated with drawing_name from local SQLite DB."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM boq_sessions_v2 WHERE drawing_name = ?", (drawing_name,))
            conn.commit()
            return True
    except Exception as e:
        log.error(f"Local SQLite delete_session_by_drawing failed: {e}")
        return False
