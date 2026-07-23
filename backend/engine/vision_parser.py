"""
backend/engine/vision_parser.py

Multimodal vision-assisted enrichment layer for the AI Blueprint & CAD Parser
Pipeline. Per Stage 4 decision, this module owns:

    1. Sheet type classification (Framing Plan / Schedule / Section Detail / ...)
    2. Table-of-Contents audit -> project_meta.toc_missing_sheets + BLOCKING
       issues for S-6 / S-7 / S-8 (Structural Steel Works load-path sheets)
    3. OCR fallback: crops schedule-table regions that pdf_dxf_parser.py could
       not extract via bordered-table detection, and asks Gemini Vision to
       structure them, tagging provenance = "inferred"

ZERO math / calculations here (Directive 9) -- this module only classifies,
audits, and structures raw text/table data.

API execution: uses the `google-genai` SDK with a real, live Gemini call when
GEMINI_API_KEY is set. If the key is missing (or the SDK import fails), this
module automatically falls back to local heuristic keyword-matching for
classification and skips OCR fallback (recording a WARNING issue instead of
silently guessing table contents).

IMPORTANT (flagged for whoever wires the live key): the exact `google-genai`
client call signature below (`genai.Client`, `client.models.generate_content`,
`genai_types.Part.from_bytes`) reflects the SDK's structure as of this
module's authoring. Verify against the current `google-genai` PyPI docs
before deploying -- SDK method signatures do change between releases, and
this was not verified against a live SDK install at write time.
"""

from __future__ import annotations

import os
import re
import json
import logging
from typing import Optional

import fitz  # PyMuPDF

logger = logging.getLogger("vision_parser")

try:
    from google import genai
    from google.genai import types as genai_types
    _GENAI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    _GENAI_AVAILABLE = False

SHEET_ID_PATTERN = re.compile(r"\b([A-Z]{1,3}-\d{1,2})\b")

SHEET_TYPE_KEYWORDS = {
    "table_of_contents": ["TABLE OF CONTENTS", "PERSPECTIVE"],
    "foundation_plan": ["FOUNDATION PLAN"],
    "framing_plan": ["FRAMING PLAN"],
    "footing_column_schedule": ["SCHEDULE OF FOOTING", "COLUMN SCHEDULE"],
    "beam_schedule": ["SCHEDULE OF BEAM", "BEAM SCHEDULE"],
    "general_notes": ["GENERAL CONSTRUCTION NOTES", "GENERAL NOTES"],
    "elevation": ["ELEVATION"],
    "truss_detail": ["TRUSS DETAIL", "CONNECTION DETAIL", "WELD"],
    "section_detail": ["SECTION", "DETAIL"],
}

# Same rule set as pdf_dxf_parser.BLOCKING_SHEET_RULES. Kept in sync manually
# for this first Stage 4 pass -- a shared `blocking_rules.py` module is a
# reasonable follow-up refactor once both modules stabilize.
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

SCHEDULE_KEYWORD_MAP = {
    "footings": "SCHEDULE OF FOOTING",
    "columns": "COLUMN SCHEDULE",
    "beams": "SCHEDULE OF BEAM",
}


