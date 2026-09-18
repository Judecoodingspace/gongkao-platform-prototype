# WDV1 G-09 Pure-Text Question Annotation E2E Implementation Contract

```text
CONTRACT_STATUS = CORRECTIVE REVISION 3 — PENDING TEAM B NARROW REVIEW
CONTRACT_REVISION = 3
IMPLEMENTATION_AUTHORIZED = NO
IMPLEMENTATION_PLAN_AUTHORIZED = NO
DATABASE_MIGRATION_AUTHORIZED = NO
API_CODE_AUTHORIZED = NO
FRONTEND_CODE_AUTHORIZED = NO
MERGE_TO_MAIN_AUTHORIZED = NO
```

## 1. Status and Authority

This document is the design contract for the next implementation slice. It is not an implementation plan and does not authorize a migration, code, tests, frontend work, or merge. Team B must review this contract independently; afterward the user must explicitly authorize any plan and later implementation.

Authority order for this slice is:

1. `WDV1_G09_PRODUCT_FROZEN_DECISIONS.md`, FD-01 through FD-29 and PD-30/PD-31;
2. the continuing G-07/G-08 privacy, provenance, processing-history, and activation invariants;
3. the repository constitution and current backend contracts where not superseded above;
4. this document's technical choices.

If implementation discovers a conflict that changes visible workflow, permissions, overwrite/delete behavior, or the meaning of completion/reopen, work must stop under section 31. An implementer may not silently reinterpret an FD.

## 2. Baseline SHAs

Both remote baselines were fetched and verified before this contract was written.

| Repository | Remote | Required and observed `origin/main` | Worktree at inspection |
|---|---|---|---|
| Governance | `Judecoodingspace/gongkao-platform-prototype` | `13177e3f4a625e4b4ef54fa39fcb075f4fd36ec1` | clean |
| Backend | `Judecoodingspace/gongkao-question-bank-api` | `c627650b63b4eb0f1531d07771ea06b5cc851d5e` | clean, detached at the exact SHA |

The backend baseline is read-only for this contract. The governance contract branch starts exactly at the governance SHA above.

## 3. Product Frozen Decisions Reference

The normative product record is `WDV1_G09_PRODUCT_FROZEN_DECISIONS.md` in this directory. It records `PRODUCT_DECISIONS = FROZEN` and `IMPLEMENTATION_AUTHORIZED = NO`. This contract preserves all FD-01 through FD-29 and PD-30/PD-31 semantics and does not repeat them as a substitute authority.

## 4. Authority / Supersession Matrix

| Earlier source | Earlier behavior/text | G-09 authority and treatment |
|---|---|---|
| clickable prototype | DOCX, derived HTML, and optional JSON are selected inside the workbench | Superseded. Package ingestion happens before the workbench; source content is loaded from backend APIs. The layout remains a UI baseline only. |
| clickable prototype | fixed simulated question positions exist before a draft | Superseded. Only persisted, human-created questions appear. Merely browsing an absent position cannot create it. |
| clickable prototype | browser-local save and submit-review simulation | Superseded. Saves are server persisted with optimistic concurrency. Submit/review is deferred. |
| old acceptance checklist | G-09 includes submit to review | Superseded by FD-28. G-09 ends at `completed` annotation and creates no review, approval, or publication state. |
| earlier annotation wording | `replace` is primary and append is only a correction aid | Superseded by FD-16: append is the default for non-empty content; replace is an explicit, confirmed, destructive secondary action. |
| earlier source-structuring wording | source-structuring failure may continue into manual annotation | Superseded by FD-05: a failed source blocks workbench entry; V1 offers explicit reprocessing, not a failed-source manual-entry bypass. |
| G-08 | processing requires explicit actor intent; results are immutable | Preserved. Package orchestration invokes the existing synchronous service explicitly and does not add a worker, implicit retry, or result mutation. |
| G-08 | initial `success` may become active; `partial` is inactive until explicit activation; `failed` is never active | Preserved. A partial source becomes usable only through the explicit, audited adopt command. Package readiness never auto-activates it. |
| G-08 | active selection is independent history | Preserved. Annotation provenance points to the exact result/block used; a later active change marks old provenance as stale, not invalid and not rewritten. |
| historical `AGENTS.md` stage text | G-08 planning-only / G-08 implementation not yet authorized | Historical stage statement at these exact baselines. It does not describe the merged Processing Service state. Its permanent safety, privacy, architecture, and test rules remain binding. |
| existing generic question API | submit and correction endpoints exist from an earlier backend slice | They remain baseline capabilities for non-package data, but G-09 UI and G-09 commands do not call them. Package-owned G-09 questions must reject submit/review operations in this slice. |
| prototype | page-like preview labels can imply reliable pages | Only persisted reliable locators may be shown. The current parser provides ordered paragraphs, not trustworthy page geometry; the production DTO therefore exposes document order, never a fabricated page number. |

## 5. Goal

Provide a contract-complete, auditable path for one Shenlun source package containing a question-paper DOCX and an explanation DOCX: immutable intake, explicit synchronous processing, readiness, source reading, dynamic pure-text question creation, human source-to-field actions, editing and save, resume, completion, and explicit reopen.

Completion means only “annotation for this package is marked complete.” It is not review, approval, publication, or release.

## 6. Non-goals

The slice excludes reviewer workflow; submit, approve, reject, publication, and searchable-bank release; bulk package import; OCR; PDF or scanned upload; production mixed content; images, equations, screenshots, tables, or A-D options; AI splitting, semantic classification, or automatic question counting; formal RBAC; workers, queues, schedulers, background processing, hidden retries; parser changes; React/component implementation; and migration or implementation work during this contract task.

## 7. Existing Backend Inventory

The contract is based on the following observed backend, not an assumed greenfield design.

| Existing capability | Baseline artifact and contract implication |
|---|---|
| immutable source identity | `papers` and append-only `paper_versions`; finalized DOCX bytes use private storage and SHA-256; `ON DELETE RESTRICT` |
| source intake | `POST /papers` and `POST /papers/{paper_id}/versions`; DOCX validation, staging/promotion compensation, actor audit, idempotency |
| controlled Shenlun taxonomy | five active `knowledge_points` seeded by M-002; `shenlun`/`subjective` enforcement |
| question identity/navigation | `questions`, dynamically inserted `question_slots`, and `question_versions`; no implementation requires pre-creating all slots |
| exact V1 text fields | `stem_text`, `requirement_text`, `question_text`, `reference_answer_text`; newline normalization and length limits already exist |
| draft concurrency | `question_versions.row_version`; stale mutation returns `STALE_DRAFT`; submitted/approved/rejected versions are immutable |
| source materials | versioned `source_materials`, `source_material_versions`, and question-version links; these are authored source-material records, not G-08 block-level provenance |
| idempotency | `idempotency_keys`, unique `(actor_id, operation_scope, client_request_id)`, canonical SHA-256 command fingerprint |
| audit | append-only `audit_events`; details can contain IDs/codes/counts but must not contain paper text, answers, or private paths |
| processing history | M-006 `source_processing_results`, `document_blocks`, `source_processing_gaps`, `paper_version_active_processings`; all provenance FKs use `RESTRICT` |
| processing lifecycle | synchronous two-transaction `ProcessingService`; terminal `success/partial/failed`; only initial success auto-activates; explicit activation accepts success or partial; failed cannot activate |
| processing read side | service methods return result summary, ordered blocks, ordered safe gaps, result list, and active result; no source-processing FastAPI router/schema exists at this baseline |
| actor boundary | temporary `X-Actor-Id` UUID context with role `annotator`; it is not production authentication or formal RBAC |
| database/testing | PostgreSQL 16, Alembic M-001 through M-006, test-environment/database-name safety guards, Ruff/Mypy/Pytest requirements |

