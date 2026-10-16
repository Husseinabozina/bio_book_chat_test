# سجل الطرق والتجارب

## History: previous outputs (before this repository)

1. **Earlier Word (editable attempt):** extraction + heuristic text paragraphs + embedded image content. User reported spelling, hamza, RTL/parentheses, line spacing, typography and alignment defects. Not accepted.
2. **Earlier Word (visually faithful):** source pages rasterized to full-page images inside DOCX; preserves appearance, not text-editable.
3. **Adobe Acrobat suggestion:** not part of the implemented method, and user explicitly chose to continue without it. Do not describe it as a conversion already performed.
4. **Word in Chat:** available for user-assisted review, but no automated plugin-driven conversion benchmark has been run in this repository.

## New reproducible methods (v0.1)

A. `inspect`: capture fonts, number of blocks and Unicode anomalies. It is not a spelling verifier.

B. `visual`: rasterize source page -> inline image per Word page. Designed to preserve appearance, not editability.

C. `editable`: read PDF spans into logical blocks, concatenate lines in a block (not individual Word paragraphs), set RTL OOXML, retain raster image regions. Restrict to sound mapping by default. **Does not** reconstruct exact layouts and vector tables.

D. `hybrid`: per-page gate; unsafe text -> visual, otherwise editable. Report lists each page's mode.

E. `audit --render`: count editable paragraphs/images/tables, suspicious output chars, attempt LibreOffice render, compare expected page count. It does not compute visual similarity yet.

## Controlled trial

Test three *different types* of page before running a batch:

- p.7: long Arabic body with English terms and mixed parentheses.
- p.10: figure/chart and chemistry notations.
- p.16: formatted table.

For wider verification, add p.8 (sidebar) and p.14 (illustrations + text).

Generate one output per method using identical source pages, page size and machine. Record run report JSON, rendering engine/version, timestamp, font availability, and reviewer flags. Never conclude that one is "best" from aesthetics alone: compare *text correctness*, *editability* and *layout fidelity* separately.

## Experiment template

```text
experiment_id:
source_hash_sha256: (store digest, not textbook)
pages:
mode:
software_versions: PyMuPDF / python-docx / LibreOffice / Word in Chat
fonts_available:
output_filename: (private, not committed)
source_unicode_flags:
editable_pages:
visual_pages:
rendered_pages:
reviewed_by:
transcription_results:
layout_results:
open_issues:
accepted: true/false
```

**Important:** Report JSON committed to Git must omit paths/private data and copyright text. Results/scan images stay local.
