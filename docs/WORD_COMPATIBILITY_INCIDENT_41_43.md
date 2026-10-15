# Word could not open the 41–43 pilot (2026-10-16)

## Symptom
The user reported that Microsoft Word flagged the pilot DOCX as problematic and refused to open it. The same file had been successfully rendered through LibreOffice; this illustrates why rendering in LibreOffice alone is **not** a Microsoft Word compatibility test.

## Reproduced concrete structural defect
The hand-authored source code `bio_pages_41_43/build_41_43.py` replaced a python-docx inline image with a `wp:anchor` and appended `wp:wrapNone` **before** copying `wp:extent`. OOXML requires ordered anchor children: `simplePos → positionH → positionV → extent → (effectExtent) → wrap* → docPr → … → graphic`.

An audit of the original pilot returned:
- `OOXML_ANCHOR_CHILD_ORDER_INVALID:1`
- `OOXML_ANCHOR_CHILD_ORDER_INVALID:2`
- `OOXML_ANCHOR_CHILD_ORDER_INVALID:3`

This is a **verified document-structure error and plausible cause** of Word's warning; the exact Microsoft Word error text and a Word Desktop repair log were not available.

## Corrections and validation
1. Reordered the XML children of all three image anchors, keeping images, their coordinates and original editable VML textboxes intact.
2. Checked ZIP CRC, parsed every XML/RELS part, opened via python-docx and rendered the corrected file through LibreOffice.
3. The corrected document rendered as three pages, pixel-identical to the earlier LibreOffice output. Its OOXML anchor-order warnings were empty.
4. Prepared a second **compatibility-first** DOCX from standard python-docx text paragraphs, tables and inline pictures, **without floating VML text boxes or custom image anchors**. It rendered as three pages and passed the same structural checks. Its layout differs from the source.

## Prevention
- Added `ooxml_checks.py` and integrated its checks with `audit_docx`.
- Added synthetic regression tests for valid and invalid anchor sequence.
- Before any delivery, check package integrity, OOXML element ordering, images and text, renderer output, and **when possible test Microsoft Word directly**.
- No claim of Word Desktop compatibility until someone actually opens the fixed file in Word; structural validation reduces but does not eliminate that risk.

## Scope
This change is on the experimental PR branch only; it does not merge into `main`. The original copyrighted source PDF and output binaries are not checked into the public repository.
