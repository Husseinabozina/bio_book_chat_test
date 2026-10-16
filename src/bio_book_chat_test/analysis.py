"""PDF preflight based on actual Unicode mapping and page geometry.

A visually correct PDF may extract corrupted characters. This module detects
known failure signals and blocks silent promotion of low-quality editable text.
It does NOT claim to automatically detect every Arabic spelling error.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median
import unicodedata
import fitz


def suspicious_chars(text: str) -> list[str]:
    """Control chars/Unicode replacement visible in damaged font mappings."""
    return [c for c in text if c == "\ufffd" or (unicodedata.category(c) == "Cc" and c not in "\t\r\n")]


def page_diagnostics(page: fitz.Page, page_number: int) -> dict:
    blocks = page.get_text("dict", sort=False)["blocks"]
    spans = [s for b in blocks if b.get("type") == 0 for ln in b.get("lines", []) for s in ln.get("spans", [])]
    txt = page.get_text("text", sort=False)
    bad = suspicious_chars(txt)
    text_boxes = [b["bbox"] for b in blocks if b.get("type") == 0]
    widths = [b[2] - b[0] for b in text_boxes]
    fonts = Counter(s.get("font", "") for s in spans)
    size_samples = [round(s.get("size", 0), 1) for s in spans if s.get("size")]
    flags = []
    if bad:
        flags.append("PDF_TEXT_HAS_SUSPICIOUS_UNICODE")
    if not txt.strip():
        flags.append("PDF_PAGE_HAS_NO_EXTRACTABLE_TEXT")
    if any(b.get("type") == 1 for b in blocks):
        flags.append("PAGE_HAS_IMAGES_REQUIRING_PLACEMENT")
    if len(text_boxes) > 14 and widths and median(widths) < page.rect.width * .65:
        flags.append("COMPLEX_LAYOUT_REVIEW_RECOMMENDED")
    return {
        "page": page_number,
        "page_size_pt": [round(page.rect.width, 2), round(page.rect.height, 2)],
        "chars_extracted": len(txt),
        "suspicious_unicode_count": len(bad),
        "suspicious_unicode_examples": list(dict.fromkeys(f"U+{ord(c):04X}" for c in bad))[:12],
        "fonts": dict(fonts.most_common(12)),
        "median_font_size_pt": round(median(size_samples), 2) if size_samples else None,
        "text_blocks": sum(b.get("type") == 0 for b in blocks),
        "image_blocks": sum(b.get("type") == 1 for b in blocks),
        "flags": flags,
        "editable_text_safe": bool(txt.strip()) and not bad,
    }


def parse_pages(spec: str | None, total_pages: int) -> list[int]:
    """Human-readable one-based page spec: 2,5-7. Returns zero-based indexes."""
    if not spec:
        return list(range(total_pages))
    result = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            raise ValueError("Empty page in --pages")
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
            if start > end:
                raise ValueError(f"Descending range: {part}")
            numbers = range(start, end + 1)
        else:
            numbers = [int(part)]
        for n in numbers:
            if not 1 <= n <= total_pages:
                raise ValueError(f"Page {n} out of range 1..{total_pages}")
            if n - 1 not in result:
                result.append(n - 1)
    return result


def inspect_pdf(source: str | Path, pages: str | None = None) -> dict:
    with fitz.open(str(source)) as pdf:
        indices = parse_pages(pages, len(pdf))
        entries = [page_diagnostics(pdf[i], i + 1) for i in indices]
        return {
            "source_filename": Path(source).name,
            "source_page_count": len(pdf),
            "pages_inspected": [i+1 for i in indices],
            "page_reports": entries,
            "requires_text_review": [e["page"] for e in entries if not e["editable_text_safe"]],
            "method_note": "Unicode heuristics are a warning, not an Arabic proofreading engine.",
        }
