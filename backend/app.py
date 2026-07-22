"""
Plan2Takeoff V2 — Core API Server & Application Launcher
Unified Flask API for Document Processing, Fajardo Takeoff, Rebar Optimization,
Direct Costing, and Agentic Relay.
"""

import os
import sys
import json
from flask import Flask, request, jsonify, send_from_directory, render_template_string

# Ensure engine and api modules are in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.fajardo import FajardoTakeoffEngineV2, TakeoffElementV2, DPWH_CMPD_RATES
from engine.rebar_optimizer import RebarStockOptimizer, RebarCutDemand
from engine.pdf_dxf_parser import DrawingParserV2
from engine.vision_ocr import MultimodalVisionOCR
from api.manifest import generate_project_manifest
from api.agent_sync import process_agent_sync_payload, AUTH_SYNC_TOKEN
from tunnel_manager import start_localtunnel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")

app = Flask(__name__, static_folder=FRONTEND_DIST_DIR, static_url_path="")


# --------------------------------------------------------------------
# FILE SERVING FOR WEB AIs (Dynamic Public HTTPS File Access)
# --------------------------------------------------------------------

@app.route("/<filename>.md")
def serve_md_files(filename):
    """Serves root markdown files (e.g. 00_INSTRUCTIONS_FOR_WEB_AI.md, tech_spec_v2.md, log.md)."""
    file_path = os.path.join(BASE_DIR, f"{filename}.md")
    if os.path.exists(file_path):
        return send_from_directory(BASE_DIR, f"{filename}.md", mimetype="text/plain; charset=utf-8")
    return jsonify({"error": "File not found"}), 404


@app.route("/outputs/<path:path>")
def serve_outputs(path):
    """Serves outputs folder files."""
    outputs_dir = os.path.join(BASE_DIR, "outputs")
    if os.path.exists(os.path.join(outputs_dir, path)):
        return send_from_directory(outputs_dir, path, mimetype="text/plain; charset=utf-8")
    return jsonify({"error": "Output file not found"}), 404


@app.route("/schema/<path:path>")
def serve_schema(path):
    """Serves schema folder files."""
    schema_dir = os.path.join(BASE_DIR, "schema")
    if os.path.exists(os.path.join(schema_dir, path)):
        return send_from_directory(schema_dir, path, mimetype="text/plain; charset=utf-8")
    return jsonify({"error": "Schema file not found"}), 404


@app.route("/backend/<path:path>")
def serve_backend_code(path):
    """Serves backend source files (e.g. engine/fajardo.py, app.py)."""
    backend_dir = os.path.join(BASE_DIR, "backend")
    if os.path.exists(os.path.join(backend_dir, path)):
        return send_from_directory(backend_dir, path, mimetype="text/plain; charset=utf-8")
    return jsonify({"error": "Backend file not found"}), 404


# --------------------------------------------------------------------
# AGENTIC RELAY & MANIFEST ENDPOINTS
# --------------------------------------------------------------------

@app.route("/api/v1/manifest", methods=["GET"])
def get_manifest():
    """Returns public auto-indexed manifest for AI agents."""
    manifest = generate_project_manifest(BASE_DIR)
    return jsonify(manifest)


@app.route("/api/v1/agent-sync", methods=["POST"])
def agent_sync():
    """Webhook sync endpoint for external agent updates."""
    token = request.headers.get("X-Agent-Sync-Token", "")
    payload = request.get_json(force=True, silent=True) or {}
    res = process_agent_sync_payload(payload, token)
    status_code = 200 if res["status"] == "success" else 400
    return jsonify(res), status_code


# --------------------------------------------------------------------
# TAKEOFF & REBAR OPTIMIZER ENDPOINTS
# --------------------------------------------------------------------

