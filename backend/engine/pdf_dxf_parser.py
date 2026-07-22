"""
Plan2Takeoff V2 — PDF & DXF Vector Path Extractor
Parses DWG/DXF (via ezdxf) and Vector PDF drawings (via PyMuPDF/pdfplumber),
extracting structural polylines, annotations, schedule text, and exact bounding boxes
for native blueprint heatmap visualization.
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

try:
    import ezdxf
except ImportError:
    ezdxf = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


@dataclass
class ExtractedVectorEntity:
    entity_type: str  # 'polyline', 'text', 'block', 'path'
    layer: str
    label: str
    bounding_box: List[float]  # [x1, y1, x2, y2]
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DrawingParseResult:
    filename: str
    width: float
    height: float
    entities: List[ExtractedVectorEntity]
    schedules: List[Dict[str, Any]] = field(default_factory=list)


class DrawingParserV2:
    def parse_pdf(self, pdf_path: str) -> DrawingParseResult:
        """Extracts vector paths and text elements from a vector PDF drawing."""
        entities = []
        schedules = []
        doc_width = 842.0  # Standard A3 width default
        doc_height = 595.0

        if fitz and os.path.exists(pdf_path):
            doc = fitz.open(pdf_path)
            page = doc[0]
            rect = page.rect
            doc_width, doc_height = rect.width, rect.height

            # Extract text blocks and structural annotations
            text_instances = page.get_text("blocks")
            for block in text_instances:
                bbox = [block[0], block[1], block[2], block[3]]
                text = block[4].strip()
                if not text:
                    continue

                # Detect beam/column/footing labels (e.g. F-1, C-2, 2B-1, 300x500)
                if re.search(r'\b(F|C|B|W|S|2B|3B)-\d+\b|\b\d{3}x\d{3}\b', text, re.IGNORECASE):
                    entities.append(ExtractedVectorEntity(
                        entity_type='text',
                        layer='ANNOTATION',
                        label=text,
                        bounding_box=bbox,
                        properties={'raw_text': text}
                    ))

            # Extract drawing vector paths
            drawings = page.get_drawings()
            for d in drawings:
                rect_box = d.get('rect', [0, 0, 0, 0])
                bbox = [rect_box[0], rect_box[1], rect_box[2], rect_box[3]]
                # Filter trivial line noise
                if (bbox[2] - bbox[0]) > 5 or (bbox[3] - bbox[1]) > 5:
                    entities.append(ExtractedVectorEntity(
                        entity_type='path',
                        layer='GEOMETRY',
                        label='VectorPath',
                        bounding_box=list(bbox)
                    ))
            doc.close()

        # Fallback sample entities if mock drawing or missing parser
        if not entities:
            entities = self._generate_sample_entities(doc_width, doc_height)

        return DrawingParseResult(
            filename=os.path.basename(pdf_path),
            width=doc_width,
            height=doc_height,
            entities=entities,
            schedules=schedules
        )

    def parse_dxf(self, dxf_path: str) -> DrawingParseResult:
        """Parses CAD DXF drawing entities via ezdxf."""
        entities = []
        if ezdxf and os.path.exists(dxf_path):
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
            for e in msp:
                layer = e.dxf.layer if hasattr(e.dxf, 'layer') else '0'
                if e.dxftype() == 'LINE':
                    p1, p2 = e.dxf.start, e.dxf.end
                    bbox = [min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y)]
                    entities.append(ExtractedVectorEntity(
                        entity_type='polyline',
                        layer=layer,
                        label=layer,
                        bounding_box=bbox
                    ))
                elif e.dxftype() in ['TEXT', 'MTEXT']:
                    text = e.plain_text() if hasattr(e, 'plain_text') else getattr(e.dxf, 'text', '')
                    pos = getattr(e.dxf, 'insert', (0, 0))
                    bbox = [pos[0], pos[1], pos[0] + 50, pos[1] + 15]
                    entities.append(ExtractedVectorEntity(
                        entity_type='text',
                        layer=layer,
                        label=text,
                        bounding_box=bbox
                    ))

        if not entities:
            entities = self._generate_sample_entities(800.0, 600.0)

        return DrawingParseResult(
            filename=os.path.basename(dxf_path),
            width=800.0,
            height=600.0,
            entities=entities
        )

    def _generate_sample_entities(self, w: float, h: float) -> List[ExtractedVectorEntity]:
        """Generates baseline structural elements for demonstration drawings."""
        return [
            ExtractedVectorEntity('polyline', 'S-FOOTING', 'F-1 (1.5x1.5m)', [100, 100, 250, 250]),
            ExtractedVectorEntity('polyline', 'S-FOOTING', 'F-2 (2.0x2.0m)', [350, 100, 550, 300]),
            ExtractedVectorEntity('polyline', 'S-COLUMN', 'C-1 (400x400)', [150, 150, 200, 200]),
            ExtractedVectorEntity('polyline', 'S-BEAM', '2B-1 (300x500)', [200, 175, 450, 175]),
            ExtractedVectorEntity('polyline', 'S-WALL', 'W-1 (150mm CHB)', [100, 350, 500, 365]),
        ]
