# Pilot: editable reconstruction of consecutive PDF pages 41–43 (2026-10-16)

## What was actually built

Three consecutive PDF pages 41, 42 and 43 from the biology textbook were converted to one three-page DOCX. Page layout was rendered and reviewed in LibreOffice. The result has 77 editable text-line boxes and three editable page numbers plus three preserved original artwork backgrounds. This is an experimental deliverable, NOT a pixel-perfect or independently character-perfect conversion.

## Source-driven procedure

1. Render the three source pages for visual reference.
2. Read original text span coordinates from PyMuPDF but do NOT trust the glyph text from AXtYasmineLight: it yields damaged Unicode.
3. Transcribe visible prose against source page images, recording a source-to-output line ledger.
4. Remove ordinary text drawing operators BT ... ET from copied PDF page streams, then render clean backgrounds. This keeps original scientific figures, colors and sidebar artwork without duplicating page prose.
5. Rebuild editable Arabic runs inside absolutely positioned Word textboxes at measured PDF coordinates on pages sized 595.276 x 841.89 points; use background artwork anchored behind.
6. Render generated DOCX to PDF/PNG and inspect EVERY page. The first run had line wrapping and overlaps; fix specifically affected line sizes, re-render, and recheck.
7. Preserve coordinates, substitute font size, review status and output SHA256 as machine-readable run artifacts outside this public repository.

## Verified

- Source pages 41, 42, 43, uninterrupted.
- Word render: exactly 3 pages.
- OOXML contains real text runs in 77 independently editable boxes, not an all-image conversion.
- Source graphics and shaded sidebar backgrounds remain intact.
- No U+FFFD character or known control glyph from the broken PDF text extraction in entered text.
- Visual review of every produced page was performed in LibreOffice.

## Open defects and limitations

- Substituted Amiri font metrics differ from source AXtYasmineLight; some lines appear narrower or smaller than the original.
- Text is segmented into editable lines, not full flowing paragraphs. Significant edits require resizing/reflowing the boxes.
- Diagram labels and footer artwork stay inside non-editable images.
- An independent word-by-word source proofread has NOT been finished; text accuracy is not certified.
- English parentheses, scientific subscript fidelity, Microsoft Word Desktop and Apple Pages rendering are NOT fully verified.
- The workflow is not a general automatic OCR converter.

## Next gates

- Store verified paragraph-level semantic text and source rectangles independently.
- Add a source-image spellcheck ledger and abstain when text is uncertain.
- Score each object bounding-box drift against the source and set tolerances.
- Explicitly isolate LTR segments, numeric references and mixed parentheses; test in multiple renderers.
- Preserve artifacts in a private or untracked folder; no source copyrighted textbook content should be committed publicly.
- Keep text accuracy, editability, layout fidelity and viewer compatibility as FOUR separate reported gates.

## Behavioral correction

A successful command, test suite or page count is NOT evidence of acceptable content fidelity. The delivered file must be rendered, inspected, independently text-reviewed and explicitly qualified before anyone calls it a faithful conversion.
