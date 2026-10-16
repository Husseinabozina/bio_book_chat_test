# External PDF → editable Word research — 2026-10-16

**Project-specific objective:** 232-page Arabic science textbook; pages 41–43 pilot; original PDF has damaged Unicode mappings in AXtYasmineLight; page fidelity and natural editing in Microsoft Word are mandatory. Arabic spelling/hamzas, Latin terms, colored sidebars, figures, tables, and source page numbering must be retained.

**Status:** External-source research and design; NOT a claim that these libraries were installed, executed, or demonstrated to work on the textbook. A feature reported by a README is not an observed benchmark. This document becomes a repeatable implementation decision, not a license to bypass AGENTS.md or release-check.

## Three distinct layers

- **Optical/semantic recognition:** image -> accurate Arabic Unicode and object types.
- **Geometric reconstruction:** semantic paragraphs/columns/tables/figure relationships and page bboxes.
- **Word writing:** editable DOCX with correct RTL/LTR runs, valid OOXML, paragraph reflow and retained appearance.

No single reviewed tool has yet been verified to satisfy all three **on this source**.

## Researched upstream candidates and explicit evidence

| Candidate | Confirmed capability from official sources | Limitation / integration risk | Proposed role / priority |
| --- | --- | --- | --- |
| [PaddleOCR PP-StructureV3](https://github.com/PaddlePaddle/PaddleOCR) | Structured OCR, layout/table/order; since 3.5 offers `res.save_to_word(save_path=...)`; docs support `PPStructureV3(lang="ar")`. Apache 2.0 code. [API/docs](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PP-StructureV3.en.md) | Its documented Arabic route is PP-OCRv3, while default is Chinese-English; the table reports 73.55 on that model's own test, **not a prediction for our pages**. May lose exact typography/biology labels. | **P0:** first direct-to-DOCX candidate, with explicit `lang="ar"` and actual Word open/save. |
| [PaddleOCR-VL](https://github.com/PaddlePaddle/PaddleOCR) | OCR/VLM complex layout and multilingual including Arabic; official README says DOCX export supported in 3.5+. [README](https://github.com/PaddlePaddle/PaddleOCR/blob/main/readme/README_ar.md) | Need to establish per-version API, GPU/CPU runtime and Arabic fidelity in a real experiment. | **P0:** second direct-to-DOCX candidate. |
| [MinerU 4.0](https://github.com/opendatalab/MinerU) | Versioned unified document model; programmatic renderer supports `RenderFormat.DOCX` returning bytes, in addition to JSON, PDF, HTML; Basic/Standard/Advanced tiers. [Actual output contract](https://github.com/opendatalab/MinerU/blob/master/docs/en/reference/output_files.md). | DOCX rendering available via Python renderer, NOT necessarily from every CLI command. The documentation's original-geometry PDF export claim **does not imply** that Word retains original geometry. Uses [custom MinerU license](https://github.com/opendatalab/MinerU/blob/master/LICENSE.md), not plain Apache. | **P0:** second independent document-model + DOCX baseline, test tiers and editing. |
| [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx) | Purpose-built PDF -> native DOCX from PyMuPDF data, detects sections/paragraphs/tables. MIT. [Technical docs](https://pdf2docx.readthedocs.io/) | Upstream explicitly states it is **no longer actively maintained by Artifex**. Embedded corrupted Arabic Unicode makes ordinary direct extraction unsafe for our PDF. | **P1:** geometry/paragraph/table algorithms and direct converter **negative control**. Never silently ship corrupted output. |
| [Docling](https://github.com/docling-project/docling) | Unified document representation, layout, tables, multiple OCR backends with Arabic-capable configurations; [OCR config](https://github.com/docling-project/docling/blob/main/docs/concepts/OCR.md). | [CLI output formats](https://github.com/docling-project/docling/blob/main/docs/reference/cli.md) list JSON/Markdown/HTML/etc., not DOCX as an output conversion target. OCR choice needs explicit Arabic setup. | **P1:** semantic layout and table extraction; adapter into OUR canonical page model, not direct Word. |
| [Surya](https://github.com/datalab-to/surya) | Layout boxes, reading order, OCR/table markup with per-block bbox/confidence; published internal Arabic score 72.7% (not our test). | Code Apache 2.0 but **weights have a modified AI Pubs license**; review startup/revenue restrictions before production. No direct DOCX in described output. | **P1:** fallback layout/reading-order extractor + Arabic OCR comparison. |
| [Marker](https://github.com/datalab-to/marker) | PDF -> tree-structured JSON, HTML, Markdown; chooses OCR for scanned/garbled pages and organizes figures/captions/equations. | Output is **not a faithful DOCX**; model licensing needs separate evaluation. | **P2:** compare paragraph/table structures for bad-font pages. |
| [Arabic-Nougat](https://github.com/MohamedAliRashad/arabic-nougat) | Arabic-book-specific image -> Markdown model; 13.7k synthetic book-page training pairs. [Paper](https://arxiv.org/abs/2411.17835). | Does not reconstruct DOCX geometry; model/code repository states CC BY-SA terms, evaluate reuse conditions. No demonstrated accuracy on Iraqi biology source. | **P1:** Arabic text / hamza recognition comparison and reviewer-assistance. |
| [book_to_word](https://github.com/GhaziRiyadh/book_to_word) | Arabic-specific FastAPI/React editor for human review against original page, OCR adapters and print styles. | README describes editor and printing but does not establish robust original-layout DOCX export. Small, little community validation. | **P2:** borrow human-review interface *design*, not assume conversion engine works. |
| [Adobe PDF Extract API](https://developer.adobe.com/document-services/docs/overview/pdf-extract-api/) | Structured JSON (paragraph, table, figure, font, bounds, reading order). [Bounds are 72 pt/PDF origin bottom-left](https://developer.adobe.com/document-services/docs/overview/pdf-extract-api/howtos/extract-api). | Not native editable DOCX. Potential Unicode extraction errors with unusual embedded fonts; cloud dependency and costs. Coordinates must convert to top-left. | **P2:** independent commercial structure benchmark, not core engine. |
| [Google Document AI Layout Parser](https://docs.cloud.google.com/document-ai/docs/processors-list) | Layout parsing and Arabic-listed language support. | API gives structured content for downstream systems, not original-layout Word; cloud dependency and costs. | **P2:** optional OCR/layout adjudicator. |
| [ABBYY FineReader](https://support.abbyy.com/hc/en-us/articles/360016365800-OCR-for-Arabic-and-Farsi) and [Adobe Acrobat](https://acrobat.adobe.com/tools/pdf-to-word) | Commercial Arabic OCR or direct PDF->DOCX solutions. | FineReader Engine Arabic is a separately licensed add-on; costs/privacy and output quality unknown until tested. | **Control group** for comparing build-vs-buy. |

## IMPORTANT source-specific inferences (not claims from the tools)

1. The custom PDF Arabic font has a faulty Unicode map. Methods that trust its text layer (including PyMuPDF/pdf2docx and `flash`/no-OCR paths) may create misleading, editable but incorrect Arabic. Force genuine image OCR or verified manual transcription for those spans.
2. A DOCX exporter that produces paragraphs and tables is a better **candidate** than 77 individually positioned line textboxes, but must still preserve multi-column/sidebar layout. Never label "editable" when the whole page is a screenshot.
3. Word shape/spacing requires separate rendered-bbox and typography measurement; JSON layout preservation does **not** equal visual fidelity in Microsoft Word.
4. Do not paste commercial/API OCR output over canonical text automatically: retain source crops, engine/version and uncertainty; human source comparison is authoritative for hamzas and scientific vocabulary.
5. Cross-language Latin terms require explicit `w:bidi` per Arabic paragraph and `w:rtl=0/1` per run, then actual Word compatibility test. No visual string reversal.
6. The best system is a **selection/routing layer**, not a blanket dependency on a single vendor.

## Target experiment: same six book pages and the *same* quality gates

**Primary:** 41, 42, 43 (consecutive, diagrams, colored boxes, columns).

**Stress:** 140, 149, 155 (mixed direction, figures, captions) to catch problems not visible in the first three.

Create 200-dpi source images and a reviewer-approved **independent** Unicode transcription with per-object bbox (don't use one candidate as ground truth). Record original PDF SHA-256, engine commit/version, language/model, hardware, execution time and raw outputs outside the public repository.

Run *without changing source pages*:

1. PaddleOCR PP-StructureV3 `lang="ar"` -> JSON + `save_to_word`.
2. PaddleOCR-VL -> structured result + DOCX using **verified installed-version** API.
3. MinerU 4.x `basic` or `standard` -> middle JSON -> Python `RenderFormat.DOCX` (check actual output contract before writing adapter).
4. pdf2docx -> direct DOCX **as a corrupt-font warning control**, not presumptively usable.
5. Optionally Docling/Surya/Arabic-Nougat -> structured OCR/Arabic text candidates. Feed into canonical JSON only after review.

Score dimensions **independently per page**:

| Dimension | Measured evidence | Reject condition |
| --- | --- | --- |
| OCR fidelity | CER/WER against manually verified text, explicit hamzas/Arabic punctuation/Latin terms, text coverage and omissions | No independent truth or unreconciled missing text |
| Semantics | paragraph grouping, heading levels, reading order, sidebars, table cells vs labeled reference | Plain PDF lines as standalone paragraphs, reordered columns, missing labels |
| Editability | Word OOXML text run coverage, native tables/figures as appropriate; paragraph edits without destructive geometry | Page image masquerading as Word, only textbox-per-line pseudo-editing |
| Layout | object bbox drift in PDF points, alignment, text size/line height, graphics and colors | Differences beyond agreed thresholds; hidden/overlapping text |
| Word compatibility | OOXML ZIP/XML/relationship validation, LibreOffice render and **real Microsoft Word desktop** open-edit-save of exact SHA | Repair prompt/corruption or lack of Word evidence |
| Reproducibility | fixed pages, versions/models, hashes, parameters, quality JSON | Report/inputs not tied to delivered artifact |

Proposed design: `SourcePage -> CandidateOCR[] + CandidateLayout[] -> Source-verified canonical JSON -> DOCX backend(s) -> independent rendered QA -> release-check`.

## Immediate engineering choices

- **Do not rewrite OOXML positioning machinery until direct DOCX baselines are measured.**
- **Do not adopt full external libraries or copy code before checking current license/weight terms.**
- Test direct-DOCX PaddleOCR and MinerU first. If one passes most criteria, wrap its exporter behind a package interface with a postprocessor for RTL, typography, and graphic positioning.
- Reuse Docling/Paddle structured output schemas to define semantic `paragraph/table/figure/heading/sidebar` in a canonical JSON, not `line` boxes.
- Keep original `bio2word release-check` and independent human review as mandatory gates for every external candidate. Existing book-to-Word samples are not a proof any newly found model works.

## Required acceptance artifact for each external tool

```json
{
  "candidate": "paddleocr_ppstructure_v3",
  "source_pages": [41, 42, 43, 140, 149, 155],
  "source_sha256": "<exact>",
  "version": "<installed>",
  "arabic_model": "<explicit>",
  "output_sha256": "<exact>",
  "ocr_cer": null,
  "ocr_wer": null,
  "layout_bbox_error_pt": null,
  "word_opened_edited_saved": false,
  "status": "NOT_TESTED_ON_USER_BOOK"
}
```

No star count, external demo score, Markdown-only output, or passing CI test substitutes for this project-specific evidence.
