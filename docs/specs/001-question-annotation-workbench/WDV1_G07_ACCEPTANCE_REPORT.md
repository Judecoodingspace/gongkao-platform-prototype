# G-07 Acceptance Report — Raw DOCX Intake

**Result:** `G-07 = PASS`
**Scope:** `WDV1-002` only. This report does not approve or implement G-08/G-09.

## 1. What was implemented

The API now accepts a safe raw `.docx` as either a new `Paper` with its first immutable `PaperVersion`, or as the next immutable version of an existing `Paper`. It validates the OOXML ZIP container without parsing document content, calculates SHA-256, stores the original bytes through a private storage adapter, records only existing source-version metadata, and finalizes the version in one transaction with safe audit/idempotency handling.

No migration was needed: M-001 already contains `papers` and `paper_versions`. No `DocumentBlock`, `SourceSpan`, preview, document parser, React UI, OCR/PDF, AI workflow, or RBAC was added.

## 2. Changed files

API commit [`9f26c0b`](https://github.com/Judecoodingspace/gongkao-question-bank-api/commit/9f26c0b) adds the papers upload router/service/schemas, private local-storage adapter, OOXML validation, Paper repository queries, upload configuration/error mapping, multipart dependency, generated OpenAPI, and G-07 API tests. It also ignores the local private storage root.

The governing API contract now records the multipart intake endpoints, duplicate-result choice, relationship policy, and final runtime safety controls. This report, the implementation contract, task list, plan, acceptance checklist, and review log record the gate result.

## 3. Private test storage

Automated tests use `LocalPrivateSourceStorage` rooted in a pytest temporary directory. It stages bytes under a non-public staging directory, promotes them to a local private object path only during finalization, stores only an opaque `private://…` reference in PostgreSQL, and is removed with the test temporary directory. Neither API response nor audit details contain the URI or absolute path.

This is a development/test adapter only. Production storage provider selection remains out of scope.

## 4. `IMPLEMENTATION_PRECHECK` and applied limits

Before implementation, ZIP metadata only was read from three local Git-ignored representative DOCX POC samples: maximum original size `594257` bytes, maximum expanded size `690465` bytes, maximum `16` ZIP entries, and maximum single-entry ratio `10.11:1`. No document contents or filenames were emitted.

The applied runtime limits are: source bytes **50 MiB**, expanded ZIP bytes **250 MiB**, ZIP entries **10,000**, and per-entry compression ratio **100:1**. They provide approximately 88×, 379×, 625×, and 9.9× headroom over the observed maxima. They are documented implementation safety controls, not a new product decision.

## 5. Database and automated verification

- PostgreSQL: `16.15 (Debian 16.15-1.pgdg13+2)` through Compose `postgres-test`.
- Database: disposable `gongkao_api_test` with `GONGKAO_APP_ENV=test`.
- Migration state: `0005_m005 (head)`; no new Alembic revision.
- Checks run: `uv run ruff check .`, `uv run mypy src`, `uv run pytest`, `uv run alembic upgrade head`, `uv run alembic current`, `uv run alembic heads`, and `uv run python scripts/export_openapi.py`.
- Result: Ruff and MyPy passed; **30 Pytest tests passed**; Alembic remained at head; OpenAPI was regenerated.

## 6. Scenario results

| Scenario | Result |
| --- | --- |
| Safe sanitized DOCX | Creates a `finalized` immutable paper version with SHA-256 and safe metadata. |
| Changed DOCX for the same paper | Creates the next version; the earlier row and stored bytes remain unchanged. |
| Same idempotency key | Returns the original version with `Idempotent-Replay: true`; changed payload conflicts. |
| Same hash, new key, same paper | Returns the existing version with `200`; creates no false new version. |
| `.doc`, damaged ZIP, macro, ActiveX/OLE-equivalent and dangerous external relationship | Rejected with no `PaperVersion`. |
| Ordinary OOXML external hyperlink | Accepted and stored; the validation path performs no network access. |
| ZIP safety limits | Unit test proves limits reject before document handling. |
| Storage failure and database-commit failure | Return safe `503 SOURCE_STORAGE_UNAVAILABLE`; no `finalized` row or stored final object remains. |

The tests directly compare persisted bytes with SHA-256 and the stored `file_hash`, proving the saved source bytes match the provenance record. They also assert normal response/audit data excludes `storage_uri`, absolute private paths, and source content.

## 7. Existing gates and limitations

The full API suite includes the prior G-04 persistence/contract checks and passed. G-05 is the previously accepted Web end-to-end baseline; no Web code or G-05 workflow was changed in this task, so it was not rerun as part of this backend-only gate.

Known limitations:

- `X-Actor-Id` remains development/test audit identity only; it is not formal login or RBAC.
- Real DOCX requires a separately demonstrated controlled internal deployment boundary. Otherwise only sanitized fixtures may be used.
- There is no original-file download, visual preview, parsing, source block, provenance-span, OCR/PDF, or field-fill capability.
- OOXML validation is structural security validation, not an antivirus product or semantic document validator.
- The applied thresholds are based on a small local POC aggregate and should be revisited through the same documented precheck when the approved fixture corpus changes materially.

## 8. Traceability and workspace state

- API branch: `main`; implementation commit: `9f26c0b` (`Implement G-07 raw DOCX intake`), currently one commit ahead of `origin/main` pending explicit push authorization.
- API issue: [#8](https://github.com/Judecoodingspace/gongkao-question-bank-api/issues/8).
- API tracked implementation worktree was clean after the commit. A pre-existing user-local untracked `compose.local.yaml` remains intentionally excluded.
- Platform documentation commit is recorded separately from the API implementation. No real DOCX, answer, storage URI, credential, database dump, or parser output was committed or posted.

With the evidence above, `G-07 = PASS`. The next permitted task is planning/approval for `WDV1-003 / G-08`; implementation of G-08 remains prohibited until that separate contract is approved.