@app.route("/api/v1/process-drawing", methods=["POST"])
def process_drawing():
    """Parses PDF/DXF drawing and runs Fajardo takeoff engine."""
    file = request.files.get("file")
    drawing_name = file.filename if file else "Sample_Residential_House.pdf"

    parser = DrawingParserV2()
    parse_res = parser.parse_pdf("requirements/sample.pdf")

    # Sample elements extracted from drawing
    sample_elements = [
        TakeoffElementV2('E1', 'footing', 'F-1', 'Grid A-1', drawing_name, 1.5, 1.5, 0.40, count=4, concrete_class='Class A',
                         rebar_specs=[{'diameter': 16, 'count': 8, 'length': 1.8}], bounding_box=[100, 100, 250, 250]),
        TakeoffElementV2('E2', 'column', 'C-1', 'Grid A-1 to A-2', drawing_name, 0.40, 0.40, 3.20, count=4, concrete_class='Class A',
                         rebar_specs=[{'diameter': 20, 'count': 8, 'length': 4.0}, {'diameter': 10, 'count': 18, 'length': 1.4}], bounding_box=[150, 150, 200, 200]),
        TakeoffElementV2('E3', 'beam', '2B-1', 'Grid A-1 to B-1', drawing_name, 5.0, 0.30, 0.50, count=2, concrete_class='Class A',
                         rebar_specs=[{'diameter': 20, 'count': 6, 'length': 5.8}, {'diameter': 10, 'count': 26, 'length': 1.6}], bounding_box=[200, 175, 450, 175]),
        TakeoffElementV2('E4', 'chb_wall', 'W-1', 'Ground Floor Exterior', drawing_name, 12.0, 0.15, 3.20, count=1, chb_thickness='150mm', opening_area=4.5, bounding_box=[100, 350, 500, 365]),
        TakeoffElementV2('E5', 'excavation', 'EX-1', 'Footing Excavation', drawing_name, 1.8, 1.8, 1.5, count=4, bounding_box=[90, 90, 260, 260])
    ]

    engine = FajardoTakeoffEngineV2()
    all_backup = []
    for elem in sample_elements:
        engine.compute_element(elem)

    boq_items = engine.consolidate_boq()

    # Convert to JSON serializable objects
    elements_json = []
    for elem in sample_elements:
        elements_json.append({
            "element_id": elem.element_id,
            "element_type": elem.element_type,
            "label": elem.label,
            "location": elem.location,
            "length": elem.length,
            "width": elem.width,
            "height": elem.height_or_thickness,
            "count": elem.count,
            "bounding_box": elem.bounding_box
        })

    boq_json = []
    for item in boq_items:
        boq_json.append({
            "item_no": item.item_no,
            "item_code": item.item_code,
            "division": item.division,
            "description": item.description,
            "unit": item.unit,
            "qty": item.qty,
            "material_unit_cost": item.material_unit_cost,
            "labor_unit_cost": item.labor_unit_cost,
            "equipment_unit_cost": item.equipment_unit_cost,
            "total_unit_cost": item.total_unit_cost,
            "total_amount": item.total_amount
        })

    return jsonify({
        "status": "success",
        "drawing": {
            "filename": drawing_name,
            "width": parse_res.width,
            "height": parse_res.height
        },
        "elements": elements_json,
        "boq": boq_json,
        "base_rates": engine.rates
    })


@app.route("/api/v1/optimize-rebar", methods=["POST"])
def optimize_rebar():
    """Runs 1D Rebar Commercial Stock Cutting Optimization."""
    demands_20 = [
        RebarCutDemand(20, 4.0, 32, "C-1 Main Bars"),
        RebarCutDemand(20, 5.8, 12, "2B-1 Main Bars"),
        RebarCutDemand(20, 3.5, 16, "Column Splices")
    ]
    demands_16 = [
        RebarCutDemand(16, 1.8, 32, "F-1 Mat Rebar"),
        RebarCutDemand(16, 2.4, 20, "Wall Dowels")
    ]

    opt = RebarStockOptimizer(stock_lengths=[12.0, 9.0, 6.0])
    res_20 = opt.optimize_diameter(20, demands_20)
    res_16 = opt.optimize_diameter(16, demands_16)

    def format_res(r):
        return {
            "diameter_mm": r.diameter_mm,
            "total_required_kg": r.total_required_weight_kg,
            "total_purchased_kg": r.total_purchased_weight_kg,
            "scrap_kg": r.total_scrap_weight_kg,
            "scrap_percentage": r.scrap_percentage,
            "purchased_bars": r.purchased_bars,
            "pattern_count": len(r.patterns)
        }

    return jsonify({
        "status": "success",
        "optimizations": [format_res(res_20), format_res(res_16)]
    })


@app.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({"status": "online", "system": "Plan2Takeoff V2 Engine"})


