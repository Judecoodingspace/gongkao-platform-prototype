# WDV1-003 / G-08 Schema + Transaction Design

**STATUS = APPROVED（migration + ORM implementation 授权）。** This schema and transaction design is approved for the strictly limited WDV1-003 Alembic migration, SQLAlchemy ORM mapping, and PostgreSQL 16 schema/integrity-test phase. It does not mean WDV1-003 is complete, and it does not authorize a parser, storage reader, processing service, worker, API, OpenAPI, React, or G-08 completion.

**Authority read for this design:** platform `main@12b55c0e539f67adbd919d349a1bbc2412b048b8`, especially the frozen G-06/G-08 decisions, approved WDV1-003 contract, T1 technical choice, and technical precheck. The API comparison baseline is `main@8fbe0a6fa9a2ed96993a220ed6d65526cd703b66`.

## 1. Design scope and fixed interpretation

- A finalized `PaperVersion` and its raw DOCX bytes remain immutable source evidence. No design below writes its bytes, hash, storage reference, upload status, identity, or legacy `parser_*` fields.
- Each explicit processing intent owns one independent processing result. A terminal result, its blocks, gaps, parser metadata, and diagnostics are immutable historical evidence.
- T1 is the only authoritative structure source: direct traversal of `word/document.xml → w:body`. `python-docx` cannot create a second source truth.
- WDV1-003 handles only main-body natural paragraph text. Tables, drawings/images, OMML, text boxes, embedded objects, and unknown main-body structures are fail-visible gaps, not business meanings and not silent omissions.
- The design is for PostgreSQL 16. It deliberately uses ordinary foreign keys, unique constraints, checks, and row locking; it needs neither triggers nor stored procedures.

## 2. Proposed entities

### 2.1 `SourceProcessingResult`

**Purpose:** represents one explicit processing intent for one immutable `PaperVersion`; after it reaches a terminal result it is the immutable parent of its usable blocks and gap evidence.

| Classification | Fields | Reason |
| --- | --- | --- |
| MUST HAVE | `id`, `paper_version_id`, `execution_state`, `result_status`, `parser_name`, `parser_version`, `parser_config`, `verified_source_hash`, `runtime_fingerprint`, `triggered_by`, `created_at`, `completed_at` | Identifies the specific historical run, its immutable source and reproducibility inputs, who asked for it, and whether a terminal source-structuring result exists. |
| MUST HAVE | `diagnostic_code`, `diagnostic_metadata` | Safe machine-readable terminal failure/integrity diagnostics; metadata is bounded and cannot contain source text, paths, raw XML, bytes, credentials, or arbitrary traceback bodies. |
| MUST HAVE | candidate key `UNIQUE (paper_version_id, id)` | Required PostgreSQL referenced candidate key for the ActiveSelection composite foreign key; it proves that a selected result belongs to the same `PaperVersion`. |
| NICE TO HAVE | an index on `(paper_version_id, created_at)` | Supports history reads. |
| DO NOT STORE | raw DOCX, `storage_uri`, absolute path, full parser output, raw XML, business labels, confidence score, duplicate `client_request_id`, page/bbox, `PaperVersion.parser_*` values | These either violate the private-source boundary, create a second source truth, invent unavailable coordinates, or belong elsewhere. |

`execution_state` is deliberately separate from D6's terminal source-structuring status:

```text
execution_state: processing | completed
result_status:   NULL while processing; success | partial | failed when completed
```

This is the minimum lifecycle needed to reserve one idempotent intent before work begins. It is not a fourth source-structuring status. A database check must require a `completed_at` and one of the three terminal values exactly when `execution_state = completed`, and require both to be absent while it is `processing`. Only the transition into `completed` plus the terminal snapshot is mutable; once terminal, the result and its children are read-only.

`verified_source_hash` is intentionally retained despite matching immutable `PaperVersion.file_hash` on successful verification. It is the immutable, run-specific assertion that this result used the checked bytes, not merely a later join to a source record. It is required for terminal `success`/`partial`; an integrity-mismatch `failed` result records the verification outcome and safe diagnostic code, but does not make the mismatched actual hash look like accepted provenance.