`DocumentBlock.text_original` is source content and may be returned only through an authorized source-read response. It must not be copied into logs, audit details, exception messages, fixtures, or idempotency records.

## 8. Domain Aggregate Design

The canonical G-09 aggregate is named `AnnotationPackage`. The product term “资料包” does not replace `Paper`/`PaperVersion`: a package coordinates two independently immutable source-document identities and the annotation workflow over them.

An `AnnotationPackage` owns:

- package metadata: title, year, region/province, `subject = shenlun`, and exam type;
- exactly two immutable role associations: `question_paper` and `explanation`;
- `created_by`, immutable `assigned_annotator_id` for this V1 slice, annotation status, aggregate `row_version`, completion timestamps, and the last successfully edited question pointer;
- dynamically added question membership/order records;
- per-actor workspace preference for the last source view.

It does not own or mutate source bytes, `PaperVersion`, processing results, blocks, or gaps. Readiness is derived from the two role associations and their current active processing selections; it is not a freely writable package flag.

V1 separates management from annotation without claiming formal RBAC. The creator (and a trusted platform-administrator policy hook where the deployment has one) may perform this slice's package import and processing-management actions. Only the current `assigned_annotator_id` may create, edit, fill, save-and-next, complete, or reopen annotation. Package-owned `Question.created_by` and `QuestionVersion.created_by` are therefore the assigned annotator, preserving the existing service's actor provenance. The package creator may differ from that annotator. The assignment is set at package creation and is immutable in this slice: no reassignment endpoint, assignment history, claim/queue, multi-user live editing, or supervisor workflow is introduced. Reads require actor context and allow the assigned annotator plus creator/management policy; exact production identity/administrator infrastructure remains outside G-09.

## 9. Source Package / Dual Source Design

Package import accepts both DOCX files, package metadata, and `assigned_annotator_id` in one multipart command. Each file is validated independently using the existing G-07 DOCX rules. The command creates two distinct `Paper` identities and one finalized `PaperVersion` for each, then associates their version IDs to the package roles. `AnnotationPackage` is the logical exam-work package; `question_paper Paper` is the canonical exam-question source identity, while `explanation Paper` is the associated explanation-source identity. The two rows therefore do not represent two business examinations. The `Paper` rows retain required baseline metadata; role-specific titles may be deterministic derivatives of the package title. The package row is the canonical metadata for this workflow.

The durable role association is immutable. Reprocessing creates another `SourceProcessingResult` for the same `PaperVersion`; it does not replace the association. A future corrected DOCX would require a separately authorized source-version/package-association decision and is not silently handled by G-09.

Import external-resource sequence is fixed:

1. validate both requests and stage both byte streams;
2. allocate both `PaperVersion` IDs and promote both staged objects to private final locations;
3. in one database transaction insert package, two papers, two finalized versions, two source-role rows, idempotency, and safe audit records;
4. on promotion or transaction failure, compensate every object promoted by this command and persist no partial package;
5. a replay with the same actor/scope/request ID and fingerprint resolves the same package identity and returns its current safe `PackageDetail` without creating another package; a different fingerprint is `IDEMPOTENCY_CONFLICT`.

No storage URI, hash, filename-derived private path, or document content appears in the package response or audit details. Existing G-07 immutability and provenance remain intact because the package only adds restrictive references.

## 10. Processing Integration

Processing remains synchronous and explicit. No worker, queue, scheduler, polling job, hidden retry, or parser change is introduced.

The API never accepts parser selection. A server-controlled canonical parser profile supplies the current authorized `parser_name`, `parser_version`, and `parser_config` to `ProcessingService`; that immutable profile metadata is persisted on each result by the existing service but is excluded from annotator UI/DTOs. After successful import, frontend/application orchestration explicitly invokes initial package processing in the same user intent/session flow. This is not a worker/background job and does not add a second user-facing “start processing” button. Later reprocessing is a new explicit user action.

Two commands are exposed:

- package processing: explicitly attempts both roles in deterministic order `question_paper`, then `explanation` and returns both terminal summaries; each child uses the existing Processing Service contract and a UUIDv5 child request ID whose namespace is the package ID and whose name is `{package_client_request_id}:{role}`;
- single-source reprocess: explicitly attempts only the named role and preserves every older result and active selection.

Package orchestration is intentionally not all-or-nothing across processing histories. If the first source terminalizes and the second fails, both truthful outcomes remain. Retrying the same package command replays the completed child and attempts/replays the other; it never duplicates a child result. The aggregate call returns HTTP 200 when both child calls resolve to terminal summaries and HTTP 202 if either child resolves to the existing Processing Service's accepted/in-progress or admission-redirect response; the body always carries a safe summary for both roles.

For each source, `effective_result` is the existing active result, if any. User-facing source state is composed as follows:

| Condition | Safe source state | Ready contribution |
|---|---|---|
| active terminal success | `ready` | yes |
| active terminal partial | `ready_with_gaps` | yes |
| no active; latest processing and not stale | `processing` | no |
| no active; latest processing classified stale by the existing service | `interrupted` | no; explicit reprocess is allowed |
| no active; latest partial | `partial_requires_adoption` | no |
| no active; latest failed | `failed` | no |
| no result | `not_processed` | no |

An older active success/partial remains effective if a later reprocess fails or becomes stale; the latest failed/interrupted attempt is exposed as a safe secondary status and does not erase a valid active result. Existing stale classification remains read-time product evidence: it does not mutate the old result, run a recovery worker, or auto-retry, but permits a new explicit reprocessing intent. Package readiness is `ready` only when both roles have an active success/partial result. It is `ready_with_warnings` if at least one effective result is partial; otherwise `ready`. Both `ready` and `ready_with_warnings` allow workbench entry. Every other combination is `not_ready` with safe per-role reasons and blocks entry.

Partial adoption is an explicit POST by the actor to the named package role and exact result ID. The same explicit command may select a newer terminal success result after reprocessing. It delegates to existing activation semantics, records `source_processing.active_changed`, and adds a package-level safe audit action. The server validates role/result ownership and terminal status in `success/partial`. There is no “adopt both automatically” path. Failed results are never adoptable, and partial is never selected without this actor command.

## 11. Annotation State Machine

```text
not_started --create question 1--> in_progress --complete(confirm)--> completed
                                              ^                    |
                                              |------reopen--------|
```

- Import creates `not_started`.
- Opening the workbench is a readiness-scoped read/orchestration action only. It never changes `not_started` and never creates a question.
- Successful creation of question 1 is the only `not_started -> in_progress` transition. It atomically creates the question/slot/version/membership and status transition.
- `not_started` therefore has zero questions; `in_progress` has at least one. A resume/open response for a ready but not-started package returns no current question and an explicit create-first-question affordance.
- All question create/save/fill/save-next mutations require `in_progress`.
- `completed` is read-only through every G-09 path and through existing generic question mutation paths when the question belongs to a package.
- `reopen` is an explicit, audited `completed -> in_progress` command. It does not change source, question, field, or provenance data.
- No G-09 transition writes `submitted`, `approved`, `rejected`, or published state.

## 12. Question Draft State / Ordering

