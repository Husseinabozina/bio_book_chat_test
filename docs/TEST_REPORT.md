# Reproducible trial outcome (2026-10-15)

Scope: source biology textbook, local-only PDF. Selected PDF page indices (1-based): 7, 8, 10, 14, 16.

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Source text preflight | FAIL for all five pages | The page-specific inspection found Unicode anomalies in each. Page 7: 28 suspicious characters. |
| Editable mode without override | BLOCKED as intended | Source mapping not trusted; no claim of successful editable textbook conversion. |
| Visual DOCX before correction | FAIL | 5 input pages unexpectedly rendered as 9 Word pages in LibreOffice. |
| Visual DOCX after correction | PASS on page count | 5 selected pages rendered as 5 output pages in LibreOffice after reducing picture dimensions to allow paragraph descent. |
| Native editability in visual mode | NOT APPLICABLE | These five output pages are images. |
| Text and layout verification in editable mode | NOT YET ACCEPTED | Requires Arabic transcription QA, region alignment, and editable table reconstruction. |
| Unit tests | PASS (8 local tests with PYTHONPATH=src) | Synthetic fixtures; success does not prove fidelity on arbitrary source books. |

The figures above are observational results of this local trial, not guarantees for other PDFs, Word renderers, fonts or page sizes. The source file and Word output are excluded from Git.


## Five-page manually reviewed editable experiment (2026-10-15)

A separate local experiment selected PDF pages **140, 145, 149, 155, 160**. It produced an **editable** Arabic DOCX using source-image guided transcription and cropped figures, rendered to 5 pages in LibreOffice. It contained approximately 6,000 editable characters, 5 figures, and two structural layout tables. The appearance remained notably different from the source in typography, spacing and text density; some terms and punctuation remain pending meticulous source-by-source proofreading. **Not approved as a faithful reproduction**.

The reviewed-manifest engine added to the repository provides a reusable, source-agnostic way to export visually verified Arabic text, figures and native tables, independently of this specific local document. Unit tests exercise RTL, native tables, Unicode protection and the CLI. Source book material remains excluded from Git.