`runtime_fingerprint` is a small JSONB object, not `pip freeze`: Python runtime version, the Direct-OOXML implementation version, and versions of any library that actually affects this route. `parser_config` is a canonicalized JSONB object. Neither is an unbounded diagnostic dump.

### 2.2 `DocumentBlock`

**Purpose:** an immutable, usable, natural-paragraph text block belonging to exactly one specific terminal `success` or `partial` processing result.

| Classification | Fields | Reason |
| --- | --- | --- |
| MUST HAVE | `id`, `processing_result_id`, `source_order`, `block_type`, `text_original` | Identifies the particular result, preserves globally stable main-body order, and preserves authoritative original paragraph text. Empty paragraphs are represented by non-null empty `text_original`. |
| NICE TO HAVE | unique `(processing_result_id, source_order)` and a positive `source_order` check | Makes each result's ordered collection deterministic and rejects malformed order. |
| DO NOT STORE | `paper_version_id`, page number, bbox, `created_at`, normalized text, business role/taxonomy, asset/image/table payload | `paper_version_id` is derivable through the result; page/bbox are unavailable in T1; a per-block timestamp adds no immutable provenance; the rest is out of scope or forbidden. |

For WDV1-003, `block_type` is constrained to `text`; non-text structures are gaps rather than placeholder text/image/table blocks. A `failed` result persists no usable `DocumentBlock` rows at all. A later, separately reviewed WDV1-004 migration may extend that vocabulary without redefining this text-first history.

### 2.3 `SourceProcessingGap`

**Purpose:** immutable evidence that known unsupported or unknown main-body structure existed at a reliable source-order vicinity. A gap proves a limitation; it does not explain business meaning.

| Classification | Fields | Reason |
| --- | --- | --- |
| MUST HAVE | `id`, `processing_result_id`, `gap_type`, `source_order`, `source_region_kind`, `diagnostic_code` | Supports multiple gaps, identifies known/unknown structure, and records a reliable body-child or within-paragraph vicinity without pretending to have a page/bbox. |
| MUST HAVE when reliably available | `before_block_source_order`, `after_block_source_order` | Gives a readable `between block A and B` location. Either may be null at document boundaries or for an inline gap. |
| NICE TO HAVE | positive checks on all present order values; result/order index for read performance | Protects reliable ordering and active-partial reads. |
| DO NOT STORE | business semantics, AI confidence, raw XML, extracted image/asset, page/bbox, arbitrary parser traceback/text | They are either forbidden inference, WDV1-004 work, unavailable geometry, or unsafe private diagnostics. |

`source_order` is the reliable main-body structural position; an inline unsupported structure may share the containing paragraph's order and is distinguished by `source_region_kind = within_paragraph`. It is not fabricated visual coordinate data. `gap_type` is a small controlled vocabulary such as `table`, `drawing`, `omml`, `textbox`, `embedded_object`, or `unknown`.

### 2.4 `PaperVersionActiveProcessing`

**Purpose:** the one mutable operational selection of the processing result currently offered as active for a `PaperVersion`. It is not source evidence and it is not a quality status.

| Classification | Fields | Reason |
| --- | --- | --- |
| MUST HAVE | `paper_version_id`, `processing_result_id`, `selected_at`, `selected_by` | One pointer per source version, its selected target, and minimum auditable selection metadata. |
| MUST HAVE | `paper_version_id` as primary key; composite FK `(paper_version_id, processing_result_id)` to `SourceProcessingResult(paper_version_id, id)` | Ensures at most one active selection and prevents cross-paper targets through a PostgreSQL-enforced same-source relationship. |
| DO NOT STORE | `active` boolean, copied result status, copied parser metadata, copied gaps, history snapshots | A row's presence is the active state; all copied fields would drift from immutable result truth. Selection change history belongs in append-only audit events. |

