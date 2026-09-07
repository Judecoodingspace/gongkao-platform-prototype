# WDV1 STEP 4.4A Source Reader Boundary Implementation Plan

## Status

**APPROVED FOR STEP 4.4A IMPLEMENTATION**

- Team A review = PASS
- Product Owner approval = APPROVED

This document is the implementation plan for the approved STEP 4.4A slice only.
It does not authorize parser implementation, processing service implementation,
API endpoint implementation, React changes, or STEP 4.4B work.

## Authority / Baseline

- Product governance repo: `Judecoodingspace/gongkao-platform-prototype`
- Governance baseline: `main@519513ba6c2968c67a0eb05994778ef959771ca9`
- Relevant frozen decisions:
  - `WDV1_G08_FROZEN_DECISIONS.md`
  - `WDV1_G08_SCHEMA_TRANSACTION_DESIGN.md`
- API repo baseline after STEP 4.3 merge: `gongkao-question-bank-api@ec06ea4038069f8c0d7475b8a1cfacb9e809425a`

## Goal

Provide a read-only, provider-neutral private source abstraction so that the
future processing service can obtain the immutable bytes of a finalized DOCX
without:

- relying on local filesystem details,
- leaking `storage_uri` or absolute paths beyond the internal source-access
  boundary to the parser, external API, user-visible errors, normal logs, or
  diagnostics,
- modifying immutable source evidence,
- coupling the parser to storage or ORM concerns.

`storage_uri` is allowed only as the opaque private-source locator passed from
the future processing service to the reader. It must not propagate into the
parser, `SourceReadResult`, or any external surface.

This slice intentionally does **not** parse DOCX content or produce processing
results.

## Non-goals

The following are explicitly out of scope for STEP 4.4A:

- Direct OOXML traversal / parser logic
- `DocumentBlock` generation
- `SourceProcessingGap` generation
- Processing-result reservation or finalization
- Idempotency trigger implementation
- FastAPI processing endpoints
- Reader dependency wiring in FastAPI / router layer (no consumer exists yet)
- React / visual preview changes
- Image/formula/table parsing
- Worker / queue / retry scheduler
- New database migration or M-006 modification
- `SourceSpan` or question-field fill semantics

## Frozen Decisions

The plan follows these already-approved decisions:

- **R1 — Read/write capability separation**
  - `PrivateSourceStorage` is the write-side capability.
  - A separate read-only capability (`PrivateSourceReader`) is introduced for
    processing. The same concrete storage implementation may implement both.

- **R2 — Responsibility boundary**
  - The business layer decides *which* source to process.
  - The reader only returns the bytes of the source that the business layer
    asked for.
  - The reader does not query the DB, decide business eligibility, or interpret
    DOCX.
  - The parser does not know `PaperVersion`, `storage_uri`, or storage
    implementation details.

- **R2-output — Reader result**
  - The reader returns the source bytes plus minimal read facts (size,
    actual SHA-256).
  - It reports what it read; it does not judge whether the bytes match business
    expectations.

- **R3 — Integrity ownership**
  - SHA-256 comparison between `PaperVersion.file_hash` and the actual hash is
    the responsibility of the future processing service.
  - The reader only computes and returns the actual hash.
  - If hashes mismatch, the processing service must mark the result as `failed`
    and must not invoke the parser.

- **R4 — Read/integrity failure semantics**
  - Reader read failures are terminal for that processing intent; the future
    processing service will finalize the result as `failed`.
  - Hash mismatch is **not** a reader error; it is a processing-service-level
    integrity failure.
  - No automatic retry worker/backoff is introduced.
  - Diagnostics must be bounded machine-readable codes; absolute paths,
    `storage_uri`, raw bytes, source text, credentials, and tracebacks must not
    leak.

## Current Code Facts

- `src/gongkao_api/modules/papers/storage.py` defines:
  - `PrivateSourceStorage` Protocol with `stage`, `promote`,
    `discard_staged`, `discard_uncommitted`.
  - `LocalPrivateSourceStorage` concrete implementation that stores files under
    `data/private_sources/objects/` and generates `private://paper-versions/{id}.docx`
    URIs.
  - A convenience method `read_for_verification(storage_uri: str) -> bytes`
    already exists, but it is **not** part of a formal read-only abstraction and
    is currently used only for verification in upload tests.
- `src/gongkao_api/core/config.py` provides `private_source_storage_root: Path`.
- M-006 schema (`source_processing_results`, `document_blocks`,
  `source_processing_gaps`, `paper_version_active_processings`) is in place and
  does **not** need modification for the reader.

## Proposed Change Surface

This plan proposes changes **only** in the API repository and only to the
storage boundary layer. No production code is written by this planning document;
the changes listed below are what STEP 4.4A implementation will be authorized to
do after plan approval.

1. **New `PrivateSourceReader` Protocol** in
   `src/gongkao_api/modules/papers/storage.py`:

   ```python
   from dataclasses import dataclass

   @dataclass(frozen=True, slots=True)
   class SourceReadResult:
       content: bytes
       size: int
       sha256: str

   class PrivateSourceReader(Protocol):
       def read(self, storage_uri: str) -> SourceReadResult: ...
   ```

   - `storage_uri` is used only as the internal opaque locator from the future
     processing service to the reader. The reader implementation is the only
     place that resolves it.
   - `SourceReadResult` is intentionally small: bytes + objective facts. It does
     not contain `PaperVersion`, `storage_uri`, expected hash, or business
     decisions.