Questions are created only by `create question` or the successful creation branch of `save-and-next`. Each creation transaction writes a `Question`, first draft `QuestionVersion`, a `QuestionSlot`, and an `AnnotationPackageQuestion` membership row. For a package-owned G-09 question, `QuestionSlot.paper_id`, `QuestionSlot.paper_version_id`, and `QuestionVersion.paper_version_id` always bind to the package `question_paper` Paper/PaperVersion. The explanation PaperVersion is never substituted into these legacy canonical fields; it is used through `AnnotationPackageSource` and exact field-level provenance. No total question count or empty slot is generated.

Ordering rules:

- `global_order` is package-wide, contiguous at creation, starts at 1, and is mirrored to `QuestionSlot.slot_number` and `QuestionVersion.source_order_index`;
- `source_question_order` is contiguous within the explicit source-document source-topic snapshot `(package, source_topic_order, source_topic_label)` and is mirrored to `QuestionVersion.source_question_order`;
- `knowledge_point_id` remains a controlled searchable taxonomy choice. It is independent of source provenance and never supplies `source_topic_order` or `source_topic_label`;
- `source_topic_order` and `source_topic_label` are explicit source-document source-topic metadata captured at first creation. The current text-first parser cannot reliably infer these business semantics, so the annotator must supply them through an explicit workbench metadata action/request; the service must not fabricate them from taxonomy name/default order;
- `AnnotationPackageQuestion` is authoritative package membership/order; legacy question fields remain populated for existing list and domain compatibility;
- changing knowledge point on a draft changes only the controlled taxonomy value; it never rewrites or reallocates the source-topic snapshot or `source_question_order`;
- save-and-next inheritance is a convenience default, not permanent provenance. After entering the next question, an assigned annotator may explicitly correct `source_topic_order` and/or `source_topic_label` when its actual source-document section differs. That correction does not change `knowledge_point_id`, invokes no parser/semantic inference, and requires no save-and-next pre-dialog;
- source-topic correction is the only G-09 operation that recalculates `source_question_order`. It requires an `in_progress` package, the assigned annotator, and a mutable current draft; a completed package must first be explicitly reopened. For each affected source-topic snapshot, questions are ordered by immutable `global_order` and numbered contiguously from 1. Moving one question recalculates both its old and new snapshot groups; client input never supplies `source_question_order`;
- on first successful execution, a correction locks the package and the old/new source-topic memberships in `global_order`, validates both the expected package and target-question row versions, increments `package.row_version` and the target draft row version, and increments every affected current draft row version whose local order changes. That first response returns the new package token and every ordering row changed by the transaction;
- an idempotent replay never enters the reorder transaction again. It resolves the already-won command through the existing idempotency record, returns the target draft and package token as current authoritative representations, returns `affected_questions = null`, and sets `ordering_refresh_required = true`; the client then refetches the package question list without asking the user to repeat or reconfirm the correction;
- physical deletion/reordering is not part of this slice.

Database uniqueness on package/global order, package/question, and package/source-topic/source-question order is the final duplicate guard. The source-topic-local uniqueness covers both source-topic metadata fields and is deferrable during one correction transaction, so a legal contiguous renumbering cannot transiently violate it. Browse/read calls never allocate a question or idempotency row.

## 13. Shenlun Four-field Contract

The only G-09 authored content fields are:

```text
stem_text
requirement_text
question_text
reference_answer_text
```

They remain four independent `Text` columns on the current draft `QuestionVersion`. The API accepts and returns independent JSON strings. CRLF and CR are canonicalized to LF exactly as the baseline schemas do; beyond that documented newline canonicalization, save does not trim, merge, infer, sanitize into HTML, or copy content between fields. Empty string is a persisted value. Rich-editor HTML is never authoritative. G-09 creates no option or correct-answer records and does not use `explanation_text` as a substitute for `reference_answer_text`.

Limits remain baseline-compatible: 200,000 characters for stem/reference answer and 20,000 for requirement/question. Oversize input is rejected before mutation.

## 14. Source-to-field Provenance

Each source action creates an immutable `QuestionFieldProvenanceRevision` and makes it the current head for exactly one `(question_version, field_name)`. Its ordered links identify:

- the package source association/role;
- its immutable `PaperVersion`;
- the exact `SourceProcessingResult` used;
- the exact `DocumentBlock` used;
- link order and the block's immutable source-order snapshot.

The four legal field identities are the four names in section 13. Selected blocks may span the two source roles only through an explicitly ordered request; within each source, links must be in ascending `DocumentBlock.source_order`. The service applies the request's source-group order and never performs semantic reordering. Duplicate block IDs in one command are invalid.

Every revision is a complete copy-on-write snapshot of current ordered provenance for that field:

- first fill contains only selected links;
- append copies current links, then adds selected links;
- replace contains only newly selected links;
- a later manual text edit leaves the provenance head unchanged;
- manual-only text has no head/link and produces a completion warning, not a hard failure.

Earlier revisions and their links remain queryable and immutable. A later active processing selection never rewrites links. Reads compute `is_current_active_result` for each link group; false means stale provenance, not broken provenance. Raw `DocumentBlock` text is not duplicated into provenance history. Each revision stores only a SHA-256 hash of the resulting field text for forensic correlation, never the text itself.

Correction-version behavior remains future-safe: if a later authorized correction creates a new `QuestionVersion`, it must copy the then-current provenance snapshot into a new initial revision linked to the new version; it must not point the new version's head at the old version's revision.

## 15. Append / Replace Semantics

The source action request contains `mode`, `target_field`, selected exact blocks, `expected_row_version`, and `client_request_id`.

| Current field | Requested mode | Result |
|---|---|---|
| empty | `fill` | selected block texts joined by LF become the field; new provenance head |
| non-empty | `fill` | reject `NON_EMPTY_OVERWRITE_FORBIDDEN`; no mutation |
| any | `append` | if empty, same text as fill; otherwise `current + "\n" + selected`; new copy-on-write provenance head |
| any | `replace` with `replace_confirmed=true` | selected text replaces current value; new provenance head containing only selected links |
| any | `replace` without confirmation | reject `REPLACE_CONFIRMATION_REQUIRED`; no mutation |

Selected text is the exact `text_original` of ordered blocks joined by one LF. It is never derived from client-supplied source text. An empty selection or a block from a failed, inactive, wrong-role, wrong-package, or no-longer-active result is rejected.

The transaction validates `expected_row_version` before reading/writing text. A successful action increments question `row_version`, updates `updated_at` and the last-edited pointer under the package lock, and appends safe audit metadata containing IDs, field, mode, counts, and before/after hashes only. It does **not** increment package `row_version`: ordinary content/provenance saves are question-version concurrency operations. Stale commands mutate nothing. An identical replay does not apply fill/append/replace again and may return the current safe question representation; same request ID/different fingerprint conflicts. Timeout retry therefore cannot append twice. Concurrent editors race on row version; one succeeds and the other receives the current safe representation with `STALE_DRAFT`.

## 16. Autosave / Manual Save / Concurrency

Autosave and manual save call the same patch command. The payload is a partial set of the four fields and optional knowledge-point change plus `expected_row_version` and `client_request_id`. Both are server-authoritative only after a 200 response.

Frontend state is explicitly separate:

| UI state | Meaning |
|---|---|
| `dirty` | local editor differs from last acknowledged server representation |
| `saving` | one request is in flight |
| `saved` | response values and returned row version are the acknowledged server truth |
| `save_failed` | local changes remain only in memory; server truth is still the last acknowledged representation |

Only one autosave per question may be in flight in one client. Later keystrokes remain dirty and are sent after the first response with its returned row version. The client must never retry a timed-out request with a new request ID; it retries the identical command ID/fingerprint. A 409 stale response is not auto-merged or overwritten: refresh/compare/reapply is required.

