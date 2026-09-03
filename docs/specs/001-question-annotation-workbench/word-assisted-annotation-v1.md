# Word-Assisted Annotation V1

## Product decision

Word V1 reduces copying and locating effort for human annotators. It does not create official questions automatically. A DOCX upload is an immutable source version; parser output is a non-authoritative source candidate; only an annotator action may copy selected source text into a draft question; submission remains subject to the existing human-review workflow.

## In scope

1. Upload one ordinary text-first DOCX as a source paper version.
2. Persist original file metadata, hash, storage reference, upload result, parser name, parser version, and parser configuration.
3. Produce deterministic, ordered, text-only `DocumentBlock` candidates with page/block provenance when available.
4. Show a left source preview beside the existing Shenlun draft form.
5. Let an annotator select source text and explicitly fill one of `stem_text`, `requirement_text`, `question_text`, or `reference_answer_text`.
6. Store a human-confirmed field-level source reference without changing the source block.
7. Preserve the existing save, switch, stale-draft, submit, audit, and immutable-version rules.

## Out of scope

PDF, OCR, scanned files, embedded images, formulae, tables, mixed content, automated question creation, automated taxonomy classification, approval/rejection, release, and production authentication are not Word V1 work.

## Required decisions before implementation (G-06)

- Object-storage provider, retention, access-control model, download authorization, file-size/type limits, malware scanning, and failed-upload recovery.
- Parser adapter contract and first DOCX implementation; parser output must be deterministic for identical input and parser version.
- Exact `DocumentBlock` and field-level `SourceSpan` migration design, including immutable provenance, indexes, constraints, and downgrade/recovery tests.
- Human interaction: selection, fill action, overwrite confirmation, source-reference visibility, and parser-failure fallback to manual entry.

## Proposed delivery gates

- **G-06 Word design**: approve the storage policy, parser boundary, schema/API contract, source-reference behavior, security limits, and sanitized fixture policy.
- **G-07 Word backend**: PostgreSQL migrations, upload/parser/source-preview API tests, failure recovery, provenance and no-auto-entry checks pass on disposable PostgreSQL 16.
- **G-08 Word end-to-end**: a human can upload a sanitized DOCX, inspect source text, explicitly fill two fields, save, switch, return, submit, and trace the draft to the uploaded paper version and selected blocks.

## Execution runbook

1. `WDV1-001`: approve G-06; do not write code first.
2. `WDV1-002`: add reviewed migrations for document blocks and source spans; do not recreate `papers` or `paper_versions`.
3. `WDV1-003`: implement safe DOCX upload/version finalization and object-storage adapter.
4. `WDV1-004`: implement parser adapter and deterministic text-only DOCX candidate extraction.
5. `WDV1-005`: expose source-preview and explicit field-fill APIs with provenance.
6. `WDV1-006`: implement the Web preview/fill workflow and pass G-08 with sanitized browser fixtures.

## Completion evidence

Evidence must include upload validation, parser success and failure cases, ordered-source assertions, field-fill provenance assertions, PostgreSQL 16 migration checks, API/Playwright tests, approved desktop screenshots, and a GitHub issue record. No real paper text, answers, uploaded files, credentials, database dumps, or parser output may be committed or posted.
