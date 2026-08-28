# API Contract: Shenlun V1 Question Persistence

## 1. Status And Scope

This document defines the implementation contract for the first database-backed Shenlun annotation slice. It is framework-neutral. Production scaffolding starts only after gates `G-01` through `G-03` in `plan.md` are approved.

V1 supports only manually confirmed, pure-text Shenlun questions with four content fields and optional reusable source-material links:

- `stem_text`: 题干正文；
- `requirement_text`: 作答要求；
- `question_text`: 问题；
- `reference_answer_text`: 教师参考答案。

`stem_text` contains question-specific text only. A passage shared by multiple questions is stored once as a versioned source material and linked to each exact question version; it must not be copied into every `stem_text`.

V1 does not accept images, editor-specific HTML/JSON, parser-generated questions, A-D options, objective answers, approval-on-create, or bulk automatic import. Rich-editor state is converted to normalized plain text before a request is sent.

## 2. Common Rules

- Base path: `/api/v1`.
- Media type: `application/json; charset=utf-8`.
- IDs are server-generated opaque UUIDs represented as strings.
- Timestamps use ISO 8601 UTC.
- Text preserves meaningful paragraph breaks as `\n`; line endings are normalized to LF at the API boundary.
- The API must not trim internal whitespace, rewrite Chinese punctuation, or silently merge paragraphs.
- The authenticated user supplies no `created_by`, reviewer, approval status, version number, or audit timestamp in request bodies. These values come from server context.
- Every write accepts `client_request_id` for idempotency. Reusing it with a different body returns `409 IDEMPOTENCY_CONFLICT`.
- Idempotency scope is `(actor_id, operation_scope, client_request_id)`. The server checks a matching idempotency record before mutable-state validation; an identical replay does not execute the operation again and returns the current resource representation with `Idempotent-Replay: true`.
- Draft updates use `expected_row_version`. A mismatch returns `409 STALE_DRAFT` and never overwrites the stored draft.
- A parser or AI may propose data only through a future candidate endpoint. It cannot call these endpoints to create an approved or submitted record without a human action.
- Annotators may create, edit, and submit their own drafts. Rejected content is corrected by creating a new version, not by reopening the rejected row. Reviewer/admin permissions are outside this persistence slice.
- Request bodies are limited to 4 MiB. Normalized limits are: `stem_text` and `reference_answer_text` 200,000 Unicode code points each; `requirement_text` and `question_text` 20,000 each; source labels 500; `change_reason` 1,000. The database uses `text`; the API rejects larger values with `413 REQUEST_TOO_LARGE` or `422 VALIDATION_ERROR`.

## 3. Controlled Values

### 3.1 Subject And Type

- `subject`: `shenlun`
- `question_type`: `subjective` (assigned by the server for Shenlun V1)

### 3.2 Shenlun Knowledge Points

The database stores stable codes and mutable display names:

| code | display_name | default_order |
| --- | --- | ---: |
| `shenlun.summary` | 归纳概括 | 1 |
| `shenlun.countermeasure` | 提出对策 | 2 |
| `shenlun.analysis` | 综合分析 | 3 |
| `shenlun.applied_writing` | 应用文写作 | 4 |
| `shenlun.essay` | 大作文 | 5 |

Requests send `knowledge_point_id`, not a display name. `source_topic_label` preserves the source document label and must not create a taxonomy entry.

## 4. Resource Shapes

### 4.1 `QuestionVersionView`

```json
{
  "question_id": "uuid",
  "question_version_id": "uuid",
  "version_number": 1,
  "row_version": 1,
  "status": "draft",
  "paper_version_id": "uuid",
  "subject": "shenlun",
  "question_type": "subjective",
  "knowledge_point_id": "uuid",
  "source_order_index": 1,
  "source_topic_order": 1,
  "source_question_order": 1,
  "source_topic_label": "示例专项",
  "source_material_version_ids": ["uuid"],
  "stem_text": "示例题干正文。",
  "requirement_text": "示例作答要求。",
  "question_text": "示例问题。",
  "reference_answer_text": "示例参考答案。",
  "explanation_text": null,
  "created_at": "2026-08-23T06:00:00Z",
  "updated_at": "2026-08-23T06:00:00Z"
}
```

The example is synthetic and must not be replaced in version-controlled fixtures with private paper text.

`status` belongs to `QuestionVersion`; `Question.status` mirrors the current version for workflow filtering. Historical versions retain their own statuses when a newer draft becomes current.

