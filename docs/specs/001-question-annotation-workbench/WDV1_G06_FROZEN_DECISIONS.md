# WDV1 G-06 Frozen Decisions

**Status:** Approved product baseline for `WDV1-002` planning and implementation. This document does not approve a cloud provider, parser library, migration, API, worker, or UI implementation.

## 1. Original DOCX is long-lived source evidence

Original DOCX files are retained as immutable source evidence. Parsing, annotation, submission, review, or correction must not automatically delete them. A changed file creates a new `PaperVersion`; it never replaces the old source file.

PostgreSQL stores only management metadata: identity, hash, version, storage reference, uploader, time, and state. The file body belongs in private controlled storage: local private storage is permitted in development; a controlled object-storage service is preferred in production without selecting a provider now. Ordinary question-bank users cannot download original Word files; authorized annotators, reviewers, and source managers may view them. Archival duration and final deletion policy are outside Word V1.

## 2. Input is real, safe `.docx`

Word V1 accepts safe, valid `.docx` only. It does not accept `.doc`, `.docm`, PDF, scanned input, or OCR input. A valid DOCX may contain text, pictures, formula images, tables, and normal exam layout. The system must preserve the original and provide the best reliable visual preview it can; unsupported content must not silently disappear.

This does not extend official question content beyond existing plain-text Shenlun fields. Word V1 does not insert images into question fields, create mixed content, crop images, run OCR, convert LaTex, or infer image business meaning.

## 3. Parser output is source structure, never question semantics

The parser may faithfully produce ordered text blocks, image blocks, other reliable source blocks, page numbers, positions, original labels, warnings, and processing status. It must not infer stem, requirement, question, reference answer, knowledge point, question type, material, or any other business role. Original labels such as a title, a printed question number, or “作答要求” may be displayed as source text only.

## 4. Human multi-block fill is explicit and ordered

An annotator may select one or more source blocks and explicitly choose one target: `stem_text`, `requirement_text`, `question_text`, or `reference_answer_text`. Multiple blocks are combined in their original source order. The system must not reorder, rewrite, or choose a target field.

An empty target field may be filled directly. Replacing non-empty human content requires an explicit confirmation. Replacement is the main flow; append is only a correction aid after a missed selection. This remains operation assistance, not automatic question splitting.

## 5. Provenance is field-to-many-blocks

Word V1 must retain this relationship:

```text
QuestionVersion -> PaperVersion -> field -> one or more DocumentBlocks
```

It records the selected block order and any reliable page/position data. It does not require character-level mapping or exact textual equality after an annotator edits a filled field. The relationship means that the field was prepared from the selected source blocks. An annotator may correct a wrong source relationship. Image blocks may remain provenance evidence even though they cannot enter current plain-text question fields.

## 6. Upload and processing failures are separate

- **Upload failure:** the DOCX was not safely and completely stored; the user must upload again.
- **Visual-preview failure:** the DOCX is stored, but no reliable visual preview is available.
- **Source-structuring failure:** the DOCX and preview remain available, but usable blocks cannot be produced.
- **Partial structuring:** reliable blocks are shown, unreliable regions are clearly marked, and partial success is never presented as complete.

An uploaded DOCX is not relabeled as an upload failure merely because a later process fails. Reprocessing creates a separate processing record/history rather than silently overwriting earlier outcomes. Word V1 requires manual reprocess, source viewing, and continued manual annotation; it does not require complex automatic retries.

## 7. Word V1 is a controlled internal pilot

Development and automated tests use only sanitized DOCX fixtures, including representative paragraphs, images, tables, pagination, formula images, long text, and multi-block structure. Real papers, answers, learner information, credentials, and private parser output are never committed.

Within a controlled internal pilot, designated annotators may upload, view, process, select source blocks, fill fields, and edit drafts. Administrators/project owners may view upload records and handle source exceptions. Ordinary users cannot upload or download original files. `X-Actor-Id` remains development/test-only and is not formal authentication or RBAC.

## 8. Success is a human workflow, not automatic accuracy

G-09 must prove with representative sanitized DOCX that an annotator can upload, view, structure sources, select one or more blocks, explicitly fill fields, edit, save, switch, return, inspect retained provenance, resolve `STALE_DRAFT`, reload latest content, and submit. At least one partial-structuring failure must demonstrate that manual work continues.

The pilot records annotator feedback on finding source text, reduced switching, long multi-block fill, provenance checking, and added burden. It has no pre-frozen percentage efficiency target. If the workflow does not improve manual work, the team improves it before expanding to AI suggestions, OCR, automatic splitting, or more complex formats.

## Gate baseline

- **G-06: PASS.** Decisions 1–8 are approved and do not conflict with the existing immutable-version, human-review, PostgreSQL 16, or pure-text-question rules.
- **G-07 Raw DOCX acceptance.** Verify safe, immutable, traceable original DOCX intake only; no source blocks or fill workflow.
- **G-08 Source structuring acceptance.** Verify faithful visual preview, structural source blocks (text/image/order/page/available position), and clear partial-failure behavior; no semantic inference or field fill.
- **G-09 Human-assisted annotation acceptance.** Verify the complete approved human workflow and retained field-to-block provenance.

## Explicitly still prohibited

No code from this decision document authorizes PDF/OCR/scanned input, image or mixed-content official questions, automated business classification, automatic question creation/submission/approval, production RBAC, review/release features, or replacement of existing G-04/G-05 behavior.
