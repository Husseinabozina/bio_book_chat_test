# Real page-41 external baseline outcomes — 2026-10-16

**Status:** ACTUAL EXECUTED RESULTS, NOT ACCEPTED CONVERSION.
Source: private original biology textbook (232 pages), PDF physical page **41 (1-based)**. Source SHA256 `1844cccd287aa49647e04f81e816c1e57229cc9bf43cf816243fe675a6e9801f`. No original page or copyrighted output is committed to this public repository.

## What was actually run

| Candidate | Method | Rendered DOCX pages | Word text chars (screening, not proven correct) | SSIM full original page | Outcome |
| --- | --- | ---: | ---: | ---: | --- |
| Existing repaired three-page pilot, page 41 | Hand-built editable line textboxes + artwork | 3 pages for three PDF source pages | Thousands across all 3 pages | **0.9011** | Best visual score but textbox-per-line, independent Arabic proofreading and Microsoft Word Desktop unverified |
| Existing compatibility-first pilot, page 41 | Native simple paragraphs/inline pictures | 3 pages for three PDF pages | Thousands across all 3 pages | 0.6926 | Layout drift, large blank spaces; Word Desktop unverified |
| pdf2docx | Plain PDF content extraction -> Word | **2** for one source page | **706** | 0.7606 | Arabic glyph-to-Unicode corruption, extra page. Rejected. |
| MinerU 4 basic forced OCR | CPU Basic tier -> unified document -> DOCX | 1 | **56** | 0.7434 | Kept diagram image, lost almost entire top Arabic prose. Rejected as direct exporter. |
| PaddleOCR 3.5 PP-StructureV3 `lang=ar` with PaddlePaddle CPU **3.2.2** | OCR/layout -> DOCX | 1 | **431** | 0.7221 | Kept diagram; Arabic/Latin merged, missing spaces and vocabulary errors, shifted layout. Rejected as direct exporter. |
| Tesseract ara+eng | Local image OCR only | n/a | n/a | n/a | Detects some Arabic; visibly corrupts small figure labels/terms. Not a Word exporter and **no reliable CER** measured. |

**Important:** Word-text characters are counted in OOXML `w:t`, not semantic editable accuracy and not exact source coverage. Diagram labels remain part of non-editable raster images in all shown outputs. Existing repaired/compatible character counts cover 3 pages, not page 41 exclusively.

## SSIM comparison method and boundaries

- Original PDF physical page 41 and **first** rendered Word page were rasterized at **144 dpi** through PyMuPDF, then compared in grayscale. Word candidates were rendered with LibreOffice, and resized to original page pixels if page format drifted.
- This was **unregistered** grayscale SSIM, so geometry offsets/whitespace dominate, figures can inflate score, and no threshold should certify a candidate. Crops on top prose and diagram were also recorded privately. SSIM is **not** CER, WER, editing quality or Microsoft Word interoperability.
- Source transcriptions have not yet undergone independent source-image signoff: CER/WER not claimable.
- Word Desktop open-edit-save was not run: interoperability **NOT VERIFIED**.

## Proven reproducible private CI experiments

- pdf2docx original: [GitHub run 38837946947](https://github.com/Husseinabozina/biology_book_to_word/actions/runs/38837946947)
- PaddleOCR installation extras mistake: same run, engine **FAILED** despite green workflow. Logged pipeline error about needing `paddlex[ocr]`.
- PaddleOCR CPU/PIR oneDNN fault: [run 38838222794](https://github.com/Husseinabozina/biology_book_to_word/actions/runs/38838222794), failure at inference after dependencies installed. `NotImplementedError: ConvertPirAttribute2RuntimeAttribute … pir::ArrayAttribute<pir::DoubleAttribute>`.
- PaddleOCR after downgrading to PaddlePaddle CPU 3.2.2: [run 38838496601](https://github.com/Husseinabozina/biology_book_to_word/actions/runs/38838496601), **RAN**, generated DOCX.
- MinerU 4 basic: [run 38838380904](https://github.com/Husseinabozina/biology_book_to_word/actions/runs/38838380904), **EXECUTED**, generated DOCX but top prose missing.
- Private workflows/scripts: `biology_book_to_word:experiment/page41-external-engines` and `biology_book_to_word:experiment/page41-mineru-basic`; private raw outputs/artifacts have 7-day retention.
- **Corrected green-CI anti-pattern:** first experiments caught per-engine exceptions and printed FAILED while returning exit 0. Scripts now exit nonzero on engine-level failure, while `if: always()` retains failure artifacts.

## Decision from user priorities

**Visual fidelity to the original PDF is the top design objective, subject to mandatory correct original Arabic Unicode, real editable prose and a DOCX that opens and saves in Microsoft Word.** Native paragraph flexibility/reflow is a secondary preference, not grounds to accept larger visual drift. Paragraph-level positioned blocks and constrained editing are allowed if they meet text editability, visual fidelity and Word compatibility; avoid the old per-line textbox anti-pattern without blindly forbidding floating elements.

**Direct output from PaddleOCR, MinerU basic, and pdf2docx does not satisfy the project as-is.** Do not equate one-page output or CI green with success.

## Next test, constrained by evidence

1. Create a **human-reviewed page-41 ground truth** (Arabic letters/hamzas and Latin terms) and per-object layout rectangles linked to source screenshot. Never use one converter as truth.
2. Compare OCR of cropped body/text (PaddleOCR, Tesseract and optionally Arabic-Nougat or PaddleOCR-VL) on **CER/WER**. MinerU Basic is not currently a viable direct text exporter.
3. Compare structured-layout candidates on region/caption/table placement independently of OCR. Preserve diagram pixels but annotate in-figure labels as non-editable unless explicitly reconstructed.
4. Build a **one-page visual-fidelity-first Word compositor**, with paragraph-level (not line-level) placements, calibrated fonts and valid OOXML anchors. Benchmark against current 0.9011 **visual score** while improving text review and natural block editing.
5. Require real Microsoft Word open/edit/save for exact DOCX hash before declaring a deliverable. Return `BLOCKED` when any proof is missing.