### 4.2 `ApiError`

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "field_errors": [
    {"field": "source_question_order", "reason": "must be greater than 0"}
  ],
  "request_id": "opaque-request-id"
}
```

## 5. Endpoints

### 5.1 List Shenlun Knowledge Points

`GET /api/v1/knowledge-points?subject=shenlun&status=active`

Returns active controlled values ordered by `default_order`, then stable code. The frontend must bind by `id` and display `name`.

### 5.2 Create Reusable Source Material

`POST /api/v1/paper-versions/{paper_version_id}/source-materials`

```json
{
  "client_request_id": "uuid-generated-by-client",
  "source_order_index": 1,
  "source_label": "材料 1",
  "content_text": "脱敏的共享材料示例。"
}
```

Creates `SourceMaterial` plus version `1` in `draft` status with `row_version = 1`. The source order is scoped to material navigation and does not occupy a `QuestionSlot`. The response is `201 Created` with material ID, material-version ID, status, row version, source metadata, and content text.

`PATCH /api/v1/source-material-versions/{source_material_version_id}` updates only the current draft material version and requires `client_request_id` plus `expected_row_version`. Submitted, approved, rejected, and non-current material versions are immutable.

`POST /api/v1/source-materials/{source_material_id}/versions` creates a correction draft from the current rejected or approved material version. It requires `base_version_id` and `change_reason`. A submitted material version cannot be superseded until the review workflow resolves it.

### 5.3 Create A Draft Question

`POST /api/v1/paper-versions/{paper_version_id}/questions`

Request:

```json
{
  "client_request_id": "uuid-generated-by-client",
  "subject": "shenlun",
  "knowledge_point_id": "uuid",
  "source_order_index": 1,
  "source_topic_order": 1,
  "source_question_order": 1,
  "source_topic_label": "示例专项",
  "source_material_version_ids": ["uuid"],
  "stem_text": "",
  "requirement_text": "示例作答要求。",
  "question_text": "示例问题。",
  "reference_answer_text": "示例参考答案。"
}
```

Server behavior:

1. Verify that the paper version exists and is finalized.
2. Verify that the knowledge point is active and belongs to Shenlun.
3. Validate the source-order tuple and ensure the global `source_order_index` is not assigned to another question slot in the same paper version.
4. Verify that every linked source-material version belongs to the same paper version and is a current `draft`, `submitted`, or `approved` version.
5. In one transaction, create `Question`, `QuestionSlot`, `QuestionVersion`, ordered material links, and an audit event.
6. Set both question and question-version status to `draft`, set `Question.current_version_id`, `QuestionVersion.version_number = 1`, and `row_version = 1`.
7. Return `201 Created` with `QuestionVersionView` and a `Location` header.

This endpoint never creates `QuestionOption`, `ReviewRecord`, `ContentBlock`, or an approved item for Shenlun V1.

### 5.4 List Questions In Source Order

`GET /api/v1/paper-versions/{paper_version_id}/questions`

Optional query parameters:

- `knowledge_point_id`
- `status`
- `cursor`
- `limit` (default `50`, maximum `100`)

The stable order is `source_order_index ASC, question_id ASC`. A specialty view filters by `knowledge_point_id` and displays `source_question_order`; it does not renumber or change the global order.

Response contains items plus an opaque `next_cursor`. Offset pagination is not part of this contract.

The cursor encodes the last `(source_order_index, question_id)` pair. Invalid or mismatched cursors return `422 VALIDATION_ERROR`.

### 5.5 Get The Current Version

`GET /api/v1/questions/{question_id}`

Returns the version referenced by `Question.current_version_id`, including its current `status` and `row_version`.

### 5.6 Update A Draft

`PATCH /api/v1/question-versions/{question_version_id}`

Request fields are optional, but at least one editable field must be present:

```json
{
  "client_request_id": "uuid-generated-by-client",
  "expected_row_version": 3,
  "knowledge_point_id": "uuid",
  "source_order_index": 2,
  "source_topic_order": 1,
  "source_question_order": 2,
  "source_topic_label": "示例专项",
  "source_material_version_ids": ["uuid"],
  "stem_text": "修订后的示例题干。",
  "requirement_text": "修订后的示例要求。",
  "question_text": "修订后的示例问题。",
  "reference_answer_text": "修订后的示例答案。"
}
```

Only the current version of a `draft` question is mutable. The server updates fields and material links and increments `row_version` atomically. If `source_order_index` changes, the service locks and moves the associated `QuestionSlot` in the same transaction after checking the target order; no version/slot mismatch may be committed. `question_id`, `paper_version_id`, `version_number`, `subject`, `question_type`, creator fields, status, and audit fields are not patchable.

Submitted, approved, rejected, archived, or non-current versions return `409 VERSION_IMMUTABLE`.

### 5.7 Submit For Review

`POST /api/v1/question-versions/{question_version_id}/submit`

```json
{
  "client_request_id": "uuid-generated-by-client",
  "expected_row_version": 4
}
```

Submission requires nonblank `requirement_text`, `question_text`, and `reference_answer_text`, plus either nonblank `stem_text` or at least one linked source-material version. It also requires the controlled knowledge point, source-order fields, and a valid source paper version. Empty rich-text shells such as whitespace-only paragraphs count as empty, but stored text is not trimmed or rewritten.

The service locks the question, question version, slot, and linked material versions. Linked draft material versions transition to `submitted`; linked submitted or approved versions remain unchanged; rejected or non-current links fail validation. On success, both question and question-version status become `submitted`, an audit event is recorded, and all transitioned versions become immutable.

### 5.8 Create A New Version For Correction

`POST /api/v1/questions/{question_id}/versions`

```json
{
  "client_request_id": "uuid-generated-by-client",
  "base_version_id": "uuid",
  "change_reason": "人工复核后修订"
}
```

The base must be the current rejected or approved version of the question. The endpoint creates a new draft with `version_number = max + 1` and `row_version = 1`; it copies content, source ordering, and exact material-version links and never mutates the base. `change_reason` is required. A later draft PATCH may correct provenance and material links. A submitted current version cannot be superseded until review resolves it.

If the base is approved, it remains discoverable through its own `QuestionVersion.status = approved` and any release links while the new draft becomes `Question.current_version_id`. `Question.status` mirrors the new current draft and does not erase historical approval.

Approval/rejection endpoints belong to the review slice and are intentionally not defined here. No implementation may invent them while executing this persistence slice.

## 6. Validation Matrix

| Field | Draft create/save | Submit | Rule |
| --- | --- | --- | --- |
| `paper_version_id` | required | required | existing, finalized, immutable source version |
| `knowledge_point_id` | required | required | active Shenlun knowledge point |
| `stem_text` | may be empty | conditionally required | nonblank, or at least one linked material on submit |
| `requirement_text` | may be empty | required | normalized LF, nonblank on submit |
| `question_text` | may be empty | required | normalized LF, nonblank on submit |
| `reference_answer_text` | may be empty | required | normalized LF, nonblank on submit |
| source order fields | required | required | positive integers; label nonblank |
| `source_material_version_ids` | optional | conditionally required | same paper version; exact ordered links; required when stem is blank |
| `explanation_text` | not accepted in V1 UI | optional later | never substituted for reference answer |

Maximum text lengths must be decided from sanitized fixtures before migration implementation. Terra must not invent arbitrary production limits. Until then use PostgreSQL `text` and enforce only request-size limits at infrastructure level.

## 7. Error Semantics

| HTTP | code | Meaning |
| ---: | --- | --- |
| 400 | `INVALID_JSON` | malformed request |
| 401 | `UNAUTHENTICATED` | no valid user context |
| 403 | `FORBIDDEN` | role cannot perform action |
| 404 | `PAPER_VERSION_NOT_FOUND` | source version missing |
| 404 | `QUESTION_NOT_FOUND` | question/version missing |
| 409 | `SOURCE_ORDER_CONFLICT` | global source order already used by another slot |
| 409 | `STALE_DRAFT` | optimistic lock mismatch |
| 409 | `VERSION_IMMUTABLE` | attempted mutation of a locked version |
| 409 | `IDEMPOTENCY_CONFLICT` | request ID reused with a different payload |
| 409 | `MATERIAL_VERSION_IMMUTABLE` | attempted mutation of a locked material version |
| 409 | `MATERIAL_LINK_CONFLICT` | linked material is rejected, non-current, or belongs to another paper version |
| 422 | `VALIDATION_ERROR` | field/domain validation failed |
| 413 | `REQUEST_TOO_LARGE` | body exceeds the approved request limit |

API logs may contain IDs, status, latency, error codes, and field names. They must not log complete stem, requirement, question, reference answer, source document text, credentials, or tokens.

## 8. Required Contract Tests

- Create one valid draft and verify all four fields and source-order fields round-trip exactly.
- Create one reusable material, link it to two question drafts, and verify the material text is stored once while both question versions reference the same material-version ID.
- Retry an identical create with the same `client_request_id` and verify that no duplicate records are created.
- Reuse a request ID with a changed payload and receive `IDEMPOTENCY_CONFLICT`.
- Reject a knowledge point from another subject.
- Reject duplicate `source_order_index` in one paper version while allowing the same index in another paper version.
- Save a draft with the expected row version and verify the counter increments.
- Send two updates with the same expected row version and verify one receives `STALE_DRAFT`.
- Reject submission when requirement, question, or reference answer is blank; allow blank stem only when a valid material version is linked.
- Submit a complete draft and reject later PATCH with `VERSION_IMMUTABLE`.
- Move a draft to another source order and verify the question slot moves atomically; force a conflict and verify neither row changes.
- Submit a question linked to a draft material and verify both versions transition atomically to submitted.
- Create a correction version and verify the old version remains byte-for-byte unchanged.
- Verify no Shenlun V1 operation creates option rows or accepts editor-specific HTML as authoritative content.

## 9. Implementation Gate

Terra may implement this contract only after `G-01` through `G-03` in `plan.md` are approved. If the selected framework changes, endpoint semantics, validation, versioning, and transaction boundaries remain unchanged; only framework-specific code and migration commands may differ.