## 3. Gap-model decision

| Option | Assessment |
| --- | --- |
| A — result JSONB | Too weak for multiple ordered gaps, explicit active-partial reads, relational immutability, and future visual vicinity linking. It also encourages mixing structured evidence with arbitrary diagnostics. |
| B — separate `SourceProcessingGap` entity | Represents many immutable, ordered, queryable gaps without declaring them usable blocks or visual assets. |

```text
GAP MODEL = SEPARATE_GAP_ENTITY
```

## 4. Active-model decision

| Option | Assessment |
| --- | --- |
| A — mutable `active_processing_result_id` on `PaperVersion` | Smallest column count, but mixes a mutable operational pointer into immutable-source evidence and makes its audit boundary less clear. |
| B — separate `PaperVersionActiveProcessing` entity | Keeps immutable source fields untouched, models one mutable relationship directly, supports atomic insert/update, and reuses append-only audit events for history. |

```text
ACTIVE MODEL = SEPARATE_SELECTION_ENTITY
```

The model does not claim that every column on `PaperVersion` is metaphysically immutable; it deliberately separates immutable source evidence from the mutable processing-selection concern.

## 5. Relationship model

```text
Paper
  │
  ▼
PaperVersion (immutable source evidence)
  │ 1
  ├───────────────────────────────────┐
  ▼                                   ▼
SourceProcessingResult #1          SourceProcessingResult #2
  │ 1                                 │ 1
  ├── DocumentBlock [ordered]         ├── DocumentBlock [ordered]
  └── SourceProcessingGap [ordered]   └── SourceProcessingGap [ordered]

PaperVersion
  │ 0..1
  ▼
PaperVersionActiveProcessing ─────────► one SourceProcessingResult
             (mutable pointer; target must belong to this PaperVersion)
```

## 6. Idempotency model and reservation lifecycle

The existing `idempotency_keys` table must be reused rather than creating a parallel idempotency system. Its current uniqueness scope is sufficient, but its required non-null `result_resource_type`, `result_resource_id`, and `result_http_status` mean it is presently a completed-response cache and cannot be treated as though it already models an in-progress reservation.

```text
operation_scope = source_processing:trigger
uniqueness      = (actor_id, operation_scope, client_request_id)
request_hash    = canonical PaperVersion identity + parser name/version + canonical parser config
result target   = SourceProcessingResult.id
```

- The key is scoped to the triggering actor and processing operation, as in the existing API baseline, not merely to a `PaperVersion`.
- First use creates the idempotency reservation and one processing-result identity atomically.
- A retry with the same key and equal request hash locks the key and returns that same result, whether it is still `processing` or terminal; it does not start a second parser execution.
- Reuse of the same key with a different `PaperVersion`, parser identity, or canonical configuration has a different request hash and is an idempotency conflict; it never silently retargets the result.
- A new explicit human action must use a new key and therefore creates a new independent result, even for identical DOCX bytes and configuration.

**Recommended compatibility strategy: in-place reservation metadata.** For the processing-trigger scope, Transaction A writes the existing non-null idempotency fields immediately: resource type `source_processing_result`, the reserved result ID, and one fixed, documented accepted/in-progress response meaning. Thus a retry can legally point to a real result even before it is terminal. Transaction B may update only the idempotency response-cache metadata to the terminal response meaning together with result finalization. This limited cache-metadata update does not modify the immutable processing result or its evidence.

The future minimal API contract must choose the actual accepted/in-progress response semantics before migration implementation, but this design deliberately does not choose an HTTP number, header, URL, or payload. If that contract cannot safely use one fixed accepted/in-progress meaning and a later terminal cache update, the approved migration must make a small additive extension of the existing `idempotency_keys` response-state metadata; it must not introduce a separate idempotency system.

## 7. Key constraints by enforcement layer

### Database-enforced

