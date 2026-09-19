# WDV1 G-09 Pure-Text Question Annotation E2E — Implementation Plan

```text
PLAN_STATUS = CORRECTIVE REVISION 2 — READY FOR TEAM B FINAL REVIEW
PLAN_REVISION = 2
IMPLEMENTATION_PLAN_AUTHORIZED = YES
IMPLEMENTATION_AUTHORIZED = NO
DATABASE_MIGRATION_AUTHORIZED = NO
BACKEND_CODE_AUTHORIZED = NO
FRONTEND_CODE_AUTHORIZED = NO
TEST_IMPLEMENTATION_AUTHORIZED = NO
MERGE_AUTHORIZED = NO
```

## 1. Status and Authorization

This document is an implementation plan only. Corrective Revision 2 aligns the passed Plan Rev1 decomposition with Contract Rev4's ephemeral next-placeholder and atomic lazy-materialization authority while preserving the five resolved Team B Plan findings. It does not authorize a migration, Python change, test implementation, frontend work, or merge. The future implementation must stop after each checkpoint in section 31 until the applicable review is complete.

The plan adds no product behavior. In particular, it does not add reassignment, review/publication, question deletion/reordering, automatic topic detection, automatic question splitting, formal RBAC, a worker, or parser behavior.

## 2. Exact Baselines

| Repository | Required baseline | Verified Git state before planning |
|---|---|---|
| Governance / Contract, `Judecoodingspace/gongkao-platform-prototype` | `dc9661b738b737d4f5a91f5dfaa9bcefcc996f2b` | the exact object and `origin/docs/20260916-wdv1-g09-annotation-e2e-contract` resolved to the required SHA; worktree clean before the Rev2 branch was created |
| Backend, `Judecoodingspace/gongkao-question-bank-api` | `c627650b63b4eb0f1531d07771ea06b5cc851d5e` | detached `HEAD` and `origin/main` both resolved to the required SHA; worktree clean |

Previous Plan source: `WDV1_G09_IMPLEMENTATION_PLAN.md` at Plan Rev1 `2da8aff2c9b741405db615b45b39a61288023559` on `plan/20260919-wdv1-g09-annotation-e2e-rev1`. Rev2 branch: `plan/20260919-wdv1-g09-annotation-e2e-rev2`, created directly from Contract Rev4 `dc9661b738b737d4f5a91f5dfaa9bcefcc996f2b` without merging the Rev1 branch. The Contract and Frozen Decisions remain read-only.

## 3. Authority

Implementation authority order is fixed:

1. `WDV1_G09_PRODUCT_FROZEN_DECISIONS.md` as contained in the Contract Rev4 lineage;
2. `WDV1_G09_IMPLEMENTATION_CONTRACT.md` at `dc9661b738b737d4f5a91f5dfaa9bcefcc996f2b`;
3. continuing G-07/G-08 privacy, provenance, immutable-history, active-selection, and no-cascade invariants;
4. backend baseline `c627650b63b4eb0f1531d07771ea06b5cc851d5e` where not superseded by the authorities above;
5. this file's internal decomposition and naming choices.

Any conflict that requires changing user-visible workflow, permission meaning, canonical question source, save-and-next, source-topic correction, completion/reopen, overwrite behavior, or provenance returns to Contract review under section 35.

## 4. Repository Inventory

The backend is not greenfield. The implementation must extend these observed baseline artifacts:

| Area | Existing files and behavior | Planned use |
|---|---|---|
| migrations | `migrations/versions/0001` through `0006`; current head is revision `0006_m006`; PostgreSQL-named PK/FK/unique/check/index conventions | add exactly one linear `0007_m007` descendant; never edit M-001–M-006 |
| paper intake | `modules/papers/{models,repository,service,router,schemas,storage,validation}.py` | reuse DOCX validation, private staging/promotion/compensation patterns, `Paper`, `PaperVersion`, finalized bytes, hashes, and restrictive ownership |
| questions | `modules/questions/{models,repository,service,router,schemas}.py` | reuse `Question`, `QuestionVersion`, `QuestionSlot`, four text columns, LF normalization, length limits, row-version rules, and non-package behavior |
| taxonomy | `modules/taxonomy/{models,repository,router,schemas}.py`; M-002 seeds five active Shenlun/subjective knowledge points | validate controlled knowledge points; never infer source topic from taxonomy |
| processing | `modules/source_processing/{models,repository,service,parser_types,parser_constants,parser}.py`; M-006 | call `trigger_processing`, `activate_processing_result`, `get_active_processing`, `get_processing_blocks`, and `get_processing_gaps`; do not change `ProcessingService` or parser |
| idempotency | `modules/idempotency/{models,repository}.py`; unique actor/scope/request key and SHA-256 fingerprints | add a reusable SAVEPOINT reserve/reload primitive for new commands without changing existing processing semantics |
| audit | `modules/audit/{models,repository}.py` | append safe IDs/codes/counts/hashes only; never source text, answers, storage data, or parser metadata |
| actor/error boundary | `api/dependencies.py`, `core/security.py`, `core/errors.py`, `api/errors.py` | retain `X-Actor-Id`; add optional actor lookup for compatible generic reads and structured safe domain-error fields/tokens |
| routing/OpenAPI | `api/v1/router.py`, `main.py`, `scripts/export_openapi.py`, `openapi/openapi.json` | register one package router and regenerate the checked-in OpenAPI artifact |
| tests | `tests/migrations`, `tests/services`, `tests/api`; destructive fixtures already call `Settings.assert_disposable_test_database()` | extend PostgreSQL 16 suites with synthetic fixtures; retain `APP_ENV=test` and `_test` guards |

Observed compatibility constraints:

- no `QuestionOption` model/table exists at this baseline; G-09 adds none and continues to use only the four Shenlun text fields;
- existing generic draft patch accepts legacy order/topic fields for non-package questions; package-specific patch must accept only four fields and optional `knowledge_point_id`;
- generic question GET/list are currently unauthenticated, so package-owned records require membership-aware filtering/authorization without breaking non-package reads;
- generic submit/correction must return `ANNOTATION_REVIEW_DEFERRED` for package-owned questions and all package-owned mutations must honor `completed` read-only state;
- `DocumentBlock` has unique `(processing_result_id, source_order)` but needs a new composite unique `(processing_result_id, id)` for exact provenance ownership;
- the processing read side has no FastAPI router; G-09 exposes safe package-scoped wrappers rather than a generic processing router;
- the historical `AGENTS.md` stage prose predates merged M-006, while its architecture, privacy, PostgreSQL, no-cascade, and verification rules remain binding.

## 5. Implementation Strategy

Create one cohesive business module at `src/gongkao_api/modules/annotation_packages/` with `models.py`, `policies.py`, `repository.py`, `service.py`, `schemas.py`, and `router.py`. Routes validate/translate, the service owns domain rules and transactions, repositories own SQL/locking, and policies centralize creator/assigned-annotator checks without claiming formal RBAC.

The package module owns orchestration, not source parsing or legacy question lifecycle. It creates package-owned questions through the existing models and mirrors authoritative package ordering into legacy fields. It wraps the existing `ProcessingService` with the canonical `ParserConfig()` profile. Exact block text is read server-side only after package/source/active-result ownership is validated.

Use one additive M-007 migration with exactly seven new G-09 tables. No command-response receipt, response JSON column, affected-row snapshot table/column, event-store snapshot, or eighth G-09 table is permitted. Use package-level serialization for aggregate mutations, `QuestionVersion.row_version` for draft mutations, workspace row versions for per-actor view state, and the existing `idempotency_keys` table with a race-safe reservation gate. Read queries do not allocate state.

G-09 replay is effect-idempotent: the same actor, scope, `client_request_id`, and fingerprint never execute the business mutation twice, while a replay may return the current safe authoritative resource representation after later legal changes. It does not promise a byte-for-byte historical HTTP response. Stable result identity remains mandatory for package import and both question-create modes. Save-and-next resolves the same existing real next question when one was originally selected; a tail placeholder has no persistent identity and replay returns current truth—real N+1 if later materialized, otherwise an equivalent ephemeral descriptor. Package-owned current questions also maintain the invariant `AnnotationPackageQuestion.knowledge_point_id == QuestionVersion.knowledge_point_id`; ordinary field or knowledge-point save updates both mirrors in one transaction without changing source-topic metadata, provenance, or `package.row_version`.

Current baseline has no administrator identity source. The V1 policy implementation is therefore explicit and bounded: creator may import, process, adopt, and read; assigned annotator may read and perform annotation mutations; no third-party administrator branch is invented. A future trusted management adapter may be added only under separate authority.

## 6. Dependency Graph

```text
Phase 0 safety snapshot
  -> Phase 1 M-007 schema
      -> Phase 2 ORM/repositories/policies
          -> Phase 3 dual-DOCX package import
          -> Phase 4 processing wrapper/readiness
              -> Phase 5 task/detail/source/open reads
                  -> Phase 6 start-first + lazy materialization/order
                      -> Phase 7 existing-draft save + draft-first materialization + generic-route guard
                      -> Phase 8 existing/source-action-first provenance
                      -> Phase 9 save-and-next + ephemeral placeholder
                      -> Phase 10 source-topic correction
                      -> Phase 11 resume/workspace
                          -> Phase 12 completion
                              -> Phase 13 reopen/all-path write protection
                                  -> Phase 14 HTTP/error/OpenAPI closure
```

Phases may share a branch but must follow the commit/checkpoint sequence in sections 30–31. A later phase cannot hide a failing earlier invariant.

Phase 8 depends on Phase 4's active-result semantics, Phase 6's package membership, and Phase 7's draft concurrency guard. Its concurrency boundary is therefore fixed before implementation: idempotency gate, then package, selected package sources/PaperVersions/active selections in `question_paper` then `explanation` order, followed by membership, Question, current QuestionVersion, and provenance head. No dependency may introduce the inverse question/version-before-active-selection order.

## 7. Phase 0 — Baseline and Safety Preparation

| Item | Plan |
|---|---|
| Goal | Prove exact inputs and establish a reproducible, disposable pre-change baseline. |
| Existing files reused | `AGENTS.md`, `pyproject.toml`, `compose.yaml`, `alembic.ini`, `core/config.py`, all current tests. |
| Files added/modified | None. Create future backend feature branch `impl/20260917-wdv1-g09-annotation-e2e` exactly from `c627650b63b4eb0f1531d07771ea06b5cc851d5e`; governance planning remains on its separate branch. |
| DB/API/service/repository/schema impact | None. |
| Concurrency/idempotency | Record current Processing Service race/idempotency tests as protected regression evidence. |
| Tests/commands | `git fetch origin --prune`; verify `origin/main`; `git status --short`; `docker compose --profile test up -d postgres-test`; set `GONGKAO_APP_ENV=test`, `GONGKAO_DATABASE_URL=postgresql+psycopg://gongkao:gongkao_test_password@localhost:5433/gongkao_api_test`, `PYTHONPATH=(Get-Location).Path`; run `uv sync --all-groups`, the explicit safety assertion, PostgreSQL version query, `uv run ruff check .`, `uv run mypy src`, `uv run pytest`, and `uv run python scripts/export_openapi.py`; store only pass/fail/counts and commit SHAs, never payloads. |
| Dependencies | Exact clean baselines and PostgreSQL 16. |
| Stop conditions | SHA drift, dirty out-of-scope files, unsafe DB name/environment, non-PostgreSQL-16 server, baseline lint/type/test/OpenAPI failure. |
| Acceptance | A recorded before-change snapshot exists and M-006 Processing Service suite is green. |

## 8. Phase 1 — Schema / Migration Foundation

| Item | Plan |
|---|---|
| Goal | Add the complete G-09 persistence foundation as one linear additive migration. |
| Existing files reused | `migrations/versions/0006_m006_source_processing_schema.py`, `questions`/`papers`/`source_processing` tables, `idempotency_keys`, `audit_events`. |
| Files added | `migrations/versions/0007_m007_g09_annotation_e2e.py`; `tests/migrations/test_g09_annotation_schema.py`. |
| Files modified | `src/gongkao_api/modules/source_processing/models.py` for ORM parity of `(processing_result_id, id)`; `tests/migrations/test_migrations.py` expected head inventory. |
| Database objects | Seven new tables, composite keys/FKs, indexes, checks, M-007 immutability trigger function/triggers, and new `document_blocks` composite unique; exact matrix in section 23. |
| API/service/repository/schema impact | None yet. |
| Concurrency/idempotency | Source-topic unique is `DEFERRABLE INITIALLY IMMEDIATE`; Phase 10 explicitly defers it inside its transaction. Nullable last-edited composite FK is deferrable to allow atomic first-question creation. |
| Tests | clean base→head, M-006→M-007, head no-op, constrained downgrade/upgrade, exact named objects, ownership failures, deferrable reorder, append-only trigger rejection, all FK delete actions non-cascade. |
| Validation | focused migration tests, then existing `tests/migrations`; `alembic current`, `alembic upgrade head`, and on disposable DB only `alembic downgrade 0006_m006` then re-upgrade. |
| Dependencies | Phase 0. |
| Stop conditions | Any destructive rewrite of M-001–M-006, unsafe downgrade needing history deletion, impossible exact ownership FK, SQLite substitution. |
| Acceptance | M-007 is one child of `0006_m006`; all objects and no-cascade/immutability rules are proven on PostgreSQL 16. |

