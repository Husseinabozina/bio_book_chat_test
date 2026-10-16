# Engineering decisions, not suggestions

Status: **adopted as policy on the experimental branch**, 2026-10-16.
Source incidents: `docs/FAILURE_POSTMORTEM.md`, `docs/PILOT_PAGES_41_43.md`,
`docs/WORD_COMPATIBILITY_INCIDENT_41_43.md`, and private project `biology_book_to_word`'s
`docs/LESSONS.md` / `docs/PRODUCTION_METHOD.md`.

**Definition of words:**
- BUILT: source code exists.
- TESTED: a synthetic regression is running in CI.
- ATTESTED: a reviewer supplied evidence for the exact final document.
- VERIFIED IN WORD: a person actually opened, edited and saved **that SHA-256 binary** in Microsoft Word.
- APPROVED: explicit final user acceptance. None of these may be substituted for another.

## Binding architectural decisions

| ID | Decision | Verified original failure or gap | Enforcement and present status |
|---|---|---|---|
| ADR-01 | One package-managed workflow; experiments can branch but cannot claim release unless they pass the same gate. | `build_41_43.py` executed outside the tested package. | `bio2word release-check` accepts artifacts from any pipeline and returns exit code 3 for failures. **Built/tested**. Automatic prevention of all ad hoc scripts is not possible; release discipline is mandatory. |
| ADR-02 | Preserve an independent page model: semantic paragraphs, figures and tables with IDs, not one textbox per PDF line. | 77 individually editable lines were not flowing paragraphs. | `release_gate._check_objects` rejects `kind=line` and missing paragraph IDs. **Built/tested**. Full semantic layout compositor: **not built**. |
| ADR-03 | Rendered source image, not corrupt PDF Unicode, is authority for visible spelling. Use extracted glyphs only as evidence. | AXtYasmine PDF maps contain malformed characters. | `analysis.py` preflight + `reviewed.py` Unicode rejection; release requires source-image reviewer with object-level provenance. **Partial**: no automatic independent human proofreader. |
| ADR-04 | Preserve the printed text verbatim, even apparent source typos; any proposed correction requires explicit review. | Dropped hamzas and invented corrections across earlier trials. | Verbatim OOXML text comparison to reviewed manifest without deleting hamzas/diacritics. **Built**; no external source truth can be automatically proved. |
| ADR-05 | Distinguish RTL paragraph direction from each Latin run's LTR. Never reverse strings manually. | 18 previously examined mixed-language runs carried a single RTL direction. | Strict manifest rejects mixed Arabic/Latin script in one run and wrong direction. **Built/tested**. Still requires checking actual Word runs and visible parentheses. |
| ADR-06 | Font size must come from measured source-and-render typography; never assume Amiri 15.3 matches AXtYasmine 18. | Script shrank individual lines by multipliers to suppress wrap. | Each text object must record `typography.calibration=measured_source_and_render`, PDF/output bboxes. **Evidence gate built**; calibrated font fitter **not implemented**. |
| ADR-07 | Geometry must be measured twice, from source AND *rendered Word*, in points. | Image and line positions drifted despite copying source coordinates. | Strict bbox tolerance, default 8.5 pt, failure `LAYOUT_DRIFT`. **Built/tested**. Automated extraction/matching of output bbox is **not implemented**. |
| ADR-08 | Preserve artwork without duplicating visible prose; do not replace editable text with a full-page screenshot. | Earlier visual mode was a misleading image-only DOCX. | Background provenance and editable OOXML text required. **Built**; visual source-layer decomposition still manual for complex pages. |
| ADR-09 | Keep figures and captions associated; preserve labels *inside* figures as an honest non-editable image exception. | Figure crops missed edges and text when preview pixels were confused with source points. | Each figure requires source provenance and measured bbox. **Built**; exact figure crop QA remains human. |
| ADR-10 | Real tables should remain Word tables when required, not a raster or layout-only substitute. | Prior baseline flattened and mocked tables. | Reviewed mode supports native tables; gate rejects lack of semantic source data indirectly. **Partial**; automatic table detector and native-cell fidelity scoring **not implemented**. |
| ADR-11 | Never inject headers, footers, labels or English page text not printed in the source. | Compatible output added heading; previous reviewed output injected “Original source page …”. | Removed automatic English footer in `reviewed.py`; optional explicit source `printed_footer`. **Built**. Source-presence verification remains review-dependent. |
| ADR-12 | Package validity is independent from LibreOffice successfully rendering. | All three `wp:anchor` figures in pilot had `wrapNone` before `extent`; Word refused to open. | `ooxml_checks.py` tests ZIP/XML/anchor order; release gate calls it. **Built/tested**. |
| ADR-13 | Microsoft Word / Pages compatibility is independent of LibreOffice. | LibreOffice rendered a DOCX that Word rejected. | Fail unless user supplies Microsoft Word version, open/edit/save outcome, and evidence linked to exact DOCX SHA. **Built** as attestation requirement. The CI cannot operate user's desktop Word. |
| ADR-14 | Never accept page-count equality as visual/layout/content accuracy. | Three pages rendered while font and line positions were wrong. | Release requires geometry, per-object text/typography and review states separately. **Built/tested** for declared metrics; genuine geometry extraction remains pending. |
| ADR-15 | No generic "successful" status without per-domain results and source-bound artifact identity. | Passing unrelated unit tests was described as success of deliverable. | Gate reports blocking issue IDs, file hash and `certified_by_automation=false`; DOCX built by reviewed mode reports `EXPERIMENTAL_NOT_APPROVED`. **Built/tested**. |
| ADR-16 | Run all checks against the exact binary delivered; no replacing the file after review. | Independent script and review were not tied to delivered output. | `ARTIFACT_HASH_MISMATCH` and `WORD_DESKTOP_NOT_VERIFIED`. **Built/tested**. |
| ADR-17 | Original pages and handwritten transcriptions are private fixtures, not public CI assets. | Public repo should not publish textbook material. | Private local manifests only; synthetic unit tests only. **Policy in AGENTS.md**, cannot enforce content provenance by static check alone. |
| ADR-18 | Every new defect needs a named regression and one reviewed correction at the root cause, not blind size scaling. | Spacing workarounds hid source font mismatch; Word XML error reached user. | CI tests XML order, mixed direction, geometry threshold, review missing, binary hash. **Partial**; automated visual/font calibration still outstanding. |

