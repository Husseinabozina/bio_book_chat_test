# Engineering contract for coding agents

**NEW SESSION REQUIRED FIRST READ:** [START_HERE.md](START_HERE.md). This is a public research repository; the actual book and current per-page source data are private in `biology_book_to_word` and MUST NOT be copied here.


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

## External engine selection / research contract (2026-10-16)

Read [docs/EXTERNAL_PDF_TO_WORD_RESEARCH_2026-10-16.md](docs/EXTERNAL_PDF_TO_WORD_RESEARCH_2026-10-16.md) before proposing or writing another full PDF→Word converter. **Benchmark PaddleOCR PP-StructureV3/VL and MinerU 4 DOCX exporters against the SAME user-approved pages before reinventing OOXML.** Use pdf2docx as an independent baseline only when documenting Unicode corruption. Do not confuse an upstream model's benchmark, an OCR-only text score, or a successful DOCX export with layout/editability/Word compatibility success. Check model-weight and code licenses independently.
Use `bio2word benchmark-ocr runs/source_verified.json runs/ocr_candidate.json --report runs/ocr_score.json` on private image-reviewed text; never add copyrighted source text to public tests. Record every tool's actual installed version and source/output SHA.

## User-mandated target and page-41 evidence (ADR-19)

**VISUAL FIDELITY FIRST:** Word must reproduce the original PDF appearance as closely as practically possible **before edits**, while preserving independently verified correct Arabic text, real editable prose and Microsoft Word file compatibility. Perfect reflow when users rewrite paragraphs is a lower priority. Semantic **paragraph-level** positioned frames are acceptable when tested; do not use fragile independent per-line textboxes as a default. Never replace an editable page with a full page screenshot.

Real third-party engine execution and rejection criteria: [page-41 measured benchmark](docs/REAL_PAGE41_EXTERNAL_BENCHMARK_2026-10-16.md). PaddleOCR PP-StructureV3, MinerU Basic and pdf2docx were **ACTUALLY RUN** on page 41, and none is acceptable as a complete direct-to-DOCX exporter. Each future engine must be separately judged for Arabic accuracy, layout, editing and viewer compatibility; a green workflow is not proof an embedded engine ran successfully.
