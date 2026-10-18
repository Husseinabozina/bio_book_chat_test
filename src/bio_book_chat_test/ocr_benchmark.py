"""Independent Arabic OCR benchmark: word and character error rates.

The reference MUST be source-image-verified; no library's output is ground truth.
This evaluates extracted TEXT ONLY, not DOCX typography/layout/editability.
Never normalize hamzas away. Input text is private and not committed publicly.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import unicodedata


def _levenshtein(a: str | list[str], b: str | list[str]) -> int:
    if len(b) > len(a):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for index, character in enumerate(a, 1):
        current = [index]
        for column, other in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[column] + 1,
                               previous[column - 1] + (character != other)))
        previous = current
    return previous[-1]


def _source_pages(data: dict, *, require_verified: bool) -> dict[int, str]:
    pages = data.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("Each input must contain a nonempty pages array")
    result = {}
    for page in pages:
        if not isinstance(page, dict) or type(page.get("source_page")) is not int or page["source_page"] < 1:
            raise ValueError("Every page needs a positive integer source_page")
        number = page["source_page"]
        if number in result:
            raise ValueError(f"Repeated source_page {number}")
        value = page.get("text")
        if not isinstance(value, str):
            raise ValueError(f"Missing text for page {number}")
        if require_verified and (page.get("verified_from_image") is not True
                                 or not page.get("reviewer")
                                 or not page.get("source_image_ref")):
            raise ValueError(f"Page {number} has no independently verified source image ground truth")
        result[number] = value
    return result


def _nfc(s: str) -> str:
    # Canonical Unicode only. Do not drop U+0623/0625/U+0622, punctuation or tashkeel.
    return unicodedata.normalize("NFC", s.replace("\r\n", "\n"))


def compare_ocr_json(reference_path: str | Path, candidate_path: str | Path) -> dict:
    """Compare two page-aware JSON manifests with original PDF 1-based page numbers."""
    reference = json.loads(Path(reference_path).read_text(encoding="utf-8"))
    candidate = json.loads(Path(candidate_path).read_text(encoding="utf-8"))
    reference_pages = _source_pages(reference, require_verified=True)
    candidate_pages = _source_pages(candidate, require_verified=False)
    if not candidate.get("engine") or not candidate.get("version"):
        raise ValueError("Candidate must record engine and installed version")
    per_page = []
    sum_ref_chars = sum(len(_nfc(t)) for t in reference_pages.values())
    sum_ref_words = sum(len(_nfc(t).split()) for t in reference_pages.values())
    sum_ce = 0
    sum_we = 0
    for page_id, expected in sorted(reference_pages.items()):
        hypothesis = candidate_pages.get(page_id, "")
        e, h = _nfc(expected), _nfc(hypothesis)
        char_distance = _levenshtein(e, h)
        word_distance = _levenshtein(e.split(), h.split())
        sum_ce += char_distance
        sum_we += word_distance
        per_page.append({
            "source_page": page_id,
            "candidate_missing": page_id not in candidate_pages,
            "reference_characters": len(e),
            "character_edits": char_distance,
            "cer": char_distance / max(len(e), 1),
            "reference_words": len(e.split()),
            "word_edits": word_distance,
            "wer": word_distance / max(len(e.split()), 1),
            "exact_text_match": e == h,
        })
    missing = sorted(set(reference_pages) - set(candidate_pages))
    extra = sorted(set(candidate_pages) - set(reference_pages))
    return {
        "engine": candidate["engine"], "version": candidate["version"],
        "source_pdf_sha256": reference.get("source_pdf_sha256"),
        "source_pages": sorted(reference_pages),
        "missing_pages": missing, "unexpected_pages": extra,
        "micro_cer": sum_ce / max(sum_ref_chars, 1),
        "micro_wer": sum_we / max(sum_ref_words, 1),
        "per_page": per_page,
        "document_layout_fidelity": "NOT_EVALUATED_BY_TEXT_BENCHMARK",
        "docx_editability": "NOT_EVALUATED_BY_TEXT_BENCHMARK",
        "microsoft_word_compatibility": "NOT_EVALUATED_BY_TEXT_BENCHMARK",
        "approved": False,
    }
