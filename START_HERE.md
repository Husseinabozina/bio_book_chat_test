> **UPDATE 2026-10-18:** The old `1–40 prepared, page 41 next` and `private feature branch current` statements below are HISTORICAL and OUTDATED. Actual private `main` contains `deliverables/biology-book-complete-001-080.docx`. Pages 130–150 underwent an OCR-first regression and are **unverified experiments**, not production. Current method is **source-visible-image-first, literal transcription and review, then editable Word and visual+desktop QA**. See `AGENTS.md` STOP-SHIP section. Never use unverified OCR strings as book ground truth. Check the live private HEAD and status before building.\n\n# START HERE — PDF → Word Research Lab (public, synthetic only)

> **If another model starts here, this is the RESEARCH repo, NOT the canonical user-book delivery repo.**

The user's actual biology-book PDF, page transcriptions 1–40, figures/backgrounds, and DOCX production live **only** in the separate **private** [`Husseinabozina/biology_book_to_word`](https://github.com/Husseinabozina/biology_book_to_word) repository. Open its **`feature/integrated-layout-engine-qa`** branch and **`START_HERE.md`** with authorized access first. The private [Draft PR #1](https://github.com/Husseinabozina/biology_book_to_word/pull/1) contains the improved existing compositor and candidate test pipeline; it is **not merged/accepted**.

## Source of truth hierarchy

1. PRIVATE `biology_book_to_word/START_HERE.md` and `docs/CURRENT_CHECKPOINT.json`: exact current state/branch/next step.
2. PRIVATE `docs/STATUS.md`, `content/assembly.json`, original book, current production Word: current book progress; **1–40 prepared, 0 user-approved, page 41 next** as of 2026-10-16.
3. PUBLIC `AGENTS.md`, `docs/ENGINEERING_DECISIONS.md` (ADR-01–ADR-19), `docs/QUALITY_GATES.md`: general quality contract and strict release semantics.
4. PUBLIC `docs/REAL_PAGE41_EXTERNAL_BENCHMARK_2026-10-16.md`, `docs/EXTERNAL_PDF_TO_WORD_RESEARCH_2026-10-16.md`: executed page-41 external OCR/DOCX baselines and upstream proposals.
5. PUBLIC `docs/PRODUCTION_ENGINE_REUSE_DECISION.md`: why the PRIVATE visual compositor must be reused, including measured 36–40 improvements.

## Mission, constraints, and immediate next step

- **User priority:** source PDF visual appearance as close as possible **before edits**, but real editable correct Arabic prose and Microsoft Word compatibility remain mandatory.
- Do **not** replace the layout compositor with a direct PaddleOCR/MinerU/pdf2docx exporter: tested page 41 produced missing/damaged Arabic and/or layout/overflow.
- Best private source-page 36–40 after RTL geometry/table fixes reached a **mean unregistered grayscale SSIM of 0.79451** vs 0.74383 before. It is a visual *signal*, not pass/fail acceptance; exact fonts/paragraphs still differ. True Microsoft Word Desktop open/edit/save and source image text proofreading **NOT VERIFIED**.
- **Next work:** build and review a canonical page-41 region proposal in PRIVATE repo (PDF image → potential text/illustration boxes → separately proofread text → measured editable Word), then run private `production_pipeline.py --render --compare-source` and public strict quality gate. Keep user source and unverified OCR out of `main`.
- Do **not** confuse an Actions green tick with successful OCR/model inference or a user-approved Word deliverable.
- Never commit user's source PDF, derived content, screenshots, font files, or private review evidence to this public repo.

## Copy-paste task for a future model

"Continue the user's Arabic biology PDF-to-editable-Word project. Start by reading `START_HERE.md` and `docs/CURRENT_CHECKPOINT.json` **in the private repo** `Husseinabozina/biology_book_to_word`, branch `feature/integrated-layout-engine-qa`; inspect HEAD GitHub state first. Then read `AGENTS.md` and benchmark documents here in `Husseinabozina/bio_book_chat_test`, branch `feature/pdf-word-engineering-lab`. Optimize maximum source visual fidelity while keeping text editable, Arabic source-exact, and Microsoft Word valid. No false success; work only on experimental branches, preserve 1–40 client Word, and document tests/new decisions back in GitHub."

**This README describes only existing documented/implemented components.** Future-page automatic segmentation, typography optimizer, real Word Desktop validation, and customer approval **do not currently exist**.
