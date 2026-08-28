# Migration Plan: Shenlun V1 Persistence

## 1. Purpose

This plan turns the approved domain model into a testable local database schema for the first pure-text Shenlun persistence slice. It is a plan, not an executable migration.

Approved implementation baseline (`G-01`, 2026-08-23):

- Node.js 22 LTS + npm 10 for the React 19, TypeScript 5.7, Ant Design 5 web application;
- CPython 3.12 + FastAPI + Pydantic + SQLAlchemy 2.x + Alembic 1.x for the API;
- PostgreSQL 16;
- Pytest and Playwright for the required verification layers.

Do not introduce a second backend, ORM, migration tool, package manager, or production runtime without a new reviewed plan decision. Preserve the tables, constraints, transaction boundaries, immutability rules, and verification steps below.

## 2. Preconditions And Stop Conditions

Terra must complete these checks before creating application code:

1. Read `AGENTS.md`, `HANDOFF.md`, `docs/constitution.md`, `data-model.md`, `api-contract.md`, this file, `plan.md`, and `tasks.md`.
2. Confirm gate `G-01`: frontend, backend, database, ORM, migration tool, package manager, and supported runtime versions are recorded in `plan.md`.
3. Confirm gate `G-02`: the four Shenlun fields, five knowledge-point codes, source-order semantics, draft mutability, and API contract are reviewed.
4. Confirm gate `G-03`: table names, FK behavior, indexes, rollback policy, and local test-database strategy are reviewed.
5. Check `git status`; preserve unrelated user changes.
6. Open or reuse a dedicated GitHub issue for this implementation slice and record start, blockers, verification, and completion with `gh`.

Stop and request a decision if any gate is not explicitly approved. Do not infer the stack from the static HTML prototype.

## 3. Schema Mapping

`G-03` fixes the following physical conventions:

- Table and column names use lowercase `snake_case` plural table names.
- IDs are application-generated UUIDv4 values stored as PostgreSQL `uuid`; migrations do not require `pgcrypto`.
- Timestamps use `timestamptz`, are stored in UTC, and default to `CURRENT_TIMESTAMP` where appropriate.
- Workflow codes use bounded `varchar` plus named `CHECK` constraints, not PostgreSQL native enums, so future values can be added with ordinary migrations.
- Business/provenance rows are never physically deleted by the API. Ordinary foreign keys use `ON DELETE RESTRICT`; the two deferred circular current-version constraints use `ON DELETE NO ACTION`. No cascade may erase versions, links, audit events, or idempotency records.
- `created_by` and `actor_id` are non-null UUIDs supplied by the authenticated identity boundary. They intentionally have no database FK until the identity/auth slice owns a user table.

### 3.1 Required Existing/Core Tables

- `papers`
- `paper_versions`
- `knowledge_points`
- `source_materials`
- `source_material_versions`
- `questions`
- `question_slots`
- `question_versions`
- `question_version_materials`
- `audit_events`
- `idempotency_keys`

The first migration may create these together if the database is new. Do not add `DocumentBlock`, `ContentBlock`, image asset, review, or release tables merely to make a future model look complete; those belong to separate slices unless already required by an approved foundational migration.

### 3.2 Core Table Decisions

- `papers`: UUID PK; title, province, year, subject, exam type, creator, and timestamps. `year` is nullable with a sensible range check because a source collection may span years.
- `paper_versions`: UUID PK; `paper_id` FK; positive version number; file metadata/hash/storage URI; upload status; optional parser metadata; creator/timestamp; `UNIQUE (paper_id, version_number)`. `upload_status` supports `uploaded`, `finalized`, and `failed`; question/material creation requires `finalized`.
- `knowledge_points`: UUID PK; nullable parent FK; unique stable code; display name; subject; optional question type; positive display order; status; timestamp. Seed IDs are fixed constants in the migration so all environments are deterministic; business code still looks values up by stable code.
- `questions`: UUID PK; non-null current-version pointer; current workflow status; creator/timestamp. Status mirrors the current `QuestionVersion` and is not the historical source of truth.
- `question_slots`: UUID PK; paper and paper-version FKs; positive slot number; nullable unique `question_id`; slot status; timestamps; `UNIQUE (paper_version_id, slot_number)`. Unstarted slots may have no question.
- `source_materials`: UUID PK; paper-version FK; positive current source-order index; non-null current-version pointer; current status; creator/timestamp; `UNIQUE (paper_version_id, source_order_index)`.
- `source_material_versions`: UUID PK; material FK; positive version number; paper-version provenance snapshot; status; positive source-order snapshot; source label; text content; optimistic row version; reason/creator/timestamps; `UNIQUE (source_material_id, version_number)`.
- `question_version_materials`: exact version-to-version link with positive order; composite PK `(question_version_id, source_material_version_id)` and `UNIQUE (question_version_id, order_index)`.

