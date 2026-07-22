"""
Plan2Takeoff V2 — Offline-First Desktop Launcher (PyWebView)
Runs the embedded Flask engine locally and opens an offline desktop window
for civil engineers on remote job sites without internet access.
"""

import os
import sys
import threading

try:
    import webview
except ImportError:
    webview = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.app import app

def run_flask():
    app.run(host="127.0.0.1", port=5001, debug=False)

if __name__ == "__main__":
    print("🚀 Initializing Plan2Takeoff V2 Desktop Executable...")
    
    # Start Flask server in background thread
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    if webview:
        webview.create_window(
            "Plan2Takeoff V2 — Automated Structural Takeoff Engine",
            "http://127.0.0.1:5001",
            width=1280,
            height=850,
            resizable=True
        )
        webview.start()
    else:
        print("PyWebView not installed. Web application running on http://127.0.0.1:5001")
        import webbrowser
        webbrowser.open("http://127.0.0.1:5001")