## Release contract

Conversion commands create **candidate** DOCX files. They MUST NOT report approved status.
Certification is blocked until the same candidate has:
1. A private JSON evidence manifest matching `docs/RELEASE_EVIDENCE_TEMPLATE.json`.
2. Independently proofread texts linked to original image crops, and all semantic objects recorded.
3. Source-vs-rendered object bounding boxes + typography calibration + visual review evidence.
4. Source artwork, readable order, figures and tables reviewed (each as an independent domain).
5. OOXML integrity check, actual DOCX render with the selected page count.
6. Open/edit/save validation in Microsoft Word for the **same SHA-256**.
7. Explicit user approval OUTSIDE the automated gates.

Run:

```bash
bio2word release-check outputs/candidate.docx runs/private_evidence.json --render --report runs/release.json
```

- Exit **3**: BLOCKED. CI must not upload or label this artifact a trusted release.
- Exit **0**: ELIGIBLE_FOR_HUMAN_FINAL_APPROVAL; this is **not** proof of user approval.
- Presence of review evidence is verified by software, while *truth of visual/manual evidence cannot be verified just by JSON fields*. Falsifying evidence violates the project contract.

## Not yet implemented (do not call these complete)

A real source-text independent proofreader; font-shaping/width calibration engine;
word-level coordinate extraction from rendered DOCX; column/reading-order inference;
automatic source-image figure/table segmentation; real Microsoft Word automation; Apple
Pages compatibility. The strict gate **blocks** missing evidence, rather than pretending
those subsystems exist.

Next implementation milestone: 1) genuine page-level source/layout model and output geometry extractor,
2) adaptive Arabic typographic compositor that preserves paragraphs,
3) measured rendered comparison, 4) real viewer acceptance on a one-page pilot.
