"""Regression for a DOCX accepted by LibreOffice but flagged by Microsoft Word.

The 41-43 trial erroneously emitted wp:wrapNone BEFORE wp:extent in CT_Anchor.
"""
from docx import Document
from bio_book_chat_test.ooxml_checks import anchor_order_warnings,docx_structure_warnings

WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
GOOD = ["simplePos", "positionH", "positionV", "extent", "wrapNone", "docPr", "graphic"]
BAD = ["simplePos", "positionH", "positionV", "wrapNone", "extent", "docPr", "graphic"]

def xml_with_anchor(order):
    return (f'<root xmlns:wp="{WP}"><wp:anchor>' + ''.join(f'<wp:{x}/>' for x in order) + '</wp:anchor></root>').encode()

def test_reject_word_anchor_with_wrap_before_extent():
    assert anchor_order_warnings(xml_with_anchor(BAD)) == ["OOXML_ANCHOR_CHILD_ORDER_INVALID:1"]

def test_accept_correct_word_anchor_order():
    assert not anchor_order_warnings(xml_with_anchor(GOOD))

def test_standard_docx_package_is_valid(tmp_path):
    path=tmp_path/"standard.docx"
    d=Document()
    d.add_paragraph("كتاب الأحياء")
    d.save(path)
    assert not docx_structure_warnings(path)

def test_broken_zip_is_detected(tmp_path):
    path=tmp_path/"not_a_docx.docx"
    path.write_bytes(b"not a zip")
    assert "DOCX_NOT_VALID_ZIP" in docx_structure_warnings(path)