2. **Extend `LocalPrivateSourceStorage`** to implement `PrivateSourceReader` by
   adding a public `read(self, storage_uri: str) -> SourceReadResult` method.
   The existing `read_for_verification` logic can be reused internally, but the
   new method returns the richer `SourceReadResult` object.

3. **Define a narrow reader-specific failure** in the storage layer, e.g.:

   ```python
   class SourceReadError(Exception):
       def __init__(self, code: str) -> None:
           self.code = code
   ```

   - This is a storage/read-layer exception, not a domain error. It carries only
     a bounded safe code such as `SOURCE_READ_FAILED`.
   - The future processing service will catch this exception and map it to the
     business diagnostic code persisted on the `SourceProcessingResult`. The
     reader itself does not decide `ProcessingResult` semantics, HTTP responses,
     or persistence.

4. **No migration or ORM change.**

5. **No FastAPI dependency wiring.** Reader/provider wiring will be introduced
   only when a real Processing Service / API consumer exists in a later approved
   slice.

## Implementation Steps

After plan approval:

1. Add `SourceReadResult` dataclass and `PrivateSourceReader` Protocol in
   `src/gongkao_api/modules/papers/storage.py`.
2. Implement `LocalPrivateSourceStorage.read()` returning
   `SourceReadResult(content, size, sha256)`.
3. Re-implement `read_for_verification()` as a thin wrapper around `read()` if
   appropriate, or keep both independently if tests depend on exact return type.
4. Add `SourceReadError` with bounded code and update module exports.
5. Verify that no call site passes `PaperVersion` into the reader; only
   `storage_uri` is used.
6. Add unit/contract tests for the reader boundary.

## Test Plan

Tests are synthetic and must not use real exam content or private paths.

| Test | Purpose |
| --- | --- |
| `test_promoted_source_can_be_read_back_byte_for_byte` | Prove reader returns the exact bytes that were promoted. |
| `test_reader_returns_exact_size` | Prove `SourceReadResult.size == len(content)`. |
| `test_reader_returns_sha256_matching_returned_bytes` | Prove returned SHA-256 matches `content`. |
| `test_missing_source_raises_safe_reader_failure` | Prove `SourceReadError` with bounded code; no path/URI leak. |
| `test_failure_does_not_expose_path_uri_or_bytes` | Inspect exception/code metadata to confirm no private details. |
| `test_read_does_not_alter_source_bytes_or_hash` | Compare bytes/hash before and after `read()`; unchanged. |
| `test_existing_writer_contracts_still_pass` | `stage` / `promote` / `discard` behavior unchanged. |
| `test_read_for_verification_remains_compatible` | Existing G-07 verification helper still works if retained. |
| `test_reader_is_instantiable_without_orm` | Reader only needs storage root/config; no `Session`, `PaperVersion`, or repository fixture required. |
| `test_storage_instance_can_serve_as_both_reader_and_writer` | Same concrete class implements both protocols. |

Tests should create a `LocalPrivateSourceStorage` with a temporary root, stage
and promote a synthetic DOCX byte sequence, then call `read(storage_uri)`.

## Failure / Security Boundaries

- The reader never returns absolute filesystem paths.
- The reader never returns `storage_uri` inside `SourceReadResult`.
- `storage_uri` is allowed only as the internal input from the future processing
  service to the reader; it does not propagate to the parser, API responses,
  user errors, logs, or diagnostics.
- Exceptions carry only bounded codes; messages and metadata are safe.
- The reader does not compare expected vs actual hashes.
- The reader does not modify files.
- The parser layer is not introduced in this slice, so no parser/storage
  coupling exists yet.

## Expected Git Diff

Only the following files should change during STEP 4.4A implementation:

```text
src/gongkao_api/modules/papers/storage.py       (+ Protocol, SourceReadResult, read impl, SourceReadError)
tests/.../test_paper_storage.py                 (+ reader boundary tests)
```

No migration, ORM, service, parser, router, or React changes are expected.

If implementation reveals that another production file must change, the plan
must be updated to explain **why it is required now** and **why it cannot wait
for a real consumer** before the work proceeds.

## Open Questions

```text
NO PRODUCT DECISION BLOCKER

Engineering choices resolved by this revision:
- internal reader locator = storage_uri string (no typed SourceRef in STEP 4.4A)
- FastAPI dependency/provider wiring deferred until a real consumer exists
- reader-specific failure kept narrow and storage-level; future Processing Service
  will normalize it to the business diagnostic code persisted on the result
```

All required product decisions for this slice are already frozen in the
authoritative STEP 4.4A decisions.

## Exit Criteria

STEP 4.4A is complete when:

1. `PrivateSourceReader` Protocol and `SourceReadResult` exist.
2. `LocalPrivateSourceStorage` implements `PrivateSourceReader.read()`.
3. `SourceReadError` with bounded `SOURCE_READ_FAILED` code exists.
4. Tests prove reader returns exact bytes + size + SHA-256, fails safely without
   leaking paths or URIs, and does not alter source files.
5. `ruff`, `mypy`, and `pytest` pass against PostgreSQL 16 test database.
6. No migration, ORM, processing service, parser, API endpoint, router, or
   React code was added.