Migration revision is planned as `revision = "0007_m007"`, `down_revision = "0006_m006"`. Downgrade requires all seven M-007 tables to be empty; it fails closed with a clear operator error if G-09 rows exist, then drops triggers/function, constraints/indexes, tables in reverse dependency order, and finally the added `document_blocks` unique. It never deletes business rows to make downgrade succeed.

## 9. Phase 2 — ORM Models, Policies, and Repositories

| Item | Plan |
|---|---|
| Goal | Map M-007 and expose deterministic persistence primitives without business workflow in repositories. |
| Existing files reused | `db/base.py`, paper/question/taxonomy/processing repositories, idempotency and audit repositories. |
| Files added | `annotation_packages/__init__.py`, `models.py`, `policies.py`, `repository.py`. |
| Files modified | `source_processing/models.py`; `idempotency/repository.py` for `reserve_or_resolve` SAVEPOINT support. |
| Repository responsibilities | `add_package_graph`, `get/lock_package`, `get/lock_source_by_role`, `list_packages_for_actor`, `list/lock_memberships_in_global_order`, `lock_source_topic_groups`, `get_membership_by_question/version`, `next_global_order`, `update_last_edited`, workspace get/lock/upsert, active-result/block/gap ownership queries, append/list provenance revisions and links, lock/move provenance head. No permission, readiness, transition, text-merge, completion, or reorder decisions live here. |
| Service responsibilities | actor policy, readiness composition, transitions, validation, ordering calculation, server text reconstruction, hashes, audit/idempotency semantics, and transaction ownership. |
| API/schema impact | None yet. |
| Concurrency/idempotency | Every lock query uses explicit deterministic ordering; `reserve_or_resolve` inserts under nested transaction, flushes, and reloads/locks the winner after unique race. Existing ProcessingService stays unchanged. |
| Tests | repository ownership joins, actor-scoped pagination, locks ordered by role/global order, workspace and provenance CRUD, race-safe idempotency primitive. |
| Validation | focused repository/service tests plus Ruff and MyPy. |
| Dependencies | Phase 1 schema. |
| Stop conditions | repository starts committing, embeds workflow policy, or requires mutable processing history. |
| Acceptance | All later phases can express their transaction using named repository calls; no generic `crud.py`/`utils.py`. |

## 10. Phase 3 — Package Intake

| Item | Plan |
|---|---|
| Goal | Implement `POST /api/v1/annotation-packages` for one atomic package with two immutable DOCX sources. |
| Existing files reused | `papers.validation.validate_docx_upload`, `PrivateSourceStorage`, `Paper`, `PaperVersion`, G-07 staging/promotion/compensation and safe audit patterns. |
| Files added/modified | add `annotation_packages/{schemas,service,router}.py`; add package service/API tests and synthetic DOCX fixture; no change to paper intake behavior. |
| DB objects | insert one package, two Papers, two finalized PaperVersions, two package-source associations, one idempotency key, safe audit rows. |
| API/schema | multipart `PackageImportRequest` fields plus `question_paper`/`explanation`; response `PackageDetail`; replay resolves the same package ID and may return its current safe representation with `200` + `Idempotent-Replay: true`; first success is `201`. |
| Service sequence | validate both and compute a safe fingerprint → perform a non-authoritative replay probe → stage both → allocate version IDs → promote both → in one DB transaction race-safely reserve/resolve the idempotency key and insert the full graph only for the winner → commit; a replay/race loser or any promotion/DB failure compensates every object created by that attempt. Role-specific Paper titles are deterministic package-title derivatives. |
| Repository | `add_package_graph`, replay lookup, package detail reads. |
| Concurrency/idempotency | scope `annotation_package.import`; fingerprint includes normalized metadata, assigned annotator, and role-bound safe upload digest/size inputs, never bytes, client filename, or private path; same key/different fingerprint conflicts. |
| Tests | creator differs from assigned; replay preserves package identity without duplication and may return current safe detail; two-role cardinality; either validation/promotion/DB failure leaves no partial package/object; private values absent from response/audit/log/idempotency. |
| Validation | focused service/API/storage tests, existing G-07 paper tests, Ruff/MyPy. |
| Dependencies | Phases 1–2. |
| Stop conditions | reuse would require separate committed paper transactions, source bytes become mutable, or partial package can persist. |
| Acceptance | Contract acceptance 1 and import half of 1a pass. After a successful import response, the formal application/client orchestration **must** issue `POST /annotation-packages/{package_id}/processing` automatically in the same user-intent/session flow, without a second user-facing click. Import and processing remain two API commands and separate transactions; no worker, queue, background job, or hidden retry is created. Later reprocess remains an explicit new user action. |

## 11. Phase 4 — Processing Integration and Package Readiness

| Item | Plan |
|---|---|
| Goal | Wrap the existing ProcessingService for two package roles and derive truthful readiness. |
| Existing files reused | `ProcessingService` five public methods, `ParserConfig()` defaults, active-selection/history/stale semantics, private source reader. |
| Files added/modified | package service/router/schemas and `tests/services/test_annotation_processing_integration.py`; ProcessingService and parser files remain unchanged. |
| DB/API | implement package processing, role reprocess, and exact-result adopt routes; no new lifecycle columns. |
| Service | authorize creator management; resolve immutable role association; call current service in role order; compose effective/latest state; derive `ready`, `ready_with_warnings`, or `not_ready`; append package-safe adoption audit after delegated activation. |
| Repository | package/source ownership reads only; ProcessingRepository remains behind ProcessingService except package-safe composed read queries. |
| Concurrency/idempotency | child UUIDv5 namespace = package ID, name = `{package_client_request_id}:{role}`; wrapper does not cache aggregate response; partial adoption delegates exact activation idempotency; failed never active. |
| Tests | success both; partial requires adoption; failed blocks without older active; older active survives later failure/stale; 200/202 composition; retry produces no duplicate child; role/result cross-binding fails. Run complete existing Processing Service suite. |
| Validation | focused package-processing tests plus `tests/services/test_source_processing_service.py` and schema tests. |
| Dependencies | Phase 3 package/source rows. |
| Stop conditions | any need to change parser, ProcessingService lifecycle, auto-activate partial, activate failed, or add a worker. |
| Acceptance | Contract acceptance 2–4 and 27 pass with no Processing Service modification. |

## 12. Phase 5 — Package Detail, Task List, Safe Source Read, and Open

| Item | Plan |
|---|---|
| Goal | Expose scoped package/task/readiness reads and stable authorized source content. |
| Existing files reused | processing blocks/gaps/active result, package repository, safe error envelope. |
| Files added/modified | package repository/service/schemas/router; package/API/privacy tests. |
| API/schema | package list/detail, source content, annotation open; DTOs exactly follow Contract §21, and created-question count is persisted membership count only. |
| Repository | actor-scoped keyset list; package/source lookup; active result; page query merging blocks/gaps ordered `(source_order,item_kind_rank,item_id)`; count persisted memberships only. |
| Service | allow creator or assigned reads; map safe source states/gap codes/messages; block open when not ready; open is read-only and returns null current question for `not_started`; no read fabricates or persists a placeholder. |
| Cursor | opaque URL-safe base64 JSON `[processing_result_id, source_order, item_kind_rank, item_id]`; decode verifies active result identity and cursor membership; active-result change invalidates cursor safely. Gap rank 0, block rank 1. |
| Concurrency/idempotency | reads use snapshot queries, no row locks, idempotency, status transition, last-edited change, or fabricated page number. |
| Tests | scopes/filter/pagination and persisted-only counts; completion list return target; same-order gap/block pagination; active result switch; safe gap mapping; no private/parser/storage values; failed/not-ready open rejection. |
| Validation | focused API/service tests, error-contract tests, Ruff/MyPy. |
| Dependencies | Phase 4 readiness. |
| Stop conditions | source content cannot remain package-scoped, cursor skips/duplicates ties, or a page number would be invented. |
| Acceptance | Contract acceptance 5, 5a, 6, open half of 7, 17, and 23a pass. |

## 13. Phase 6 — Start-first, Lazy Materialization, and Package Ordering

| Item | Plan |
|---|---|
| Goal | Implement the existing question-create route as the closed `start_first | materialize_after` request union, with canonical question-paper ownership and authoritative membership order. |
| Existing files reused | `Question`, `QuestionVersion`, `QuestionSlot`, `TaxonomyRepository`, four-field baseline defaults/limits. |
| Files added/modified | package service/repository/schemas/router; question creation tests. |
| API/schema | `POST /annotation-packages/{package_id}/questions` remains one route. `start_first` carries final metadata and is valid only for ready/not-started/zero-membership state. `materialize_after` carries client request ID, expected package token, real tail `after_question_id`, expected tail-question token, final knowledge point/source-topic metadata, and discriminated `initial_mutation=draft_patch|source_action`; it never accepts `source_question_order`. |
| Start-first transaction | reserve idempotency → lock package → validate ready/not-started/zero membership, assigned actor, and package token → validate metadata → create the only permitted empty real Q1/first version/slot/membership → transition to `in_progress` → increment package token once → safe audit/commit. |
| Materialize-after base | reserve/resolve idempotency → lock package → validate assigned actor/in-progress/expected package token → verify `after_question_id` and expected question token still identify the real persisted tail → lock memberships in global order → validate final taxonomy/source-topic metadata → derive `global_order=tail+1` and server-only `source_question_order` → create Question, QuestionVersion directly in final initial state with `row_version=1`, QuestionSlot, and membership → apply the meaningful initial mutation through Phase 7 or 8 in this same transaction → set last-edited to the new question → increment package token exactly once → safe audit/commit. No empty intermediate commit is allowed. |
| Canonical source | `QuestionSlot.paper_id`, `QuestionSlot.paper_version_id`, and `QuestionVersion.paper_version_id` all use the package `question_paper`; explanation is never placed in those fields. |
| Ordering | membership `global_order` is authoritative and mirrored to slot/source-order index; server allocates local `source_question_order`; client submits only source-topic metadata. |
| Meaningful boundary | Materialize only for a successful authored-field save/autosave, explicit knowledge-point change, explicit source-topic metadata change, or source action. View/tab switch/scroll/temporary selection/popover/local typing before acknowledged save/enter/leave do nothing. Empty/no-op requests return `VALIDATION_ERROR`. |
| Concurrency/idempotency | package lock, both expected tokens, tail recheck, and DB unique constraints ensure two tabs over the same shell produce exactly one N+1, never N+1 and N+2. A loser is `STALE_PACKAGE`, `STALE_DRAFT`, or exact replay. Replay resolves the same materialized question/version identity without reapplying the mutation or incrementing tokens. |
| Failure | Validation, stale token/source, ownership, DB, or commit failure rolls back Question, QuestionVersion, QuestionSlot, membership, provenance, count, last-edited, package token, and success audit together. The client remains on its ephemeral shell. |
| Tests | open creates nothing; exact first transition; request-union/schema/no-op rejection; draft/metadata/source-action first materialization; rollback leaves zero rows; two-tab and replay create one N+1; wrong actor/readiness/tokens; five valid knowledge points; explanation-canonical negative check; no empty/precreated slots. |
| Validation | focused creation/concurrency tests plus existing Shenlun question tests. |
| Dependencies | Phases 2, 4, 5. |
| Stop conditions | canonical Question source must change, total question count is inferred, or package ordering cannot remain contiguous. |
| Acceptance | Contract acceptance 7, 13, 15e–15h, and creation/order aspects of 16 pass. |

## 14. Phase 7 — Draft Save, Autosave, and Last-edited