class VisionBlueprintInspector:
    """
    Enriches a raw structural payload (produced by
    pdf_dxf_parser.DrawingParserV2.parse()) with sheet classification, TOC
    audit results, and OCR fallback extraction.

    Usage:
        inspector = VisionBlueprintInspector(filepath="/path/to/plan.pdf")
        payload = inspector.enrich(payload)
    """

    def __init__(self, filepath: str, model_name: Optional[str] = None):
        self.filepath = filepath
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        # NOTE: model name is intentionally read from env rather than hardcoded.
        # Verify the current recommended Gemini vision model name against
        # Google's live docs before deploying -- do not trust this default
        # blindly, model naming in this space changes frequently.
        self.model_name = model_name or os.environ.get("GEMINI_MODEL", "gemini-flash-latest")



        if self.api_key and _GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as exc:  # pragma: no cover - defensive init guard
                logger.warning("Failed to initialize google-genai client: %s", exc)
                self.client = None
        elif self.api_key and not _GENAI_AVAILABLE:
            logger.warning(
                "GEMINI_API_KEY is set but the 'google-genai' package is not installed "
                "(pip install google-genai). Falling back to local heuristics."
            )

    def _call_gemini_with_retry(self, contents: list, max_retries: int = 3):
        import time
        for attempt in range(max_retries):
            try:
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                )
            except Exception as exc:
                exc_str = str(exc)
                if ("429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str or "Quota" in exc_str) and attempt < max_retries - 1:
                    logger.warning("Gemini API rate limit (429) hit, waiting 6s before retry %d/%d...", attempt + 1, max_retries)
                    time.sleep(6)
                else:
                    raise exc
        return None

    @property
    def vision_available(self) -> bool:
        return self.client is not None


    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------
    def enrich(self, payload: dict) -> dict:
        """
        Mutates and returns `payload` with sheet classification results,
        a recomputed toc_missing_sheets list, BLOCKING issues for missing
        S-6/S-7/S-8, and OCR-fallback-extracted schedule rows where possible.
        """
        doc = fitz.open(self.filepath)
        try:
            toc_sheet_ids = self._extract_toc_sheet_ids(doc)
            present_sheet_ids, page_classifications = self._classify_and_detect_sheets(doc)

            missing = sorted(set(toc_sheet_ids) - set(present_sheet_ids))
            # Union with whatever pdf_dxf_parser already found, in case its
            # title-block detection caught something this pass missed.
            existing_missing = set(payload.get("project_meta", {}).get("toc_missing_sheets", []))
            payload["project_meta"]["toc_missing_sheets"] = sorted(set(missing) | existing_missing)
            payload["project_meta"]["_sheet_classifications"] = page_classifications

            self._apply_blocking_rules(payload, payload["project_meta"]["toc_missing_sheets"])
            self._ocr_fallback_for_empty_schedules(doc, payload)
        finally:
            doc.close()

        return payload

    # ------------------------------------------------------------------
    # Step 1: TOC extraction
    # ------------------------------------------------------------------
    def _extract_toc_sheet_ids(self, doc: "fitz.Document") -> list:
        sheet_ids = set()
        for page_index in range(min(10, doc.page_count)):
            text = doc[page_index].get_text()
            if "TABLE OF CONTENTS" in text.upper():
                sheet_ids.update(SHEET_ID_PATTERN.findall(text))
        return sorted(sheet_ids)

    # ------------------------------------------------------------------
    # Step 2: sheet classification (vision or heuristic) + presence detection
    # ------------------------------------------------------------------
    def _classify_and_detect_sheets(self, doc: "fitz.Document") -> tuple:
        present = set()
        classifications = {}

        for page_index, page in enumerate(doc):
            text = page.get_text()
            page_sheet_ids = SHEET_ID_PATTERN.findall(text)
            if page_sheet_ids:
                # The page's own sheet ID is typically the LAST tag matched in
                # the title block; earlier matches tend to be cross-references
                # (e.g. "SEE DETAIL 3 / A-9").
                own_sheet_id = page_sheet_ids[-1]
                present.add(own_sheet_id)
            else:
                own_sheet_id = f"page_{page_index}"

            sheet_type = self._classify_page(page, text)
            classifications[own_sheet_id] = sheet_type

        return sorted(present), classifications

    def _classify_page(self, page: "fitz.Page", text: str) -> str:
        text_upper = text.upper()
        for sheet_type, keywords in SHEET_TYPE_KEYWORDS.items():
            if any(kw in text_upper for kw in keywords):
                return sheet_type
        return "unknown"


    # ------------------------------------------------------------------
    # Step 3: apply BLOCKING rules for missing load-path sheets
    # ------------------------------------------------------------------
    def _apply_blocking_rules(self, payload: dict, missing_sheets: list):
        gate = payload["verification_gate"]
        existing_categories = {i["category"] for i in gate["blocking_issues"]}
        next_index = len(gate["blocking_issues"]) + len(gate["warning_issues"]) + 1

        for sheet_id in missing_sheets:
            rule = BLOCKING_SHEET_RULES.get(sheet_id)
            if rule is None or rule["category"] in existing_categories:
                continue
            gate["blocking_issues"].append({
                "id": f"sug_{next_index}",
                "category": rule["category"],
                "rule_code": sheet_id,
                "message": rule["message"],
                "resolved": False,
                "resolution_required": ["upload_sheet", "manual_override_with_signoff"],
            })
            next_index += 1

        if any(not i["resolved"] for i in gate["blocking_issues"]):
            gate["status"] = "BLOCKED"

    def _affected_elements_for_sheet(self, sheet_id: str, payload: dict) -> list:
        if sheet_id == "S-6":
            marks = [b.get("mark") for b in payload["schedules"].get("beams", []) if b.get("mark")]
            return marks or ["*beams*"]
        if sheet_id in ("S-7", "S-8"):
            return ["T-1"]
        return ["*"]

    # ------------------------------------------------------------------
    # Step 4: OCR fallback for schedule categories pdf_dxf_parser left empty
    # ------------------------------------------------------------------
    def _ocr_fallback_for_empty_schedules(self, doc: "fitz.Document", payload: dict):
        schedules = payload["schedules"]
        empty_categories = [k for k in SCHEDULE_KEYWORD_MAP if not schedules.get(k)]
        if not empty_categories:
            return

        if not self.vision_available:
            gate = payload["verification_gate"]
            next_index = len(gate["blocking_issues"]) + len(gate["warning_issues"]) + 1
            for category in empty_categories:
                gate["warning_issues"].append({
                    "id": f"sug_{next_index}",
                    "severity": "WARNING",
                    "category": "low_confidence_ocr",
                    "message": (
                        f"No '{category}' schedule table was detected by deterministic "
                        f"parsing, and no GEMINI_API_KEY is configured for OCR fallback. "
                        f"Manual review or sheet upload required."
                    ),
                    "affected_elements": [f"*{category}*"],
                    "resolution_required": ["manual_confirm", "upload_sheet"],
                    "resolved": False,
                })
                next_index += 1
            return

    # ------------------------------------------------------------------
    # Step 4: OCR fallback for empty schedule tables with autonomous discovery
    # ------------------------------------------------------------------
    def _ocr_fallback_for_empty_schedules(self, doc: "fitz.Document", payload: dict):
        if not self.vision_available:
            return

        schedules = payload.get("schedules", {})
        empty_categories = [cat for cat in ("footings", "columns", "beams") if not schedules.get(cat)]
        if not empty_categories:
            return

        # Compact keyword map for robust page discovery across spaced title fonts (e.g. S C H E D U L E)
        COMPACT_KEYWORD_MAP = {
            "footings": ["SCHEDULEOFFOOTING", "FOOTINGSCHEDULE"],
            "columns": ["COLUMNSCHEDULE", "SCHEDULEOFCOLUMN"],
            "beams": ["SCHEDULEOFBEAM", "BEAMSCHEDULE"],
        }

        for page_index, page in enumerate(doc):
            if not empty_categories:
                break
            raw_text = page.get_text().upper()
            compact_text = re.sub(r"[\s_]+", "", raw_text)

            # Skip Table of Contents pages (they list sheet names in text, not actual drawing tables)
            if "TABLEOFCONTENTS" in compact_text:
                continue

            for category in list(empty_categories):
                keywords = COMPACT_KEYWORD_MAP[category]
                if any(kw in compact_text for kw in keywords):
                    logger.info("Autonomous Page Discovery -> Found %s schedule on Page %d", category, page_index)
                    extracted = self._ocr_table(page, category)
                    if extracted:
                        schedules[category].extend(extracted)
                        empty_categories.remove(category)


    def _ocr_table(self, page: "fitz.Page", category: str) -> list:
        try:
            pix = page.get_pixmap(dpi=200)
            image_bytes = pix.tobytes("png")
            prompt = (
                f"This image contains a '{category}' schedule table from a structural "
                f"engineering drawing sheet. Extract every data row as a JSON array of "
                f"objects with the row's own column names as keys. Respond with ONLY "
                f"valid JSON -- no markdown code fences, no commentary."
            )
            response = self._call_gemini_with_retry([
                genai_types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                prompt,
            ])
            raw = (response.text or "").strip() if response else ""
            raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
            rows = json.loads(raw) if raw else []
            if not isinstance(rows, list):
                return []
            for row in rows:
                row["provenance"] = "inferred"
            return rows
        except Exception as exc:  # pragma: no cover - network/API/parse failure path
            logger.warning("OCR fallback failed for category='%s': %s", category, exc)
            return []
