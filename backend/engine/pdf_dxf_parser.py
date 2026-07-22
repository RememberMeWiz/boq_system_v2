"""
Plan2Takeoff V2 — PDF & DXF Vector Path Extractor
Parses structural annotation text from PDFs to extract real project dimensions,
then falls back to sample inputs when no parseable data is found.
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import ezdxf
except ImportError:
    ezdxf = None


@dataclass
class ExtractedVectorEntity:
    entity_type: str          # 'polyline', 'text', 'block', 'path'
    layer: str
    label: str
    bounding_box: List[float] # [x1, y1, x2, y2]
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DrawingParseResult:
    filename: str
    width: float
    height: float
    entities: List[ExtractedVectorEntity]
    schedules: List[Dict[str, Any]] = field(default_factory=list)
    project_inputs: Optional[Dict] = None   # structured inputs for fajardo.py


# ---------------------------------------------------------------------------
# Regex patterns for structural annotation parsing
# ---------------------------------------------------------------------------

# Footing: "F-1 (1.5x1.5m)", "F-2 (2.00x2.00m)", "FOOTING 2.0x2.0x0.45"
_RE_FOOTING = re.compile(
    r'(?:F-\d+|FOOTING)[^\d]*(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)'
    r'(?:\s*[xX×]\s*(\d+\.?\d*))?',
    re.IGNORECASE
)

# Column: "C-1 (300x300)", "COL 0.30x0.30", "300x300 col"
_RE_COLUMN = re.compile(
    r'(?:C-\d+|COL(?:UMN)?)[^\d]*(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)',
    re.IGNORECASE
)

# Beam: "2B-1 (250x400)", "BEAM 300x500", "B-1 0.25x0.40"
_RE_BEAM = re.compile(
    r'(?:\d?B-\d+|BEAM)[^\d]*(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)',
    re.IGNORECASE
)

# Slab: "SL-1 (120 sq.m.)", "SLAB 15x8", "SUSPENDED SLAB t=100mm"
_RE_SLAB_AREA = re.compile(
    r'(?:SL-\d+|SLAB)[^\d]*(\d+\.?\d*)\s*(?:sq\.?m\.?|m2)',
    re.IGNORECASE
)
_RE_SLAB_DIM = re.compile(
    r'(?:SL-\d+|SLAB)[^\d]*(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)',
    re.IGNORECASE
)

# CHB wall: "W-1 (150mm CHB)", "CHB WALL L=14.0m H=3.2m"
_RE_WALL = re.compile(
    r'(?:W-\d+|CHB\s*WALL)[^\d]*(?:L\s*=\s*)?(\d+\.?\d*)\s*m?'
    r'[^\d]*(?:H\s*=\s*)?(\d+\.?\d*)',
    re.IGNORECASE
)

# Rebar: "Ø16mm - 8 pcs @ 200mm o.c.", "#5 - 6 pcs", "16dia, 12 bars, L=1.8m"
_RE_REBAR = re.compile(
    r'[ØO∅#]?\s*(\d+)\s*(?:mm|dia|diam)?[^a-z\d]*(\d+)\s*(?:pcs?|bars?|nos?)'
    r'(?:[^a-z\d]*(?:L=|@|,\s*)?(\d+\.?\d*))?',
    re.IGNORECASE
)

# Story height: "3.20m", "H=3.20", "height 3.2m"
_RE_HEIGHT = re.compile(r'(?:H=|height\s*)(\d+\.?\d*)\s*m', re.IGNORECASE)

# Roof area: "ROOF PLAN AREA = 140 sq.m.", "140m2 ROOF"
_RE_ROOF = re.compile(r'(?:ROOF[^\d]*)(\d+\.?\d*)\s*(?:sq\.?m\.?|m2)', re.IGNORECASE)


def _to_m(val: float, original_text: str = "") -> float:
    """Convert mm to m if value looks like mm (>= 100 and text doesn't say 'm')."""
    if val >= 100 and 'm' not in original_text.lower():
        return val / 1000.0
    return val


class DrawingAnnotationParser:
    """Extracts structured project_inputs from raw annotation text blocks."""

    def parse(self, text_blocks: List[str]) -> Dict:
        footings, columns, beams = [], [], []
        slab_area = 0.0
        walls = []
        rebar_elements = []
        roof_area = 0.0
        story_height = 3.20  # default

        all_text = "\n".join(text_blocks)

        # Story height
        hm = _RE_HEIGHT.search(all_text)
        if hm:
            story_height = float(hm.group(1))

        # Footings
        for m in _RE_FOOTING.finditer(all_text):
            l = _to_m(float(m.group(1)))
            w = _to_m(float(m.group(2)))
            h = _to_m(float(m.group(3))) if m.group(3) else 0.40
            footings.append({"length_m": l, "width_m": w, "depth_m": h, "count": 1,
                              "type": "footing", "class": "A"})

        # Columns
        for m in _RE_COLUMN.finditer(all_text):
            cw = _to_m(float(m.group(1)))
            cd = _to_m(float(m.group(2)))
            columns.append({"type": "column", "class": "A", "count": 1,
                             "width_m": cw, "depth_m": cd, "clear_height_m": story_height})

        # Beams
        for m in _RE_BEAM.finditer(all_text):
            bw = _to_m(float(m.group(1)))
            bd = _to_m(float(m.group(2)))
            beams.append({"type": "beam", "class": "A", "count": 1,
                           "width_m": bw, "depth_m": bd, "clear_span_m": 4.50})

        # Slab area
        sm = _RE_SLAB_AREA.search(all_text)
        if sm:
            slab_area = float(sm.group(1))
        else:
            sdm = _RE_SLAB_DIM.search(all_text)
            if sdm:
                slab_area = float(sdm.group(1)) * float(sdm.group(2))

        # CHB walls
        for m in _RE_WALL.finditer(all_text):
            wl = float(m.group(1))
            wh = float(m.group(2)) if m.group(2) else story_height
            walls.append({"length_m": wl, "height_m": wh, "thickness_mm": 150,
                           "openings": [], "plaster_faces": 2})

        # Rebar schedule
        for m in _RE_REBAR.finditer(all_text):
            dia = int(m.group(1))
            cnt = int(m.group(2))
            length = float(m.group(3)) if m.group(3) else 1.50
            if dia in (10, 12, 16, 20, 25, 28, 32) and cnt > 0:
                rebar_elements.append({
                    "member": "generic",
                    "diameter_mm": dia,
                    "count": cnt,
                    "length_m": length,
                })

        # Roof
        rm = _RE_ROOF.search(all_text)
        if rm:
            roof_area = float(rm.group(1))

        # Build project_inputs dict (Sections 2–13)
        sec3_elements = []
        for f in footings:
            sec3_elements.append({**f})
        for c in columns:
            sec3_elements.append({**c})
        for b in beams:
            sec3_elements.append({**b})
        if slab_area > 0:
            sec3_elements.append({"type": "slab", "class": "B", "count": 1,
                                   "area_m2": slab_area, "thickness_m": 0.10})

        project_inputs = {}

        if footings:
            # Section 2: Earthworks — derive from footing dims
            total_footing_vol = sum(
                f["length_m"] * f["width_m"] * f["depth_m"] * f.get("count", 1)
                for f in footings
            )
            project_inputs[2] = {
                "footing_specs": footings,
                "slab_area": slab_area or 80.0,
                "slab_t": 0.10,
            }

        if sec3_elements:
            project_inputs[3] = {"elements": sec3_elements}

        if walls:
            project_inputs[4] = {"wall_elements": walls}

        if rebar_elements:
            project_inputs[5] = {"rebar_elements": rebar_elements, "structural_steel_kg": 0.0}

        if roof_area > 0:
            project_inputs[6] = {"roof_plan_area": roof_area, "pitch_deg": 18.0, "ceiling_area": roof_area * 0.9}

        return project_inputs if project_inputs else {}


# ---------------------------------------------------------------------------
# Main parser class
# ---------------------------------------------------------------------------

class DrawingParserV2:
    def __init__(self):
        self._annotation_parser = DrawingAnnotationParser()

    def parse_pdf(self, pdf_path: str) -> DrawingParseResult:
        """Extracts vector paths, text annotations, and structured project inputs from a vector PDF."""
        entities = []
        schedules = []
        text_blocks = []
        doc_width, doc_height = 842.0, 595.0  # A3 default
        project_inputs = {}

        if fitz and os.path.exists(pdf_path):
            doc = fitz.open(pdf_path)
            page = doc[0]
            rect = page.rect
            doc_width, doc_height = rect.width, rect.height

            # Extract text blocks
            for block in page.get_text("blocks"):
                text = block[4].strip()
                if not text:
                    continue
                bbox = [block[0], block[1], block[2], block[3]]
                text_blocks.append(text)

                # Tag structural annotation entities
                if re.search(
                    r'\b(F|C|B|W|S|2B|3B)-\d+\b|\b\d{2,3}[xX×]\d{2,3}\b|'
                    r'\bCHB\b|\bFOOTING\b|\bCOLUMN\b|\bBEAM\b|\bSLAB\b',
                    text, re.IGNORECASE
                ):
                    entities.append(ExtractedVectorEntity(
                        entity_type='text',
                        layer='ANNOTATION',
                        label=text[:60],
                        bounding_box=bbox,
                        properties={'raw_text': text}
                    ))

                # Tag schedule-like rows (rebar tables)
                if re.search(r'[ØO∅#]\s*\d+|dia\s*\d+|\d+\s*(?:pcs|bars|nos)', text, re.IGNORECASE):
                    schedules.append({"text": text, "bbox": bbox})
                    entities.append(ExtractedVectorEntity(
                        entity_type='text',
                        layer='SCHEDULE',
                        label=text[:60],
                        bounding_box=bbox,
                        properties={'raw_text': text}
                    ))

            # Extract vector drawing paths
            for d in page.get_drawings():
                rb = d.get('rect', [0, 0, 0, 0])
                bbox = [rb[0], rb[1], rb[2], rb[3]]
                if (bbox[2] - bbox[0]) > 5 or (bbox[3] - bbox[1]) > 5:
                    entities.append(ExtractedVectorEntity(
                        entity_type='path',
                        layer='GEOMETRY',
                        label='VectorPath',
                        bounding_box=bbox
                    ))

            doc.close()

            # Try to extract structured inputs from text
            project_inputs = self._annotation_parser.parse(text_blocks)

        if not entities:
            entities = self._generate_sample_entities(doc_width, doc_height)

        return DrawingParseResult(
            filename=os.path.basename(pdf_path),
            width=doc_width,
            height=doc_height,
            entities=entities,
            schedules=schedules,
            project_inputs=project_inputs if project_inputs else None,
        )

    def parse_dxf(self, dxf_path: str) -> DrawingParseResult:
        """Parses CAD DXF entities via ezdxf."""
        entities = []
        text_blocks = []
        if ezdxf and os.path.exists(dxf_path):
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
            for e in msp:
                layer = e.dxf.layer if hasattr(e.dxf, 'layer') else '0'
                if e.dxftype() == 'LINE':
                    p1, p2 = e.dxf.start, e.dxf.end
                    bbox = [min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y)]
                    entities.append(ExtractedVectorEntity('polyline', layer, layer, bbox))
                elif e.dxftype() in ('TEXT', 'MTEXT'):
                    text = e.plain_text() if hasattr(e, 'plain_text') else getattr(e.dxf, 'text', '')
                    text_blocks.append(text)
                    pos = getattr(e.dxf, 'insert', (0, 0))
                    bbox = [pos[0], pos[1], pos[0] + 50, pos[1] + 15]
                    entities.append(ExtractedVectorEntity('text', layer, text[:60], bbox))

        if not entities:
            entities = self._generate_sample_entities(800.0, 600.0)

        project_inputs = self._annotation_parser.parse(text_blocks) if text_blocks else {}

        return DrawingParseResult(
            filename=os.path.basename(dxf_path),
            width=800.0, height=600.0,
            entities=entities,
            project_inputs=project_inputs if project_inputs else None,
        )

    def parse_text_blocks(self, text_blocks: List[str]) -> Dict:
        """Public method: parse raw text into project_inputs (for vision OCR pipeline)."""
        return self._annotation_parser.parse(text_blocks)

    def _generate_sample_entities(self, w: float, h: float) -> List[ExtractedVectorEntity]:
        return [
            ExtractedVectorEntity('polyline', 'S-FOOTING', 'F-1 (1.5x1.5m)',  [100, 100, 250, 250]),
            ExtractedVectorEntity('polyline', 'S-FOOTING', 'F-2 (2.0x2.0m)',  [350, 100, 550, 300]),
            ExtractedVectorEntity('polyline', 'S-COLUMN',  'C-1 (300x300)',   [150, 150, 200, 200]),
            ExtractedVectorEntity('polyline', 'S-BEAM',    '2B-1 (250x500)',  [200, 175, 450, 175]),
            ExtractedVectorEntity('polyline', 'S-WALL',    'W-1 (150mm CHB)', [100, 350, 500, 365]),
        ]