- UUID primary keys; NOT NULL identities and timestamps where stated.
- `SourceProcessingResult` has PK `(id)` and candidate key `UNIQUE (paper_version_id, id)`; `PaperVersion → SourceProcessingResult`, `SourceProcessingResult → DocumentBlock`, `SourceProcessingResult → SourceProcessingGap`, and selection references all use `ON DELETE RESTRICT`.
- Result status check: only `success`, `partial`, `failed`; lifecycle consistency check between `execution_state`, `result_status`, and `completed_at`.
- `DocumentBlock` and `SourceProcessingGap` order values are positive; block `source_order` is unique within a result.
- `PaperVersionActiveProcessing.paper_version_id` is its PK; its composite FK `(paper_version_id, processing_result_id)` references `SourceProcessingResult(paper_version_id, id)`. This rejects a cross-PaperVersion active target and enforces at most one selection row per PaperVersion without an unnecessary `UNIQUE(processing_result_id)`.
- Existing `idempotency_keys` uniqueness and request-hash checks continue to protect retry identity; its response cache must use the reservation compatibility strategy above.

### Service / transaction-enforced

- Only finalized DOCX versions may be processed; bytes are read through the future provider-neutral read-only storage abstraction and hash-reverified before terminal persistence.
- Only `success` may obtain automatic initial activation; `partial` only through an explicit audited activation; `failed` is never selectable.
- A later `success` or `partial` never replaces any existing active selection automatically.
- Reservation and terminalization are two short transactions with parser execution outside either database transaction. Terminal `success`/`partial` metadata, blocks, gaps, audit event, and any initial active selection commit atomically. A DB failure leaves no terminal `success`/`partial` with partial children.
- Explicit activation locks and validates the candidate result, target `PaperVersion`, and current selection before one atomic pointer update.
- Terminal rows and child evidence are never patched/deleted; a correction is a new result. A `failed` result persists no usable `DocumentBlock`; safe failed diagnostics are never exposed through normal ordered-block reads.

### Parser-enforced

- Direct OOXML traversal is the only source of natural paragraph order/identity.
- Natural paragraphs become text blocks without semantic split/merge/reorder; visual line breaks do not create blocks.
- Known unsupported structures become explicit gaps; unknown main-body structures cannot silently produce `success`.
- Page/bbox is unavailable in WDV1-003 and is never manufactured.

## 8. Transaction design

### 8.1 Intent reservation and terminalization

**Transaction A — reserve the processing intent.** In a short transaction, lock the existing idempotency key if present. A matching replay returns its referenced result identity/state. Otherwise validate the finalized `PaperVersion`; create `SourceProcessingResult(execution_state = processing, result_status = NULL)`; bind the idempotency key immediately to that real result using the documented non-null accepted/in-progress response-cache metadata; and commit. A retry that finds this reservation returns it and must not launch a second parser.

**Parser phase — outside a database transaction.** Read source bytes through the future provider-neutral read-only storage boundary, recompute SHA-256, and run T1 Direct OOXML parsing. It yields either safe terminal diagnostics or candidate usable blocks/gaps and terminal status. No source content enters logs or the database beyond permitted text blocks of a terminal `success`/`partial` result.

**Transaction B — finalize the reserved result.** Lock the reserved result and its `PaperVersion` row (`SELECT … FOR UPDATE`) before reading/updating selection state. For `success`/`partial`, insert the complete blocks and gaps; for `failed`, insert no usable blocks and retain only permitted safe diagnostic/parser/runtime/source-verification metadata. Set `execution_state = completed`, set the terminal `result_status`, set `completed_at`, append the safe audit event, update idempotency response-cache metadata if required, and only for an initial `success` insert active selection if absent. Commit once.

The parent-row lock serializes competing first-success terminalizations. It is necessary even though the selection table has a one-row structural invariant: two transactions cannot both observe and insert an absent selection while holding the same `PaperVersion` lock.

### 8.2 Explicit active switch