| Item | Plan |
|---|---|
| Goal | Persist partial four-field/knowledge-point patches on real drafts, implement draft/metadata-first lazy materialization, and protect generic routes. |
| Existing files reused | LF normalization, field limits, `QuestionVersion.row_version`, legacy QuestionService non-package behavior. |
| Files added/modified | package schemas/service/router/repository; `questions/{repository,service,router}.py`; `api/dependencies.py`; save and compatibility tests. |
| API/schema | Existing real drafts use `PATCH /question-versions/{version_id}` with request ID, expected question row version, any subset of four fields, and optional knowledge point; it forbids source-topic/order/material fields. A placeholder has no version ID, so its first authored or metadata mutation uses the Phase 6 create route with `mode=materialize_after`, final metadata, and `initial_mutation={kind:"draft_patch", fields?, explicit_metadata_changes?}`. |
| Service | reserve/resolve idempotency → lock package → resolve and lock membership → lock Question/current QuestionVersion → require assigned/in-progress/current draft → validate expected question row version and taxonomy → mutate exact supplied fields; when `knowledge_point_id` changes, update `QuestionVersion.knowledge_point_id` and the membership mirror `AnnotationPackageQuestion.knowledge_point_id` in the same transaction → increment question row version exactly once → update last-edited → safe audit/commit. Source-topic fields/local order and provenance remain unchanged; package row version remains unchanged. |
| Generic protection | Before `QuestionService.create_draft()` or any generic create path inserts rows, query whether the requested `paper_version_id` is referenced by any `AnnotationPackageSource`, for either `question_paper` or `explanation`. If bound, return safe `403 FORBIDDEN` and create no Question, QuestionVersion, or QuestionSlot; package-owned questions are created only through `POST /annotation-packages/{package_id}/questions`. Existing membership-aware patch/submit/correction/list/detail protections remain: package mutations route through package policy or reject; submit/correction return `ANNOTATION_REVIEW_DEFERRED`; completed returns read-only error; generic unauthenticated lists exclude package-owned rows; package detail requires creator/assigned optional actor. Standalone PaperVersion generic create behavior and schemas remain compatible. |
| Lazy draft/metadata transaction | Execute inside Phase 6 materialization: validate at least one authored value differs from the empty initial value or one declared metadata value differs from inherited defaults; write the first QuestionVersion directly with final fields/metadata and `row_version=1`; keep membership/version knowledge-point mirrors equal; derive local order from final source-topic metadata; create no provenance for manual text; update last-edited and package token once. There is no create-blank-then-PATCH sequence. |
| Concurrency/idempotency | existing scope `annotation.question.patch:{version_id}` remains unchanged. Lazy scope includes package/tail identity; fingerprint covers both expected tokens, final metadata, discriminator, fields, and explicit metadata-change markers. Exact replay returns the same new question and applies nothing twice; changed payload conflicts; stale returns safe tokens; no automatic merge/overwrite. |
| Tests | independent round trips and LF-only normalization; autosave replay/conflict/two-tab stale; draft-first and metadata-only first materialization, final inherited/overridden metadata, row_version 1, one package-token increment, full rollback/no rows, exact replay; knowledge-point A→B mirror behavior on existing drafts; last-edited only on success; generic-create bypass tests reject both package source roles with no rows while standalone and package-route creation work; all other generic bypass attempts and non-package regressions. |
| Validation | focused save/API tests plus existing `test_shenlun_services.py` and `test_shenlun_contract.py`. |
| Dependencies | Phase 6. |
| Stop conditions | package status/assignment can be bypassed, non-package API compatibility breaks, or autosave becomes last-write-wins. |
| Acceptance | Contract acceptance 8, 12–14, 15e, 15g–15h, 17, and relevant 22/24 pass. |

## 15. Phase 8 — Source Actions and Exact Field Provenance

| Item | Plan |
|---|---|
| Goal | Implement transactional fill/append/replace from exact active blocks with immutable copy-on-write provenance for both existing drafts and a placeholder's source-action-first materialization. |
| Existing files reused | active processing selection, immutable blocks, question row version, audit/idempotency. `source_materials` is not used for G-08 block provenance. |
| Files added/modified | package models/repository/service/schemas/router; provenance service/API/migration tests. |
| Existing-draft validation | reserve/resolve idempotency → lock package and validate assigned/in-progress status → resolve selected package source roles → lock selected package-source rows in deterministic role order `question_paper`, `explanation` → lock corresponding PaperVersion rows in the same role order → lock active-processing selection rows in the same role order → validate every selected ProcessingResult is the current active result → lock package-question membership → lock Question → lock current QuestionVersion → validate expected question row version, field, and mode → lock provenance head → validate exact result/block composite ownership → reject empty/duplicates/bad within-source order → read exact immutable server text. No section may acquire question/version before selected active-source locks. |
| Placeholder orchestration | A placeholder has no version ID and never calls the existing source-action route first. It uses the Phase 6 create route with `mode=materialize_after` and `initial_mutation={kind:"source_action", ...}`. After the idempotency gate/package validation/tail recheck, lock selected package sources in role order, corresponding PaperVersions, active selections, then memberships/order; validate exact immutable blocks; create Question/final initial QuestionVersion/slot/membership; append revision/links and move the provenance head; set last-edited; increment package token once; audit/commit. This preserves source-before-question lock order and never commits an empty question. |
| Mutation sequence | apply fill/append/confirmed replace; SHA-256 resulting text; append complete provenance revision; copy old links for append then new links, or only new links for fill/replace; move head; increment question row version; update last-edited; safe audit; commit. Never mutate/copy block text into history. |
| API | source-action command and paginated immutable provenance-history query; response computes `is_current_active_result`. |
| Concurrency/idempotency | existing-draft actions cause no package-token churn and use the question token. Source-action-first materialization fingerprints tail/tokens/final metadata plus field/mode/confirmation/ordered result+block IDs, never source text; replay never repeats fill/append/replace, provenance, creation, or token increments. |
| Tests | all existing action cases plus source-action-first exact provenance, inherited/overridden metadata, no intermediate blank version, stale-selection/ownership/DB failure zero-row rollback, same-request replay, changed-payload conflict, and two-tab materialization versus active-result adoption/completion with deterministic lock order and no stale acceptance/deadlock. |
| Validation | focused provenance/service/API tests plus M-006 ownership regressions. |
| Dependencies | Phases 4, 6, 7. |
| Stop conditions | exact result+block ownership cannot be enforced, text must enter audit/idempotency/logs, or prior history would mutate. |
| Acceptance | Contract acceptance 9–12, 15f–15h, and provenance portions of 18/20/25/26 pass. |

## 16. Phase 9 — Save-and-next and Ephemeral Next Placeholder

| Item | Plan |
|---|---|
| Goal | Atomically save the current real question and return either an existing real next question or a non-persisted tail placeholder; save-and-next never creates the next question. |
| Existing files reused | Phase 7 existing-draft patch helper and package/membership locks. Phase 6 lazy materialization is a later, separate first-mutation command. |
| Files added/modified | package service/schemas/router/repository and concurrency tests. |
| Transaction | reserve/resolve idempotency → lock package → validate assigned actor/in-progress/expected package token → lock current membership/Question/current QuestionVersion → validate expected question token → apply optional current draft patch → set last-edited to current real question → locate persisted `global_order+1`; if present return its `QuestionDraft`, otherwise construct a `NextQuestionPlaceholder` response only → safe save/navigation audit → commit current save. Tail creates no Question/Version/Slot/membership/provenance/question-creation audit and changes neither package token nor persisted count. |
| API/schema | no `next_knowledge_point_id`. `SaveAndNextResult={saved_question, next_question|null, next_placeholder|null, package_row_version}` with exactly one next target. `NextQuestionPlaceholder={display_order, default_knowledge_point_id, default_source_topic_order, default_source_topic_label}` and contains no question/version/membership/draft ID or row version. Delete `created_next`. |
| Concurrency/idempotency | Replay never repeats current save, materializes nothing, and does not increment package token. If the original target was an existing real question, return that same stable identity's current representation. If it was a tail shell, return current persisted N+1 if later materialized, otherwise an equivalent ephemeral descriptor; never invent historical placeholder identity. |
| Tests | save failure rolls back acknowledgement; existing next vs tail; tail creates zero rows/count/token; exact DTO mutual exclusion/no IDs; double-click/timeout replay; N+1 later materialized before replay; inheritance defaults; placeholder excluded from list/count/resume/completion; no duplicate or persisted shell. |
| Validation | focused service/concurrency/API tests. |
| Dependencies | Phases 6–7. |
| Stop conditions | current save and next selection cannot share one commit, tail requires persistence or token/count change, inheritance changes, or a pre-dialog/new knowledge-point input is required. |
| Acceptance | Contract acceptance 15, 15a–15d, 15i, and navigation aspects of 16 pass. |

## 17. Phase 10 — Source-topic Correction

| Item | Plan |
|---|---|
| Goal | Implement the frozen aggregate-level metadata correction and safe local renumbering. |
| Existing files reused | deferrable local-order unique, package/membership/question/version locks, idempotency/audit. |
| Files added/modified | package service/repository/schemas/router and source-topic concurrency tests. |
| Transaction | replay gate first: an identical winner exits without entering the reorder transaction or incrementing any token. First execution reserves idempotency → locks package → validates assigned actor, `in_progress`, expected package token → resolves/locks target current draft and expected row version → identifies old/new `(source_topic_order,source_topic_label)` groups → locks their union in `global_order` → `SET CONSTRAINTS uq_annotation_package_questions_source_topic_order DEFERRED` → updates target metadata → stable-sorts each group by `global_order` and assigns contiguous 1..N → mirrors membership metadata/local order to current QuestionVersions → increments the target row version and every other affected draft whose local order changed → increments package row version → writes safe audit/result identity → flushes the deferred constraint and commits. |
| API/schema | dedicated PATCH; client cannot submit `source_question_order`. `SourceTopicCorrectionResult` contains current `updated_question`, current `package_row_version`, nullable `affected_questions`, and `ordering_refresh_required`. First success has no replay header, returns the committed target/package token and actual rows changed by that transaction, and sets refresh false. Replay sets `Idempotent-Replay: true`, returns current target/package truth, `affected_questions=null`, and refresh true. Knowledge point is untouched. |
| Concurrency/idempotency | fingerprint contains both expected tokens and target topic metadata. Identical replay never renumbers, guesses/reconstructs historical affected rows, or increments question/package row versions; changed fingerprint conflicts. When refresh is true, the client issues `GET /annotation-packages/{package_id}/questions` without another user confirmation or correction command. Package lock serializes first executions with create/save-next/completion. |
| Tests | first-success same-group and cross-group cases return exact committed changed rows and refresh false; move first/middle/last across populated/empty groups; old/new contiguous order; stale package/target; immediate identical replay has replay header, null affected rows, refresh true, and no token change; replay after an unrelated legal mutation returns current target/package truth without mutation; same ID changed metadata conflicts; no receipt persistence; concurrent create/correction; completed rejection then reopen success. |
| Validation | focused migration/service/concurrency/API tests. |
| Dependencies | Phases 1, 6–7. |
| Stop conditions | legal reorder requires transient uniqueness violation outside controlled deferral, client must choose local order, or knowledge point changes. |
| Acceptance | Contract acceptance 16a–16d pass. |

## 18. Phase 11 — Resume and Workspace State

| Item | Plan |
|---|---|
| Goal | Restore server truth and per-actor source view without treating browsing as editing. |
| Existing files reused | package detail/question DTO builders, provenance heads, last-edited pointer. |
| Files added/modified | package service/repository/schemas/router and resume/workspace tests. |
| API/schema | resume query and workspace PATCH with `question_paper|explanation|compare`, expected workspace row version. |
| Service | resume chooses last-edited persisted current question; an untouched placeholder is unknown and cannot be returned. If in-progress pointer null use first persisted question; not-started returns null; completed marks read-only; response includes fields, provenance, workspace and both tokens. Before lazy materialization, resume returns real N; after successful materialization/first mutation it returns new real N+1. Workspace stores only source view. `PATCH /workspace` unconditionally returns `409 ANNOTATION_COMPLETED_READ_ONLY` when the package is completed; only explicit reopen restores workspace mutation. |
| Concurrency/idempotency | workspace scope uses actor/package key, own row version and idempotency; it does not touch package token or last-edited. Replay performs no second workspace mutation and may return current safe workspace state. GET has no locks/idempotency/mutation. |
| Tests | last edited not last viewed; untouched placeholder exit resumes N and never appears in list/count; successful materialization resumes N+1; not-started/in-progress fallback; creator vs assigned separate workspace; stale/replay; temporary selection/popup/dirty/scroll absent; completed resume GET succeeds, completed workspace PATCH is rejected, reopen then workspace PATCH succeeds. |
| Validation | focused service/API tests. |
| Dependencies | Phases 5–8. |
| Stop conditions | a read mutates progress, ephemeral UI state must persist, or workspace becomes global package state. |
| Acceptance | Contract acceptance 17–18, workspace token portion of 13, and completed workspace portion of 22 pass. |

## 19. Phase 12 — Completion