Successful content or knowledge-point mutation updates the package's last-edited pointer under the package lock but does not increment package `row_version`. An idempotent replay returns the current safe question representation and does not increment any row version again. GET, navigation, source-tab viewing, preview, and list operations never change the pointer. A source-view preference update changes only workspace preference and does not count as question editing. Every `QuestionDraft` response also includes the current `package_row_version`; every aggregate mutation that changes that token returns the new token, so there is no package-token black hole.

The backend does not persist browser `dirty` or `save_failed`; therefore there is no server-known unsaved flag in V1. Navigation/unload guards and the three choices in FD-23 are frontend responsibilities based on client state. Completion UI must not issue the command while locally dirty or failed; the completion transaction still validates server truth.

## 17. Save-and-next

`save-and-next` is one database transaction and one idempotent command:

1. lock package and validate `in_progress` plus expected package revision;
2. lock current membership/question/version and validate expected question row version;
3. apply the optional current draft patch and provenance-neutral manual-save rules;
4. locate `global_order + 1`;
5. if it exists, select it as the returned working target; if current is the tail, create exactly one next question with the current question's `knowledge_point_id` and the current source-topic snapshot. `next_knowledge_point_id` is not a save-and-next input;
6. update last-edited pointer to the current question because its save succeeded; creation of an empty next draft does not falsely claim it was edited;
7. write audit/idempotency, flush all uniqueness constraints, increment `package.row_version` only if a next question was created, and commit; every `SaveAndNextResult` returns the committed package token;
8. only after the 200 response may the client switch the working target.

After entering the next question, the annotator may explicitly change its controlled `knowledge_point_id`; that later change never rewrites source-topic provenance. If save validation or commit fails, creation and advancement roll back. Double-click and timeout retry resolve the same originally selected/created next-question identity and never create another next question; returned DTOs may reflect later legal state. A concurrent different command is serialized by the package row lock; uniqueness is the final guard. If a conflicting next question was legally created by the winner, the loser receives `STALE_PACKAGE`/`STALE_DRAFT`, not another question.

## 18. Resume / Last-edited Semantics

`GET /annotation-packages/{id}/annotation/resume` returns:

- package status/readiness and row version;
- persisted created-question count;
- the last successfully edited question and its current persisted four fields, row version, metadata, and current provenance heads;
- the caller's last source view: `question_paper`, `explanation`, or `compare`;
- safe source summaries needed to load the workbench.

If `in_progress` has questions but no last-edited pointer (for example, only an empty first question was created), resume returns the first question. If `not_started`, `current_question` is null and the ready workbench-open response offers “开始第1题”; opening does not create it. `completed` resume is the same persisted view marked read-only. Successful completion returns the package/task-list route, from which the user chooses a next package; it never automatically opens another package.

Temporary selections, popovers, pending replace confirmation, unacknowledged local content, and scroll offset are never persisted. Workspace source view is keyed by `(package_id, actor_id)` so it does not become global package business state.

## 19. Complete / Reopen State Transitions

Completion request fields are `client_request_id`, `expected_package_row_version`, `confirm_completion`, optional `warning_set_token`, and the exact acknowledged warning codes. The service locks in this fixed order: package → `question_paper` package-source association → `explanation` package-source association → each source PaperVersion → each active-processing selection row → package-question memberships in global order → current draft versions. In that one lock scope it recomputes readiness/warnings, validates the warning token, validates completion, and transitions status. Active selection therefore cannot race the warning-preview/confirmation decision.

Hard validation requires non-blank (Unicode whitespace stripped only for validation) values for all four fields on every created current version. It returns safe entries shaped as `{question_order, missing_fields[]}`. No text is echoed. A stale aggregate, persistence failure, or any future persisted failed-work marker is also hard. The frozen hard-blocker list does not add a minimum-question-count rule; the backend must not invent one. Because V1 persists no dirty/save-failed marker, local unsaved state is client-only as described in section 16.

Soft warnings are recomputed inside the same lock scope:

- an effective source result is partial;
- an effective result has one or more gaps;
- a non-blank field has no current provenance head.

The first valid attempt with warnings returns `409 COMPLETION_WARNINGS_REQUIRE_CONFIRMATION`, a safe warning array, current package row version, and `warning_set_token = SHA-256(package_id + row_version + canonical warning codes/locations)`. This response is not stored as a successful idempotency result. The UI obtains explicit user confirmation and sends a new `client_request_id`, `confirm_completion=true`, the unchanged expected row version, token, and exact acknowledged codes. The service recomputes warnings under lock; any drift is `STALE_COMPLETION_CONFIRMATION`. With no warnings, `confirm_completion=true` is still required by FD-26.

Success atomically changes `in_progress -> completed`, increments package row version, sets completion actor/time, and writes audit/idempotency. Every package-owned mutation path then rejects with `ANNOTATION_COMPLETED_READ_ONLY`. The success response directs the client to the package/task-list read route; no automatic next-package navigation occurs.

Reopen accepts a new `client_request_id`, expected package row version, and optional bounded reason. It locks the package, requires `completed`, changes only status to `in_progress`, clears the current completion timestamp/actor into append-only audit history (the audit event preserves both transition endpoints and prior completion metadata), increments row version, and returns resume state. It does not alter questions/provenance or imply rejection. Reopen is explicit and idempotent.

## 20. API Contract

All routes are under `/api/v1`, use JSON unless import is multipart, and use the existing `ApiError` envelope. Mutation routes require `X-Actor-Id`; package reads require actor context and creator/assigned-annotator/management-policy scope as defined in section 8. UUIDs below are opaque and are not displayed as technical labels in the UI.

### Package, processing, and source reads

| Method and route | Request | Success |
|---|---|---|
| `POST /annotation-packages` | multipart: `client_request_id`, title/year/region/subject/exam_type, `assigned_annotator_id`, `question_paper`, `explanation` | `201 PackageDetail`; replay resolves the same package ID, returns current safe `PackageDetail`, and uses `200` + `Idempotent-Replay: true` |
| `GET /annotation-packages` | `scope=assigned|created`, optional annotation/readiness status, cursor, limit | `200 PackageTaskList`; only packages assigned to or created/managed by caller; completion returns here |
| `GET /annotation-packages/{package_id}` | none | `200 PackageDetail` including composed readiness and safe role summaries |
| `POST /annotation-packages/{package_id}/processing` | `{client_request_id}` | `200 PackageProcessingOutcome` when both terminal; `202` if either child is accepted/in progress; always includes two safe role summaries |
| `POST /annotation-packages/{package_id}/sources/{role}/processing-results` | `{client_request_id}` | `200 SourceProcessingSummary` terminal; `202` accepted/in-progress redirect; explicit single-source reprocess |
| `POST /annotation-packages/{package_id}/sources/{role}/processing-results/{result_id}/adopt` | `{client_request_id}` | `200 SourceProcessingSummary`; explicit active selection for an exact terminal success/partial result; mandatory actor intent for partial |
| `GET /annotation-packages/{package_id}/sources/{role}/content` | opaque `cursor?`, `limit` (1–200) | `200 SourceContentPage`; active result only, ordered blocks and intervening safe gaps |

`role` is exactly `question_paper` or `explanation`. Package processing is a synchronous orchestrator over the existing Processing Service; it is not a new processing lifecycle.

### Annotation, question, save, and navigation