Within one transaction: lock the target `PaperVersion`; lock its active-selection row if present; lock and validate the candidate result belongs to that version and is terminal `success` or `partial`; then insert or update the single selection row and append an audit event. It never changes candidate status, historical results, blocks, gaps, or parser metadata. PostgreSQL MVCC makes the pointer change visible atomically, with no committed two-active or no-active intermediate state.

## 9. Transaction scenarios

| Scenario | Result | Why |
| --- | --- | --- |
| 1 — first success | PASS | Terminal snapshot and initial selection are committed together while the `PaperVersion` row is locked. |
| 2 — first partial | PASS | Terminal partial commits inactive; a later explicit audited selection can point to it without changing its status. |
| 3 — active success + new success | PASS | Parent lock sees an existing selection; new result commits immutable and inactive. |
| 4 — active partial + new success | PASS | Existing selection of any eligible status blocks automatic replacement; new success remains inactive. |
| 5 — failed | PASS | Service rejects activation; `failed` is terminal diagnostic history only. |
| 6 — retry | PASS | Existing actor/scope/client-request key locks to the same result; a changed request hash conflicts. |
| 7 — concurrent first success | PASS | `PaperVersion FOR UPDATE` serializes terminalization; the first inserts selection, the second sees it and stays inactive. |
| 8 — transaction failure during block write | PASS | The terminal transaction rolls back blocks, gaps, terminal state, audit, and selection together; no usable half-result is committed. |
| 9 — retry during processing | PASS | The reservation's existing idempotency key returns the same `processing` result; no second result or parser work begins. |
| 10 — cross-Paper active FK attempt | PASS | The composite FK to `(paper_version_id, id)` rejects a selection whose result belongs to another PaperVersion. |

## 10. Legacy `PaperVersion.parser_*` fields

```text
PaperVersion.parser_*
WDV1-003 write: NO
drop now: NO
repurpose: NO
future cleanup candidate: YES
```

They remain untouched compatibility/legacy candidates. Specific processing metadata belongs only to `SourceProcessingResult`; any cleanup requires a later separately approved migration review.

## 11. JSONB boundary

**JSONB:** canonical `parser_config`; bounded `runtime_fingerprint`; bounded safe `diagnostic_metadata`.

**Strong typed columns:** IDs/FKs, `execution_state`, terminal `result_status`, hash, parser name/version, order indices, block type, gap type, diagnostic code, idempotency identity, timestamps, and active relationship. The model must not collapse ordered blocks, gaps, lifecycle, or active selection into JSONB.

## 12. Migration implications (no migration is created here)

The next approved implementation stage would need additive PostgreSQL 16 concepts for:

1. processing-result history with minimal lifecycle/terminal metadata;
2. result-scoped ordered text blocks;
3. result-scoped immutable gap evidence;
4. one mutable active-selection relationship per `PaperVersion` with same-source integrity; and
5. indexes/checks/FKs described above, plus integration with the existing generic idempotency and audit mechanisms.

It must not drop, rename, repurpose, or backfill `PaperVersion.parser_*`; alter raw DOCX storage; add `SourceSpan`; or use cascade delete.

## 13. Remaining questions and risks

```text
PRODUCT QUESTIONS = NONE
```

Implementation risks to resolve through tests, without changing frozen semantics:

- The future storage abstraction needs a provider-neutral read capability that verifies bytes without exposing `storage_uri` or local paths.
- A controlled policy is required for safely recovering an abandoned `processing` reservation after infrastructure interruption; it must not create a second result for the same idempotency key or silently expose partial blocks.
- PostgreSQL 16 integration tests must prove row-lock behavior for concurrent initial successes, selection integrity, idempotency conflict/replay, and rollback of a failed terminal transaction.
- Synthetic fixtures must cover ordinary/empty paragraphs, visible hyperlinks, tabs/manual breaks, table, drawing/image, OMML, textbox/drawing text, and unknown main-body structures, without expanding WDV1-003 into preview or full Word research.

## 14. Review gate

```text
SCHEMA + TRANSACTION DESIGN = APPROVED

IMPLEMENTATION CODE
= NOT STARTED
```