| Item | Plan |
|---|---|
| Goal | Validate every persisted package-membership question, ignore any client-only placeholder, provide stable warning confirmation, and transition only on explicit confirmation. |
| Existing files reused | package/readiness/provenance repositories, safe hashing/audit, fixed contract lock order. |
| Files added/modified | package service/schemas/router/repository and completion tests. |
| Locks | package → package sources in role order → PaperVersions → active pointers → memberships in global order → Questions/current QuestionVersions. Recompute all truth inside this scope. |
| Hard validation | only persisted `AnnotationPackageQuestion` memberships/current versions participate; all four fields must be nonblank after Unicode whitespace validation. Emit safe `field_errors` keyed by question order/field, never values; no invented minimum count. An untouched placeholder produces no missing-field error/warning and cannot block completion. Frontend-local dirty placeholder content remains subject to the FD-23 unsaved guard, not server completion state. |
| Soft warnings | effective partial, gaps, and each nonblank field with no head; canonical sort; token `SHA-256(package_id + row_version + canonical warning codes/locations)`. |
| Two-step command | initial warnings return `COMPLETION_WARNINGS_REQUIRE_CONFIRMATION` and are not stored as success; confirmed call uses new request ID, exact token/codes and unchanged package token; recompute and return `STALE_COMPLETION_CONFIRMATION` on drift. Even no-warning completion requires `confirm_completion=true`. |
| Success | `in_progress -> completed`, increment package token, set actor/time, audit/idempotency, return read-only resume/task-list target; create no submission/review state. |
| Concurrency/idempotency | package lock prevents save/activation/correction races; replay never transitions twice and may return the current safe package/resume representation; conflicting confirmation cannot transition. |
| Tests | aggregate missing-field list; all-real-valid plus untouched placeholder completes without fake error/warning; local dirty guard orchestration; all warning classes; token deterministic/drift; activation race; save/materialization race; explicit confirmation; retry; no warnings still confirm; no review entity. |
| Validation | focused completion/concurrency/API/privacy tests. |
| Dependencies | Phases 4–11. |
| Stop conditions | lock order must change, active truth cannot be recomputed atomically, completion would create review/submission, or semantics change. |
| Acceptance | Contract acceptance 19–21, 23a, and 24 pass. |

## 20. Phase 13 — Reopen and Completed Write Protection

| Item | Plan |
|---|---|
| Goal | Make completed packages read-only across every path and provide explicit audited reopen. |
| Existing files reused | package policy/status lookup, generic-question integration, idempotency/audit. |
| Files added/modified | package service/router/schemas; question service/router/repository; protection tests. |
| Reopen | reserve → lock package → require assigned actor/completed/expected package token → set in-progress → clear current completion fields while audit preserves prior actor/time → increment token → audit/idempotency → return resume. No data/provenance change. |
| Write protection | enforce `ANNOTATION_COMPLETED_READ_ONLY` on package create/save/source-action/save-next/source-topic/workspace without qualification, complete repeat with conflicting key, and all generic question mutation routes; completed workspace PATCH is always blocked even when it changes only `source_view`. Processing management remains governed by creator policy and cannot mutate annotations. |
| Review protection | generic submit and correction for any package-owned question return `ANNOTATION_REVIEW_DEFERRED` regardless of package status. |
| Concurrency/idempotency | reopen scope includes expected package token; replay never transitions twice and may return current safe package/resume state; concurrent stale mutation loses on package lock/token. |
| Tests | every write route table-driven while completed, including workspace PATCH; completed resume GET works; submit/correction; reopen replay/stale/wrong actor; questions/provenance unchanged; post-reopen edit and workspace PATCH work. |
| Validation | focused protection tests plus all legacy question API/service tests. |
| Dependencies | Phase 12. |
| Stop conditions | any side door remains or reopen alters domain content. |
| Acceptance | Contract acceptance 22–24 pass. |

## 21. Phase 14 — HTTP, Error, Schema, Router, and OpenAPI Closure

| Item | Plan |
|---|---|
| Goal | Close all 20 routes, DTO boundaries, error mappings, privacy rules, and generated contract. |
| Existing files reused | FastAPI router/dependencies, `ApiError`, request ID middleware, OpenAPI export script. |
| Files added/modified | package schemas/router; `api/v1/router.py`, `api/dependencies.py`, `core/errors.py`, `api/errors.py`, `openapi/openapi.json`; API/error/privacy tests. |
| Error model | extend `DomainRuleViolation` with allow-listed safe field entries while preserving existing constructor behavior. Map every Contract §22 code/status. Encode safe current tokens and completion warning data within the existing `field_errors` envelope using controlled field names (`row_version`, `package_row_version`, `workspace_row_version`, `warning_set_token`, `warnings.<n>`); never put source text/private data in reasons. |
| DTO closure | forbid extra request fields; freeze `start_first|materialize_after` discrimination and `draft_patch|source_action` initial mutations; normalize only documented LF fields; enforce no-op rejection, bounds, and enums; freeze mutually exclusive `SaveAndNextResult` targets and ID-less `NextQuestionPlaceholder`; responses expose only Contract §21 fields. |
| Router closure | register package router; ensure dependency construction injects storage/reader/session; status/replay headers exact; regenerate OpenAPI and inspect all error responses. |
| Concurrency/idempotency | verify each mutation advertises its required token and request ID; reads advertise neither. |
| Tests | all route/status/header/error shapes, malformed input, missing actor, scoped not-found, privacy/log capture, OpenAPI route/schema snapshot. |
| Validation | focused API suite; Ruff/MyPy; OpenAPI regeneration and clean diff; full Pytest. |
| Dependencies | Phases 3–13. |
| Stop conditions | an error needs traceback/private content, a Contract route is missing, or DTO exposes parser/storage metadata. |
| Acceptance | All API and privacy traceability rows pass; candidate is ready for Checkpoint E, not merge. |

Phase 14 must verify an explicit status mapping for every Contract code: `UNAUTHENTICATED`, `FORBIDDEN`, `ANNOTATION_NOT_ASSIGNED`, `ANNOTATION_PACKAGE_NOT_FOUND`, `QUESTION_NOT_FOUND`, `SOURCE_RESULT_NOT_FOUND`, `IDEMPOTENCY_CONFLICT`, `STALE_DRAFT`, `STALE_PACKAGE`, `STALE_WORKSPACE`, `SOURCE_ORDER_CONFLICT`, `SOURCE_QUESTION_ORDER_CONFLICT`, `NON_EMPTY_OVERWRITE_FORBIDDEN`, `REPLACE_CONFIRMATION_REQUIRED`, `SOURCE_SELECTION_STALE`, `ANNOTATION_COMPLETED_READ_ONLY`, `COMPLETION_WARNINGS_REQUIRE_CONFIRMATION`, `STALE_COMPLETION_CONFIRMATION`, `ANNOTATION_REVIEW_DEFERRED`, `PACKAGE_NOT_READY`, `SOURCE_FAILED`, `PARTIAL_NOT_ADOPTED`, `PROCESSING_RESULT_NOT_ADOPTABLE`, `INVALID_SOURCE_TARGET`, `ANNOTATION_INCOMPLETE`, `VALIDATION_ERROR`, `SOURCE_STORAGE_UNAVAILABLE`, and `PROCESSING_UNAVAILABLE`. Existing non-G-09 codes retain their baseline mappings.

## 22. File Change Matrix

The canonical future backend change set contains 29 files. Paths are exact relative to the backend repository.

| # | File | Action | Phase | Responsibility |
|---:|---|---|---|---|
| 1 | `migrations/versions/0007_m007_g09_annotation_e2e.py` | ADD | 1 | single additive schema descendant of M-006 |
| 2 | `src/gongkao_api/modules/annotation_packages/__init__.py` | ADD | 2 | package module boundary/exports only |
| 3 | `src/gongkao_api/modules/annotation_packages/models.py` | ADD | 2 | seven G-09 ORM mappings and named constraints parity |
| 4 | `src/gongkao_api/modules/annotation_packages/policies.py` | ADD | 2 | creator/assigned read, management, and annotation checks; no formal RBAC claim |
| 5 | `src/gongkao_api/modules/annotation_packages/repository.py` | ADD | 2 | package/source/membership/workspace/provenance persistence and locks |
| 6 | `src/gongkao_api/modules/annotation_packages/schemas.py` | ADD | 3–14 | all package request/response DTOs and package/source/question cursors |
| 7 | `src/gongkao_api/modules/annotation_packages/service.py` | ADD | 3–13 | commands, queries, transactions, readiness, ordering, provenance, completion |
| 8 | `src/gongkao_api/modules/annotation_packages/router.py` | ADD | 3–14 | all 20 Contract HTTP routes and dependency translation |
| 9 | `src/gongkao_api/modules/source_processing/models.py` | MODIFY | 1 | ORM composite unique `(processing_result_id,id)` only; ProcessingService unchanged |
| 10 | `src/gongkao_api/modules/idempotency/repository.py` | MODIFY | 2 | reusable SAVEPOINT reserve/reload-winner primitive for new commands |
| 11 | `src/gongkao_api/modules/questions/repository.py` | MODIFY | 7,13 | package-source PaperVersion binding lookup plus membership-aware generic list/detail/mutation lookup |
| 12 | `src/gongkao_api/modules/questions/service.py` | MODIFY | 7,13 | pre-create package-bound PaperVersion rejection and package assignment/status/no-review bypass enforcement; preserve non-package paths |
| 13 | `src/gongkao_api/modules/questions/router.py` | MODIFY | 7,13 | optional actor on compatible reads and scoped package-owned responses |
| 14 | `src/gongkao_api/api/dependencies.py` | MODIFY | 7,14 | optional actor dependency without weakening mutation authentication |
| 15 | `src/gongkao_api/core/errors.py` | MODIFY | 14 | safe structured domain fields/tokens with backward-compatible constructor |
| 16 | `src/gongkao_api/api/errors.py` | MODIFY | 14 | complete Contract error/status mapping and safe field propagation |
| 17 | `src/gongkao_api/api/v1/router.py` | MODIFY | 14 | register annotation package router |
| 18 | `openapi/openapi.json` | MODIFY | 14 | regenerated checked-in API contract |
| 19 | `tests/migrations/test_migrations.py` | MODIFY | 1 | head table/column/FK/check/unique/index inventory and downgrade expectations |
| 20 | `tests/migrations/test_g09_annotation_schema.py` | ADD | 1 | M-007 ownership, deferral, triggers, no-cascade, M-006→M-007 tests |
| 21 | `tests/services/fixtures/annotation_packages.py` | ADD | 3 | sanitized dual-DOCX/package/question/provenance builders |
| 22 | `tests/services/test_annotation_package_service.py` | ADD | 3,5–7,9,11–13 | intake, mandatory processing boundary, persisted-only reads/count, start-first, draft/metadata materialization, save/KP mirror/generic-create guard/resume/completion/reopen |
| 23 | `tests/services/test_annotation_processing_integration.py` | ADD | 4 | wrapper/readiness/adoption plus ProcessingService regression boundary |
| 24 | `tests/services/test_annotation_provenance_service.py` | ADD | 8 | existing and source-action-first actions, immutable history, exact ownership, manual-edit behavior |
| 25 | `tests/services/test_annotation_concurrency.py` | ADD | 2,6–13 | SAVEPOINT races, lazy rollback/two-tab/replay, stale tokens, source action vs adoption/completion, save-next zero-row replay, truthful source-topic replay, completion races |
| 26 | `tests/api/conftest.py` | MODIFY | 3–14 | multiple synthetic actors, storage override, package helpers; retain DB guard |
| 27 | `tests/api/test_annotation_packages_contract.py` | ADD | 3–5,14 | import/list/detail/process/adopt/source/open wire contract |
| 28 | `tests/api/test_annotation_workbench_contract.py` | ADD | 6–14 | create union, placeholder DTO, question/save/action/next/topic/resume/workspace/completed guard/generic-create bypass/complete/reopen routes |
| 29 | `tests/api/test_annotation_privacy.py` | ADD | 3–14 | response/error/log/audit/idempotency/OpenAPI privacy, no receipt persistence, and cross-package probing |

No parser file, ProcessingService file, frontend file, Contract, or Frozen Decisions file belongs in this change set.

## 23. Migration Object Matrix

All UUIDs use PostgreSQL UUID, times are timezone-aware, and every FK is named and uses `ON DELETE RESTRICT` or `NO ACTION`; no cascade is allowed.

