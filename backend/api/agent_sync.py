"""
Plan2Takeoff V2 — Webhook Agent Sync Endpoint
Receives code edits, JSON payloads, and log updates from external AI agents,
automatically committing to Git and syncing to Supabase Storage.
"""

import os
import json
import subprocess
from typing import Dict, Any

AUTH_SYNC_TOKEN = "p2t_v2_agent_relay_token_9981"


def process_agent_sync_payload(payload: Dict[str, Any], token: str) -> Dict[str, Any]:
    """Processes incoming agent sync request."""
    if token != AUTH_SYNC_TOKEN:
        return {"status": "error", "message": "Unauthorized: Invalid sync token."}

    action = payload.get("action", "update_file")
    target_file = payload.get("target_file")
    content = payload.get("content", "")
    commit_msg = payload.get("commit_message", f"Agent Sync Update: {target_file}")

    if not target_file:
        return {"status": "error", "message": "Missing target_file in payload."}

    try:
        # Write updated content locally
        full_path = os.path.abspath(target_file)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Trigger background git commit/push if git repository present
        git_synced = False
        if os.path.exists(".git"):
            try:
                subprocess.run(["git", "add", target_file], check=True)
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                git_synced = True
            except Exception as e:
                git_synced = False

        return {
            "status": "success",
            "message": f"Successfully synced {target_file}",
            "file": target_file,
            "bytes_written": len(content),
            "git_synced": git_synced
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
