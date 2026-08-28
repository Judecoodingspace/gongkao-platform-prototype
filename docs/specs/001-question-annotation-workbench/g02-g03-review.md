# G-02 / G-03 Review Record: Shenlun V1 Persistence

## Review Metadata

- Review date: 2026-08-28
- Scope: pure-text Shenlun persistence contract and PostgreSQL migration design
- GitHub issue: [#4 Shenlun V1: API contract and database migration review](https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/4)
- Result: `G-02 approved`, `G-03 approved`
- Implementation authorization: begin `SHV1-004`; this record does not claim that application code or a database already exists

## G-02 Contract Decisions

1. A question version owns four distinct text fields: `stem_text`, `requirement_text`, `question_text`, and `reference_answer_text`.
2. Reusable Shenlun passages are not duplicated in `stem_text`. They use `SourceMaterial`, `SourceMaterialVersion`, and ordered `QuestionVersionMaterial` links.
3. Draft creation requires a finalized paper version, controlled Shenlun knowledge point, and complete source-order tuple. Content may remain incomplete while the record is a draft.
4. Submission requires nonblank requirement, question, and reference answer, plus either a nonblank question-specific stem or at least one valid linked source-material version.
5. `QuestionVersion.status` is authoritative for historical workflow state. `Question.status` mirrors the current version for filtering.
6. Only current draft versions are mutable. Submitted, approved, and rejected versions are immutable.
7. A rejected or approved current version is corrected by creating a new draft version. A submitted version cannot be superseded until review resolves it.
8. Changing a draft's global source order moves its `QuestionSlot` atomically. A conflict changes neither row.
9. Optimistic concurrency uses `expected_row_version`; stale writes return `409 STALE_DRAFT`.
10. Idempotency scope is actor + operation + client request ID. Replays are checked before mutable-state validation and never repeat a successful write.
11. wangEditor HTML/JSON is not authoritative backend data. V1 accepts normalized plain text and exact material-version IDs.
12. Review/approval endpoints, objective options, image content, parser candidate ingestion, and bulk import remain outside this slice.

## G-03 Migration Decisions

1. PostgreSQL 16 is the only accepted migration and contract-test database; SQLite is not a substitute.
2. SQL names use plural `snake_case`. IDs are application-generated UUIDv4 values. Timestamps are UTC `timestamptz`.
3. Workflow values use bounded `varchar` plus named checks, not PostgreSQL native enums.
4. Required tables are fixed in `migration-plan.md`, including versioned shared materials, exact material links, audit events, and idempotency keys.
5. Ordinary business FKs use `ON DELETE RESTRICT`. Deferred circular current-version ownership FKs use `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`. The application exposes no physical-delete workflow.
6. Composite current-version FKs guarantee that a current pointer belongs to its own question or material aggregate.
7. Question global order is unique in `question_slots`, not `question_versions`, so historical versions may preserve the same source order.
8. Material global order is unique in `source_materials`; material versions preserve source-order snapshots.
9. Authenticated actor UUIDs are required but have no database FK until the identity slice owns a user table.
10. Audit and idempotency records store identifiers, hashes, statuses, and safe metadata only; they do not store complete private text payloads.
11. Local/CI migration tests use a disposable PostgreSQL 16 service, require `APP_ENV=test`, and reject database names not ending in `_test`.
12. Shared-environment upgrades require a verified custom-format backup. Once annotation data exists, recovery uses restore or reviewed forward-fix migrations, not destructive downgrade.

## Findings Resolved During Review

| Finding | Resolution |
| --- | --- |
| API exposed version status but schema did not store it | Added `QuestionVersion.status` and migration mapping |
| Shared source material would be duplicated per question | Added versioned reusable material entities, endpoints, links, and tests |
| Source-order PATCH could diverge from `QuestionSlot` | Required one atomic slot/version transaction |
| Correction-version eligibility was ambiguous | Limited to current rejected or approved versions; submitted remains locked |
| Approved history could disappear behind a new draft | Historical `QuestionVersion.status` and release links remain authoritative |
| Circular current-version FKs were underspecified | Defined composite deferred ownership FKs and migration order |
| Delete behavior was unspecified | Fixed non-cascading FK policy |
| Idempotency storage could leak private payloads | Store request hash/result metadata only; no request or response body |
| Test database could accidentally target developer data | Added environment and `_test` database-name guards |
| SourceSpan rule conflicted with HTML preview limitations | Require spans when coordinates exist; prohibit fabricated spans |

## Deferred Decisions

- Difficulty ownership remains unresolved. The column is nullable and not accepted by this API slice.
- File/object storage is still a separate decision. Contract tests create sanitized finalized paper-version fixtures.
- Identity-provider integration is deferred; actor IDs enter through the API authentication boundary.
- Reviewer approval/rejection endpoints and review records are the next workflow slice after persistence acceptance.
- V2 mixed-content fields and assets remain governed by `ContentBlock`/`DocumentAsset` design and are not implemented here.

## Entry Criteria For SHV1-004

Terra may scaffold the approved FastAPI/Alembic/PostgreSQL backend and tests when it:

1. reads the files listed in `migration-plan.md`;
2. checks and preserves the dirty worktree;
3. records implementation start on issue #4;
4. creates only the approved backend/migration/test structure;
5. does not begin React persistence wiring before `G-04` passes.
