# Reuse of existing private biology-book visual layout engine
**2026-10-16 | Decision; no copyrighted textbook assets in this repository**

## Verified repository comparison

1. Private `Husseinabozina/biology_book_to_word` is the actual authoring/delivery repository. It stores the source PDF, canonical per-page JSON for pages 1–40, extracted artwork and existing batch assembler. Its `scripts/build_layout_batch.py` composes real editable Arabic VML regions, source figures and native tables. It does not automatically read/segment page 41.
2. Public `Husseinabozina/bio_book_chat_test` is the research/quality repository. It holds structure audits, synthetic OCR scoring and source-image/Word evidence gates. It is NOT the authoritative book deliverable repository.
3. The direct-DOCX tests on page 41 actually rejected `pdf2docx`, PaddleOCR PP-StructureV3 Arabic and MinerU Basic due to damaged text and layout, despite technical generation of a DOCX. Thus replacing the production layout compositor with them would be an unjustified regression.
4. **Confirmed code-level defect in private authoring:** the shared artwork anchor writer emitted `wp:wrapNone` in the wrong OOXML order, reproducing the type of Word-compatibility incident documented in the lab. Fix and synthetic regression were committed on PRIVATE branch `feature/integrated-layout-engine-qa`, not merged into main.
5. The private constructor used a hard-coded macOS Amiri font directory. It now discovers valid fonts via an explicit `--font-dir` flag / env / checked system directories, or fails rather than silently changing typography.

## Integration contract

```
source PDF + verified private content/pages/pNNNN.json + assets
  → PRIVATE production_pipeline.py (source and asset checksum, bbox/table checks)
  → existing build_layout_batch.py (visual-fidelity-first DOCX candidate)
  → actual candidate OOXML / text / native table / media integrity + optional render
  → PRIVATE export_release_evidence.py (draft, independent reviews PENDING)
  → PUBLIC-LAB-compatible release evidence format / release-check after human reviews
  → user approval → private existing cumulative-book assembler
```

Do not confuse the bridge's manifest fields with proof of source-independent review. Figure-internal text is preserved with artwork, not falsely claimed editable. The existing rendered designs remain *experimental* pending Word Desktop open/edit/save and user approval.

## Small-model work allocation (planned, not yet automated)

- Deterministic scripts: PDF rasterization, source SHA, asset crop extraction, bbox validation, DOCX rendering, media CRC/OOXML tests, assembly and report.
- Optional OCR/layout model: proposes `text/figure/sidebar/table` blocks and candidate transcriptions **with provenance/confidence**, never overwrites private canonical source text.
- Small vision model: inspect **a single cropped region** with page ID and existing block schema; returns proposed JSON, not executable Word code. Escalate unreadable hamza/scientific terms or geometry ambiguities to a reviewer.
- Stronger/human source review: approves literal transcriptions and hard layout ambiguities before committing canonical pages.
- Existing Word compositor: executes known block instructions; no model writes new ad-hoc OOXML per page.
- Quality gate: blocks release when source, layout, editability or Word compatibility evidence missing.

## What was built / tested and what was not

**Built on private branch:** source/asset/layout JSON preflight, portable font discovery, OOXML anchor fix, real DOCX text/table/media audit, isolated `runs/` candidate builder, release-evidence export that stays explicitly unapproved, synthetic regression tests and a private 36–40 smoke-test workflow. Output of the smoke test must be read before claiming success.

**Not built:** automatic page segmentation/transcription, automated font/paragraph bbox fitting, independently verified text for new page 41, font-glyph matching, Microsoft Word Desktop automation, real client acceptance, general plug-and-play converter.

Existing project main and client `deliverables/` are not changed by this development branch. Never publish the user's original PDF, text or figures here.

See private `docs/INTEGRATION_VISUAL_FIDELITY_LAB.md` for reproducible candidate commands.


## Measured private production-engine integration findings, 2026-10-16

This section contains only reproducible **non-copyrighted metrics and engineering defects**. Real page assets/text remain in the private authoring repository.

- The visual compositor's shared geometry anchor paragraph inherited RTL from the Arabic Normal style. LibreOffice thereby **mirrored physical page X positions** of overlaid figures and textboxes, while original full-width backgrounds concealed the defect. Fixed by explicitly setting `w:bidi=0` on the geometry anchor only; text in each editable Arabic VML box remains RTL.
- A real editable Word table with `w:tblpPr` floated to the TOP of page 38 in LibreOffice despite valid OOXML. Moved `w:tbl` inside a page-positioned VML box, and updated table auditors to accept genuine Word tables in either main body or VML. **Microsoft Word Desktop editing of this shape still unverified.**
- Five-page private (physical PDF pages 36–40) before/after same-environment comparison, 144-DPI grayscale SSIM: 36: 0.71273→0.76641; 37: 0.74891→0.82141; 38: 0.80341→0.81306; 39: 0.73117→0.73973; 40: 0.72294→0.83194. Mean 0.74383→0.79451. **These scores do not certify fidelity; the page-38 table can look correctly positioned while overall SSIM is lower than an earlier defective layout.**
- Actual private pipeline result: 5 source pages → 5 rendered DOCX pages, 45 editable text paragraphs, 1 native editable table, 10 anchored figures/backgrounds, zero declared ZIP/OOXML/text/assets errors. The resulting Word **still has font/line-wrap differences** and has **not** undergone Microsoft Word Desktop testing or independent source-image proofreading.
- Dedicated private tests prevent both invalid anchor element ordering and mirrored page-geometry anchor direction; audits parse actual DOCX, not merely source JSON. CI green means no **coded** structural regression, not user acceptance.
- Source/QA split is now operational: private `production_pipeline.py` performs preflight/candidate build/structural QA/visual evidence, private `export_release_evidence.py` creates an intentionally unapproved draft in the public lab's strict schema.

Private CI reproducibility link (requires repository access):
[GitHub Actions run 38846467747](https://github.com/Husseinabozina/biology_book_to_word/actions/runs/38846467747).

**Decision:** keep source-driven visual compositor, retain exact original artwork, route external OCR/layout models to candidate **data** only. Fix Word-native geometry and independently source-review text before scaling to page 41+. Avoid moving user's book/media or private evidence to this public lab.