| Method and route | Request | Success |
|---|---|---|
| `GET /annotation-packages/{package_id}/annotation/open` | none | `200 AnnotationResume`; readiness/open-workbench query only, no annotation status mutation |
| `POST /annotation-packages/{package_id}/questions` | `{client_request_id, expected_package_row_version, knowledge_point_id, source_topic_order, source_topic_label}` | `201 QuestionDraft`; creates first or explicit tail question only; first creation atomically transitions to `in_progress` |
| `GET /annotation-packages/{package_id}/questions` | cursor, limit, optional knowledge point | `200 PackageQuestionList`, ordered only over existing questions |
| `GET /annotation-packages/{package_id}/questions/{question_id}` | none | `200 QuestionDraft`; no pointer mutation |
| `PATCH /annotation-packages/{package_id}/question-versions/{version_id}` | `{client_request_id, expected_row_version, fields?, knowledge_point_id?}` | `200 QuestionDraft`; autosave/manual save; source-topic fields are rejected here and do not change the package token |
| `PATCH /annotation-packages/{package_id}/question-versions/{version_id}/source-topic` | `{client_request_id, expected_package_row_version, expected_row_version, source_topic_order, source_topic_label}` | `200 SourceTopicCorrectionResult {updated_question, package_row_version, affected_questions: list[AffectedOrderingRow] | null, ordering_refresh_required}`; first success returns changed rows/`false`; replay returns current authoritative target/package state, `null`/`true`, and `Idempotent-Replay: true` without renumbering |
| `POST /annotation-packages/{package_id}/question-versions/{version_id}/source-actions` | `{client_request_id, expected_row_version, target_field, mode, replace_confirmed, selections:[{processing_result_id, document_block_id}]}` | `200 QuestionDraft` with current provenance |
| `POST /annotation-packages/{package_id}/question-versions/{version_id}/save-and-next` | `{client_request_id, expected_package_row_version, expected_row_version, fields?}` | `200 SaveAndNextResult {saved_question, next_question, created_next}`; next inherits current knowledge point |
| `GET /annotation-packages/{package_id}/annotation/resume` | none | `200 AnnotationResume`; no mutation |
| `GET /annotation-packages/{package_id}/question-versions/{version_id}/field-provenance/{field_name}/history` | cursor, limit | `200 FieldProvenanceHistory`; creator/assigned-annotator scoped immutable revision evidence |
| `PATCH /annotation-packages/{package_id}/workspace` | `{client_request_id, expected_row_version, source_view}` | `200 WorkspaceState`; does not change last-edited |
| `POST /annotation-packages/{package_id}/annotation/complete` | completion request in section 19 | `200 AnnotationResume` or safe 409/422 validation response |
| `POST /annotation-packages/{package_id}/annotation/reopen` | `{client_request_id, expected_package_row_version, reason?}` | `200 AnnotationResume` |

Existing generic question endpoints remain backward-compatible for non-package questions. Their service mutations must resolve package membership and enforce assignment, package status/read-only, and G-09 no-submit restrictions for package-owned questions so they cannot bypass this contract. Generic question list/detail reads must likewise detect package ownership and require creator/assigned-annotator/management-policy scope (using an optional actor dependency for legacy non-package reads if compatibility requires it); unauthenticated generic routes must not become a side door to package question text or answers.

## 21. DTO / Safe Response Boundary

`PackageDetail` contains exactly: `package_id`; `title`, `year`, `region`, `subject`, `exam_type`; opaque `created_by`, opaque `assigned_annotator_id`; `annotation_status`, `row_version`, `created_question_count`, nullable `last_edited_question_id`; `readiness` (`ready`, `ready_with_warnings`, or `not_ready`); and `sources[]`. Each source item contains `role`, `display_name`, `effective_state`, nullable `effective_result_status`, `partial_adoption_required`, `block_count`, `gap_count`, nullable `latest_attempt_state`, `latest_attempt_result_status`, `latest_attempt_interrupted`, and safe timestamps. It excludes storage URI, file hash, parser config/fingerprint, diagnostic metadata, private path, raw document bytes, and traceback.

`SourceProcessingSummary` contains `role`, opaque `processing_result_id`, `execution_state`, nullable `result_status`, `block_count`, `gap_count`, `is_active`, `interrupted`, safe `diagnostic_code`, and timestamps. `PackageProcessingOutcome` contains `package_id`, recomputed `readiness`, and exactly two such summaries in role order. It does not expose parser/runtime metadata.

`SourceContentPage` contains its opaque active `processing_result_id` as the selection identity, a stable opaque cursor, and:

```json
{
  "source": {"role": "question_paper", "display_name": "题本"},
  "processing_result_id": "uuid",
  "effective_status": "ready_with_gaps",
  "position_kind": "document_order",
  "items": [
    {"kind": "block", "block_id": "uuid", "source_order": 12, "text": "authorized source text"},
    {"kind": "gap", "gap_id": "uuid", "source_order": 13, "display_code": "UNREADABLE_CONTENT", "message": "此处有内容无法可靠读取"}
  ],
  "next_cursor": null
}
```

The IDs support selection/provenance but the UI displays human labels/order, not technical IDs. A gap is an item in source order; it is never silently omitted or represented as recovered text. Blocks and gaps are merged deterministically by `(source_order, item_kind_rank, item_id)`, where `gap` has rank 0 and `block` rank 1; the cursor encodes this full triple. This guarantees deterministic pagination with no skipped/duplicated same-order gaps or blocks. The gap's safe before/after block-order anchors remain available to the UI. Only an allow-listed `display_code` and localized generic message cross the boundary. Current G-08 parsing has reliable paragraph order but no page geometry, so `position_kind=document_order` and `source_order` are the only locator. A page number/coordinates may be added only by a later parser contract that can prove them.

`QuestionDraft` returns `question_id`, `question_version_id`, `version_number`, `row_version`, current `package_row_version`, `status=draft`, `global_order`, `knowledge_point_id`, `source_question_order`, `source_topic_order`, `source_topic_label`, the four strings separately, and `field_provenance` keyed by the four field names.

`SourceTopicCorrectionResult` contains `updated_question`, `package_row_version`, nullable `affected_questions`, and `ordering_refresh_required`. On first successful execution, `Idempotent-Replay` is absent or false, `updated_question` is the committed target `QuestionDraft`, `package_row_version` is the committed aggregate token, `affected_questions` contains the question/version IDs, committed draft row versions, `global_order`, source-topic metadata, and recomputed `source_question_order` for every row changed by that transaction, and `ordering_refresh_required=false`. On an identical replay, the response carries `Idempotent-Replay: true`; `updated_question` and `package_row_version` are current authoritative representations, `affected_questions=null`, and `ordering_refresh_required=true`. The server must not guess historical affected rows, rerun ordering to reconstruct them, or derive a fake historical result from current group membership. When refresh is required, the client issues `GET /annotation-packages/{package_id}/questions` and replaces its ordering state; this is technical recovery after retry, not a new user confirmation or a repeated correction.

A field provenance value contains nullable head revision ID and ordered links with `processing_result_id`, `document_block_id`, `source_role`, `source_order`, and `is_current_active_result`. `FieldProvenanceHistory` returns immutable revisions and the same exact link evidence, scoped to the package creator/assigned annotator (or trusted management policy), so a later active-result change never makes historical evidence uninspectable.

`AnnotationResume` contains `PackageDetail`, nullable `current_question: QuestionDraft`, `workspace: {source_view, row_version}`, and `read_only`. `PackageQuestionList` items contain only safe navigation metadata plus persisted completeness booleans; it never returns an invented/unstarted position. Cursor ordering is `(global_order, question_id)`. `PackageTaskList` items contain `package_id`, safe display metadata, assignment relationship (`assigned`/`created`), annotation status, readiness, created-question count, last safe update timestamp, and pagination cursor; it contains no source text, answer, parser, or storage data.

