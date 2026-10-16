# Repeatable experiment and acceptance process

## 0. Scope and sample
Select representative pages for Arabic prose, mixed-direction equations, photographs, multi-column sidebars, and genuine tables. The teaching-book case uses pages 7, 8, 10, 14, 16 *locally*; the original source and derived outputs must not be committed to this public repository.

## 1. Preflight (gate before writing DOCX)
Run `bio2word inspect input/book.pdf --pages 7,8,10,14,16 --report runs/preflight.json`. Verify font names, Unicode anomaly count and image-block count. If mapping is suspect, **do not** run editable as an accepted production conversion. Opt for `visual` or `hybrid`, or implement visual verification/OCR and manually review transcriptions before approving.

## 2. Run comparable strategies
Use identical source pages and rendering environment. Generate `visual`, `editable` (only when source mapping is safe), and `hybrid` outputs; never call Adobe, ABBYY, Word or Word in Chat a benchmark unless explicitly run and documented. Capture software versions, SHA-256 source fingerprint, selected page list, mode, CPU environment and font fallback.

## 3. Audit and inspect
Run `bio2word audit outputs/visual.docx --source input/book.pdf --pages 7,8,10,14,16 --render --report runs/audit.json`. Rendering requires LibreOffice. Check the Word's actual rendered page count; the prior five-page trial generated nine pages and this was a release-blocking bug, fixed in the visual mode by reserving image-line space. Then inspect every rendered page; an equal page count does not guarantee equal layout or correct text.

## 4. Review with Word in Chat
Open the DOCX in Word in Chat as a reviewer. Verify Arabic characters/hamza, RTL paragraph/run direction, parentheses and English runs, table cells, captions and graphics. Export revisions, rerun automated audit and visual QA; record what changed. Word in Chat does not guarantee the PDF extraction was correct.

## 5. Acceptance rules
- Visual mode: every selected source page corresponds to exactly one output page, no clipping, imagery legible. **Editable text is not promised.**
- Editable mode: source Unicode gate passes, native editable paragraphs exist, all source words verified against original image for accuracy, table/figure layout reviewed. **This prototype is not ready for complex textbook acceptance**.
- Hybrid mode: report lists visual and editable pages separately; do not claim all pages editable.

## 6. Issue and release
Use defect IDs from `FAILURE_POSTMORTEM.md`. In a PR, record test results and manual screenshot QA without embedding unauthorized copyrighted textbook images. No automatic merge solely because CI passes.