The `questions.current_version_id` and `source_materials.current_version_id` ownership FKs are composite and `DEFERRABLE INITIALLY DEFERRED`: `(questions.id, current_version_id)` references `(question_versions.question_id, question_versions.id)`, and the material equivalent references `(source_material_id, id)`. This both resolves circular inserts within one transaction and prevents a current pointer from targeting another aggregate's version. The supporting `(owner_id, id)` pairs are unique.

Approved Shenlun seed IDs:

| id | code |
| --- | --- |
| `10000000-0000-4000-8000-000000000001` | `shenlun.summary` |
| `10000000-0000-4000-8000-000000000002` | `shenlun.countermeasure` |
| `10000000-0000-4000-8000-000000000003` | `shenlun.analysis` |
| `10000000-0000-4000-8000-000000000004` | `shenlun.applied_writing` |
| `10000000-0000-4000-8000-000000000005` | `shenlun.essay` |

### 3.3 `question_versions` Shenlun Columns

| Column | PostgreSQL type | Nullability/default | Rule |
| --- | --- | --- | --- |
| `id` | `uuid` | PK | server-generated |
| `question_id` | `uuid` | not null, FK | stable question identity |
| `version_number` | `integer` | not null | starts at 1 |
| `paper_version_id` | `uuid` | not null, FK | immutable source upload |
| `status` | `varchar(16)` | not null | `draft`, `submitted`, `approved`, or `rejected` |
| `subject` | `varchar(32)` | not null | `shenlun` in this slice |
| `question_type` | `varchar(32)` | not null | `subjective` in this slice |
| `knowledge_point_id` | `uuid` | not null, FK | active Shenlun taxonomy row |
| `stem_text` | `text` | not null, default `''` for draft | nonblank on submit |
| `requirement_text` | `text` | not null, default `''` for draft | nonblank on submit |
| `question_text` | `text` | not null, default `''` for draft | nonblank on submit |
| `reference_answer_text` | `text` | not null, default `''` for draft | nonblank on submit |
| `explanation_text` | `text` | nullable | not used as reference answer |
| `province` | `text` | nullable | snapshot copied from paper when present |
| `year` | `smallint` | nullable | snapshot copied from paper when present |
| `difficulty` | `smallint` | nullable | deferred product decision; check 1 through 5 when present |
| `source_order_index` | `integer` | not null | greater than 0 |
| `source_topic_order` | `integer` | not null | greater than 0 |
| `source_question_order` | `integer` | not null | greater than 0 |
| `source_topic_label` | `text` | not null | nonblank |
| `row_version` | `integer` | not null, default 1 | optimistic lock, greater than 0 |
| `change_reason` | `text` | nullable on v1, required for later versions | audit context |
| `created_at` | `timestamptz` | not null | server time |
| `created_by` | `uuid` | not null | authenticated actor |
| `updated_at` | `timestamptz` | not null | server time |

Do not store wangEditor HTML/JSON in these columns. Convert editor state to normalized plain text at the application boundary. Do not put source ordering into a JSONB catch-all.

### 3.4 Required Constraints And Indexes