| Object | Columns | PK | FK / exact ownership | Unique / checks / indexes | Deferrable / trigger | Downgrade rule |
|---|---|---|---|---|---|---|
| `annotation_packages` | `id`, `title`, nullable `year`, nullable `region`, `subject`, `exam_type`, `created_by`, `assigned_annotator_id`, `annotation_status`, `row_version`, nullable `last_edited_question_id`, `created_at`, `updated_at`, nullable `completed_at`, nullable `completed_by` | `id` | `(id,last_edited_question_id) -> annotation_package_questions(package_id,question_id)` using `NO ACTION` | checks: nonblank title/exam type, year 1900–2100 if set, subject=`shenlun`, status in three states, positive row version, completion columns both null or both non-null and only completed; indexes `(assigned_annotator_id,annotation_status,updated_at,id)` and `(created_by,annotation_status,updated_at,id)` | last-edited FK `DEFERRABLE INITIALLY DEFERRED` | table must be empty before drop |
| `annotation_package_sources` | `id`, `package_id`, `source_role`, `paper_version_id`, `created_at` | `id` | package and PaperVersion restrictive FKs | unique `(package_id,source_role)`, unique `paper_version_id`, unique `(package_id,id,paper_version_id)`; role check; index `paper_version_id` | immutable UPDATE/DELETE trigger using shared M-007 reject function | empty precondition; drop trigger/table |
| `annotation_package_questions` | `package_id`, `question_id`, `global_order`, `knowledge_point_id`, `source_topic_order`, `source_topic_label`, `source_question_order`, `created_at` | `(package_id,question_id)` | package, Question, KnowledgePoint restrictive FKs | unique `question_id`; unique `(package_id,global_order)`; unique `(package_id,source_topic_order,source_topic_label,source_question_order)`; positive orders/nonblank label; indexes `(package_id,knowledge_point_id,global_order,question_id)` and `(package_id,source_topic_order,source_topic_label,global_order)` | source-topic-local unique is `DEFERRABLE INITIALLY IMMEDIATE` and explicitly deferred only by Phase 10 | empty precondition; last-edited FK removed first |
| `annotation_workspace_states` | `package_id`, `actor_id`, `source_view`, `row_version`, `updated_at` | `(package_id,actor_id)` | package restrictive FK | source view enum check, positive row version; index `(actor_id,updated_at)` | none | empty precondition |
| `question_field_provenance_revisions` | `id`, `package_id`, `question_id`, `question_version_id`, `field_name`, `revision_number`, `operation`, nullable `previous_revision_id`, `resulting_text_hash`, `actor_id`, `client_request_id`, `created_at` | `id` | membership `(package_id,question_id)`; QuestionVersion `(question_id,question_version_id)`; same-stream previous revision `(question_version_id,field_name,previous_revision_id)` | unique `(id,package_id)`; unique `(question_version_id,field_name,revision_number)`; unique `(question_version_id,field_name,id)`; unique `(package_id,question_id,question_version_id,field_name,id)`; four-field/operation/hash/positive revision checks; index `(question_version_id,field_name,revision_number)` | immutable UPDATE/DELETE trigger; previous FK restrictive | empty precondition; drop trigger/table after heads/links |
| `question_field_provenance_links` | `revision_id`, `link_order`, `package_id`, `package_source_id`, `paper_version_id`, `processing_result_id`, `document_block_id`, `source_order_snapshot` | `(revision_id,link_order)` | revision/package exact FK; `(package_id,package_source_id,paper_version_id)` source FK; `(paper_version_id,processing_result_id)` result FK; `(processing_result_id,document_block_id)` block FK | positive link/source order; indexes by result/block and package source; duplicate IDs in one request are rejected by the service, while a later append may intentionally cite a block already present in the copied snapshot | immutable UPDATE/DELETE trigger | empty precondition; drop before revisions |
| `question_field_provenance_heads` | `question_version_id`, `field_name`, `package_id`, `question_id`, `revision_id`, `updated_at` | `(question_version_id,field_name)` | QuestionVersion ownership; membership ownership; exact `(package_id,question_id,question_version_id,field_name,revision_id)` revision FK | four-field check; index `revision_id` | head is deliberately mutable; all FKs restrictive | empty precondition; drop before revisions |
| ALTER `document_blocks` | no new column | existing | supplies exact block target for links | add unique `(processing_result_id,id)` named `uq_document_blocks_processing_result_id_id` | not deferrable | drop only after links are gone; never alter M-006 file |

The trigger function stores no row content and raises a bounded integrity message. Migration tests prove package-source identity and provenance revisions/links reject both UPDATE and DELETE, while provenance heads remain movable.

## 24. API Implementation Matrix

All routes are under `/api/v1`; `annotation_packages.router` supplies the listed router functions. Contract §18's shorthand `GET /annotation-packages/{id}/annotation/resume` is the same endpoint as the canonical §20 route using `{package_id}`, not a twenty-first route. `APRepo` means `AnnotationPackageRepository`; `PRepo`, `QRepo`, `TRepo`, and `SPRepo` are existing paper, question, taxonomy, and source-processing repositories.

| # | Route | Router function | Request → response | Service / repositories | Locks | Idempotency / token | Primary errors | Tests / phase |
|---:|---|---|---|---|---|---|---|---|
| 1 | `POST /annotation-packages` | `import_annotation_package` | multipart import → `PackageDetail` | `import_package`; APRepo + storage + Paper models + audit/idempotency | idempotency key; new graph only | required; import scope; no concurrency token | validation, idempotency, storage unavailable | package API/import, P3 |
| 2 | `GET /annotation-packages` | `list_annotation_packages` | scope/filters/cursor/limit → `PackageTaskList` | `list_packages`; APRepo | none | none | unauthenticated, validation | list scope/cursor, P5 |
| 3 | `GET /annotation-packages/{package_id}` | `get_annotation_package` | none → `PackageDetail` | `get_package_detail`; APRepo + SPRepo reads | none | none | package not found, forbidden | detail/readiness, P5 |
| 4 | `POST /annotation-packages/{package_id}/processing` | `process_annotation_package` | `PackageProcessingRequest` → `PackageProcessingOutcome` | `process_package`; APRepo + existing ProcessingService | ProcessingService locks per child | aggregate ID derives two UUIDv5 child IDs; no package token | forbidden, processing unavailable | wrapper replay/200/202, P4 |
| 5 | `POST /annotation-packages/{package_id}/sources/{role}/processing-results` | `reprocess_annotation_source` | `SourceProcessingRequest` → `SourceProcessingSummary` | `process_source`; APRepo + ProcessingService | existing processing admission locks | child request ID required; no package token | source/package not found, processing unavailable | role reprocess/history, P4 |
| 6 | `POST /annotation-packages/{package_id}/sources/{role}/processing-results/{result_id}/adopt` | `adopt_annotation_source_result` | `AdoptProcessingResultRequest` → summary | `adopt_result`; APRepo + ProcessingService activation + audit | existing PaperVersion/result/active locks | required; existing activation gate | result not found/not adoptable/forbidden | partial/failed/cross-role, P4 |
| 7 | `GET /annotation-packages/{package_id}/sources/{role}/content` | `get_annotation_source_content` | cursor/limit → `SourceContentPage` | `get_source_content`; APRepo + SPRepo | none | none; cursor binds active result | not ready/source failed/partial not adopted/validation | content cursor/gaps/privacy, P5 |
| 8 | `GET /annotation-packages/{package_id}/annotation/open` | `open_annotation_workbench` | none → `AnnotationResume` | `open_annotation`; APRepo/readiness/resume builder | none | none | not ready/source failed/forbidden | no state creation, P5 |
| 9 | `POST /annotation-packages/{package_id}/questions` | `create_annotation_question` | `StartFirstRequest | MaterializeAfterRequest` → `QuestionDraft` | `start_first` or `materialize_after`; APRepo + QRepo + TRepo + optional SPRepo/provenance | start-first: package→memberships; materialize draft: package→tail/memberships; materialize source action: package→selected sources/PaperVersions/active selections→memberships→new question/provenance | required + expected package token; materialize also expected tail token and full initial-mutation fingerprint | not assigned/not ready/stale/order/source selection/idempotency conflict/completed/validation | Q1, draft/metadata/source-action first mutation, rollback/race/replay, P6–8 |
| 10 | `GET /annotation-packages/{package_id}/questions` | `list_annotation_questions` | cursor/limit/kp → persisted-only `PackageQuestionList` | `list_questions`; APRepo | none | none | forbidden/validation | keyset/filter/placeholder absent, P5–6,9,11 |
| 11 | `GET /annotation-packages/{package_id}/questions/{question_id}` | `get_annotation_question` | none → `QuestionDraft` | `get_question`; APRepo + QRepo + provenance reads | none | none | scoped question/package not found | safe detail/no pointer, P5–8 |
| 12 | `PATCH /annotation-packages/{package_id}/question-versions/{version_id}` | `patch_annotation_draft` | `PatchAnnotationDraftRequest` → `QuestionDraft` | `patch_draft`; APRepo + QRepo + TRepo | package → membership → Question → current version | required + expected question token; package token unchanged | stale/not assigned/completed/validation | autosave/replay/LF/KP mirror, P7 |
| 13 | `PATCH /annotation-packages/{package_id}/question-versions/{version_id}/source-topic` | `correct_source_topic` | request → result with nullable affected rows + refresh flag | `correct_source_topic`; APRepo + QRepo | replay gate; first execution package → old/new memberships → Questions/versions in global order | required + package and target tokens; replay returns current truth/null/refresh | stale/order conflict/not assigned/completed | first/replay/later-mutation/race, P10 |
| 14 | `POST /annotation-packages/{package_id}/question-versions/{version_id}/source-actions` | `apply_source_action` | `SourceActionRequest` → `QuestionDraft` | `apply_source_action`; APRepo + QRepo + SPRepo | package → selected package sources/PaperVersions/active selections in role order → membership → Question/version → provenance head | required + expected question token; package unchanged | nonempty fill/replace confirm/stale selection/invalid target | provenance/adoption/completion races, P8 |
| 15 | `POST /annotation-packages/{package_id}/question-versions/{version_id}/save-and-next` | `save_and_next` | `SaveAndNextRequest` → `SaveAndNextResult` with exactly one real next/ephemeral placeholder | `save_and_next`; APRepo + QRepo | package/current membership/question/version | required + package/question tokens; replay saves/materializes nothing | stale/not assigned/completed | double-click, tail zero-row/token/count, later N+1 replay, P9 |
| 16 | `GET /annotation-packages/{package_id}/annotation/resume` | `resume_annotation` | none → persisted-only `AnnotationResume` | `resume_annotation`; APRepo + provenance | none | none | forbidden/not found | last real edit before materialization/new real after, read-only, P11 |
| 17 | `GET /annotation-packages/{package_id}/question-versions/{version_id}/field-provenance/{field_name}/history` | `get_field_provenance_history` | cursor/limit → `FieldProvenanceHistory` | `get_provenance_history`; APRepo | none | none | scoped not found/validation | immutable/stale evidence, P8 |
| 18 | `PATCH /annotation-packages/{package_id}/workspace` | `patch_annotation_workspace` | `WorkspacePatchRequest` → `WorkspaceState` | `patch_workspace`; APRepo | package then workspace row | required + expected workspace token | stale workspace/forbidden/completed read-only/validation | actor isolation/replay/reopen, P11/13 |
| 19 | `POST /annotation-packages/{package_id}/annotation/complete` | `complete_annotation` | `CompleteAnnotationRequest` → `AnnotationResume` | `complete`; APRepo + PRepo/QRepo/SPRepo | full fixed completion order | required + package token; warning preview not persisted; confirmation new ID | incomplete/warnings/stale confirmation/stale package | hard/soft/race, P12 |
| 20 | `POST /annotation-packages/{package_id}/annotation/reopen` | `reopen_annotation` | `ReopenAnnotationRequest` → `AnnotationResume` | `reopen`; APRepo | package | required + package token | stale/not assigned/validation | replay/read-only recovery, P13 |

The existing generic `POST /paper-versions/{paper_version_id}/questions` is not a twenty-first G-09 route, but its service/API implementation is part of Phase 7 compatibility protection. Before insertion, `QuestionService.create_draft()` queries `annotation_package_sources` by `paper_version_id`; either role binding returns `403 FORBIDDEN` with no Question, QuestionVersion, or QuestionSlot. Standalone PaperVersions continue through the unchanged generic create behavior, while package-owned creation uses route 9. Route 1 success and route 4 initial processing remain separate commands, but formal client/application orchestration must call route 4 automatically after route 1 in the same import flow.

## 25. Transaction / Lock Matrix