## 22. Error Semantics

All errors use `{code, message, field_errors, request_id}` and generic safe messages. Field errors may contain field names, question order, source role/order, and controlled codes, never source text, answers, paths, hashes, parser metadata, or tracebacks.

| HTTP | Code | Meaning |
|---|---|---|
| 401 | `UNAUTHENTICATED` | missing/invalid current actor context |
| 403 | `FORBIDDEN` | package is not accessible to actor |
| 403 | `ANNOTATION_NOT_ASSIGNED` | actor may read/manage the package but is not its assigned annotator for an annotation mutation |
| 404 | `ANNOTATION_PACKAGE_NOT_FOUND`, `QUESTION_NOT_FOUND`, `SOURCE_RESULT_NOT_FOUND` | scoped resource absent; cross-package IDs use the same not-found behavior |
| 409 | `IDEMPOTENCY_CONFLICT` | same actor/scope/request ID, different fingerprint |
| 409 | `STALE_DRAFT`, `STALE_PACKAGE`, `STALE_WORKSPACE` | optimistic token mismatch; include safe current tokens |
| 409 | `SOURCE_ORDER_CONFLICT`, `SOURCE_QUESTION_ORDER_CONFLICT` | uniqueness conflict after locking/race recovery |
| 409 | `NON_EMPTY_OVERWRITE_FORBIDDEN` | ordinary fill targeted non-empty field |
| 409 | `REPLACE_CONFIRMATION_REQUIRED` | replace lacked explicit confirmation |
| 409 | `SOURCE_SELECTION_STALE` | selected result is no longer the role's active result |
| 409 | `ANNOTATION_COMPLETED_READ_ONLY` | mutation attempted before explicit reopen |
| 409 | `COMPLETION_WARNINGS_REQUIRE_CONFIRMATION` | hard validation passed; warning confirmation required |
| 409 | `STALE_COMPLETION_CONFIRMATION` | warning token/acknowledgement no longer matches locked truth |
| 409 | `ANNOTATION_REVIEW_DEFERRED` | submit/review attempted for a package-owned G-09 question |
| 422 | `PACKAGE_NOT_READY` | both effective sources are not success/partial active results |
| 422 | `SOURCE_FAILED` | named source has no usable active result and latest is failed |
| 422 | `PARTIAL_NOT_ADOPTED` | terminal partial exists but actor has not explicitly adopted it |
| 422 | `PROCESSING_RESULT_NOT_ADOPTABLE` | wrong role, nonterminal, failed, or foreign result |
| 422 | `INVALID_SOURCE_TARGET` | invalid field, role, result/block ownership, empty/duplicate selection, or ordering |
| 422 | `ANNOTATION_INCOMPLETE` | one or more created questions lack required fields |
| 422 | `VALIDATION_ERROR` | bounded input/schema failure |
| 503 | `SOURCE_STORAGE_UNAVAILABLE`, `PROCESSING_UNAVAILABLE` | operational intake/processing failure; safe retry guidance only |

A parser terminal `failed` result is a successful HTTP processing command with `result_status=failed`, not an exception. The package stays not ready unless an older valid active result remains. An operational reprocess exception returns the safe 503 and never discards older history/active selection.

## 23. Idempotency

Commands requiring `client_request_id` are import, package process, per-source process, result adoption, question create, save, source action, source-topic correction, save-and-next, workspace preference update, complete, and reopen. GET open/resume/list/history reads do not use idempotency. Package process uses its request ID only to derive the two stable child IDs; it does not cache a separate aggregate 202 response, so later replay can truthfully observe children reaching terminal state.

G-09 idempotency is **effect idempotency**, not permanent historical HTTP-response snapshot storage. Given the same actor, operation scope, `client_request_id`, and fingerprint, the business mutation must not execute again. A replay must therefore never repeat append/replace, renumber a source-topic group, create another next question or package, increment a row version because of replay, or perform completion/reopen twice. If the fingerprint differs, the command returns `IDEMPOTENCY_CONFLICT`.

The existing `idempotency_keys` record proves that one semantic command won and committed. On replay, the service resolves its stable primary identity through `result_resource_type`/`result_resource_id`, returns that resource or aggregate's current safe authoritative representation, and sets `Idempotent-Replay: true`. It does not promise byte-for-byte reproduction of the original historical HTTP body after later legal mutations. Effect identity remains stable where required: import resolves the same `package_id`; question create resolves the same question/version identity; save-and-next resolves the originally selected/created next-question identity; source action cannot append or replace twice; completion/reopen cannot transition twice or force current state back to a historical state.

Each scope includes the aggregate/resource identity, for example `annotation_package.import`, `annotation_package.process:{id}`, `annotation_source.process:{source_id}`, `question.source_action:{version_id}`, `question.source_topic:{version_id}`, and `annotation.complete:{package_id}`. Fingerprints include every semantic input and exclude server-derived text. A source action fingerprint includes ordered block IDs, exact result IDs, mode, field, confirmation, and expected row version. A source-topic correction fingerprint includes the target source-topic metadata and both expected row-version tokens. Its replay returns the current target/package representations with `affected_questions=null` and `ordering_refresh_required=true`; it never renumbers again.

The implementation must strengthen the baseline lock-then-insert pattern against simultaneous first use: insert/reserve the unique key inside a SAVEPOINT, flush, and on unique violation reload/lock the winner and apply replay/conflict rules. No command may perform its domain mutation before it owns/resolves the idempotency key. For the existing Processing Service, its approved two-transaction admission/terminalization semantics remain authoritative.

Rejected validation/stale/warning-preview requests are not persisted as successful idempotency results. Retrying a timed-out potentially successful command uses the same ID and identical fingerprint. A user-confirmed completion uses a new request ID because it is a different command from the warning preview.

No immutable command-response receipt table, response JSON column, affected-question snapshot column, or event-store replay snapshot is added. `idempotency_keys` must not store source text, answers, document bytes, full/partial HTTP response bodies, affected-question JSON, storage URI, private path, parser output, or traceback. Fingerprints contain only safe semantic inputs, opaque IDs, and concurrency tokens. The existing approved `ProcessingService` trigger, activation, result replay, and two-transaction semantics are explicitly exempt from redesign and remain unchanged.

## 24. Transaction / Locking Boundaries

Lock order is deterministic to avoid deadlock: package → package-source associations in role order `question_paper`, `explanation` → their `PaperVersion` rows → active-processing selection rows in the same role order → package-question membership in global order → `Question` → current `QuestionVersion` → provenance head. A source-topic correction locks the package, then all memberships in its old and new source-topic snapshots in `global_order`, followed by their Questions and current QuestionVersions in the same order. Idempotency reservation occurs according to the approved command gate before domain derivation; locks then follow this order. There is no global table lock.

