"""Reproducible conversion with explicit fidelity / editability tradeoffs.

Modes:
- visual: one high resolution source-page image per Word page. NOT editable.
- editable: native Word text and detected raster images; fails on suspect Unicode
  unless explicitly overridden. Layout is heuristic, NOT pixel-perfect.
- hybrid: page-by-page auto fallback to visual when text extraction fails gate.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re
import fitz
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from .analysis import page_diagnostics, parse_pages

ARABIC = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]")


def set_rtl(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    ppr = paragraph._p.get_or_add_pPr()
    bidi = ppr.find(qn("w:bidi"))
    if bidi is None:
        bidi = OxmlElement("w:bidi")
        ppr.append(bidi)
    bidi.set(qn("w:val"), "1")


def set_run_rtl(run, value: bool) -> None:
    rpr = run._r.get_or_add_rPr()
    rtl = rpr.find(qn("w:rtl"))
    if rtl is None:
        rtl = OxmlElement("w:rtl")
        rpr.append(rtl)
    rtl.set(qn("w:val"), "1" if value else "0")


def add_mixed_runs(paragraph, text: str, font_size: float = 12.0) -> None:
    """Split Arabic/non-Arabic script segments; no manual string reversal.

    Punctuation in mixed RTL/LTR spans still requires final visual inspection.
    """
    chunks = re.findall(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\s]+|[^\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\s]+", text)
    for chunk in chunks:
        run = paragraph.add_run(chunk)
        run.font.size = Pt(max(7, min(font_size, 28)))
        if ARABIC.search(chunk):
            run.font.name = "Arial"
            set_run_rtl(run, True)
        else:
            run.font.name = "Arial"
            set_run_rtl(run, False)


def _new_doc(page: fitz.Page) -> Document:
    doc = Document()
    s = doc.sections[0]
    s.page_width = Pt(page.rect.width)
    s.page_height = Pt(page.rect.height)
    for edge in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(s, edge, Pt(10))
    norm = doc.styles["Normal"]
    norm.font.name = "Arial"
    norm.font.size = Pt(12)
    norm.paragraph_format.space_before = Pt(0)
    norm.paragraph_format.space_after = Pt(0)
    norm.paragraph_format.line_spacing = 1.0
    return doc


def _set_zero_para(p) -> None:
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1


def _visual_page(doc: Document, page: fitz.Page, dpi: int = 150, page_break_before: bool = False) -> None:
    png = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72), alpha=False).tobytes("png")
    p = doc.add_paragraph()
    _set_zero_para(p)
    p.paragraph_format.page_break_before = page_break_before
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # A Word picture is an inline glyph inside a paragraph: the line also has
    # ascent/descent and must not exactly fill the writable page height.
    # Reserve extra vertical space or a trailing spill/blank page is created.
    available_w = page.rect.width - 40
    available_h = page.rect.height - 60
    scale = min(available_w/page.rect.width, available_h/page.rect.height)
    p.add_run().add_picture(BytesIO(png), width=Pt(page.rect.width * scale), height=Pt(page.rect.height * scale))


def _editable_page(doc: Document, page: fitz.Page, page_break_before: bool = False) -> dict:
    """Editable baseline with blocks in reading order and extracted figure clips.

    It deliberately does not claim faithful sidebars or editable vector charts.
    """
    info = page.get_text("dict", sort=False)
    items = [b for b in info["blocks"] if b.get("type") in (0, 1)]
    # Primarily top-to-bottom. Within a horizontal band prefer right-to-left.
    items.sort(key=lambda b: (round(b["bbox"][1]/12), -b["bbox"][0], b["bbox"][1]))
    paragraphs, figures = 0, 0
    is_first = True
    for block in items:
        if block["type"] == 1:
            bbox = fitz.Rect(block["bbox"]) & page.rect
            if bbox.is_empty or bbox.width < 15 or bbox.height < 15:
                continue
            pix = page.get_pixmap(matrix=fitz.Matrix(2,2), clip=bbox, alpha=False)
            p = doc.add_paragraph()
            _set_zero_para(p)
            if is_first:
                p.paragraph_format.page_break_before = page_break_before
                is_first = False
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            avail_w = page.rect.width - 30
            p.add_run().add_picture(BytesIO(pix.tobytes("png")), width=Pt(min(bbox.width, avail_w)))
            figures += 1
            continue
        lines = block.get("lines", [])
        line_strings = []
        all_sizes = []
        for line in lines:
            spans = line.get("spans", [])
            content = "".join(s.get("text", "") for s in spans).strip()
            if content:
                line_strings.append(content)
                all_sizes.extend(s.get("size", 12) for s in spans)
        if not line_strings:
            continue
        p = doc.add_paragraph()
        _set_zero_para(p)
        if is_first:
            p.paragraph_format.page_break_before = page_break_before
            is_first = False
        set_rtl(p)
        # Lines in the same PDF block form one flowing Word paragraph.
        # Keep explicit line breaks only when text looks like a short isolated label.
        text = " ".join(line_strings)
        size = sum(all_sizes)/len(all_sizes) if all_sizes else 12
        add_mixed_runs(p, text, size)
        paragraphs += 1
    return {"editable_paragraphs": paragraphs, "figure_clips": figures}


def convert_pdf(source: str | Path, target: str | Path, *, pages: str | None = None,
                mode: str = "hybrid", dpi: int = 150, allow_suspect_text: bool = False) -> dict:
    if mode not in {"editable", "hybrid", "visual"}:
        raise ValueError("mode must be editable, hybrid or visual")
    with fitz.open(str(source)) as pdf:
        indices = parse_pages(pages, len(pdf))
        if not indices:
            raise ValueError("No pages selected")
        diagnostics = [page_diagnostics(pdf[i], i+1) for i in indices]
        if mode == "editable" and not allow_suspect_text:
            blocked = [d["page"] for d in diagnostics if not d["editable_text_safe"]]
            if blocked:
                raise ValueError(f"Unsafe extracted Unicode on pages {blocked}; review/OCR first or use --mode hybrid/visual (override: --allow-suspect-text)")
        doc = _new_doc(pdf[indices[0]])
        records = []
        for j, idx in enumerate(indices):
            page = pdf[idx]
            safe = diagnostics[j]["editable_text_safe"]
            page_mode = "visual" if (mode == "visual" or (mode == "hybrid" and not safe)) else "editable"
            if page_mode == "visual":
                _visual_page(doc, page, dpi, page_break_before=bool(j))
                details = {"editable_paragraphs": 0, "figure_clips": 0}
            else:
                details = _editable_page(doc, page, page_break_before=bool(j))
            records.append({"page": idx+1, "page_mode": page_mode, "warnings": diagnostics[j]["flags"], **details})
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(target))
        return {
            "source": Path(source).name, "output": str(target), "mode": mode,
            "pages": records, "editable_pages": sum(p["page_mode"]=="editable" for p in records),
            "visual_pages": sum(p["page_mode"]=="visual" for p in records),
            "limitations": "Visual pages are not editable; editable layout is heuristic; review punctuation, columns, tables and images in Word."
        }
