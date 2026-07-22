"""
Plan2Takeoff V2 — Persistent Server & Tunnel Runner
Keeps local server on port 5001 and localtunnel HTTPS gateway active continuously.
"""

import os
import sys
import time
import subprocess


def run_persistent_server():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_script = os.path.join(base_dir, "backend", "app.py")

    print("========================================================")
    print("      Plan2Takeoff V2 Persistent Server & Tunnel        ")
    print("========================================================")

    while True:
        try:
            print(f"[RUNNER] Starting Plan2Takeoff V2 Engine on http://127.0.0.1:5001 ...")
            proc = subprocess.Popen([sys.executable, app_script], cwd=base_dir)
            proc.wait()
            print("[RUNNER] Server process exited. Restarting in 3 seconds...")
            time.sleep(3)
        except KeyboardInterrupt:
            print("[RUNNER] Shutting down persistent runner...")
            break
        except Exception as e:
            print(f"[RUNNER ERROR] {e}. Retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    run_persistent_server()