| Operation | Boundary and locks |
|---|---|
| import | stage/promote external objects, then one DB transaction for package/two sources/idempotency/audit; compensate both objects on DB failure |
| package process | package authorization/read transaction plus two explicit existing Processing Service lifecycles; truthful child histories are not rolled back as a group |
| adopt partial | existing activation transaction locks paper version, exact result, and active pointer; package/role ownership validated before delegation |
| open/create | open is a readiness read only; create locks package and atomically creates question 1 plus `not_started -> in_progress`, or creates a tail question; uniqueness is final guard |
| manual/autosave | one transaction; reserve idempotency, lock package then current version; compare question row version; mutate question and last-edited pointer without aggregate row-version churn |
| source-topic correction | replay gate first: an identical winner exits without package/group locks or mutation and returns current target/package state with refresh required; first execution uses one transaction to reserve idempotency, lock package plus old/new source-topic snapshot memberships in global order, validate package/target tokens and mutable assigned-annotator scope, update target metadata, recompute both local sequences, update affected draft row versions, increment the package token, audit, and return every changed ordering row |
| fill/append/replace | same save locks plus active pointer and provenance head; server reads immutable blocks; field, revision, links, head, pointer, audit commit atomically |
| save-and-next | one transaction covering current save and existing-next selection or single next creation; no advancement outside commit |
| complete | one transaction; lock package, both sources/PaperVersions/active rows in fixed role order, then all current memberships/versions in global order; recompute readiness/warnings, validate token, and transition without TOCTOU |
| reopen | one transaction; lock package, validate expected row version/completed, transition and audit |

Package-level serialization is intentional for its own question sequence and completion revision; it is not a global lock and prevents completion racing a save. Source reads and question GETs are non-locking snapshots.

## 25. Proposed Schema Delta

This is design only. Migration numbering is intentionally not assigned in this contract.

### REUSE

- `papers`, `paper_versions`, private source storage, upload validation;
- `source_processing_results`, `document_blocks`, `source_processing_gaps`, `paper_version_active_processings`;
- `questions`, `question_versions`, `question_slots`, five Shenlun knowledge points;
- `idempotency_keys` and `audit_events`.

`source_materials` and `question_version_materials` remain valid authored-material capabilities but are not used as a substitute for exact G-08 block provenance.

### ADD

1. `annotation_packages`: `id`, display metadata, `created_by`, immutable `assigned_annotator_id`, status, `row_version`, nullable `last_edited_question_id`, created/updated/completed actor/timestamps.
2. `annotation_package_sources`: `id`, `package_id`, `source_role`, `paper_version_id`, `created_at`; association rows are immutable.
3. `annotation_package_questions`: `package_id`, `question_id`, `global_order`, `knowledge_point_id`, `source_topic_order`, `source_topic_label`, `source_question_order`, `created_at`.
4. `annotation_workspace_states`: `package_id`, `actor_id`, `source_view`, `row_version`, `updated_at`.
5. `question_field_provenance_revisions`: `id`, package/question/version IDs, `field_name`, monotonically increasing `revision_number`, `operation`, nullable previous revision, `resulting_text_hash`, actor/request IDs, timestamp.
6. `question_field_provenance_links`: `revision_id`, `link_order`, package-source ID, paper-version ID, processing-result ID, document-block ID, `source_order_snapshot`.
7. `question_field_provenance_heads`: `(question_version_id, field_name)` to current revision, with package/question ownership columns needed for composite integrity.

### ALTER

- Add a composite unique key `(processing_result_id, id)` to `document_blocks` so a provenance link can enforce exact result/block ownership.
- Add only the composite unique keys required for deferrable ownership FKs; do not alter or weaken M-001–M-006 values, status rules, or delete behavior.
- Existing question mutation services must consult package membership/status; this is service behavior, not a destructive schema rewrite.

### INDEX / UNIQUE / FK / CHECK

- one source per `(package_id, source_role)` and one package binding per `paper_version_id` in V1;
- source role check in `('question_paper','explanation')`;
- package status check in `('not_started','in_progress','completed')`, positive row version, subject check `shenlun`, year range retained; non-null UUID `assigned_annotator_id` validation (the current backend has no user table to reference); no V1 reassignment mutation path;
- unique package-question membership, `(package_id, global_order)`, and deferrable `(package_id, source_topic_order, source_topic_label, source_question_order)`; positive orders and nonblank source-topic label;
- workspace PK `(package_id, actor_id)`, source view check in `('question_paper','explanation','compare')`, positive row version;
- provenance field check over four exact fields; operation check `fill/append/replace/copy_forward`; positive revision/link/source order; unique `(question_version_id, field_name, revision_number)` and `(revision_id, link_order)`;
- composite restrictive FKs prove package source → paper version → processing result → block; restrictive FKs prove provenance question/version and package membership;
- nullable package `last_edited_question_id` uses a composite, deferrable restrictive FK to membership so it cannot point outside the package;
- every new FK uses `ON DELETE RESTRICT`/`NO ACTION`; no cascade deletion.

### Immutable/history constraint

Package-source associations and provenance revisions/links are append-only. The application exposes no update/delete repository methods for them. The migration must add PostgreSQL trigger protection against UPDATE/DELETE of provenance revision/link rows and UPDATE/DELETE of a package-source identity after insert; tests must prove rejection. The provenance head is deliberately mutable because it selects current history, just as active processing selects current immutable processing history.

## 26. Migration Constraints

Future migration work must be a single linear additive descendant of M-006; it may not recreate, squash, merge, renumber, or mutate M-001 through M-006. Upgrade and downgrade must never cascade-delete source, processing, question-version, provenance, idempotency, or audit history. If a safe downgrade cannot remove tables because referenced production history exists, the implementation plan must explicitly require an empty/new-table precondition rather than destructive cleanup.

All constraints are validated on PostgreSQL 16. Migration tests must run only with `APP_ENV=test` and a database name ending `_test`, cover clean upgrade from base and M-006, current-head upgrade, downgrade/upgrade round trip where safe, named constraints/indexes, composite ownership, immutability triggers, and no-cascade behavior. SQLite is forbidden.

No migration is authorized by this document.

## 27. Privacy / Security

- Treat both DOCX files as untrusted ZIP/XML. Reuse size/type/archive validation, never execute macros/active content, and never follow external document relationships or network fetches.
- Store bytes only in private source storage. Do not expose storage URI, private path, verified hash, OOXML, parser config/fingerprint, diagnostic metadata, credentials, or traceback.
- Source block text and answers are permitted only in authenticated, package-scoped content/question response bodies. They are prohibited from application logs, audit details, idempotency payload/storage, command-response receipts, metrics labels, Git, issue comments, screenshots, and fixtures. Idempotency storage also excludes document bytes, HTTP response bodies, affected-question JSON, storage URI, private path, parser output, and traceback.
- Audit stores IDs, safe codes, counts, state transitions, field names, and hashes only.
- Error responses are allow-listed and generic. Cross-package resource probing returns scoped not-found.
- Test fixtures are synthetic and sanitized. No real paper, answer, source path, parser output, database dump, or credential is committed.
- `X-Actor-Id` remains a temporary development/test identity mechanism. This contract does not claim formal authentication/RBAC; production exposure must remain blocked until that separately governed control exists.

## 28. Acceptance / Test Matrix

