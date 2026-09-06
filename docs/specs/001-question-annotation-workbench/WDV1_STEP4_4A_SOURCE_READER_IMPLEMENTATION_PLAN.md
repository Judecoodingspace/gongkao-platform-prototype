# WDV1 STEP 4.4A Source Reader Boundary Implementation Plan

## Status

**DRAFT / PENDING TEAM A AND PRODUCT OWNER REVIEW**

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
- exposing `storage_uri` or absolute paths outside the storage layer,
- modifying immutable source evidence,
- coupling the parser to storage or ORM concerns.

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
  - Reader read failures (`SOURCE_READ_FAILED`) and hash mismatches
    (`SOURCE_HASH_MISMATCH`) are terminal processing failures for that intent.
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
- `src/gongkao_api/core/errors.py` defines `DomainError` / `DomainRuleViolation`
  for expected domain failures.
- Dependency injection in `src/gongkao_api/modules/papers/router.py` currently
  creates `LocalPrivateSourceStorage` from settings.
- M-006 schema (`source_processing_results`, `document_blocks`,
  `source_processing_gaps`, `paper_version_active_processings`) is in place and
  does **not** need modification for the reader.

## Proposed Change Surface

This plan proposes changes **only** in the API repository and only to the
storage boundary layer. No production code is written by this planning document;
the changes listed below are what STEP 4.4A implementation will be authorized to
do after plan approval.

1. **New `PrivateSourceReader` Protocol** in
   `src/gongkao_api/modules/papers/storage.py` (or a sibling file if repo
   conventions prefer):

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

   - `storage_uri` is used as the reader input because the API already persists
     this value and it is not an absolute path. The reader implementation is the
     only place that knows how to resolve it.
   - `SourceReadResult` is intentionally small: bytes + objective facts. It does
     not contain `PaperVersion`, expected hash, or business decisions.

2. **Extend `LocalPrivateSourceStorage`** to implement `PrivateSourceReader` by
   adding a public `read(self, storage_uri: str) -> SourceReadResult` method.
   The existing `read_for_verification` logic can be reused internally, but the
   new method returns the richer `SourceReadResult` object.

3. **Define reader-side error vocabulary** in the storage layer, e.g.:

   ```python
   class SourceReadError(DomainError):
       def __init__(self, code: str) -> None:
           self.code = code
   ```

   Initial codes: `SOURCE_READ_FAILED`, `SOURCE_HASH_MISMATCH` is **not** a
   reader error (it is a processing-service error). This keeps the reader
   responsibility clean.

4. **Add a FastAPI dependency** `get_private_source_reader()` that returns the
   same `LocalPrivateSourceStorage` instance but typed as
   `PrivateSourceReader`, mirroring the existing `get_private_source_storage()`
   pattern.

5. **No migration or ORM change.**

## Implementation Steps

After plan approval:

1. Add `SourceReadResult` dataclass and `PrivateSourceReader` Protocol in the
   storage module.
2. Implement `LocalPrivateSourceStorage.read()` returning
   `SourceReadResult(content, size, sha256)`.
3. Re-implement `read_for_verification()` as a thin wrapper around `read()` if
   appropriate, or keep both independently if tests depend on exact return type.
4. Add `SourceReadError` with bounded codes and update module exports.
5. Add `get_private_source_reader()` dependency provider in the papers router
   module (or storage module if that is where dependency providers live).
6. Verify that no call site passes `PaperVersion` into the reader; only
   `storage_uri` is used.
7. Add unit/contract tests for the reader boundary.

## Test Plan

Tests are synthetic and must not use real exam content or private paths.

| Test | Purpose |
| --- | --- |
| `test_reader_returns_bytes_size_and_sha256` | Prove reader returns objective read facts. |
| `test_reader_fails_with_safe_code_on_missing_source` | Prove `SOURCE_READ_FAILED` is raised without leaking paths. |
| `test_read_for_verification_still_works` | Preserve existing G-07 contract behavior. |
| `test_reader_signature_does_not_depend_on_papervention` | Confirm reader is independent from ORM/DB. |
| `test_storage_instance_can_serve_as_both_reader_and_writer` | Confirm same concrete class implements both protocols. |
| `test_reader_result_does_not_contain_storage_uri_or_path` | Confirm no private implementation details leak. |

Tests should create a `LocalPrivateSourceStorage` with a temporary root, stage
and promote a synthetic DOCX byte sequence, then call `read(storage_uri)`.

## Failure / Security Boundaries

- The reader never returns absolute filesystem paths.
- The reader never returns the `storage_uri` inside `SourceReadResult`.
- Exceptions carry only bounded codes; messages and metadata are safe.
- The reader does not compare expected vs actual hashes.
- The reader does not modify files.
- The parser layer is not introduced in this slice, so no parser/storage
  coupling exists yet.

## Expected Git Diff

Only the following files should change during STEP 4.4A implementation:

```text
src/gongkao_api/modules/papers/storage.py       (+ Protocol, SourceReadResult, read impl, SourceReadError)
src/gongkao_api/modules/papers/router.py        (+ get_private_source_reader dependency if added here)
tests/.../test_paper_storage.py                 (+ reader boundary tests)
```

No migration, ORM, service, parser, or React changes are expected.

## Open Questions

```text
NO PRODUCT DECISION BLOCKER
```

All required decisions for this slice are already frozen in the authoritative
STEP 4.4A decisions. The only implementation-level choices (e.g., exact module
file for the Protocol, whether to keep `read_for_verification` as-is) are
ordinary engineering decisions that stay within the frozen boundary and can be
resolved during code review.

## Exit Criteria

STEP 4.4A is complete when:

1. `PrivateSourceReader` Protocol and `SourceReadResult` exist.
2. `LocalPrivateSourceStorage` implements `PrivateSourceReader.read()`.
3. `SourceReadError` with bounded `SOURCE_READ_FAILED` code exists.
4. Tests prove reader returns bytes + size + SHA-256 and fails safely without
   leaking paths or URIs.
5. `ruff`, `mypy`, and `pytest` pass against PostgreSQL 16 test database.
6. No migration, ORM, processing service, parser, API endpoint, or React code
   was added.
