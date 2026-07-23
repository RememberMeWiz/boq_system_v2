"""
backend/engine/pdf_dxf_parser.py

Primary deterministic extraction engine for the AI Blueprint & CAD Parser Pipeline.
Per Stage 4 decision (Section 2 of parser_design_spec.md + tech_spec_parser_v2.md):

    pdf_dxf_parser.py = primary deterministic engine
        - PyMuPDF (fitz)   -> page text, vector geometry, grid-node text association
        - pdfplumber       -> bordered schedule table extraction (Footings, Columns, ...)
        - ezdxf            -> native CAD layer/text extraction (S-FOOTING, S-COLUMN, S-BEAM)

    vision_parser.py = sheet classification, OCR fallback, TOC missing-sheet audit
        (imports and enriches the payload this module produces — see vision_parser.py)

ZERO math / calculations are performed here (Directive 9). This module only
extracts, structures, and flags data quality issues. All volume/weight/cost
math lives exclusively in backend/engine/fajardo.py.

Output conforms to tech_spec_parser_v2.md Section 3.1 (Structural Payload Schema).
"""

from __future__ import annotations

import re
import logging
from datetime import datetime, timezone
from typing import Optional

import fitz  # PyMuPDF
import pdfplumber

try:
    import ezdxf
except ImportError:  # pragma: no cover - optional dependency for CAD ingestion
    ezdxf = None

logger = logging.getLogger("pdf_dxf_parser")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SHEET_ID_PATTERN = re.compile(r"\b([A-Z]{1,3}-\d{1,2})\b")
GRID_NODE_PATTERN = re.compile(r"\b(\d{1,2})-([A-Z])\b")
MARK_PATTERN = re.compile(r"\b([FC]-?\d{1,2})\b")

# Missing-sheet -> BLOCKING issue rules, per tech_spec_parser_v2.md Section 4.1.
# vision_parser.py applies the SAME rule set during its own TOC audit pass;
# both modules import from a shared source would be ideal in a later refactor,
# but are kept duplicated-but-consistent here to avoid a circular import for
# this first Stage 4 pass.
BLOCKING_SHEET_RULES = {
    "S-6": {
        "category": "missing_schedule_sheet",
        "message": "Beam Schedule S-6 referenced in TOC but missing from uploaded file",
    },
    "S-7": {
        "category": "missing_connection_details",
        "message": (
            "Truss connection/weld detail sheet S-7 missing \u2014 gusset plates, base "
            "plate anchors, and weld lengths cannot be quantified for Structural Steel Works"
        ),
    },
    "S-8": {
        "category": "load_bearing_default_used",
        "message": (
            "Truss member schedule S-8 missing \u2014 roof truss steel weight cannot be "
            "computed without member list"
        ),
    },
}


def _new_issue(issue_id: str, severity: str, category: str, message: str,
               affected_elements: list, resolution_required: list) -> dict:
    return {
        "id": issue_id,
        "severity": severity,
        "category": category,
        "message": message,
        "affected_elements": affected_elements,
        "resolution_required": resolution_required,
        "resolved": False,
    }


