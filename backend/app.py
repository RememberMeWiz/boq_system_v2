"""
Plan2Takeoff V2 — Core API Server
Flask backend wiring the 13-trade fajardo.py engine, rebar optimizer,
PDF parser, manifest, agent-sync, and export routes.
"""

import os
import sys
import json
import csv
import io
from flask import Flask, request, jsonify, send_from_directory, render_template_string, send_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Engine imports (function-based V2 engine)
from engine.fajardo import (
    run_full_takeoff,
    calculate_section_2_earthworks,
    calculate_section_3_concrete_and_formworks,
    calculate_section_4_masonry_works,
    calculate_section_5_metals_and_rebar,
    calculate_section_6_roofing_and_ceiling,
    calculate_section_7_doors_and_windows,
    calculate_section_8_tile_and_flooring,
    calculate_section_9_painting_works,
    calculate_section_10_plumbing_works,
    calculate_section_11_electrical_works,
    calculate_section_12_sanitary_mechanical,
    calculate_section_13_special_works,
    DPWH_RATES,
    rebar_unit_weight_kg_per_m,
)
from engine.rebar_optimizer import RebarStockOptimizer, RebarCutDemand
from engine.pdf_dxf_parser import DrawingParserV2
from api.manifest import generate_project_manifest
from api.agent_sync import process_agent_sync_payload, AUTH_SYNC_TOKEN

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")

app = Flask(__name__, static_folder=FRONTEND_DIST_DIR, static_url_path="")

# CORS for Vite dev server
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Agent-Sync-Token"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/api/v1/<path:p>", methods=["OPTIONS"])
def options_handler(p):
    return "", 204


# --------------------------------------------------------------------
# Static file serving for Web AIs
# --------------------------------------------------------------------

@app.route("/<filename>.md")
def serve_md_files(filename):
    fp = os.path.join(BASE_DIR, f"{filename}.md")
    if os.path.exists(fp):
        return send_from_directory(BASE_DIR, f"{filename}.md", mimetype="text/plain; charset=utf-8")
    return jsonify({"error": "Not found"}), 404

@app.route("/outputs/<path:path>")
def serve_outputs(path):
    d = os.path.join(BASE_DIR, "outputs")
    if os.path.exists(os.path.join(d, path)):
        return send_from_directory(d, path, mimetype="text/plain; charset=utf-8")
    return jsonify({"error": "Not found"}), 404

@app.route("/schema/<path:path>")
def serve_schema(path):
    d = os.path.join(BASE_DIR, "schema")
    if os.path.exists(os.path.join(d, path)):
        return send_from_directory(d, path, mimetype="text/plain; charset=utf-8")
    return jsonify({"error": "Not found"}), 404

@app.route("/backend/<path:path>")
def serve_backend_code(path):
    d = os.path.join(BASE_DIR, "backend")
    if os.path.exists(os.path.join(d, path)):
        return send_from_directory(d, path, mimetype="text/plain; charset=utf-8")
    return jsonify({"error": "Not found"}), 404


# --------------------------------------------------------------------
# Health & Manifest
# --------------------------------------------------------------------

@app.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({"status": "online", "system": "Plan2Takeoff V2 Engine", "engine": "fajardo.py v2.0"})

@app.route("/api/v1/manifest", methods=["GET"])
def get_manifest():
    return jsonify(generate_project_manifest(BASE_DIR))

@app.route("/api/v1/agent-sync", methods=["POST"])
def agent_sync():
    token = request.headers.get("X-Agent-Sync-Token", "")
    payload = request.get_json(force=True, silent=True) or {}
    res = process_agent_sync_payload(payload, token)
    return jsonify(res), (200 if res["status"] == "success" else 400)


# --------------------------------------------------------------------
# DPWH CMPD Rates endpoint
# --------------------------------------------------------------------

@app.route("/api/v1/cmpd-rates", methods=["GET"])
def get_cmpd_rates():
    """Returns the full DPWH_RATES table as JSON for the frontend."""
    rates_json = {
        key: {"material": m, "labor": l, "equipment": e}
        for key, (m, l, e) in DPWH_RATES.items()
    }
    return jsonify({"status": "success", "rates": rates_json})


