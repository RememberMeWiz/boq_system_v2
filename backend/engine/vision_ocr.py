"""
Plan2Takeoff V2 — Vision OCR & Schedule Table Parser
Crops structural schedule regions from PDFs and extracts rebar/element data via regex.
No paid AI API required — pure text extraction + pattern matching.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple

log = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


# ---------------------------------------------------------------------------
# Region Cropping
# ---------------------------------------------------------------------------

def crop_schedule_region(pdf_path: str, region_bbox: List[float], page_num: int = 0) -> str:
    """
    Crops a rectangular region from a PDF page and extracts its text content.

    Args:
        pdf_path:    Path to the PDF file.
        region_bbox: [x1, y1, x2, y2] in PDF points (72 pts = 1 inch).
        page_num:    0-indexed page number (default: 0).

    Returns:
        Extracted text string from that region, or "" if extraction fails.
    """
    if not fitz:
        log.warning("PyMuPDF not installed — cannot crop schedule region.")
        return ""
    if not os.path.exists(pdf_path):
        log.warning(f"PDF not found: {pdf_path}")
        return ""

    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        rect = fitz.Rect(region_bbox[0], region_bbox[1], region_bbox[2], region_bbox[3])
        text = page.get_text("text", clip=rect).strip()
        doc.close()
        return text
    except Exception as e:
        log.error(f"crop_schedule_region failed: {e}")
        return ""


def extract_all_page_text(pdf_path: str, page_num: int = 0) -> str:
    """Returns all text from a PDF page."""
    if not fitz or not os.path.exists(pdf_path):
        return ""
    try:
        doc = fitz.open(pdf_path)
        text = doc[page_num].get_text("text")
        doc.close()
        return text
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Schedule Parsers
# ---------------------------------------------------------------------------

def parse_rebar_schedule(text: str) -> List[Dict]:
    """
    Parses a rebar schedule table from text extracted from a PDF region.

    Handles formats like:
      BAR MARK   DIA   NO. OF BARS   LENGTH
      B1         Ø16   8             1.80m
      B2         #20   6             5.80m

    Returns list of dicts: {member, diameter_mm, count, length_m}
    """
    results = []

    # Pattern: optional bar mark, then diameter, count, optional length
    pattern = re.compile(
        r'(?P<mark>[A-Z]\d+)?\s*'
        r'[ØO∅#Φ]?\s*(?P<dia>\d{2})\s*(?:mm|dia|diam)?\s+'
        r'(?P<count>\d+)\s*(?:pcs?|bars?|nos?|ea)?'
        r'(?:\s+(?P<length>\d+\.?\d*)\s*m?)?',
        re.IGNORECASE | re.MULTILINE
    )

    for m in pattern.finditer(text):
        dia = int(m.group('dia'))
        cnt = int(m.group('count'))
        length = float(m.group('length')) if m.group('length') else 1.50
        mark = m.group('mark') or 'generic'

        # Sanity: only standard rebar diameters
        if dia not in (10, 12, 16, 20, 25, 28, 32):
            continue
        if cnt <= 0 or cnt > 1000:
            continue

        results.append({
            "member":      mark.lower(),
            "diameter_mm": dia,
            "count":       cnt,
            "length_m":    round(length, 3),
        })

    return results


def parse_column_schedule(text: str) -> List[Dict]:
    """
    Parses a column schedule: label, dimension (WxD), clear height, main bars, ties.

    Returns list of dicts: {label, width_m, depth_m, clear_height_m, main_bars: [...]}
    """
    results = []

    # Match: "C-1  300x300  3.20m  8-Ø20  Ø10@200"
    col_pattern = re.compile(
        r'(C-\d+|COL-?\d*)\s+'
        r'(\d+)\s*[xX×]\s*(\d+)'
        r'(?:\s+(\d+\.?\d*)\s*m)?'
        r'(?:\s+(\d+)-[ØO∅#Φ](\d+))?',
        re.IGNORECASE
    )

    for m in col_pattern.finditer(text):
        label = m.group(1)
        w = int(m.group(2)) / 1000.0 if int(m.group(2)) >= 100 else float(m.group(2))
        d = int(m.group(3)) / 1000.0 if int(m.group(3)) >= 100 else float(m.group(3))
        h = float(m.group(4)) if m.group(4) else 3.20
        bar_count = int(m.group(5)) if m.group(5) else 8
        bar_dia = int(m.group(6)) if m.group(6) else 20

        results.append({
            "label": label,
            "type": "column",
            "class": "A",
            "width_m": round(w, 3),
            "depth_m": round(d, 3),
            "clear_height_m": h,
            "count": 1,
            "main_bars": [{"diameter_mm": bar_dia, "count": bar_count}],
        })

    return results


def parse_beam_schedule(text: str) -> List[Dict]:
    """
    Parses a beam schedule: label, WxD, span, main bars, stirrups.

    Returns list of dicts: {label, width_m, depth_m, clear_span_m, rebar: [...]}
    """
    results = []

    beam_pattern = re.compile(
        r'(\d?B-\d+|BEAM-?\d*)\s+'
        r'(\d+)\s*[xX×]\s*(\d+)'
        r'(?:\s+(\d+\.?\d*)\s*m)?',
        re.IGNORECASE
    )

    for m in beam_pattern.finditer(text):
        label = m.group(1)
        w = int(m.group(2)) / 1000.0 if int(m.group(2)) >= 100 else float(m.group(2))
        d = int(m.group(3)) / 1000.0 if int(m.group(3)) >= 100 else float(m.group(3))
        span = float(m.group(4)) if m.group(4) else 4.50

        results.append({
            "label": label,
            "type": "beam",
            "class": "A",
            "width_m": round(w, 3),
            "depth_m": round(d, 3),
            "clear_span_m": span,
            "count": 1,
        })

    return results


def parse_footing_schedule(text: str) -> List[Dict]:
    """
    Parses footing schedule: label, LxWxH, rebar.

    Returns list of dicts matching fajardo.py footing input format.
    """
    results = []

    ftg_pattern = re.compile(
        r'(F-\d+)\s+'
        r'(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)'
        r'(?:\s*[xX×]\s*(\d+\.?\d*))?'
        r'(?:\s+(\d+)\s*pcs?)?',
        re.IGNORECASE
    )

    for m in ftg_pattern.finditer(text):
        label = m.group(1)
        l = float(m.group(2))
        w = float(m.group(3))
        h = float(m.group(4)) if m.group(4) else 0.40
        cnt = int(m.group(5)) if m.group(5) else 1

        # Convert mm → m where needed
        if l >= 100: l /= 1000.0
        if w >= 100: w /= 1000.0
        if h >= 100: h /= 1000.0

        results.append({
            "label": label,
            "type": "footing",
            "class": "A",
            "length_m": round(l, 3),
            "width_m": round(w, 3),
            "depth_m": round(h, 3),
            "count": cnt,
        })

    return results


# ---------------------------------------------------------------------------
# Master parse dispatcher
# ---------------------------------------------------------------------------

def parse_schedule_text(text: str, schedule_type: str = "auto") -> Dict:
    """
    Dispatches text to the appropriate schedule parser.

    Args:
        text:          Raw text extracted from PDF schedule region.
        schedule_type: "rebar" | "column" | "beam" | "footing" | "auto"

    Returns:
        {"type": str, "items": list, "count": int}
    """
    if schedule_type == "rebar" or (
        schedule_type == "auto" and re.search(r'[ØO∅#Φ]\s*\d{2}|dia\s*\d{2}', text, re.IGNORECASE)
    ):
        items = parse_rebar_schedule(text)
        return {"type": "rebar_schedule", "items": items, "count": len(items)}

    if schedule_type == "column" or (
        schedule_type == "auto" and re.search(r'\bC-\d+\b', text, re.IGNORECASE)
    ):
        items = parse_column_schedule(text)
        return {"type": "column_schedule", "items": items, "count": len(items)}

    if schedule_type == "beam" or (
        schedule_type == "auto" and re.search(r'\d?B-\d+', text, re.IGNORECASE)
    ):
        items = parse_beam_schedule(text)
        return {"type": "beam_schedule", "items": items, "count": len(items)}

    if schedule_type == "footing" or (
        schedule_type == "auto" and re.search(r'\bF-\d+\b', text, re.IGNORECASE)
    ):
        items = parse_footing_schedule(text)
        return {"type": "footing_schedule", "items": items, "count": len(items)}

    # Auto-fallback: try all
    all_items = []
    for parser in [parse_rebar_schedule, parse_column_schedule, parse_beam_schedule, parse_footing_schedule]:
        all_items.extend(parser(text))
    return {"type": "mixed", "items": all_items, "count": len(all_items)}


# ---------------------------------------------------------------------------
# Full-page auto-scan
# ---------------------------------------------------------------------------

def auto_scan_pdf_schedules(pdf_path: str) -> Dict:
    """
    Scans all pages of a PDF for schedule tables and extracts all structural data.

    Returns:
        {"rebar": [...], "columns": [...], "beams": [...], "footings": [...], "page_count": int}
    """
    if not fitz or not os.path.exists(pdf_path):
        return {"rebar": [], "columns": [], "beams": [], "footings": [], "page_count": 0}

    all_rebar, all_columns, all_beams, all_footings = [], [], [], []

    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            text = doc[page_num].get_text("text")
            all_rebar.extend(parse_rebar_schedule(text))
            all_columns.extend(parse_column_schedule(text))
            all_beams.extend(parse_beam_schedule(text))
            all_footings.extend(parse_footing_schedule(text))
        doc.close()
    except Exception as e:
        log.error(f"auto_scan_pdf_schedules failed: {e}")

    return {
        "rebar":    all_rebar,
        "columns":  all_columns,
        "beams":    all_beams,
        "footings": all_footings,
        "page_count": len(all_rebar) + len(all_columns) + len(all_beams) + len(all_footings),
    }
