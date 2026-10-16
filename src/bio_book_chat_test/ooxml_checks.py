"""Catch WordprocessingML package and drawing-order errors before release."""
from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile, BadZipFile
from lxml import etree

WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"

def anchor_order_warnings(document_xml: bytes) -> list[str]:
    root = etree.fromstring(document_xml)
    issues = []
    for index, anchor in enumerate(root.iter(f"{{{WP}}}anchor"), 1):
        names = [etree.QName(child).localname for child in anchor]
        wrap = next((name for name in names if name.startswith("wrap")), None)
        required = ("simplePos", "positionH", "positionV", "extent", "docPr", "graphic")
        if not all(name in names for name in required) or wrap is None:
            issues.append(f"OOXML_ANCHOR_INCOMPLETE:{index}")
            continue
        positions = [names.index(name) for name in ("simplePos", "positionH", "positionV", "extent", wrap, "docPr", "graphic")]
        if positions != sorted(positions):
            issues.append(f"OOXML_ANCHOR_CHILD_ORDER_INVALID:{index}")
    return issues

def docx_structure_warnings(path: str | Path) -> list[str]:
    issues = []
    try:
        with ZipFile(path) as archive:
            if archive.testzip() is not None:
                return ["DOCX_ZIP_CRC_FAILED"]
            if "word/document.xml" not in archive.namelist():
                return ["DOCX_MAIN_DOCUMENT_MISSING"]
            for part in archive.namelist():
                if part.endswith((".xml", ".rels")) or part == "[Content_Types].xml":
                    try:
                        etree.fromstring(archive.read(part))
                    except etree.XMLSyntaxError:
                        issues.append(f"DOCX_INVALID_XML:{part}")
            if "DOCX_INVALID_XML:word/document.xml" not in issues:
                issues.extend(anchor_order_warnings(archive.read("word/document.xml")))
    except (OSError, BadZipFile):
        issues.append("DOCX_NOT_VALID_ZIP")
    return issues