# --------------------------------------------------------------------
# Drawing Takeoff — POST /api/v1/process-drawing
# --------------------------------------------------------------------

# Sample structural drawing elements (used when no file is uploaded)
SAMPLE_PROJECT_INPUTS = {
    2: {
        "footing_specs": [
            {"length_m": 1.50, "width_m": 1.50, "depth_m": 0.40, "count": 4},
            {"length_m": 2.00, "width_m": 2.00, "depth_m": 0.45, "count": 2},
        ],
        "slab_area": 120.0,
        "slab_t": 0.10,
    },
    3: {
        "elements": [
            {"type": "footing", "class": "A", "count": 4, "length_m": 1.50, "width_m": 1.50, "height_m": 0.40},
            {"type": "footing", "class": "A", "count": 2, "length_m": 2.00, "width_m": 2.00, "height_m": 0.45},
            {"type": "column", "class": "A", "count": 6, "width_m": 0.30, "depth_m": 0.30, "clear_height_m": 3.20},
            {"type": "beam",   "class": "A", "count": 4, "width_m": 0.25, "depth_m": 0.40, "clear_span_m": 4.50},
            {"type": "slab",   "class": "B", "count": 1, "area_m2": 120.0, "thickness_m": 0.10},
        ]
    },
    4: {
        "wall_elements": [
            {"length_m": 14.0, "height_m": 3.20, "thickness_mm": 150,
             "openings": [{"width_m": 1.2, "height_m": 2.1}, {"width_m": 0.9, "height_m": 2.1}],
             "plaster_faces": 2},
            {"length_m": 8.0,  "height_m": 3.20, "thickness_mm": 150,
             "openings": [{"width_m": 1.5, "height_m": 1.2}],
             "plaster_faces": 2},
        ]
    },
    5: {
        "rebar_elements": [
            {"member": "footing_mat",  "diameter_mm": 16, "count": 40, "member_length_m": 1.50},
            {"member": "footing_mat",  "diameter_mm": 16, "count": 40, "member_length_m": 1.50},
            {"member": "footing_mat",  "diameter_mm": 16, "count": 24, "member_length_m": 2.00},
            {"member": "footing_mat",  "diameter_mm": 16, "count": 24, "member_length_m": 2.00},
            {"member": "column_main",  "diameter_mm": 20, "count": 48, "story_height_m": 3.20, "dowel_length_m": 0.40},
            {"member": "beam_stirrup", "diameter_mm": 10, "count": 52, "beam_width_m": 0.25, "beam_depth_m": 0.40},
            {"member": "beam_stirrup", "diameter_mm": 10, "count": 52, "beam_width_m": 0.25, "beam_depth_m": 0.40},
            {"member": "generic",      "diameter_mm": 16, "count": 8,  "length_m": 5.20},
        ],
        "structural_steel_kg": 0.0,
    },
    6: {"roof_plan_area": 140.0, "pitch_deg": 18.0, "ceiling_area": 130.0},
    7: {
        "windows_sqm": 14.4,
        "doors": [
            {"type": "panel", "count": 2, "jamb_lumber_bdft_each": 8.0},
            {"type": "flush", "count": 2, "jamb_lumber_bdft_each": 6.0},
        ],
    },
    8: {"floor_area": 110.0, "wall_area": 38.0, "is_diagonal": False},
    9: {"masonry_area": 210.0, "ceiling_area": 130.0, "metal_area": 12.0, "is_rough_chb": False},
    10: {"sanitary_run_m": 32.0, "water_run_m": 28.0, "fixtures_count": 5},
    11: {"outlets_count": 20, "homerun_m": 55.0},
    12: {"room_area_m2": 65.0, "pipe_run_m": 12.0},
    13: {"handrail_m": 10.0, "acp_m2": 0.0, "waterproofing_m2": 35.0},
}

# BOQ item code prefix map per section
SECTION_CODES = {
    1: "GR", 2: "EW", 3: "CON", 4: "MW", 5: "REB",
    6: "RF", 7: "DW", 8: "TF", 9: "PW", 10: "PL",
    11: "EL", 12: "MC", 13: "SW",
}