| # | Required future verification |
|---:|---|
| 1 | one idempotent import binds exactly one finalized question-paper source and one finalized explanation source |
| 1a | creator may assign a different annotator; only that annotator can mutate annotation while creator/management policy can import/process/read within scope |
| 2 | readiness requires usable active results for both roles and reports composed safe state |
| 3 | either role failed with no older usable active result blocks start/workbench |
| 4 | partial stays inactive until exact explicit audited adoption; failed adoption is rejected |
| 5 | source API returns blocks in immutable source order with stable cursor behavior |
| 5a | same-`source_order` gap/block items paginate by `(source_order, item_kind_rank, item_id)` without loss or duplicate |
| 6 | partial gaps appear as ordered safe markers and leak no diagnostic/path/traceback |
| 7 | workbench open creates no slots or status transition; explicit first-question command creates exactly one question/order 1 and atomically enters `in_progress` |
| 8 | all four fields independently round-trip with documented LF normalization only |
| 9 | single- and multi-block source actions persist exact result/block ordered provenance |
| 10 | non-empty ordinary fill is rejected; append preserves human content and appends once |
| 11 | replace requires explicit confirmation and preserves prior provenance revision history |
| 12 | manual edit changes text but keeps the provenance head and never mutates a block |
| 13 | stale question/workspace row versions and stale aggregate commands are rejected without partial mutation; ordinary saves do not create package-token churn |
| 14 | autosave timeout retry with the same ID replays once; same ID/different payload conflicts |
| 15 | save-and-next saves before advancing and is idempotent under double-click/retry |
| 15a | save-and-next requires no next knowledge-point input and newly created next question inherits current knowledge point/source-topic snapshot |
| 16 | concurrent next creation cannot duplicate `global_order` or source-topic-local `source_question_order` |
| 16a | first successful source-topic correction leaves `knowledge_point_id` unchanged, recalculates old and new source-topic groups by `global_order`, returns every affected row with committed row versions/package token, and sets `ordering_refresh_required=false` |
| 16b | an immediate identical retry returns `Idempotent-Replay: true`, performs no second reorder, increments no question/package row version, returns current authoritative target/package state, `affected_questions=null`, and `ordering_refresh_required=true`; changed metadata under the same request ID conflicts |
| 16c | after a later unrelated legal mutation, retrying the original correction still performs no mutation, returns `Idempotent-Replay: true`, and truthfully returns current target/package tokens with `affected_questions=null` and `ordering_refresh_required=true`; client question-list refetch recovers current ordering |
| 16d | replay safety uses existing `idempotency_keys` without any command-response receipt table, response JSON column, affected-row snapshot, or reconstructed historical response |
| 17 | GET, preview, list, navigation, and source-view reads do not change last-edited |
| 18 | resume/open returns the last successfully edited persisted question, provenance, and caller source view; a not-started package returns no current question |
| 19 | completion returns every question-order/missing-field hard error and does not transition |
| 20 | partial, gaps, and manual-only fields return safe soft warnings/token |
| 21 | explicit confirmation with unchanged warning token and locked active selections transitions exactly once to completed and returns task-list navigation |
| 22 | every package-owned write path, including generic question routes, is blocked while completed |
| 23 | explicit idempotent reopen returns to in-progress and audits the transition |
| 23a | completed response/task-list route returns only scoped package tasks and never auto-opens the next package |
| 24 | G-09 creates no submit/review/approve/reject/publish entity or transition |
| 25 | log/audit/error/fixture capture contains no source text, answers, paths, hashes, or secrets |
| 25a | idempotency records/fingerprints contain no source text, answers, document bytes, HTTP response body, affected-row JSON, storage/private path, parser output, or traceback |
| 26 | additive PostgreSQL 16 migration proves composite FKs, uniqueness, append-only history, and RESTRICT deletion |
| 27 | every existing Processing Service test and response/idempotency/activation behavior remains valid |

Future implementation verification also includes the smallest focused tests plus `uv run ruff check .`, `uv run mypy src`, and the complete PostgreSQL-backed `uv run pytest` suite.

## 29. Manual Acceptance Scenario

Using synthetic pure-text DOCX fixtures only:

1. import one package with metadata and two DOCX files; replay the request and confirm no duplicate package/source/version;
2. process both; demonstrate failed blocks entry, then reprocess; demonstrate partial requires explicit adoption and visible gap marker;
3. open a ready package workbench and confirm no question/status transition existed until “开始第1题”; create question 1 and confirm atomic `not_started -> in_progress`;
4. switch `题本`/`解析`/`对照查看`; verify ordered content and human gap label without technical details;
5. create question 1 with one of the five controlled knowledge points; fill the four fields using one and multiple blocks from either role;
6. manually edit a filled field; confirm text persists and provenance remains;
7. attempt ordinary fill over non-empty content and observe rejection; append once; explicitly confirm replace and inspect current versus historical provenance;
8. simulate two tabs and a timeout: stale save is rejected, identical retry is replayed, and content is not duplicated;
9. use save-and-next twice/double-click; confirm question 1 saves before one question 2 appears and question 2 inherits question 1 knowledge point/source-topic metadata; then perform a source-topic correction, confirm its knowledge point is unchanged and its old/new source-topic groups are renumbered by `global_order`, and record the returned package/question tokens and affected rows; perform another legal mutation, retry the original correction with the same request ID/payload, confirm no reorder or row-version increment runs again and `Idempotent-Replay: true`, confirm current authoritative target/package tokens with `affected_questions=null` and `ordering_refresh_required=true`, then refetch the question list and recover current ordering state;
10. browse other questions without editing, leave, then resume; confirm return to last edited question, saved values/provenance, and last source view;
11. attempt completion with a missing field; observe question-order/field error; fill it, observe soft warnings, explicitly confirm under locked active selections, reach completed, and return to the task list without automatic next-package opening;
12. verify all editing paths are read-only, then explicitly reopen and edit again;
13. inspect logs/audit/API payloads for prohibited data and confirm no review/approval/publication object was created.

## 30. Out of Scope

Reviewer workflow, submit, approval/rejection, release/publication, searchable official bank, bulk import, OCR, PDF/scanned upload, mixed-content production fields, image/equation/table support, AI question splitting/classification, automatic question count, formal RBAC, worker/queue/background processing, parser modification, and frontend/React implementation remain out of scope.

## 31. Stop Conditions

Implementation planning or work must stop and return `PRODUCT_DECISION_REQUIRED` / `CONTRACT_STATUS = BLOCKED_PENDING_PRODUCT_DECISION` if a discovered issue would change what users see, can do, or when they can do it; allow different overwrite/delete behavior; redefine completion/reopen; or alter annotation workflow. It must also stop for baseline drift, a dirty out-of-scope worktree, any need to mutate M-001–M-006 history, inability to preserve exact source/result/block provenance, pressure to auto-activate partial or activate failed, private-data leakage, a requirement for background processing, pressure to add response-snapshot/receipt persistence without a new formal technical review, or an attempt to rerun a mutation/guess historical affected rows merely to reconstruct a replay body.

Technical implementation uncertainty that stays within frozen behavior must return to Team B contract review; it must not be resolved by silent product invention.

## 32. Open Technical Decisions

No technical decision is intentionally left open for plan generation. The contract fixes aggregate naming, role model, derived readiness, explicit partial adoption, API surface, ordering authority, copy-on-write provenance, concurrency tokens, idempotency race handling, locking order, schema decomposition, safe source locator, and the Rev3 distinction between effect idempotency and historical response snapshot storage. Replay uses existing `idempotency_keys`, never reruns a won mutation, returns current safe authoritative representations, and adds no response-receipt schema.

Implementation may choose internal Python class/function names and pagination encoding only if wire behavior, constraints, and invariants above remain exact.

```text
OPEN_TECHNICAL_DECISION_COUNT = 0
```

## 33. Product Decisions Required, if any

The baseline inventory exposed no unresolved question that changes frozen user-visible behavior. Reliable page geometry is not promised by FD-01–FD-29/PD-30/PD-31; the contract truthfully uses document order rather than inventing pages. Existing submit APIs are isolated from package-owned questions without adding a G-09 review workflow.

```text
PRODUCT_DECISION_REQUIRED_COUNT = 0
CONTRACT_STATUS = CORRECTIVE REVISION 3 — PENDING TEAM B NARROW REVIEW
IMPLEMENTATION_AUTHORIZED = NO
NEXT_STAGE = TEAM B CONTRACT REV3 NARROW REVIEW
```