class DrawingParserV2:
    """
    Deterministic PDF/DXF structural drawing parser.

    Usage:
        parser = DrawingParserV2(filepath="/path/to/plan.pdf", filename="plan.pdf")
        payload = parser.parse()
    """

    def __init__(self, filepath: str, filename: Optional[str] = None):
        self.filepath = filepath
        self.filename = filename or filepath.rsplit("/", 1)[-1]
        self.file_ext = self.filename.lower().rsplit(".", 1)[-1]
        self._issue_counter = 0
        self.blocking_issues: list = []
        self.warning_issues: list = []

    # ------------------------------------------------------------------
    # Issue helpers
    # ------------------------------------------------------------------
    def _next_issue_id(self) -> str:
        self._issue_counter += 1
        return f"sug_{self._issue_counter}"

    def _add_blocking(self, category, message, affected_elements, resolution_required=None):
        issue = _new_issue(
            self._next_issue_id(), "BLOCKING", category, message, affected_elements,
            resolution_required or ["upload_sheet", "manual_override_with_signoff"],
        )
        self.blocking_issues.append(issue)
        return issue

    def _add_warning(self, category, message, affected_elements, resolution_required=None):
        issue = _new_issue(
            self._next_issue_id(), "WARNING", category, message, affected_elements,
            resolution_required or ["manual_confirm"],
        )
        self.warning_issues.append(issue)
        return issue

    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------
    def parse(self) -> dict:
        if self.file_ext == "pdf":
            return self._parse_pdf()
        elif self.file_ext in ("dxf", "dwg"):
            return self._parse_cad()
        raise ValueError(f"Unsupported file extension: '{self.file_ext}'")

    # ------------------------------------------------------------------
    # PDF pipeline
    # ------------------------------------------------------------------
    def _parse_pdf(self) -> dict:
        doc = fitz.open(self.filepath)
        try:
            toc_sheets = self._extract_table_of_contents(doc)
            present_sheets = self._detect_present_sheets(doc)
            missing_sheets = sorted(set(toc_sheets) - set(present_sheets))

            grid_nodes = self._extract_grid_nodes(doc)
        finally:
            doc.close()

        schedules = self._extract_schedules_pdfplumber()
        self._audit_missing_sheets(missing_sheets, schedules)

        return self._assemble_payload(
            grid_nodes=grid_nodes,
            schedules=schedules,
            toc_missing_sheets=missing_sheets,
        )

    def _extract_table_of_contents(self, doc: "fitz.Document") -> list:
        """Scans early pages for a 'TABLE OF CONTENTS' block and pulls referenced sheet IDs."""
        sheet_ids = set()
        for page_index in range(min(10, doc.page_count)):
            text = doc[page_index].get_text()
            if "TABLE OF CONTENTS" in text.upper():
                sheet_ids.update(SHEET_ID_PATTERN.findall(text))
        return sorted(sheet_ids)

    def _detect_present_sheets(self, doc: "fitz.Document") -> list:
        """
        Scans each page's title-block region (bottom-right quadrant, matching
        DPWH standard sheet layout) for that page's OWN sheet ID.
        """
        present = set()
        for page in doc:
            rect = page.rect
            title_block = fitz.Rect(rect.width * 0.75, rect.height * 0.85, rect.width, rect.height)
            text = page.get_text("text", clip=title_block)
            matches = SHEET_ID_PATTERN.findall(text)
            if matches:
                present.add(matches[-1])
        return sorted(present)

    def _extract_grid_nodes(self, doc: "fitz.Document") -> list:
        """
        Heuristic proximity-based extraction of grid intersections and any
        footing/column marks in the same text block (e.g. "1-A F-3 C-3").
        Entries lacking both marks are still emitted (mark fields = None) so
        downstream consumers can see a node exists even if unresolved.
        """
        grid_nodes = []
        for page in doc:
            for block in page.get_text("blocks"):
                x0, y0, x1, y1, text, *_ = block
                node_match = GRID_NODE_PATTERN.search(text)
                if not node_match:
                    continue
                grid_id = f"{node_match.group(1)}-{node_match.group(2)}"
                marks = MARK_PATTERN.findall(text)
                footing_mark = next((m.upper() for m in marks if m.upper().startswith("F")), None)
                column_mark = next((m.upper() for m in marks if m.upper().startswith("C")), None)
                grid_nodes.append({
                    "grid_id": grid_id,
                    "footing_mark": footing_mark,
                    "column_mark": column_mark,
                    "x": round((x0 + x1) / 2, 2),
                    "y": round((y0 + y1) / 2, 2),
                })

        # De-duplicate by grid_id; prefer the entry with both marks populated.
        deduped: dict = {}
        for node in grid_nodes:
            key = node["grid_id"]
            if key not in deduped or (node["footing_mark"] and node["column_mark"]):
                deduped[key] = node
        return list(deduped.values())

    def _extract_schedules_pdfplumber(self) -> dict:
        """
        Uses pdfplumber's cell-border detection for bordered schedule tables.
        Empty categories are left for vision_parser's OCR fallback to attempt.
        """
        schedules = {"footings": [], "columns": [], "beams": [], "slabs": [], "walls": []}

        with pdfplumber.open(self.filepath) as pdf:
            for page in pdf.pages:
                page_text_upper = (page.extract_text() or "").upper()
                for table in page.extract_tables():
                    if not table or len(table) < 2:
                        continue
                    header_row = " ".join(c or "" for c in table[0]).upper()

                    if "SCHEDULE OF FOOTING" in page_text_upper or "FOOTING" in header_row:
                        schedules["footings"].extend(self._parse_footing_table(table))
                    elif "COLUMN SCHEDULE" in page_text_upper or "COLUMN" in header_row:
                        schedules["columns"].extend(self._parse_column_table(table))
                    elif "BEAM SCHEDULE" in page_text_upper or "BEAM" in header_row:
                        schedules["beams"].extend(self._parse_beam_table(table))
                    elif "SLAB SCHEDULE" in page_text_upper or "SLAB" in header_row:
                        schedules["slabs"].extend(self._parse_slab_table(table))

        if not schedules["footings"]:
            self._add_warning(
                "low_confidence_ocr",
                "No footing schedule table detected via pdfplumber border detection. "
                "Default sample values will be used for missing structural components.",
                affected_elements=["*footings*"],
                resolution_required=["manual_confirm", "upload_sheet"],
            )

        return schedules

    @staticmethod
    def _find_col(header: list, *keywords) -> Optional[int]:
        for i, h in enumerate(header):
            if any(k in h for k in keywords):
                return i
        return None

    def _parse_footing_table(self, table: list) -> list:
        """
        Column order varies between DPWH sheet revisions, so columns are
        matched by header keyword rather than fixed position.
        """
        results = []
        header = [str(c or "").strip().upper() for c in table[0]]

        col_mark = self._find_col(header, "MARK", "FOOTING")
        col_len = self._find_col(header, "LENGTH", "L (")
        col_wid = self._find_col(header, "WIDTH", "W (")
        col_dep = self._find_col(header, "DEPTH", "D (")
        col_bar = self._find_col(header, "BAR", "REINFORCEMENT")

        def to_float(row, idx):
            if idx is None or not row[idx]:
                return None
            try:
                return float(re.sub(r"[^\d.]", "", str(row[idx])))
            except ValueError:
                return None

        for row in table[1:]:
            if col_mark is None or not row[col_mark]:
                continue
            mark = str(row[col_mark]).strip().upper().replace(" ", "")
            if not re.match(r"^F-?\d+$", mark):
                continue

            length_mm = to_float(row, col_len)
            width_mm = to_float(row, col_wid)
            depth_mm = to_float(row, col_dep)
            bar_raw = str(row[col_bar]) if col_bar is not None and row[col_bar] else ""
            bar_size_match = re.search(r"(\d{1,2})\s*mm", bar_raw, re.IGNORECASE)
            bar_count_match = re.search(r"(\d{1,2})\s*[-\u2013]\s*\d{1,2}\s*mm", bar_raw, re.IGNORECASE)

            complete = bool(length_mm and width_mm and depth_mm)
            results.append({
                "mark": mark,
                "length_m": round(length_mm / 1000, 3) if length_mm else None,
                "width_m": round(width_mm / 1000, 3) if width_mm else None,
                "thickness_m": round(depth_mm / 1000, 3) if depth_mm else None,
                "rebar": {
                    "size_mm": int(bar_size_match.group(1)) if bar_size_match else None,
                    "count": int(bar_count_match.group(1)) if bar_count_match else None,
                    "type": "grid_mat",
                },
                "provenance": "vector_text" if complete else "inferred",
            })
        return results

    def _parse_column_table(self, table: list) -> list:
        """
        DPWH column schedules typically split each mark into TWO rows:
        'Foundation Level to 2nd Floor Level' and '2nd Floor Level to Roof
        Level'. Both are emitted as distinct entries with the same `mark`
        but different `story_level`. Cross-section dimensions are extracted
        from explicit 'SIZE' columns or parsed from WxD text patterns.
        """
        results = []
        header = [str(c or "").strip().upper() for c in table[0]]

        col_level = self._find_col(header, "LEVEL")
        col_main = self._find_col(header, "MAIN BAR")
        col_ties = self._find_col(header, "TIES")
        col_size = self._find_col(header, "SIZE", "DIMENSION", "W X D", "WXD", "SECTION")

        current_mark = None
        for row in table[1:]:
            cell0 = str(row[0] or "").strip().upper().replace(" ", "")
            mark_match = re.match(r"^(C-?\d+)$", cell0)
            if mark_match:
                current_mark = mark_match.group(1)

            story_text = str(row[col_level] or "") if col_level is not None else ""
            if not any(k in story_text.upper() for k in ("FOUNDATION", "FLOOR", "ROOF")):
                continue
            if not current_mark:
                continue

            main_bar_raw = str(row[col_main] or "") if col_main is not None else ""
            ties_raw = str(row[col_ties] or "") if col_ties is not None else ""
            main_match = re.search(r"(\d{1,2})\s*[-\u2013]\s*(\d{1,2})\s*mm", main_bar_raw, re.IGNORECASE)

            # Extract width_m and depth_m from size column or full row text search
            width_m, depth_m = None, None
            size_text = (str(row[col_size] or "") if col_size is not None else "") or " ".join(str(c or "") for c in row)
            dim_mm_match = re.search(r"(\d{3,4})\s*[xX×]\s*(\d{3,4})", size_text)
            dim_m_match = re.search(r"0\.(\d{2})\s*[xX×]\s*0\.(\d{2})", size_text)

            if dim_mm_match:
                width_m = round(float(dim_mm_match.group(1)) / 1000, 3)
                depth_m = round(float(dim_mm_match.group(2)) / 1000, 3)
            elif dim_m_match:
                width_m = round(float("0." + dim_m_match.group(1)), 3)
                depth_m = round(float("0." + dim_m_match.group(2)), 3)

            results.append({
                "mark": current_mark,
                "story_level": story_text.strip(),
                "width_m": width_m,
                "depth_m": depth_m,
                "clear_height_m": 3.0,
                "main_bars": {
                    "size_mm": int(main_match.group(2)) if main_match else None,
                    "count": int(main_match.group(1)) if main_match else None,
                },
                "ties": {
                    "size_mm": None,
                    "spacing_mm": ties_raw.strip() or None,
                },
                "provenance": "vector_text" if (width_m and depth_m and main_match) else "inferred",
            })
        return results

    def _parse_beam_table(self, table: list) -> list:
        """Parses beam schedule tables into structured beam elements."""
        results = []
        header = [str(c or "").strip().upper() for c in table[0]]

        col_mark = self._find_col(header, "MARK", "BEAM")
        col_size = self._find_col(header, "SIZE", "DIMENSION", "SECTION")
        col_top  = self._find_col(header, "TOP", "TOP BAR")
        col_bot  = self._find_col(header, "BOT", "BOTTOM", "BOTTOM BAR")
        col_stir = self._find_col(header, "STIRRUP", "TIES", "SPACING")

        for row in table[1:]:
            mark_text = str(row[col_mark] if col_mark is not None else row[0] or "").strip().upper().replace(" ", "")
            mark_match = re.match(r"^([G?B]-?\d+)$", mark_text)
            if not mark_match:
                continue

            beam_mark = mark_match.group(1)
            row_text = " ".join(str(c or "") for c in row)

            width_m, depth_m = None, None
            dim_mm_match = re.search(r"(\d{3,4})\s*[xX×]\s*(\d{3,4})", row_text)
            dim_m_match = re.search(r"0\.(\d{2})\s*[xX×]\s*0\.(\d{2})", row_text)

            if dim_mm_match:
                width_m = round(float(dim_mm_match.group(1)) / 1000, 3)
                depth_m = round(float(dim_mm_match.group(2)) / 1000, 3)
            elif dim_m_match:
                width_m = round(float("0." + dim_m_match.group(1)), 3)
                depth_m = round(float("0." + dim_m_match.group(2)), 3)

            top_raw = str(row[col_top] if col_top is not None else "")
            bot_raw = str(row[col_bot] if col_bot is not None else "")
            top_match = re.search(r"(\d{1,2})\s*[-\u2013]\s*(\d{1,2})\s*mm", top_raw, re.IGNORECASE)
            bot_match = re.search(r"(\d{1,2})\s*[-\u2013]\s*(\d{1,2})\s*mm", bot_raw, re.IGNORECASE)

            results.append({
                "mark": beam_mark,
                "width_m": width_m or 0.25,
                "depth_m": depth_m or 0.40,
                "span_m": 5.0,
                "top_bars": {
                    "count": int(top_match.group(1)) if top_match else 2,
                    "size_mm": int(top_match.group(2)) if top_match else 16,
                },
                "bottom_bars": {
                    "count": int(bot_match.group(1)) if bot_match else 3,
                    "size_mm": int(bot_match.group(2)) if bot_match else 16,
                },
                "provenance": "vector_text" if (width_m and depth_m) else "inferred",
            })
        return results

    def _parse_slab_table(self, table: list) -> list:
        """Parses slab schedule tables into structured slab elements."""
        results = []
        header = [str(c or "").strip().upper() for c in table[0]]

        col_mark = self._find_col(header, "MARK", "SLAB", "PANEL")
        col_thk  = self._find_col(header, "THICKNESS", "THK", "DEPTH", "T (")

        for row in table[1:]:
            mark_text = str(row[col_mark] if col_mark is not None else row[0] or "").strip().upper().replace(" ", "")
            mark_match = re.match(r"^(S-?\d+)$", mark_text)
            if not mark_match:
                continue

            slab_mark = mark_match.group(1)
            thk_text = str(row[col_thk] if col_thk is not None else " ".join(str(c or "") for c in row))
            thk_match = re.search(r"(\d{2,3})\s*mm", thk_text, re.IGNORECASE)
            thickness_m = round(float(thk_match.group(1)) / 1000, 3) if thk_match else 0.125

            results.append({
                "mark": slab_mark,
                "thickness_m": thickness_m,
                "length_m": 4.0,
                "width_m": 4.0,
                "provenance": "vector_text" if thk_match else "inferred",
            })
        return results

    # ------------------------------------------------------------------
    # CAD (DXF) pipeline
    # ------------------------------------------------------------------
    def _parse_cad(self) -> dict:
        if ezdxf is None:
            raise RuntimeError("ezdxf is not installed. Run: pip install ezdxf")

        if self.file_ext == "dwg":
            # Per tech_spec_parser_v2.md Section 4, Failure Point 3: DWG must be
            # converted via the ODA File Converter CLI *before* this module runs.
            # That conversion step belongs in app.py's ingest route, not here.
            raise RuntimeError(
                "Native .dwg files must be converted to .dxf via the ODA File Converter "
                "CLI before calling DrawingParserV2.parse(). See ingest route in app.py."
            )

        doc = ezdxf.readfile(self.filepath)
        msp = doc.modelspace()

        schedules = {"footings": [], "columns": [], "beams": [], "slabs": [], "walls": []}
        layer_targets = {"S-FOOTING": "footings", "S-COLUMN": "columns", "S-BEAM": "beams"}

        for entity in msp:
            if entity.dxftype() != "TEXT":
                continue
            layer = entity.dxf.layer.upper()
            for layer_key, schedule_key in layer_targets.items():
                if layer_key not in layer:
                    continue
                text_value = entity.dxf.text.strip().upper().replace(" ", "")
                mark_match = re.match(r"^([FCB]-?\d+)$", text_value)
                if mark_match:
                    schedules[schedule_key].append({
                        "mark": mark_match.group(1),
                        "provenance": "parsed_cad_layer",
                        "source_layer": entity.dxf.layer,
                    })

        # DXF layer text gives marks/locations but not necessarily TOC context,
        # so toc_missing_sheets audit is skipped here (no cover-sheet TOC to read).
        return self._assemble_payload(grid_nodes=[], schedules=schedules, toc_missing_sheets=[])

    # ------------------------------------------------------------------
    # Missing-sheet audit (BLOCKING issues for S-6 / S-7 / S-8)
    # ------------------------------------------------------------------
    def _audit_missing_sheets(self, missing_sheets: list, schedules: dict):
        for sheet_id in missing_sheets:
            rule = BLOCKING_SHEET_RULES.get(sheet_id)
            if rule is None:
                self._add_warning(
                    "missing_referenced_sheet",
                    f"Sheet {sheet_id} referenced in Table of Contents but not found in "
                    f"uploaded file.",
                    affected_elements=["*"],
                )
                continue

            affected = ["*"]
            if sheet_id == "S-6":
                marks = [b["mark"] for b in schedules.get("beams", []) if b.get("mark")]
                affected = marks or ["*beams*"]
            elif sheet_id in ("S-7", "S-8"):
                affected = ["T-1"]  # truss mark convention observed on DPWH standard plans

            self._add_blocking(rule["category"], rule["message"], affected_elements=affected)

    # ------------------------------------------------------------------
    # Payload assembly
    # ------------------------------------------------------------------
    def _assemble_payload(self, grid_nodes: list, schedules: dict, toc_missing_sheets: list) -> dict:
        status = "BLOCKED" if any(not i["resolved"] for i in self.blocking_issues) else "READY"

        return {
            "project_meta": {
                "filename": self.filename,
                "detected_variant": None,  # populated by vision_parser.py sheet classification
                "grid_scope": {"bays": None, "total_length_mm": None},
                "toc_missing_sheets": toc_missing_sheets,
            },
            "grid_nodes": grid_nodes,
            "schedules": schedules,
            "structural_notes": {
                "concrete_cover_earth_mm": None,
                "concrete_cover_col_beam_mm": None,
                "lap_splice_multiplier": None,
                "seismic_hook_deg": None,
            },
            "verification_gate": {
                "status": status,
                "computed_at": datetime.now(timezone.utc).isoformat(),
                "blocking_issues": self.blocking_issues,
                "warning_issues": self.warning_issues,
                "resolution_log": [],
            },
        }
