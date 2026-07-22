"""
Plan2Takeoff V2 — Public Tunnel Manager (Localtunnel Integration)
Spawns an automatic public HTTPS gateway for local server (port 5001),
capturing the live public URL and serving zero-touch requests to Web AIs (Claude Web).
"""

import os
import sys
import time
import subprocess
import threading
from typing import Optional

TUNNEL_URL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "public_tunnel_url.txt")

_current_tunnel_url: Optional[str] = None


def get_public_tunnel_url() -> Optional[str]:
    """Returns live public tunnel URL if active."""
    global _current_tunnel_url
    if _current_tunnel_url:
        return _current_tunnel_url
    if os.path.exists(TUNNEL_URL_FILE):
        try:
            with open(TUNNEL_URL_FILE, "r", encoding="utf-8") as f:
                url = f.read().strip()
                if url.startswith("http"):
                    _current_tunnel_url = url
                    return url
        except Exception:
            pass
    return None


def start_localtunnel(port: int = 5001, preferred_subdomain: str = "plan2takeoff-v2"):
    """Launches localtunnel in background thread and captures public URL."""
    global _current_tunnel_url

    cmd = ["cmd", "/c", "npx", "-y", "localtunnel", "--port", str(port), "--subdomain", preferred_subdomain]
    print(f"[TUNNEL] Provisioning public HTTPS gateway on port {port}...")

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        def monitor_output():
            global _current_tunnel_url
            for line in iter(proc.stdout.readline, ''):
                if not line:
                    break
                line_str = line.strip()
                print(f"[TUNNEL STDOUT] {line_str}")
                if "your url is:" in line_str.lower() or "https://" in line_str:
                    parts = line_str.split()
                    for p in parts:
                        if p.startswith("https://"):
                            _current_tunnel_url = p
                            os.makedirs(os.path.dirname(TUNNEL_URL_FILE), exist_ok=True)
                            with open(TUNNEL_URL_FILE, "w", encoding="utf-8") as f:
                                f.write(p)
                            print(f"\n========================================================")
                            print(f"[TUNNEL] PUBLIC ZERO-TOUCH TUNNEL LIVE FOR CLAUDE WEB:")
                            print(f"[TUNNEL] Manifest URL : {p}/api/v1/manifest")
                            print(f"[TUNNEL] Agent Sync   : {p}/api/v1/agent-sync")
                            print(f"========================================================\n")

        thread = threading.Thread(target=monitor_output, daemon=True)
        thread.start()
        return proc

    except Exception as e:
        print(f"[TUNNEL ERROR] Could not start localtunnel: {e}")
        return None


if __name__ == "__main__":
    p = start_localtunnel()
    if p:
        try:
            p.wait()
        except KeyboardInterrupt:
            p.terminate()