SECTION_NAMES = {
    1: "General Requirements",    2: "Earthworks",
    3: "Concrete Works",          4: "Masonry Works",
    5: "Steel Reinforcement",     6: "Roofing & Ceiling",
    7: "Doors & Windows",         8: "Tile & Flooring",
    9: "Painting Works",         10: "Plumbing Works",
    11: "Electrical Works",      12: "Sanitary/Mechanical",
    13: "Special Works",
}


def _takeoff_to_boq_rows(takeoff_result: dict) -> list:
    """Converts run_full_takeoff() output into flat BOQ row dicts for the frontend."""
    rows = []
    sections = takeoff_result.get("sections", {})

    for sec_num, sec_data in sorted(sections.items()):
        prefix = SECTION_CODES.get(sec_num, f"S{sec_num}")
        trade  = SECTION_NAMES.get(sec_num, f"Section {sec_num}")
        cost   = sec_data.get("cost", {})
        qtys   = sec_data.get("quantities", {})
        mats   = sec_data.get("materials", {})

        # Build meaningful line items from quantities dict
        item_idx = 1
        for qty_key, qty_val in qtys.items():
            if qty_key in ("volume_by_class_m3", "rebar_weight_by_diameter_kg", "basis_direct_cost", "door_counts"):
                continue
            if not isinstance(qty_val, (int, float)) or qty_val == 0:
                continue

            # Derive unit from key suffix
            unit = "lot"
            if qty_key.endswith("_m3"):     unit = "cu.m."
            elif qty_key.endswith("_m2"):   unit = "sq.m."
            elif qty_key.endswith("_kg"):   unit = "kg"
            elif qty_key.endswith("_m"):    unit = "lin.m"
            elif qty_key.endswith("_l"):    unit = "ltr"
            elif qty_key.endswith("_pcs"):  unit = "pc"
            elif qty_key.endswith("count"): unit = "unit"

            desc = qty_key.replace("_", " ").replace("m3", "").replace("m2", "").replace("kg","").strip().title()

            # Proportional cost per qty unit (rough split)
            total_amt = cost.get("total", 0)
            total_qty_sum = sum(v for v in qtys.values() if isinstance(v, (int, float)) and v > 0)
            unit_total = (total_amt / total_qty_sum) if total_qty_sum > 0 else 0
            mat_r  = (cost.get("material", 0) / total_qty_sum) if total_qty_sum > 0 else 0
            lab_r  = (cost.get("labor", 0) / total_qty_sum)    if total_qty_sum > 0 else 0
            eqp_r  = (cost.get("equipment", 0) / total_qty_sum) if total_qty_sum > 0 else 0

            rows.append({
                "item_code":   f"{prefix}-{sec_num}.{item_idx}",
                "section_id":  str(sec_num),
                "division":    f"Section {['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII'][sec_num-1]} — {trade}",
                "trade":       trade,
                "description": desc,
                "quantity":    round(qty_val, 4),
                "unit":        unit,
                "material_unit_cost":   round(mat_r, 4),
                "labor_unit_cost":      round(lab_r, 4),
                "equipment_unit_cost":  round(eqp_r, 4),
                "total_unit_cost":      round(unit_total, 4),
                "total_amount":         round(qty_val * unit_total, 2),
                "backup_qty":           round(qty_val * 0.97, 4),  # engineer's estimate ≈ 97% of computed
                "status": "Confirmed",
            })
            item_idx += 1

    return rows


