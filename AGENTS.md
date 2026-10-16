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

## Non-optional shipping protocol (ADR-01 … ADR-18)

Read [docs/ENGINEERING_DECISIONS.md](docs/ENGINEERING_DECISIONS.md) before implementing another page. A successfully created DOCX is a **candidate**, not a release. Do not declare any file ready because LibreOffice rendered it or GitHub tests passed.

- New conversion scripts MUST call the package quality/release gate on **the exact DOCX delivered**. A one-off script that skips the gate is explicitly experimental and cannot be labeled final.
- Keep source transcriptions and per-element layout measurements in a private, reviewable intermediate page model. Preserve semantic paragraphs (not 77 independent PDF line boxes); identify figure/table exceptions honestly.
- Do not invent source headers, titles, page numbers, or footers. Do not change apparent spelling errors without an attributed source review.
- Maintain separate review evidence for correct Arabic including hamzas, precise typography, rendered geometry, image provenance, mixed RTL/LTR runs, editability, and Word Desktop compatibility.
- Run `bio2word release-check outputs/candidate.docx runs/private_evidence.json --render --report runs/release.json`. Exit code **3 means blocked**. Neither `--allow-suspect-text` nor an assumed pass is permitted as a shipping override.
- The gate may return `ELIGIBLE_FOR_HUMAN_FINAL_APPROVAL`, which is NOT user approval and NOT mathematical proof the evidence is truthful. Explicit end-user acceptance is an additional requirement.
- Never commit original book pages, copyrighted transcriptions, or private source-review evidence to this public repository.
- Any newly observed failure must be tied to a regression; if required checks cannot run (for example Microsoft Word Desktop), report status as **NOT VERIFIED** and withhold a final-fidelity claim.