- `UNIQUE (question_id, version_number)` on `question_versions`.
- `CHECK (version_number > 0)` and `CHECK (row_version > 0)`.
- Positive checks for all three numeric source-order fields.
- Named status checks on questions, question versions, slots, materials, material versions, paper versions, and knowledge points.
- `UNIQUE (paper_version_id, slot_number)` on `question_slots`.
- `UNIQUE (question_id)` on `question_slots`; PostgreSQL permits multiple nulls for unstarted slots.
- `UNIQUE (paper_version_id, source_order_index)` on `source_materials` and version uniqueness on material versions.
- B-tree index on `(paper_version_id, source_order_index)` for current-version listing.
- B-tree index on `(paper_version_id, knowledge_point_id, source_question_order)` for specialty views.
- B-tree index on `(question_id, status)` for historical approved/rejected version lookup.
- B-tree index on `(source_material_id, status)` for material history.
- B-tree index on `questions(status)`.
- B-tree index on `question_versions(knowledge_point_id)`.

Do not place a global unique constraint on `(paper_version_id, source_order_index)` in `question_versions`: multiple immutable versions of the same question legitimately copy the same source order. The uniqueness boundary belongs to `question_slots`, while application logic verifies that a version's `source_order_index` matches its slot.

Taxonomy subject membership, question-slot/version order equality, material current-order/version-snapshot equality, nonblank-on-submit rules, and same-paper material linking cross rows or depend on workflow state. Enforce them in service transactions and contract tests; do not use fragile database checks that query another table.

### 3.5 Audit And Idempotency Tables

`audit_events` is append-only and stores: ID, actor ID, action code, entity type, entity ID, optional question/question-version/material-version IDs, request ID, safe `details jsonb`, and timestamp. `details` may contain changed field names and status transitions, never complete text values or source document content.

`idempotency_keys` stores: ID, actor ID, operation scope, client request UUID, SHA-256 request hash, result resource type/ID, result HTTP status, optional result row version, and created timestamp. It has `UNIQUE (actor_id, operation_scope, client_request_id)`. V1 has no automatic expiry; deleting keys could make old create requests execute twice. It stores neither request bodies nor full response snapshots.

## 4. Migration Sequence

Each migration must be small enough to review and test independently. The `M-001` through `M-005` boundaries and physical conventions are approved; implementation may add descriptive Alembic revision identifiers but must not merge or reorder the domain dependencies without a new review.

### M-001: Core Identity And Source Tables

Create `papers`, `paper_versions`, and any required actor reference boundary. Add immutable file metadata and foreign keys. Verify duplicate paper-version numbers and hashes follow the approved existing model.

### M-002: Controlled Taxonomy

Create `knowledge_points` with stable `code`, `name`, `subject`, `default_order`, and `status`. Add `UNIQUE (code)` and seed the five Shenlun values transactionally. Seeds are reference data, not extracted document labels.

### M-003: Question Identity And Navigation

Create `questions` and `question_slots`. Add stable slot uniqueness per paper version. Keep unstarted slots independent from question creation if the approved workflow pre-creates slots.

### M-004: Versioned Pure-Text Content

Create `source_materials`, `source_material_versions`, `question_versions`, and `question_version_materials` with the approved text fields, exact version links, source-order snapshots, optimistic locks, constraints, and indexes. Create owner and version tables first without circular current-version FKs, then add the approved composite `DEFERRABLE INITIALLY DEFERRED` constraints in the same revision after all tables exist.

### M-005: Idempotency And Audit

Create or reuse append-only audit and idempotency storage. Store request ID, operation scope, actor, request hash, response resource ID, and timestamps. Do not store full private question payloads in these tables.

### M-006: Service-Level Integrity Tests

Add transaction tests for create, update, submit, stale-write rejection, source-order conflict, and new-version correction before exposing the endpoint to the frontend.

## 5. Existing Data And Backfill

At the time of this plan, there is no production database and no approved production schema. Therefore the expected first implementation is a clean local schema; there is no automatic backfill.

If a database or ad hoc prototype records appear before implementation:

1. Stop the migration and inventory schema/version/counts without printing private text.
2. Export a backup and record its checksum and location outside version control.
3. Write a one-off importer with sanitized fixture tests.
4. Import records only as `draft`; never infer `approved`, knowledge points, source order, requirements, or reference answers.
5. Quarantine rows whose four fields or source mapping cannot be determined, and produce counts/IDs only.
6. Require human review before submit.

Static prototype JavaScript state and wangEditor HTML are not database migration sources.

## 6. Transaction Boundaries

- Draft create: `Question` + `QuestionSlot` + `QuestionVersion` + current-version pointer + audit + idempotency record in one transaction.
- Material create: `SourceMaterial` + `SourceMaterialVersion` + current pointer + audit + idempotency record in one transaction.
- Draft patch: conditional update where `row_version = expected_row_version`; if source order changes, lock and update the stable slot/material row in the same transaction; increment the counter and append audit atomically.
- Submit: lock current question/version, slot, and linked material versions in deterministic UUID order; validate completeness and ownership; transition the question/version and linked draft material versions; append audit and commit atomically.
- New correction version: lock the aggregate, verify current base status is rejected or approved, calculate the next version number, copy fields and exact material-version links, create a draft, update current pointer/status, append audit, and commit atomically.

Any failure rolls back the complete operation. Do not publish events or return success before commit.

## 7. Upgrade Verification

Run against a disposable local PostgreSQL database:

1. Upgrade an empty database to head.
2. Assert all expected tables, columns, FKs, checks, and indexes exist.
3. Verify exactly five active Shenlun taxonomy seeds with the expected stable codes.
4. Run the API contract tests from `api-contract.md`.
5. Re-run upgrade and seed operations to prove idempotency.
6. Create two versions of one question with the same source order and verify this is allowed.
7. Attempt a second question slot with the same paper/version global order and verify rejection.
8. Verify submitted content and the earlier version remain unchanged after creating a correction draft.
9. Inspect logs to ensure complete private text is absent.
10. Verify every FK has the approved non-cascading delete action and both current-version composite FKs are deferred.
11. Link one material version to two question versions and verify one stored material body with two ordered links.

The approved FastAPI/SQLAlchemy/Alembic command family is:

```powershell
alembic upgrade head
pytest tests/migrations tests/api/test_shenlun_questions.py
```

Terra must replace paths only after inspecting the generated repository structure. It must not fabricate passing commands or tests.

The local/CI test database is PostgreSQL 16 in a disposable Docker Compose service by default. Tests require a database name ending in `_test` and an explicit `APP_ENV=test`; startup must abort if either guard fails. A developer may point the same test harness at another disposable PostgreSQL 16 instance, but SQLite is not an accepted migration or contract-test substitute.

## 8. Rollback And Recovery

- Before shared-environment upgrade, take and verify a database backup.
- For a shared PostgreSQL environment, use a custom-format `pg_dump`, verify it with `pg_restore --list`, and record the database migration revision and backup checksum outside version control before upgrading.
- On a disposable empty local database, downgrade may remove newly created objects for migration-test purposes.
- Once any shared environment contains annotation data, destructive downgrade is prohibited. Restore from the verified backup or use a reviewed forward-fix migration.
- Never drop, truncate, rewrite, or mass-update question/version/audit tables automatically as a recovery shortcut.
- If an upgrade fails before commit, fix the migration in local development and retry from a clean disposable database.
- If an upgrade partially commits in a shared environment, stop writes, record the exact migration state, restore or forward-fix after review, and keep an incident note.

## 9. Definition Of Done

- Gates `G-01` through `G-03` are approved and linked from the implementation issue.
- Migration upgrade passes from an empty disposable database.
- Schema inspection confirms all four text fields and all four source-order fields.
- API contract tests pass, including optimistic concurrency and immutable submitted versions.
- No private paper content is committed in fixtures, snapshots, logs, comments, or migration seeds.
- Data model, API contract, generated migration, tests, and actual endpoint payloads use the same names.
- GitHub issue contains commands run, test result counts, known limitations, and migration/rollback notes.

Failure of any item leaves the slice incomplete. Do not move to frontend persistence wiring merely because tables were created.
