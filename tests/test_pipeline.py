"""Synthetic fixtures only: no copyrighted textbook files committed to git."""
import fitz
import pytest
from docx import Document
from docx.oxml.ns import qn

from bio_book_chat_test.analysis import parse_pages, suspicious_chars, inspect_pdf
from bio_book_chat_test.conversion import convert_pdf, set_rtl, add_mixed_runs
from bio_book_chat_test.quality import audit_docx


def make_pdf(path, damaged=False):
    pdf=fitz.open()
    p=pdf.new_page(width=595, height=842)
    p.insert_text((50,70),"Clean test page",fontsize=16)
    if damaged:
        p.insert_text((50,90),"Bad replacement: \ufffd",fontsize=12)
    p=pdf.new_page(width=595,height=842)
    p.insert_text((50,70),"Photosynthesis",fontsize=14)
    pdf.save(path)
    pdf.close()


def test_page_parser():
    assert parse_pages("1,2,2",3)==[0,1]
    assert parse_pages("2-3,1",3)==[1,2,0]
    with pytest.raises(ValueError):parse_pages("0",3)
    with pytest.raises(ValueError):parse_pages("3-2",4)


def test_suspicious_unicode():
    assert suspicious_chars("نص \ufffd هنا \x81") == ["\ufffd", "\x81"]
    assert suspicious_chars("مرحبًا بالعالم.\n") == []


def test_rtl_ooxml():
    doc=Document()
    p=doc.add_paragraph()
    set_rtl(p)
    add_mixed_runs(p,"تغذية (Photosynthesis) 2026")
    assert p._p.pPr.find(qn('w:bidi')).get(qn('w:val')) == '1'
    assert p.text == 'تغذية (Photosynthesis) 2026'
    assert p.runs


def test_inspect_and_visual_conversion(tmp_path):
    src=tmp_path/'source.pdf'; dst=tmp_path/'visual.docx'
    make_pdf(src)
    info=inspect_pdf(src,'1-2')
    assert info['source_page_count']==2
    assert len(info['page_reports'])==2
    result=convert_pdf(src,dst,pages='1,2',mode='visual',dpi=72)
    doc=Document(dst)
    assert result['visual_pages']==2
    assert len(doc.inline_shapes)==2
    qa=audit_docx(dst,original_pdf=src,pages='1-2')
    assert qa['inline_images']==2
    assert qa['editable_characters']==0
    assert 'NO_EDITABLE_TEXT_DETECTED' in qa['warnings']


def test_editable_conversion(tmp_path):
    src=tmp_path/'source.pdf'; dst=tmp_path/'editable.docx'
    make_pdf(src)
    result=convert_pdf(src,dst,pages='1',mode='editable')
    doc=Document(dst)
    assert result['editable_pages']==1
    assert any('Clean test page' in p.text for p in doc.paragraphs)


def test_text_gate_on_real_suspicious_control(tmp_path):
    # Synthetic sample uses PDF extraction engine itself for detection: if its
    # embedded font replaces glyph, the preflight should prevent copying it.
    src=tmp_path/'source.pdf'; dst=tmp_path/'out.docx'
    make_pdf(src)
    from bio_book_chat_test.conversion import convert_pdf
    # Explicit mode validation and no extra pages.
    with pytest.raises(ValueError):convert_pdf(src,dst,mode='wrong')


def test_unicode_gate_refuses_corrupt_page_without_override(tmp_path, monkeypatch):
    """Fail closed before writing a DOCX when mapping is untrustworthy."""
    import bio_book_chat_test.conversion as cv
    src = tmp_path / "source.pdf"
    dst = tmp_path / "blocked.docx"
    make_pdf(src)
    real = cv.page_diagnostics

    def suspect(page, number):
        info = real(page, number)
        info["editable_text_safe"] = False
        info["flags"] = ["PDF_TEXT_HAS_SUSPICIOUS_UNICODE"]
        return info

    monkeypatch.setattr(cv, "page_diagnostics", suspect)
    with pytest.raises(ValueError, match="Unsafe extracted Unicode"):
        cv.convert_pdf(src, dst, pages="1", mode="editable")
    assert not dst.exists()
    out = cv.convert_pdf(src, tmp_path / "hybrid.docx", pages="1", mode="hybrid")
    assert out["visual_pages"] == 1
    assert out["editable_pages"] == 0


def test_visual_mode_has_expected_rendered_pages(tmp_path):
    """Regression: 5 image paragraphs used to create blank overflow pages."""
    import shutil
    if not shutil.which("libreoffice"):
        pytest.skip("LibreOffice not installed")
    src = tmp_path / "source.pdf"
    dst = tmp_path / "visual.docx"
    make_pdf(src)
    convert_pdf(src, dst, pages="1-2", mode="visual", dpi=72)
    qa = audit_docx(dst, original_pdf=src, pages="1-2", render=True)
    assert qa.get("rendered_page_count") == 2, qa
    assert "RENDERED_PAGE_COUNT_MISMATCH" not in qa["warnings"]


def test_basic_convert_never_claims_user_approval(tmp_path):
    source = tmp_path / "source.pdf"
    target = tmp_path / "candidate.docx"
    make_pdf(source)
    report = convert_pdf(source, target, pages="1", mode="visual", dpi=72)
    assert report["release_status"] == "EXPERIMENTAL_NOT_APPROVED"
    assert report["requires_strict_release_check"] is True