def _sample_elements_json():
    """Returns mock structural element bounding boxes for blueprint viewer."""
    return [
        {"element_id": "F-1a", "element_type": "footing", "label": "F-1", "location": "Grid A-1",
         "length": 1.5, "width": 1.5, "height": 0.40, "count": 1, "bounding_box": [40, 40, 90, 80]},
        {"element_id": "F-1b", "element_type": "footing", "label": "F-1", "location": "Grid B-1",
         "length": 1.5, "width": 1.5, "height": 0.40, "count": 1, "bounding_box": [130, 40, 180, 80]},
        {"element_id": "F-1c", "element_type": "footing", "label": "F-1", "location": "Grid C-1",
         "length": 1.5, "width": 1.5, "height": 0.40, "count": 1, "bounding_box": [220, 40, 270, 80]},
        {"element_id": "F-2a", "element_type": "footing", "label": "F-2", "location": "Grid A-2",
         "length": 2.0, "width": 2.0, "height": 0.45, "count": 1, "bounding_box": [310, 30, 370, 90]},
        {"element_id": "C-1a", "element_type": "column", "label": "C-1", "location": "Grid A-1",
         "length": 0.30, "width": 0.30, "height": 3.2, "count": 1, "bounding_box": [55, 95, 80, 120]},
        {"element_id": "C-1b", "element_type": "column", "label": "C-1", "location": "Grid B-1",
         "length": 0.30, "width": 0.30, "height": 3.2, "count": 1, "bounding_box": [145, 95, 170, 120]},
        {"element_id": "C-1c", "element_type": "column", "label": "C-1", "location": "Grid C-1",
         "length": 0.30, "width": 0.30, "height": 3.2, "count": 1, "bounding_box": [235, 95, 260, 120]},
        {"element_id": "2B-1", "element_type": "beam", "label": "2B-1", "location": "Grid A-1 to B-1",
         "length": 4.5, "width": 0.25, "height": 0.40, "count": 1, "bounding_box": [80, 100, 145, 115]},
        {"element_id": "2B-2", "element_type": "beam", "label": "2B-2", "location": "Grid B-1 to C-1",
         "length": 4.5, "width": 0.25, "height": 0.40, "count": 1, "bounding_box": [170, 100, 235, 115]},
        {"element_id": "SL-1", "element_type": "slab", "label": "SL-1", "location": "Ground Floor",
         "length": 14.0, "width": 8.0, "height": 0.10, "count": 1, "bounding_box": [40, 130, 280, 210]},
        {"element_id": "W-1a", "element_type": "chb_wall", "label": "W-1", "location": "N Exterior",
         "length": 14.0, "width": 0.15, "height": 3.2, "count": 1, "bounding_box": [40, 215, 280, 230]},
        {"element_id": "W-1b", "element_type": "chb_wall", "label": "W-2", "location": "S Exterior",
         "length": 8.0, "width": 0.15, "height": 3.2, "count": 1, "bounding_box": [40, 215, 40, 130]},
    ]


@app.route("/api/v1/process-drawing", methods=["POST"])
def process_drawing():
    """
    Runs the full 13-trade Fajardo takeoff on sample project inputs.
    Accepts optional multipart file upload (ignored for now — uses sample inputs).
    """
    file = request.files.get("file")
    drawing_name = file.filename if file else "sample_structural_plan.pdf"

    # Parse drawing (graceful degradation when PyMuPDF not installed)
    parser = DrawingParserV2()
    sample_pdf = os.path.join(BASE_DIR, "sample_structural_plan.pdf")
    parse_res = parser.parse_pdf(sample_pdf)

    # Run full 13-trade engine
    takeoff = run_full_takeoff(SAMPLE_PROJECT_INPUTS)
    boq_rows = _takeoff_to_boq_rows(takeoff)

    return jsonify({
        "status": "success",
        "drawing": {
            "filename": drawing_name,
            "width": parse_res.width,
            "height": parse_res.height,
        },
        "elements": _sample_elements_json(),
        "boq": boq_rows,
        "summary": {
            "sections_2_to_13_subtotal": takeoff["sections_2_to_13_subtotal"],
            "grand_total_direct_cost":   takeoff["grand_total_direct_cost"],
        },
    })


# --------------------------------------------------------------------
# Rebar Optimizer — POST /api/v1/optimize-rebar
# --------------------------------------------------------------------

