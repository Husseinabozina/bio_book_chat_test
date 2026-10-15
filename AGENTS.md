# Engineering contract for coding agents

This repository is a quality-controlled research prototype, not an OCR product. Follow these rules for every contribution:

1. **Inspect before converting**: run `inspect` and store a run report outside version control. Do not assume PDF text streams are correct, especially Arabic custom-font encodings.
2. **Separate goals**: report spelling/text accuracy, editable content, and visual fidelity independently. Never call an image-only DOCX editable.
3. **Fail closed**: never bypass Unicode source warnings in production. The unsafe override is for experiments only. Do not fix Arabic by blind character replacement or invent text.
4. **RTL matters**: retain logical string order; use OOXML paragraph `w:bidi` and run `w:rtl`, then visually inspect mixed Latin, numbers, parentheses, and formulae.
5. **Treat layout as structured data**: preserve reading order, sidebars, figures, captions, equations and editable tables independently; do not convert all PDF lines into separate Word paragraphs.
6. **Render every DOCX**: at minimum verify page count, inspect all rendered pages, and record the rendering engine and font availability. Any unexpected overflow page is a failing regression.
7. **Test all changes**: use synthetic PDFs for unit tests; add a regression for every defect. CI cannot claim visual perfection, so note manual checks explicitly.
8. **Do not commit book pages, derived PDF/DOCX, screenshots, or raw copyrighted text to this public repository**. Only code, documentation, anonymized metrics and synthetic fixtures belong here.
9. **Report evidence and limitations**: every benchmark must list method, source page selection, code revision, accepted/failed checks, and unresolved issues. Avoid claiming plugins/tools were used unless executed.
10. **Never silently replace a user's original file**. Work on an isolated branch, describe changes in the PR and require review.

Workflow: `inspect → select explicit strategy → convert → audit --render → compare visually → review text with source image → document defects → iterate`. See `docs/WORKFLOW.md`.
