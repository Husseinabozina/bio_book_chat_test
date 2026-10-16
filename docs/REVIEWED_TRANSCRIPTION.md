# Reviewed image transcription (editable DOCX)

This mode addresses PDFs whose embedded Arabic fonts expose corrupt Unicode. It is **not OCR magic**: a reviewer supplies text verified against a rendered source image, and the pipeline places that text in real Word paragraphs. It never treats a page screenshot as proof of editability.

## Evidence from October 2026 five-page prototype

- Selected source pages: 140, 145, 149, 155, 160 (chapter: transport).
- Direct PDF extraction contained malformed characters; independent OCR also garbled Latin terms, hamzas and some numbers.
- Main prose was transcribed/corrected with source images as authority, using PDF extraction as an aid.
- Figures were cropped at source resolution and kept as **non-editable pictures**. Headings, captions, ordinary paragraphs, and the blue knowledge sidebar were built as native Word text.
- First crop attempt used coordinates from a 1024-pixel *display preview* against a 1608-pixel file; crops were wrong. Fix: use source-image pixel dimensions, or preferably use `crop_pdf_pt` measured directly in PDF points.
- First RTL heading style anchored text to the left in LibreOffice when the run began with numbers. Workaround tested: physical right alignment without paragraph-level bidi on headings. Paragraph RTL retained for ordinary prose.
- Wrapped multi-word English scientific terms caused reversed fragments around parentheses. Use non-breaking spaces inside LTR runs and **inspect every render**; complex punctuation still needs review.
- Final local DOCX produced **five rendered pages** using LibreOffice and contained 5 image elements, 2 Word tables used for layout, and thousands of editable Arabic characters. Rendering/page count do not prove exact word accuracy.

The test document is not committed to this *public* repository. Book material stays local and must not enter tests or fixtures.

## Schema and usage

```json
{
  "input_pdf": "../input/book.pdf",
  "pages": [
    {"source_page": 30, "blocks": [
      {"kind": "heading", "text": "عنوان راجعه إنسان"},
      {"kind": "paragraph", "text": "نص تمت مراجعته على صورة الصفحة"},
      {"kind": "figure", "source_page": 30, "crop_pdf_pt": [32, 100, 530, 400], "width_in": 6.3},
      {"kind": "caption", "text": "شكل توضيحي"},
      {"kind": "table", "header": true, "rows": [["العنصر", "الصيغة"], ["الماء", "H2O"]]}
    ]}
  ]
}
```

Run via CLI:

```bash
bio2word reviewed runs/checked.json outputs/checked.docx --report runs/reviewed-report.json
bio2word audit outputs/checked.docx --render --report runs/audit.json
```

Or via Python:

```python
from bio_book_chat_test.reviewed import render_reviewed_manifest
report = render_reviewed_manifest("runs/checked.json", "outputs/checked.docx")
print(report)
```

Supported blocks: `heading`, `paragraph`, `sidebar`, `caption`, `figure` (external image or PDF crop), `image_text_row`, and editable `table` (rectangular `rows` arrays; optional `header`). A PDF crop is expressed in **PDF points** (not rendered image pixels). Supports page-specific sections, explicit RTL in Word, and Latin-term runs. The pipeline rejects Unicode replacement characters and unexpected controls. Review content yourself; it cannot infer lost words from a corrupted PDF.

## Quality gate for each page

1. Render original source at 200+ DPI and inspect the actual page.
2. Get text/layout from PDF, OCR or a visual reader; do **not** accept any one as ground truth.
3. Correct manually or via source-grounded visual review; mark doubtful technical terms explicitly.
4. Rebuild editable elements. Figure internals stay raster unless independently reconstructed.
5. Render DOCX with Word/LibreOffice; inspect all output pages for clipped figures, unexpected blank pages, direction, parentheses, and typography.
6. Compare character-by-character where a validated reference transcription exists, and compare layout with source screenshots.
7. Report word accuracy and visual fidelity as **unmeasured** unless actually measured. Do not claim pixel-perfect similarity, complete editability, or verified Arabic spelling from the page count alone.

Known gaps: `reviewed.py` is a simple sequential document writer, not a full absolute-position compositor. Table extraction/recoding, exact font metrics, page overflow recovery, automatic transcription and equation reconstruction remain pending.

A Word table is editable, but source row/column detection is **not automatic**: a reviewer must explicitly reconstruct the rows and verify every cell. Font matching remains approximate.
