# Word-Assisted Annotation V1

## Product decision

Word V1 reduces copying and locating effort for human annotators. It does not create official questions automatically. A DOCX upload is an immutable source version; parser output is a non-authoritative source candidate; only an annotator action may copy selected source text into a draft question; submission remains subject to the existing human-review workflow.

## In scope

1. Upload one ordinary text-first DOCX as a source paper version.
2. Persist original file metadata, hash, storage reference, upload result, parser name, parser version, and parser configuration.
3. Produce deterministic, ordered structural source blocks (text, image, and other reliable blocks) with page/position provenance when available, without business-semantic inference.
4. Show a left source preview beside the existing Shenlun draft form.
5. Let an annotator select source text and explicitly fill one of `stem_text`, `requirement_text`, `question_text`, or `reference_answer_text`.
6. Store a human-confirmed field-level source reference without changing the source block.
7. Preserve the existing save, switch, stale-draft, submit, audit, and immutable-version rules.

## Out of scope

PDF, OCR, scanned files, image/mixed-content official question fields, automated question creation, automated taxonomy classification, approval/rejection, release, and production authentication are not Word V1 work. Images, formula images, and tables in a valid DOCX may be retained and previewed as source evidence only.

## Frozen G-06 decisions

The authoritative approved decisions are in [`WDV1_G06_FROZEN_DECISIONS.md`](./WDV1_G06_FROZEN_DECISIONS.md). They freeze product behavior and boundaries, not a cloud vendor, parser library, schema, API, worker, or UI implementation.

## Frozen G-08 design decisions

The authoritative G-08 design input is [`WDV1_G08_FROZEN_DECISIONS.md`](./WDV1_G08_FROZEN_DECISIONS.md): it freezes dual visual/structure representations, natural-paragraph blocks, independent processing history, the WDV1-003 text-first slice, direct DOCX/OOXML structural reading, and `success`/`partial`/`failed` semantics. It does not authorize implementation; WDV1-003 still requires its separately approved implementation contract.

## Proposed delivery gates

- **G-06 Word design**: passed; Decisions 1–8 are frozen in the authoritative decision document.
- **G-07 Raw DOCX acceptance**: passed; safe, immutable, traceable DOCX intake is verified in `WDV1_G07_ACCEPTANCE_REPORT.md`. It does not verify blocks or field fill.
- **G-08 Source structuring acceptance**: verify faithful visual preview, structural source blocks, available provenance, and partial-failure behavior; it does not verify semantic inference or field fill.
- **G-09 Human-assisted annotation acceptance**: verify explicit multi-block fill, field-to-block provenance, save/switch/conflict/reload/submit, and manual continuation when assistance is partial.

## Execution runbook

1. `WDV1-001`: approve G-06; completed by the frozen decision baseline.
2. `WDV1-002`: completed approved raw-DOCX intake/version-finalization work for G-07; do not recreate `papers` or `paper_versions`.
3. `WDV1-003`: after its implementation contract is approved, implement the reviewed text-first source-structuring foundation: independent history and natural-paragraph ordered text blocks for G-08.
4. `WDV1-004`: implement faithful visual preview, visual/source linking, image/other reliable evidence, and remaining partial-failure behavior for G-08.
5. `WDV1-005`: implement explicit multi-block field fill and field-to-block provenance for G-09.
6. `WDV1-006`: implement the Web workflow and pass G-09 with sanitized browser fixtures.

## Completion evidence

Evidence must include upload validation, parser success and failure cases, ordered-source assertions, field-fill provenance assertions, PostgreSQL 16 migration checks, API/Playwright tests, approved desktop screenshots, and a GitHub issue record. No real paper text, answers, uploaded files, credentials, database dumps, or parser output may be committed or posted.