| Operation | Transaction boundary and canonical lock order | Commit-visible mutation |
|---|---|---|
| import | external validate/stage/promote around one DB transaction; reserve key before domain insert | package, two papers/versions/sources, audit, idempotency atomically; storage compensated on failure |
| package processing | one authorization/read scope plus two independent existing two-transaction ProcessingService lifecycles | truthful child histories remain even if sibling fails |
| adopt | validate package role, then delegate existing PaperVersion → result → active selection lock order | active pointer plus existing/package audit |
| start-first | package → memberships in global order → new Question/final empty first version/slot/membership | only permitted empty Q1; not-started→in-progress; package token +1 once |
| materialize-after / draft-patch | idempotency gate → package → validate tokens/tail → memberships global order → new Question/final row-version-1 version/slot/membership | final authored fields and/or explicit KP/topic mutation, mirrors/orders, last-edited, count and package token +1 exactly once; all-or-nothing |
| materialize-after / source-action | idempotency gate → package → selected sources in role order → corresponding PaperVersions → active selections → memberships/order → new Question/version/slot/membership → provenance head/exact blocks | first field result and revision/links/head plus new real question, last-edited and package token +1 exactly once; all-or-nothing |
| draft patch | package → membership → Question → current QuestionVersion | fields and both KP mirrors, question token +1 exactly once, last-edited; source-topic/provenance and package token unchanged |
| source action | package → selected package sources in role order → corresponding PaperVersions in role order → active selections in role order → membership → Question → current QuestionVersion → provenance head | validate active result before question mutation; field, immutable revision/links, head, question token, last-edited |
| save-and-next | package → current membership → Question/version → persisted next lookup | current save plus existing real next or response-only placeholder; no next rows, question-creation audit, count, or package-token change |
| source-topic correction | replay gate first; first execution package → union old/new memberships in global order → Questions/current versions in same order | first execution updates metadata/local-order mirrors, affected question tokens, package token; replay mutates nothing and returns current target/package plus refresh required |
| workspace | package authorization/status → `(package,actor)` workspace | source view/workspace token only; completed rejects before mutation |
| completion | package → sources role order → PaperVersions → active pointers → memberships global order → Questions/current versions | completed state/token/audit/idempotency only after recomputation |
| reopen | package | in-progress state/token/audit/idempotency; content unchanged |

All G-09 domain transactions are service-owned and have no implicit repository commit. Package-level serialization is per package, never a global/table lock. Source-action tests must interleave the canonical lock chain against active-result adoption and completion, proving deterministic role order, no deadlock, and rejection rather than silent use of a stale selection.

## 26. Idempotency Matrix

| Command | Scope | Fingerprint inputs | Stable effect identity / replay rule |
|---|---|---|---|
| import | `annotation_package.import` | normalized metadata, assigned annotator, two role-bound safe file descriptors/hashes/sizes | same package ID; never create another package; current safe `PackageDetail` allowed |
| package process | no aggregate result key; child names are UUIDv5 | package request ID + fixed role | replay/attempt each existing ProcessingService child; response rebuilt |
| source process | existing `source_processing:trigger` | exact PaperVersion + canonical server parser profile | existing result semantics unchanged |
| adopt | existing `source_processing.activate` plus package-safe audit | exact result ID | existing activation replay; ownership checked before delegation/result exposure |
| start-first | `annotation.question.create:{package_id}` | package token and final knowledge-point/source-topic metadata | same Q1/version identity; never create another question; current safe representation allowed |
| materialize-after | `annotation_question.materialize_after:{package_id}:{after_question_id}` | after-question ID, both expected tokens, final knowledge-point/source-topic metadata, mutation discriminator, and all draft-patch or source-action semantic inputs | same N+1/version identity; never create a second question, apply the first mutation/provenance twice, or increment tokens twice; changed payload conflicts |
| draft patch | `annotation.question.patch:{version_id}` | expected question token and exact supplied fields/KP | no second mutation or row-version increment; current safe question representation allowed |
| source action | `annotation.question.source_action:{version_id}` | expected token, field, mode, confirmation, ordered result/block IDs | never fill/append/replace twice; resolve version/head identity without storing text; current safe question allowed |
| save-and-next | `annotation.question.save_next:{version_id}` | both tokens and optional current field patch | never repeat current save or materialize/increment package token; original real-next selection resolves that stable question, while an original shell replay returns current real N+1 if one exists or an equivalent ID-less placeholder |
| source-topic correction | `annotation.question.source_topic:{version_id}` | both tokens, topic order/label | first success returns actual changed rows/refresh false; replay never reorders and returns current target/package, null affected rows, refresh true |
| workspace | `annotation.workspace.patch:{package_id}:{actor_id}` | expected workspace token/source view | no second mutation/token increment; current safe workspace allowed; completed always rejects new mutation |
| complete | `annotation.complete:{package_id}` | package token, confirm flag, optional warning token and exact acknowledgements | successful transition occurs once; warning preview rejected/unrecorded; current safe package/resume allowed on replay |
| reopen | `annotation.reopen:{package_id}` | package token and bounded reason | transition occurs once and never forces historical state; current safe package/resume allowed |

Every G-09 command uses the same effect-idempotency gate: canonical hash → lock existing key; otherwise nested SAVEPOINT insert/flush → on unique race reload/lock winner → replay if identical or `IDEMPOTENCY_CONFLICT`; only the winner derives and mutates domain state. Replay resolves stable primary identities using the existing `idempotency_keys` resource fields and returns current safe authoritative representations with `Idempotent-Replay: true`; it does not reconstruct a historical HTTP body. Validation/stale/warning-preview failures are not recorded as successful results.

M-007 adds no receipt persistence. Idempotency records/fingerprints must contain no source text, answers, document bytes, full or partial HTTP response body, affected-question JSON, storage URI, private path, parser output, or traceback. Fingerprints contain only safe semantic inputs, opaque IDs, and concurrency tokens. The existing ProcessingService trigger/activation/result-replay/two-transaction semantics are exempt and unchanged.

## 27. Test Matrix

Nine explicit test groups are planned; “unit tests” is not an acceptance substitute.

| Group | Files | Required scenarios |
|---:|---|---|
| 1. Migration | `test_migrations.py`, `test_g09_annotation_schema.py` | clean and M-006 upgrades; exact columns/names; composite ownership; source-topic deferral; illegal duplicates; immutable UPDATE/DELETE; restrictive deletes; empty downgrade/re-upgrade and populated downgrade refusal |
| 2. Repository | service tests exercising APRepo | actor-scoped keyset lists; role lookup; membership/version binding; deterministic locks; cursor anchor validation; provenance append/head/history; no implicit commits |
| 3. Package/intake service | `test_annotation_package_service.py` | two-DOCX atomicity/compensation; same-package replay/conflict; mandatory same-flow initial-processing boundary; creator != assigned; assignment/management boundaries; canonical question-paper source; KP mirror; generic-create guard; persisted-only task/detail/open/list/count/resume/workspace |
| 4. Processing/readiness integration | `test_annotation_processing_integration.py` plus existing processing suite | package child IDs/order; success/partial/failed/stale/older-active combinations; explicit adoption; 200/202; no parser/ProcessingService changes |
| 5. Annotation/provenance service | package/provenance service tests | start-first; draft/metadata/source-action-first materialization; four fields; KP mirror; autosave; fill/append/replace; multi-block/role lock ordering; exact links; manual edit head preservation; history; save-next placeholder; persisted-only completion/resume; source-topic correction; reopen |
| 6. Router/API contract | two new annotation API files plus existing error/Shenlun tests | all 20 routes; create request union; placeholder/result DTO mutual exclusion and no IDs; status/replay headers; forbidden/not-found; DTO extra forbid; cursor; error envelope/tokens; generic package-bound create rejection/non-package compatibility; completed workspace protection; OpenAPI presence |
| 7. Concurrency/idempotency | `test_annotation_concurrency.py` | simultaneous first-key reservation; draft/metadata/source-action materialization rollback and two-tab one-N+1 race; materialize replay/conflict; autosave; append retry; source action vs adoption/completion; save-next zero-row double-click/later-N+1 replay; source-topic first success/replays; completion races; reopen |
| 8. Privacy/regression | `test_annotation_privacy.py` plus G-07/G-08/current full tests | no source/answer/document bytes/HTTP body/affected-row JSON/path/parser/traceback in logs/audit/errors/idempotency; no receipt schema; cross-package probing; raw source only authorized content response; all existing Paper/Question/Processing behavior green |
| 9. Manual E2E | section 32 | synthetic dual DOCX from import through reopen, including Q1 start, Q2 shell zero-row/list/count/resume, draft-first materialization, untouched Q3 completion, source-action-first, rollback, two-tab race, both replay forms, other Rev1 invariants and privacy |

## 28. Contract Acceptance Traceability

Every Contract §28 acceptance item maps to a concrete future test. Test names are canonical plan targets; implementation may only rename them while preserving one-to-one traceability in the PR description.

| Contract ID | Invariant | Test file → planned test/category | Phase |
|---:|---|---|---:|
| 1 | one replay-safe package/two finalized sources | `tests/api/test_annotation_packages_contract.py::test_import_replay_binds_exactly_two_finalized_roles` | 3 |
| 1a | creator/assigned differ and permissions split | `tests/services/test_annotation_package_service.py::test_creator_and_assigned_annotator_policies_are_distinct` | 3,7 |
| 2 | both effective sources determine readiness | `tests/services/test_annotation_processing_integration.py::test_readiness_composes_two_active_sources` | 4 |
| 3 | failed source blocks without older active | `tests/services/test_annotation_processing_integration.py::test_failed_role_blocks_open_without_usable_active` | 4–5 |
| 4 | partial explicit adoption; failed rejected | `tests/services/test_annotation_processing_integration.py::test_partial_requires_exact_adoption_and_failed_cannot_activate` | 4 |
| 5 | immutable-order source content | `tests/api/test_annotation_packages_contract.py::test_source_content_orders_active_blocks` | 5 |
| 5a | full triple cursor ties | `tests/api/test_annotation_packages_contract.py::test_source_cursor_paginates_same_order_gap_and_block_without_loss` | 5 |
| 6 | safe visible gaps | `tests/api/test_annotation_privacy.py::test_gap_marker_is_safe_and_contains_no_diagnostic_detail` | 5,14 |
| 7 | open read-only; first create transition | `tests/api/test_annotation_workbench_contract.py::test_open_creates_nothing_and_first_question_enters_in_progress` | 5–6 |
| 8 | four independent LF-normalized fields | `tests/api/test_annotation_workbench_contract.py::test_four_fields_round_trip_independently_with_lf_normalization` | 7 |
| 9 | exact ordered single/multi-block provenance | `tests/services/test_annotation_provenance_service.py::test_source_action_persists_exact_ordered_result_block_links` | 8 |
| 10 | fill reject; append once | `tests/services/test_annotation_provenance_service.py::test_fill_protects_nonempty_and_append_is_retry_safe` | 8 |
| 11 | confirmed replace/history | `tests/services/test_annotation_provenance_service.py::test_replace_requires_confirmation_and_preserves_history` | 8 |
| 12 | manual edit keeps head/block immutable | `tests/services/test_annotation_provenance_service.py::test_manual_edit_keeps_head_and_never_changes_block` | 7–8 |
| 13 | all stale tokens/no package churn on save | `tests/services/test_annotation_concurrency.py::test_stale_tokens_are_atomic_and_ordinary_save_keeps_package_token` | 7,10–11 |
| 14 | autosave retry/conflict | `tests/services/test_annotation_concurrency.py::test_autosave_same_id_replays_and_changed_payload_conflicts` | 7 |
| 15 | save-before-next/idempotent | `tests/services/test_annotation_concurrency.py::test_save_and_next_is_atomic_under_retry_and_double_click` | 9 |
| 15a | no next KP input; real next or inherited placeholder defaults | `tests/services/test_annotation_package_service.py::test_save_and_next_returns_real_next_or_inherited_placeholder_without_next_kp_input` | 9 |
| 15b | tail save-next creates no row/count/token | `tests/services/test_annotation_package_service.py::test_tail_save_and_next_returns_placeholder_without_persistence_or_package_churn` | 9 |
| 15c | untouched exit resumes N; materialized resumes N+1 | `tests/api/test_annotation_workbench_contract.py::test_placeholder_exit_resumes_last_real_then_materialization_resumes_new_question` | 9,11 |
| 15d | list/count/completion ignore untouched placeholder | `tests/services/test_annotation_package_service.py::test_placeholder_is_absent_from_list_count_and_completion_validation` | 9,11–12 |
| 15e | authored/metadata first mutation atomically materializes | `tests/services/test_annotation_package_service.py::test_draft_or_metadata_first_mutation_materializes_one_final_state_question` | 6–7 |
| 15f | source-action first mutation creates exact provenance atomically | `tests/services/test_annotation_provenance_service.py::test_source_action_first_materialization_is_atomic_with_exact_provenance` | 6,8 |
| 15g | failed first mutation leaves zero rows/effects | `tests/services/test_annotation_concurrency.py::test_failed_materialization_rolls_back_all_rows_pointer_count_and_tokens` | 6–8 |
| 15h | two-tab shell creates one N+1 and no N+2 | `tests/services/test_annotation_concurrency.py::test_two_tab_materialization_creates_exactly_one_logical_next_question` | 6–8 |
| 15i | save-next replay never materializes/token-churns | `tests/services/test_annotation_concurrency.py::test_tail_save_next_replay_returns_current_real_or_ephemeral_target_without_materialization` | 9 |
| 16 | concurrent materialization has unique global/local order | `tests/services/test_annotation_concurrency.py::test_concurrent_materialization_creates_one_unique_tail_order` | 6–8 |
| 16a | first correction leaves KP unchanged and returns committed rows/tokens with refresh false | `tests/services/test_annotation_concurrency.py::test_source_topic_first_success_returns_exact_changed_rows` | 10 |
| 16b | immediate replay has no reorder/token increment, returns replay header/null/refresh, and changed payload conflicts | `tests/services/test_annotation_concurrency.py::test_source_topic_immediate_replay_is_effect_idempotent` | 10 |
| 16c | replay after later legal mutation returns replay header/current truth/null/refresh | `tests/services/test_annotation_concurrency.py::test_source_topic_replay_after_later_mutation_returns_current_truth` | 10 |
| 16d | existing idempotency keys; no response receipt/snapshot | `tests/migrations/test_g09_annotation_schema.py::test_m007_adds_no_idempotency_receipt_storage` plus `tests/services/test_annotation_concurrency.py::test_source_topic_replay_needs_no_response_receipt` | 1,10 |
| 17 | reads do not update last-edited | `tests/services/test_annotation_package_service.py::test_all_reads_and_source_view_leave_last_edited_unchanged` | 5,11 |
| 18 | resume exact last edit/provenance/view/null start | `tests/api/test_annotation_workbench_contract.py::test_resume_restores_server_truth_and_not_started_is_null` | 11 |
| 19 | aggregate four-field hard errors | `tests/services/test_annotation_package_service.py::test_completion_reports_all_missing_fields_by_global_order` | 12 |
| 20 | partial/gap/manual-only warnings | `tests/services/test_annotation_package_service.py::test_completion_builds_canonical_safe_warning_set` | 12 |
| 21 | locked confirmation exactly once | `tests/services/test_annotation_concurrency.py::test_confirmed_completion_revalidates_locked_warning_set_once` | 12 |
| 22 | every package write blocked completed | `tests/api/test_annotation_workbench_contract.py::test_completed_package_blocks_every_annotation_and_generic_write` | 13 |
| 23 | explicit idempotent reopen | `tests/api/test_annotation_workbench_contract.py::test_reopen_is_idempotent_audited_and_content_neutral` | 13 |
| 23a | scoped task list/no automatic next | `tests/api/test_annotation_packages_contract.py::test_completion_returns_task_list_target_without_auto_open` | 5,12 |
| 24 | no submit/review/publish | `tests/api/test_annotation_workbench_contract.py::test_package_questions_reject_submit_and_correction_and_create_no_review_state` | 7,13 |
| 25 | no private content in observability/fixtures | `tests/api/test_annotation_privacy.py::test_logs_audit_errors_and_idempotency_exclude_prohibited_data` | 3–14 |
| 25a | idempotency storage excludes private content/response snapshots | `tests/api/test_annotation_privacy.py::test_idempotency_storage_excludes_content_bodies_affected_rows_and_private_metadata` | 2–14 |
| 26 | additive PG16 constraints/history/delete | `tests/migrations/test_g09_annotation_schema.py` full group | 1 |
| 27 | Processing Service remains exact | existing `tests/services/test_source_processing_service.py`, parser and M-006 schema suites | 0,4,final |