@app.route("/api/v1/optimize-rebar", methods=["POST"])
def optimize_rebar():
    """1D bin-packing rebar optimization across diameters 10, 16, 20mm."""
    payload = request.get_json(force=True, silent=True) or {}
    demands_raw = payload.get("demands", None)

    if demands_raw:
        # Accept custom demands from frontend
        by_diameter: dict[int, list] = {}
        for d in demands_raw:
            dia = int(d["diameter_mm"])
            by_diameter.setdefault(dia, []).append(
                RebarCutDemand(dia, float(d["length_m"]), int(d["quantity"]), d.get("ref", ""))
            )
    else:
        # Default sample cut list matching the sample project inputs
        by_diameter = {
            20: [
                RebarCutDemand(20, 4.08, 48, "C-1 Main Bars (3.2m + 40db splice)"),
                RebarCutDemand(20, 5.60, 8,  "Beam Main Bars"),
            ],
            16: [
                RebarCutDemand(16, 1.878, 80, "F-1/F-2 Mat Rebar (1.5m footing)"),
                RebarCutDemand(16, 5.20,  8,  "Generic 16mm bars"),
            ],
            10: [
                RebarCutDemand(10, 1.42, 104, "Beam Stirrups"),
            ],
        }

    opt = RebarStockOptimizer(stock_lengths=[12.0, 9.0, 6.0])
    results = []
    for dia, demands in sorted(by_diameter.items()):
        r = opt.optimize_diameter(dia, demands)
        results.append({
            "diameter_mm":          r.diameter_mm,
            "total_required_kg":    r.total_required_weight_kg,
            "total_purchased_kg":   r.total_purchased_weight_kg,
            "scrap_kg":             r.total_scrap_weight_kg,
            "scrap_percentage":     r.scrap_percentage,
            "purchased_bars":       {str(k): v for k, v in r.purchased_bars.items()},
            "pattern_count":        len(r.patterns),
        })

    return jsonify({"status": "success", "optimizations": results})


# --------------------------------------------------------------------
# Export endpoints
# --------------------------------------------------------------------

@app.route("/api/v1/export-csv", methods=["GET", "POST"])
def export_csv():
    """Exports the BOQ as a downloadable CSV file."""
    takeoff = run_full_takeoff(SAMPLE_PROJECT_INPUTS)
    rows = _takeoff_to_boq_rows(takeoff)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=[
        "item_code", "trade", "description", "quantity", "unit",
        "material_unit_cost", "labor_unit_cost", "equipment_unit_cost",
        "total_unit_cost", "total_amount", "status"
    ])
    writer.writeheader()
    for r in rows:
        writer.writerow({k: r.get(k, "") for k in writer.fieldnames})

    buf.seek(0)
    return send_file(
        io.BytesIO(buf.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="Plan2Takeoff_V2_BOQ.csv",
    )


@app.route("/api/v1/export-json", methods=["GET", "POST"])
def export_json_full():
    """Exports the complete takeoff result as a JSON download."""
    takeoff = run_full_takeoff(SAMPLE_PROJECT_INPUTS)
    buf = io.BytesIO(json.dumps(takeoff, indent=2).encode("utf-8"))
    return send_file(
        buf,
        mimetype="application/json",
        as_attachment=True,
        download_name="Plan2Takeoff_V2_Takeoff.json",
    )


# --------------------------------------------------------------------
# SPA fallback (serves Vite production build or plain fallback)
# --------------------------------------------------------------------

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    full = os.path.join(FRONTEND_DIST_DIR, path)
    if path and os.path.exists(full):
        return send_from_directory(FRONTEND_DIST_DIR, path)
    idx = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.exists(idx):
        return send_from_directory(FRONTEND_DIST_DIR, "index.html")
    # Minimal JSON status page when no frontend dist built yet
    return jsonify({
        "system": "Plan2Takeoff V2 Engine",
        "status": "online",
        "hint": "Run `npm run build` in frontend/ or start Vite dev server on port 5173",
        "api_routes": [
            "GET  /api/v1/health",
            "GET  /api/v1/manifest",
            "GET  /api/v1/cmpd-rates",
            "POST /api/v1/process-drawing",
            "POST /api/v1/optimize-rebar",
            "GET  /api/v1/export-csv",
            "GET  /api/v1/export-json",
            "POST /api/v1/agent-sync",
        ]
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[Plan2Takeoff V2] Backend API running on http://127.0.0.1:{port}")
    print(f"[Plan2Takeoff V2] API routes: /api/v1/health, /api/v1/process-drawing, /api/v1/optimize-rebar")
    print(f"[Plan2Takeoff V2] Export: /api/v1/export-csv, /api/v1/export-json")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
