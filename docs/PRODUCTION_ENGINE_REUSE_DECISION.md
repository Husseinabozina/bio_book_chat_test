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