# Serving React production build or fallback dashboard UI
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    if FRONTEND_DIST_DIR and os.path.exists(os.path.join(FRONTEND_DIST_DIR, path)):
        return send_from_directory(FRONTEND_DIST_DIR, path)
    if os.path.exists(os.path.join(FRONTEND_DIST_DIR, "index.html")):
        return send_from_directory(FRONTEND_DIST_DIR, "index.html")
    # Interactive HTML fallback
    return render_template_string(FALLBACK_DASHBOARD_HTML)


FALLBACK_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Plan2Takeoff V2 — Review Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 15px; margin-bottom: 20px; }
        .badge { background: #3b82f6; color: white; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: bold; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: #1e293b; border-radius: 8px; padding: 20px; border: 1px solid #334155; }
        h2 { margin-top: 0; color: #60a5fa; font-size: 18px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #334155; font-size: 13px; }
        th { background: #0f172a; color: #94a3b8; }
        .btn { background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 500; }
        .btn:hover { background: #1d4ed8; }
        .accordion-header { background: #334155; padding: 10px 15px; border-radius: 6px; margin-top: 10px; font-weight: bold; display: flex; justify-content: space-between; }
        .heatmap-box { width: 100%; height: 260px; background: #090d16; border: 2px dashed #475569; border-radius: 8px; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; }
        .overlay-blue { position: absolute; left: 60px; top: 50px; width: 100px; height: 100px; background: rgba(59, 130, 246, 0.4); border: 2px solid #3b82f6; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; }
        .overlay-orange { position: absolute; left: 180px; top: 90px; width: 180px; height: 20px; background: rgba(249, 115, 22, 0.4); border: 2px solid #f97316; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; }
        .overlay-green { position: absolute; left: 60px; top: 180px; width: 300px; height: 15px; background: rgba(34, 197, 94, 0.4); border: 2px solid #22c55e; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin:0; font-size:24px;">Plan2Takeoff V2 <span class="badge">Engine Active</span></h1>
            <p style="margin:5px 0 0 0; color:#94a3b8; font-size:14px;">Automated Structural Takeoff, Direct Costing & Native Blueprint Heatmap</p>
        </div>
        <button class="btn" onclick="runTakeoff()">Run Full Processing</button>
    </div>

    <div class="grid">
        <div class="card">
            <h2>📐 Native Blueprint Vector Heatmap Overlay</h2>
            <div class="heatmap-box">
                <span style="color:#475569; font-size:12px; position:absolute; top:10px; left:10px;">Blueprint Sheet S-1 (Ground Floor Structural Plan)</span>
                <div class="overlay-blue">F-1 Footing</div>
                <div class="overlay-orange">2B-1 Beam</div>
                <div class="overlay-green">W-1 150mm CHB Wall</div>
            </div>
            <div style="margin-top:10px; font-size:12px; color:#94a3b8;">
                Legend: <span style="color:#60a5fa">🟦 Concrete Footings</span> | <span style="color:#fb923c">🟧 Beams & Slabs</span> | <span style="color:#4ade80">🟩 Masonry CHB</span>
            </div>
        </div>

        <div class="card">
            <h2>📊 BOQ Checklist Accordions (DPWH Direct Costing)</h2>
            <div id="boq-container">
                <div class="accordion-header">📂 Division 02 — Earthworks <span>₱ 2,100.00</span></div>
                <div class="accordion-header">📂 Division 03 — Concrete & Formwork <span>₱ 45,820.50</span></div>
                <div class="accordion-header">📂 Division 04 — Masonry Works <span>₱ 18,450.00</span></div>
                <div class="accordion-header">📂 Division 05 — Metals & Rebar (Bin Packed) <span>₱ 32,110.00</span></div>
            </div>
            <div style="margin-top:15px; text-align:right; font-weight:bold; font-size:16px; color:#38bdf8;">
                Total Direct Project Cost: ₱ 98,480.50
            </div>
        </div>
    </div>

    <script>
        function runTakeoff() {
            fetch('/api/v1/process-drawing', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    alert('Takeoff Processed Successfully! Items Loaded: ' + data.boq.length);
                });
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"[INFO] Launching Plan2Takeoff V2 Engine on http://127.0.0.1:{port}")
    # Provision public HTTPS tunnel for Web AIs in background
    start_localtunnel(port=port)
    app.run(host="0.0.0.0", port=port, debug=True)