```text
CONTRACT_ACCEPTANCE_IDENTIFIER_COUNT = 44
ALL_44_ACCEPTANCE_IDENTIFIERS_MAPPED = YES
```

Additional invariant traceability:

| Material Contract invariant | Phase | Backend file(s) | Verification |
|---|---:|---|---|
| dual immutable sources | 1,3 | M-007, package models/service | IDs 1,26 and storage compensation tests |
| assigned annotator | 2,3,7 | policies/service/generic question service | ID 1a and all wrong-actor route tests |
| mandatory initial processing in same import flow | 3–4 | package import/process routers plus formal client/application orchestration | import orchestration service/API/manual test; still two commands and transactions |
| start-first/lazy question creation / canonical question-paper source | 6–8 | package service/repository/schemas | IDs 7,15e–15h,16 plus explanation-negative FK/value assertions |
| package question knowledge-point mirror | 7 | package/question repositories and package service | A→B mirror/list/filter/token/source-topic invariant test |
| block generic create for either package source role | 7 | question repository/service/router | service/API bypass tests plus standalone and package-route regressions |
| append default / explicit replace | 8 | package service/schemas | IDs 10–11 |
| source-action canonical lock order | 8 | package/source/question/provenance repositories and service | existing and source-action-first action-vs-adoption/completion no-deadlock and stale-selection tests |
| exact provenance / human edit keeps provenance | 1,8 | M-007/repository/service | IDs 9,11–12,26 |
| placeholder/list/count/resume/completion boundary | 9,11–12 | package service/schemas | IDs 15a–15d,15i,17–19 |
| last-edited / lazy materialization / knowledge inheritance | 6–9,11 | package service | IDs 15,15a,15c,15e–15i,17–18 |
| source-topic-local ordering | 1,6,10 | M-007/repository/service | IDs 15e–15h,16–16d,26 |
| four-field completion / warnings / read-only / reopen | 12–13 | package service/policies/question guard | IDs 19–23 |
| completed workspace mutation protection | 11,13 | package service/policies | completed GET/PATCH/reopen/PATCH sequence under ID 22 |
| effect-idempotency and truthful topic replay | 2–14 | idempotency repository plus command services | IDs 14–16d,21,23,25a |
| no review and privacy | 7,13–14 | question service, error/DTO boundary | IDs 24–25a |

## 29. Regression Strategy

Protected baseline capabilities are: G-07 Paper/PaperVersion intake and private storage; standalone non-package Question creation/patch/submission/correction/versioning; QuestionSlot ordering; five Shenlun knowledge points and subject/type validation; generic API compatibility except the required package-bound PaperVersion create guard; the entire M-006 Processing Service, activation, idempotency, immutable history, parser, stale classification, and read side; PostgreSQL test guards; and all G-07/G-08 behaviors. Regression evidence must additionally prove both knowledge-point mirrors remain equal, source-action/adoption/completion use one lock order, save-and-next persists no untouched tail, lazy materialization is atomic and replay-safe, completion ignores client-only shells, and M-007 remains exactly seven tables with no placeholder or response-receipt storage.

Regression cadence:

1. Phase 0 records full green baseline before any backend change.
2. Every commit runs its smallest focused tests plus Ruff/MyPy.
3. Checkpoint A runs all migration and existing G-04/G-07 schema tests.
4. Checkpoint B runs all paper-storage/intake and Processing Service/parser/schema tests.
5. Checkpoint C runs all existing Shenlun service/API tests plus annotation creation/save/provenance/concurrency.
6. Checkpoint D runs all route/error/privacy/completion/reopen tests plus the full existing question suite.
7. Checkpoint E runs clean upgrade, downgrade/re-upgrade on disposable DB, focused G-09 suite, every G-07/G-08 suite, full `uv run pytest`, static checks, OpenAPI regeneration, and manual E2E.

Any protected regression is a checkpoint blocker; it is not waived as “unrelated.”

## 30. Canonical Commit Sequence

| Commit | Scope | Reviewable atomic outcome |
|---:|---|---|
| 1 | `feat(schema): add g09 annotation package persistence` | M-007, ORM parity, migration tests only |
| 2 | `feat(annotation): add package models policies and repositories` | persistence primitives and race-safe idempotency helper |
| 3 | `feat(annotation): add dual source package intake` | atomic import and intake tests |
| 4 | `feat(annotation): integrate package processing readiness` | unchanged ProcessingService wrapper/adoption/readiness |
| 5 | `feat(annotation): add scoped package and source reads` | task/detail/content/open and cursor tests |
| 6 | `feat(annotation): add start-first and lazy question materialization` | dynamic Q1, create request union, draft/metadata-first atomic materialization, ordering, autosave/KP mirror/last-edited and generic-create guard |
| 7 | `feat(annotation): add exact source field provenance` | canonical source lock order, fill/append/replace/history, and source-action-first atomic materialization |
| 8 | `feat(annotation): add ephemeral save-and-next navigation` | real-next selection or ID-less placeholder, zero-row tail behavior, materialization race/replay closure |
| 9 | `feat(annotation): add source topic correction` | aggregate reorder, truthful effect-idempotent replay, tokens, deferred uniqueness |
| 10 | `feat(annotation): add resume workspace completion and reopen` | remaining state machine and unconditional completed workspace/write protection |
| 11 | `feat(api): finalize g09 errors schemas routes and openapi` | all wire/error/privacy boundaries |
| 12 | `test(annotation): harden g09 acceptance and regressions` | traceability closure, concurrency/privacy/manual support |

No commit is an 8,000-line catch-all, and no atomic transaction is split across commits in a way that leaves a route enabled without its invariants.

## 31. Team B Review Checkpoints

| Checkpoint | Expected commits | Required evidence | Team B focus | Stop condition |
|---|---|---|---|---|
| A — Migration/schema | 1–2 | PostgreSQL 16 migration/repository tests; named-object dump; downgrade proof | ownership FKs, deferral, triggers, no cascade, repository/service boundary | any schema invariant ambiguous or destructive |
| B — Package + Processing | 3–5 | intake/storage, mandatory same-flow initial processing harness, complete existing Processing suite, readiness/adoption/source pagination tests | dual source atomicity, separate commands with mandatory orchestration, no Processing/parser change, partial/failed truth, privacy | processing invariant/regression or private-data exposure |
| C — Annotation core/provenance | 6–9 | existing Shenlun regressions; KP mirror/generic-create guard; tail save-next zero-row/count/token; draft-first and source-action-first materialization; failure rollback; two-tab one-N+1 race; save-next/materialize replay; source-action lock races; IDs 7–18 including all 15a–15i and 16–16d | canonical source, exact provenance, ephemeral placeholder boundary, atomic materialization, effect idempotency, one lock order, generic bypass closure, truthful replay | any persisted untouched placeholder, duplicate N+1/N+2 from one shell, completion blocked by shell, stale overwrite/source acceptance, mirror divergence, or unverifiable provenance |
| D — Completion/reopen/security | 10–11 | completion races, every completed write path including workspace, errors/privacy/OpenAPI | hard/soft validation, confirmation token, unconditional completed read-only, no review, actor scope | any side door, TOCTOU, or error leakage |
| E — Full E2E candidate | 12 plus all prior | full suite/static/migration/OpenAPI/manual report, 44-ID traceability proof, no-placeholder/no-receipt schema proof, and clean diff | acceptance traceability, protected regressions, operational reproducibility | any unmapped acceptance item, failing regression, or scope drift |

Passing a checkpoint authorizes review of the next work package only when the user has separately authorized implementation. This plan itself grants no such authority.

## 32. Manual Acceptance Plan

Use only synthetic, generated pure-text DOCX files and opaque synthetic answers:

1. Perform one import user action with different creator/assigned IDs; confirm one package, two Papers/versions, and two roles are committed, then confirm the formal client/application flow automatically issues the initial package-processing command without a second click. Replay import and confirm the same package identity/current safe detail and no duplicate package/source/version.
2. Confirm import and initial processing were separate API transactions; show failed blocks open, explicitly reprocess as a later new user action, then show partial needs explicit adoption and remains visible as a safe gap.
3. Inspect task/detail; open a ready package and prove status/questions unchanged.
4. Before package creation, prove generic create still works for a standalone PaperVersion; after import, try generic create against both package `question_paper` and `explanation` PaperVersions and prove `403 FORBIDDEN` with no Question/Version/Slot; then use the package route to create question 1 and prove atomic `not_started -> in_progress`, canonical question-paper IDs, and no preallocated question 2.
5. Page question-paper/explanation/compare source content across a same-order gap/block boundary without loss/duplicate/page fabrication.
6. Fill each of four fields from one/multiple exact blocks; inspect current provenance; manually edit and prove head remains.
7. Reject fill over nonempty; append once under timeout replay; require confirmation for replace; inspect immutable prior revisions; race a source action against active-result adoption and completion and prove deterministic lock order, no deadlock, and no stale source acceptance.
8. Run two-tab autosave stale case; change knowledge point A→B and verify QuestionDraft, membership, list and filter all report B while source-topic/provenance and package token stay unchanged and the question token increments once; verify no merge/overwrite and last-edited updates only after success.
9. Double-click save-and-next from real Q1 tail; prove Q1 saves and the response returns an ID-less Q2 `NextQuestionPlaceholder` with inherited knowledge-point/source-topic defaults. GET list/count and inspect DB-safe evidence: Q2 does not exist, count remains 1, no Question/Version/Slot/membership/provenance or question-creation audit exists, and package token is unchanged merely for the shell.
10. Exit without touching Q2 and resume; prove Q1 is restored. Enter the Q2 shell again, perform its first authored-field autosave through `materialize_after/draft_patch`, and prove one Q2 is created directly in final initial state with `row_version=1`, count becomes 2, package token increments exactly once, and last-edited becomes Q2.
11. Change Q2 knowledge point/source-topic defaults before a separate metadata-first materialization run; prove final explicit metadata is used, both knowledge-point mirrors match, `source_question_order` is server-derived, and the client cannot submit it. Fill Q2's remaining required fields.
12. Save-and-next from Q2 into an untouched Q3 shell, leave Q3 untouched, and confirm list/count/resume still expose only Q1/Q2 and resume Q2. With real Q1/Q2 valid, exercise soft-warning confirmation and complete; prove Q3 generates no missing-field error/warning and does not block completion or task-list return.
13. In an isolated rerun, make a source action the Q2 shell's first mutation. Prove selected package sources/PaperVersions/active selections lock before question/version, exactly one Q2 and exact ordered provenance commit atomically, and no empty intermediate question exists.
14. Force validation, stale package/tail token, stale source selection, ownership, DB, and commit failures during first mutation; after each, prove zero new question/version/slot/membership/provenance rows, unchanged count/pointer/package token, and the client remains on the ephemeral shell.
15. In two tabs holding the same Q2 shell, issue different first mutations. Prove package lock + both tokens + tail recheck + uniqueness yield exactly one real Q2, no Q3, one package-token increment, and `STALE_PACKAGE`/`STALE_DRAFT` for the loser.
16. Retry the winning materialization with the same request ID/fingerprint and prove no second question/action/provenance/token change; changed payload conflicts. Replay the earlier tail save-and-next before and after Q2 exists and prove it never repeats Q1 save or materializes: it returns an equivalent shell before, current real Q2 after.
17. Correct a materialized question's source topic; prove first success leaves knowledge point unchanged, makes old/new groups contiguous by global order, returns committed rows/tokens and `ordering_refresh_required=false`; after another legal mutation, replay the original correction and prove no reorder/version increment, current truth, null affected rows, refresh true, list recovery, and changed-payload conflict.
18. Change source view and browse without editing; exit/resume and prove last real edited question, fields, provenance, view, and current tokens restore while no placeholder is ever persisted or resumed.
19. Prove every annotation/generic write including workspace PATCH is blocked while completed; explicitly reopen, then prove workspace PATCH and content edit succeed.
20. Inspect safe audit/log/error/idempotency records and schema; confirm no source/answer/document bytes/HTTP body/affected-row JSON/private path/parser output/traceback, placeholder schema, or replay-receipt storage, and prove no submit/review/approval/publication record exists.

## 33. Final Verification Commands

Future implementation must run these from the clean backend feature worktree in PowerShell. The destructive migration tests are permitted only after the two safety assertions pass.

```powershell
git fetch origin --prune
git rev-parse origin/main
git status --short

docker compose --profile test up -d postgres-test
docker compose --profile test exec postgres-test pg_isready -U gongkao -d gongkao_api_test
docker compose --profile test exec postgres-test psql -U gongkao -d gongkao_api_test -tAc "SHOW server_version_num"

$env:GONGKAO_APP_ENV = "test"
$env:GONGKAO_DATABASE_URL = "postgresql+psycopg://gongkao:gongkao_test_password@localhost:5433/gongkao_api_test"
$env:PYTHONPATH = (Get-Location).Path

uv sync --all-groups
uv run python -c "from gongkao_api.core.config import Settings; Settings().assert_disposable_test_database(); print('TEST DATABASE SAFETY CHECK: PASS')"

uv run alembic upgrade head
uv run pytest tests/migrations/test_migrations.py tests/migrations/test_source_processing_schema.py tests/migrations/test_g09_annotation_schema.py
uv run alembic downgrade 0006_m006
uv run alembic upgrade head

uv run pytest tests/services/test_annotation_package_service.py tests/services/test_annotation_processing_integration.py tests/services/test_annotation_provenance_service.py tests/services/test_annotation_concurrency.py
uv run pytest tests/api/test_annotation_packages_contract.py tests/api/test_annotation_workbench_contract.py tests/api/test_annotation_privacy.py tests/api/test_error_contract.py
uv run pytest tests/api/test_paper_docx_upload_contract.py tests/api/test_paper_storage.py tests/api/test_shenlun_contract.py tests/services/test_shenlun_services.py
uv run pytest tests/services/test_source_processing_parser.py tests/services/test_source_processing_service.py tests/migrations/test_source_processing_schema.py

uv run ruff check .
uv run mypy src
uv run pytest
uv run python scripts/export_openapi.py
git diff --check
git status --short
```

Before the downgrade command, the M-007-specific tables must be empty; a populated-history refusal is separately tested and is the correct safe behavior. Final evidence records only SHAs, command outcomes, test counts, and safe codes—never source text, answers, paths, hashes, credentials, or parser output.

## 34. Out of Scope

Frontend/React code; reviewer workflow; submit/approve/reject/publish/release; search-bank release; reassignment/claim/queue/collaboration; bulk import; OCR/PDF/scanned input; mixed content, images, formulas, screenshots, tables or options; AI splitting/classification/topic inference; question deletion/reorder UI; automatic question count; formal RBAC/authentication; worker/queue/background processing; parser changes; ProcessingService lifecycle changes; response-receipt/snapshot persistence; source-version replacement; modification of M-001–M-006; migration/code/tests during this planning task; and merge.

## 35. Stop Conditions

Return `PLAN_STATUS = BLOCKED_CONTRACT_REVIEW_REQUIRED` or stop future implementation immediately if:

- exact Contract or backend baseline drifts before the authorized implementation branch is created;
- the Contract cannot be implemented on the baseline without product-visible change;
- existing schema requires destructive history rewrite or weakening M-001–M-006;
- G-08 immutable history, active-selection, partial/failed, or two-transaction processing semantics must weaken;
- exact `ProcessingResult + DocumentBlock` provenance cannot remain restrictive and queryable;
- the canonical Question source would need to become explanation or package rather than question-paper PaperVersion;
- save-and-next, knowledge inheritance, source-topic correction, completion, or reopen semantics must change;
- save-and-next would persist an untouched tail placeholder, create any next-question row, or increment package count/token merely for entering the shell;
- lazy materialization cannot create exactly one N+1 and apply its first meaningful draft/metadata/source mutation in one transaction, or failure cannot roll back every row/pointer/token effect;
- the same logical shell can produce N+1 and N+2 under concurrency, or save-next/materialization replay repeats an effect;
- list/count/resume/completion cannot exclude the ephemeral placeholder, or completion is blocked by an untouched shell;
- package question knowledge-point mirrors cannot remain transactionally equal without package-token churn or source-topic/provenance mutation;
- generic creation cannot reject a PaperVersion already bound to either package source role before creating Question/Version/Slot rows;
- source action would require acquiring question/version before selected package-source/PaperVersion/active-selection locks, or cannot reject a concurrently stale selection without deadlock;
- formal RBAC or a background worker becomes necessary;
- idempotent replay would require rerunning a won mutation, guessing historical affected rows, or adding response/affected-row receipt storage;
- private source text/answers/document bytes/HTTP bodies/affected-row JSON/paths/hashes/parser data/tracebacks would enter logs, audit, errors, idempotency, fixtures, Git, screenshots, or issue comments;
- any protected baseline regression cannot be resolved within this Contract;
- a worktree contains unowned/out-of-scope changes or test DB safety cannot be proven.

No implementer may “fix” a stop condition by editing the passed Contract on the implementation branch.

## 36. Open Technical Decisions

All internal choices required for execution are fixed here: module name; single seven-table M-007 revision with no placeholder schema; exact table/constraint decomposition; policy mapping for the existing actor model; cursor payload; repository/service boundary; one 20-route API whose question-create route has `start_first|materialize_after`; exact placeholder/result DTOs; draft/metadata/source-action-first atomic materialization; effect-idempotency without response receipts; save-next versus materialize replay; truthful source-topic replay; knowledge-point mirror transaction; canonical source-action lock order; generic package-source create guard; mandatory same-flow initial-processing orchestration boundary; unconditional completed workspace protection; files, tests, commits, and checkpoints.

```text
OPEN_TECHNICAL_DECISION_COUNT = 0
```

## 37. Product Decisions Required and Plan Self-review

No new product decision is required. The plan preserves all frozen behavior and assigns every material requirement to a phase, concrete file, and verification.

```text
CONTRACT_REV4_SHA_VERIFIED = YES
BACKEND_BASELINE_SHA_VERIFIED = YES

PLAN_BRANCH_DESCENDS_FROM_CONTRACT_REV4 = YES

SAVE_AND_NEXT_CREATES_NEXT_QUESTION = NO
TAIL_SAVE_NEXT_RETURNS_EPHEMERAL_PLACEHOLDER = YES
PLACEHOLDER_HAS_PERSISTENT_ID = NO
PLACEHOLDER_INCREMENTS_PACKAGE_TOKEN = NO
PLACEHOLDER_INCREMENTS_CREATED_COUNT = NO

START_FIRST_EMPTY_Q1_PRESERVED = YES

MATERIALIZE_AFTER_REQUEST_UNION_PLANNED = YES
DRAFT_FIRST_MUTATION_ATOMIC_MATERIALIZATION_PLANNED = YES
METADATA_FIRST_MUTATION_ATOMIC_MATERIALIZATION_PLANNED = YES
SOURCE_ACTION_FIRST_MUTATION_ATOMIC_MATERIALIZATION_PLANNED = YES

MATERIALIZATION_FAILURE_ROLLBACK_PLANNED = YES
MATERIALIZATION_CONCURRENCY_PLANNED = YES
MATERIALIZATION_REPLAY_PLANNED = YES

PLACEHOLDER_EXCLUDED_FROM_LIST_COUNT_RESUME_COMPLETION = YES

P1_01_KNOWLEDGE_POINT_MIRROR_RESOLVED = YES
P1_02_SOURCE_ACTION_LOCK_ORDER_RESOLVED = YES
P1_03_GENERIC_CREATE_BYPASS_RESOLVED = YES

P2_01_INITIAL_PROCESSING_MANDATORY_FLOW_RESOLVED = YES
P2_02_COMPLETED_WORKSPACE_READ_ONLY_RESOLVED = YES

REV3_EFFECT_IDEMPOTENCY_PRESERVED = YES
REV3_SOURCE_TOPIC_REPLAY_PRESERVED = YES
REV3_NO_RESPONSE_RECEIPT_SCHEMA = YES

G09_NEW_TABLE_COUNT = 7
PLACEHOLDER_PERSISTENCE_SCHEMA_ADDED = NO

CONTRACT_ACCEPTANCE_IDENTIFIER_COUNT = 44
ALL_44_ACCEPTANCE_IDENTIFIERS_MAPPED = YES

ALL_CONTRACT_ROUTES_PLANNED = YES
ALL_SCHEMA_DELTA_PLANNED = YES
ALL_CONCURRENCY_RULES_MAPPED = YES
ALL_IDEMPOTENCY_RULES_MAPPED = YES
ALL_PRIVACY_RULES_MAPPED = YES

PROCESSING_SERVICE_MODIFICATION_REQUIRED = NO
PARSER_MODIFICATION_REQUIRED = NO
PRODUCT_BEHAVIOR_CHANGED = NO

PHASE_COUNT = 15
PLANNED_BACKEND_FILE_COUNT = 29
PLANNED_MIGRATION_COUNT = 1
PLANNED_API_ROUTE_COUNT = 20
PLANNED_TEST_GROUP_COUNT = 9
REVIEW_CHECKPOINT_COUNT = 5

PRODUCT_DECISION_REQUIRED_COUNT = 0
OPEN_TECHNICAL_DECISION_COUNT = 0

PLAN_STATUS = CORRECTIVE REVISION 2 — READY FOR TEAM B FINAL REVIEW
IMPLEMENTATION_PLAN_AUTHORIZED = YES
IMPLEMENTATION_AUTHORIZED = NO
NEXT_STAGE = TEAM B IMPLEMENTATION PLAN REV2 FINAL REVIEW
```
