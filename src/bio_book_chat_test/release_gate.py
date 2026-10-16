"""Strict release gate for SOURCE-MATCHED, editable PDF-to-Word documents.

This is NOT an OCR validator: human source-image evidence remains mandatory.
No unverified artifact can be certified just because CI/LibreOffice passed.
The manifest intentionally lives outside the public repository with the book.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile, BadZipFile
from lxml import etree

from .ooxml_checks import docx_structure_warnings

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
ARABIC = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]")
LATIN = re.compile(r"[A-Za-z]")
REQUIRED_REVIEWS = ("source_text", "visual_layout", "illustrations", "editability")
TEXT_KINDS = {"paragraph", "heading", "caption", "sidebar", "table_cell", "footnote"}


def _issue(items: list, code: str, where: str, detail: str) -> None:
    items.append({"code": code, "location": where, "detail": detail})


def _normalise(text: str) -> str:
    # Strip only rendering direction controls; NEVER remove hamzas or harakat.
    return text.replace("\u00a0", " ").translate(
        dict.fromkeys(map(ord, "\u200e\u200f\u202a\u202b\u202c\u2066\u2067\u2068\u2069"), None)
    )


def _bbox(value) -> bool:
    return (isinstance(value, list) and len(value) == 4
            and all(type(n) in (int, float) for n in value)
            and value[2] > value[0] and value[3] > value[1])


def _check_objects(page: dict, number: int, output_text: str, issues: list) -> None:
    objects = page.get("objects")
    if not isinstance(objects, list) or not objects:
        _issue(issues, "PAGE_OBJECTS_MISSING", f"page:{number}", "No semantic page objects recorded")
        return
    seen = set()
    for idx, obj in enumerate(objects):
        loc = f"page:{number}/object:{idx}"
        if not isinstance(obj, dict):
            _issue(issues, "OBJECT_INVALID", loc, "Expected object data")
            continue
        name = obj.get("id")
        if not isinstance(name, str) or not name or name in seen:
            _issue(issues, "OBJECT_ID_INVALID", loc, "IDs must be distinct and nonempty")
        seen.add(name)
        kind = obj.get("kind")
        if kind == "line":
            _issue(issues, "SPLIT_PARAGRAPH_INTO_LINES", loc, "Store a semantic paragraph, not a PDF display line")
        if kind not in TEXT_KINDS | {"figure"}:
            _issue(issues, "OBJECT_KIND_INVALID", loc, "Unsupported or unknown semantic kind")
            continue
        source_box, result_box = obj.get("source_bbox_pt"), obj.get("rendered_bbox_pt")
        if not _bbox(source_box) or not _bbox(result_box):
            _issue(issues, "LAYOUT_NOT_MEASURED", loc, "Both PDF and *rendered* Word bboxes required")
        else:
            tolerance = page.get("bbox_tolerance_pt", 8.5)
            if type(tolerance) not in (int, float) or not 0 < tolerance <= 20:
                _issue(issues, "INVALID_LAYOUT_TOLERANCE", loc, "Tolerance must be within (0, 20] pt")
            elif max(abs(a-b) for a, b in zip(source_box, result_box)) > tolerance:
                _issue(issues, "LAYOUT_DRIFT", loc, "Rendered Word object is outside declared bbox tolerance")
        if kind == "figure":
            if obj.get("graphic_source") not in ("pdf_original_crop", "original_embedded_image"):
                _issue(issues, "FIGURE_PROVENANCE_MISSING", loc, "Figure must retain source provenance")
            continue
        text = obj.get("text")
        if not isinstance(text, str) or not text:
            _issue(issues, "TEXT_MISSING", loc, "Editable prose must have text")
            continue
        if "\ufffd" in text or any(0x80 <= ord(c) <= 0x9f for c in text):
            _issue(issues, "DAMAGED_UNICODE", loc, "Cannot accept replacement/control chars")
        if _normalise(text) not in output_text:
            _issue(issues, "TEXT_NOT_IN_DOCX", loc, "Reviewed text not found verbatim in Word OOXML")
        verified = obj.get("text_review", {})
        if not isinstance(verified, dict) or verified.get("status") != "verified" or not verified.get("source_image_ref") or not verified.get("reviewer"):
            _issue(issues, "TEXT_UNVERIFIED", loc, "Source-image proofread and reviewer attribution required")
        if not obj.get("paragraph_id") and kind == "paragraph":
            _issue(issues, "SEMANTIC_PARAGRAPH_ID_MISSING", loc, "Use stable paragraph identity")
        runs = obj.get("runs")
        if not isinstance(runs, list) or not runs:
            _issue(issues, "RUN_DIRECTION_UNCHECKED", loc, "Explicit RTL/LTR logical segments required")
        else:
            pieces = []
            for run in runs:
                if not isinstance(run, dict) or not isinstance(run.get("text"), str) or run.get("direction") not in ("rtl", "ltr"):
                    _issue(issues, "RUN_SEGMENT_INVALID", loc, "Run requires text and rtl/ltr direction")
                    continue
                t = run["text"]
                pieces.append(t)
                if ARABIC.search(t) and LATIN.search(t):
                    _issue(issues, "MIXED_SCRIPTS_IN_ONE_RUN", loc, "Separate Arabic and Latin script runs")
                if LATIN.search(t) and run["direction"] != "ltr":
                    _issue(issues, "LATIN_DIRECTION_WRONG", loc, "Latin should be isolated in an LTR run")
                if ARABIC.search(t) and run["direction"] != "rtl":
                    _issue(issues, "ARABIC_DIRECTION_WRONG", loc, "Arabic should be isolated in an RTL run")
            if _normalise("".join(pieces)) != _normalise(text):
                _issue(issues, "RUNS_TEXT_MISMATCH", loc, "Direction segmentation changed logical source text")
        typography = obj.get("typography", {})
        if not isinstance(typography, dict) or typography.get("calibration") != "measured_source_and_render":
            _issue(issues, "FONT_NOT_CALIBRATED", loc, "Font and line-height need measured source/render metrics")


def _review_ok(item) -> bool:
    return (isinstance(item, dict) and item.get("status") == "verified"
            and bool(item.get("evidence")) and bool(item.get("reviewer")))


def release_check(docx_path: str | Path, manifest_path: str | Path, *,
                  render: bool = False) -> dict:
    """Fail closed. The check validates evidence *presence*, not its truth.

    Human approval and actual Microsoft Word opening are never inferred.
    """
    from .quality import audit_docx
    docx_path = Path(docx_path)
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    issues = []
    if manifest.get("schema_version") != 1:
        _issue(issues, "SCHEMA_VERSION_UNSUPPORTED", "manifest", "Expected schema_version=1")
    if not docx_path.is_file():
        raise FileNotFoundError(docx_path)
    document_hash = sha256(docx_path.read_bytes()).hexdigest()
    if manifest.get("docx_sha256") != document_hash:
        _issue(issues, "ARTIFACT_HASH_MISMATCH", "manifest", "Review is not bound to these exact DOCX bytes")
    if not isinstance(manifest.get("source_pdf_sha256"), str) or len(manifest["source_pdf_sha256"]) != 64:
        _issue(issues, "SOURCE_FINGERPRINT_MISSING", "manifest", "Source book hash required")
    for flag in REQUIRED_REVIEWS:
        if not _review_ok(manifest.get("reviews", {}).get(flag) if isinstance(manifest.get("reviews"), dict) else None):
            _issue(issues, "REVIEW_NOT_APPROVED", f"review:{flag}", "Verified review with evidence/reviewer required")
    compatibility = manifest.get("word_compatibility", {})
    if not (isinstance(compatibility, dict) and compatibility.get("application") == "Microsoft Word"
            and compatibility.get("result") == "opened_edited_saved_without_repair"
            and compatibility.get("version") and compatibility.get("evidence")
            and compatibility.get("tested_docx_sha256") == document_hash):
        _issue(issues, "WORD_DESKTOP_NOT_VERIFIED", "compatibility",
               "Actual Microsoft Word open/edit/save test for exact file required")
    issues.extend({"code": x, "location": "docx", "detail": "Invalid Word package structure"} for x in docx_structure_warnings(docx_path))
    output_text = ""
    try:
        with ZipFile(docx_path) as z:
            root = etree.fromstring(z.read("word/document.xml"))
            output_text = _normalise("".join(node.text or "" for node in root.iter(W + "t")))
    except (BadZipFile, KeyError, etree.XMLSyntaxError):
        _issue(issues, "DOCX_TEXT_UNREADABLE", "docx", "Cannot extract Word OOXML text")
    if not output_text.strip():
        _issue(issues, "NOT_EDITABLE", "docx", "No Word text runs (image-only document)")
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        _issue(issues, "PAGES_MISSING", "manifest", "At least one page required")
        pages = []
    for n, page in enumerate(pages, 1):
        if not isinstance(page, dict) or type(page.get("source_pdf_page")) is not int or page["source_pdf_page"] < 1:
            _issue(issues, "SOURCE_PAGE_INVALID", f"page:{n}", "One-based PDF source page required")
            continue
        if page.get("background_provenance") not in ("text_removed_artwork", "no_background"):
            _issue(issues, "BACKGROUND_NOT_VERIFIED", f"page:{n}", "Avoid duplicated embedded page text")
        if page.get("reading_order_reviewed") is not True:
            _issue(issues, "READING_ORDER_UNVERIFIED", f"page:{n}", "Columns/sidebars order not signed off")
        _check_objects(page, n, output_text, issues)
    rendered_pages = None
    if not render:
        _issue(issues, "RENDER_REQUIRED", "release", "Render actual DOCX, inspect every page before release")
    else:
        audit = audit_docx(docx_path, render=True)
        rendered_pages = audit.get("rendered_page_count")
        if "DOCX_RENDER_FAILED" in audit.get("warnings", []) or rendered_pages is None:
            _issue(issues, "RENDER_FAILED", "release", "Unable to render Word document")
        elif rendered_pages != len(pages):
            _issue(issues, "PAGE_COUNT_MISMATCH", "release", f"Rendered {rendered_pages}; expected {len(pages)}")
    return {
        "decision": "BLOCKED" if issues else "ELIGIBLE_FOR_HUMAN_FINAL_APPROVAL",
        "certified_by_automation": False,
        "docx_sha256": document_hash,
        "rendered_pages": rendered_pages,
        "issues": issues,
        "issue_count": len(issues),
        "note": "Evidence attestation is not proof of source truth or actual Microsoft Word operation; final user approval remains separate.",
    }
