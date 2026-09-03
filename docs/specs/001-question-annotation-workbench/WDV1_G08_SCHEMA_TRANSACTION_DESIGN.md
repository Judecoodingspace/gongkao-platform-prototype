# WDV1-003 / G-08 Schema + Transaction Design

**STATUS = PENDING IMPLEMENTATION REVIEW.** This is a schema and transaction design for the already-approved WDV1-003 contract. It neither creates nor approves a migration, ORM model, parser, API, worker, storage-read implementation, or PostgreSQL change. `WDV1-003 IMPLEMENTATION = NOT STARTED` and `G-08 = IN PROGRESS` remain unchanged.

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
| NICE TO HAVE | an index on `(paper_version_id, created_at)` and a composite uniqueness target `(id, paper_version_id)` | Supports history reads and lets ActiveSelection prove that its target belongs to the same `PaperVersion`. |
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

**Purpose:** an immutable, usable, natural-paragraph text block belonging to exactly one specific terminal processing result.

| Classification | Fields | Reason |
| --- | --- | --- |
| MUST HAVE | `id`, `processing_result_id`, `source_order`, `block_type`, `text_original` | Identifies the particular result, preserves globally stable main-body order, and preserves authoritative original paragraph text. Empty paragraphs are represented by non-null empty `text_original`. |
| NICE TO HAVE | unique `(processing_result_id, source_order)` and a positive `source_order` check | Makes each result's ordered collection deterministic and rejects malformed order. |
| DO NOT STORE | `paper_version_id`, page number, bbox, `created_at`, normalized text, business role/taxonomy, asset/image/table payload | `paper_version_id` is derivable through the result; page/bbox are unavailable in T1; a per-block timestamp adds no immutable provenance; the rest is out of scope or forbidden. |

For WDV1-003, `block_type` is constrained to `text`; non-text structures are gaps rather than placeholder text/image/table blocks. A later, separately reviewed WDV1-004 migration may extend that vocabulary without redefining this text-first history.

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
| NICE TO HAVE | `paper_version_id` as primary key; unique `processing_result_id`; composite FK `(processing_result_id, paper_version_id)` to `SourceProcessingResult` | Ensures at most one active selection, prevents cross-paper targets, and makes selection lookup simple. |
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

## 6. Idempotency model

The existing `idempotency_keys` pattern is sufficient and should be reused rather than duplicating a request key on `SourceProcessingResult`.

```text
operation_scope = source_processing:trigger
uniqueness      = (actor_id, operation_scope, client_request_id)
request_hash    = canonical PaperVersion identity + parser name/version + canonical parser config
result target   = SourceProcessingResult.id
```

- The key is scoped to the triggering actor and processing operation, as in the existing API baseline, not merely to a `PaperVersion`.
- First use creates the idempotency reservation and one processing-result identity atomically.
- A retry with the same key and equal request hash locks the key and returns that same result, whether it is still `processing` or terminal.
- Reuse of the same key with a different `PaperVersion`, parser identity, or canonical configuration has a different request hash and is an idempotency conflict; it never silently retargets the result.
- A new explicit human action must use a new key and therefore creates a new independent result, even for identical DOCX bytes and configuration.

This describes data sufficiency only; it does not choose an HTTP header, response status, URL, or retry payload.

## 7. Key constraints by enforcement layer

### Database-enforced

- UUID primary keys; NOT NULL identities and timestamps where stated.
- `PaperVersion → SourceProcessingResult`, `SourceProcessingResult → DocumentBlock`, `SourceProcessingResult → SourceProcessingGap`, and selection references all use `ON DELETE RESTRICT`.
- Result status check: only `success`, `partial`, `failed`; lifecycle consistency check between `execution_state`, `result_status`, and `completed_at`.
- `DocumentBlock` and `SourceProcessingGap` order values are positive; block `source_order` is unique within a result.
- `PaperVersionActiveProcessing.paper_version_id` is primary key/unique, enforcing at most one active selection per `PaperVersion`.
- Composite selection FK proves the selected result belongs to its `PaperVersion`; a unique target prevents one result from being selected twice.
- Existing `idempotency_keys` uniqueness and request-hash checks continue to protect retry identity.

### Service / transaction-enforced

- Only finalized DOCX versions may be processed; bytes are read through the future provider-neutral read-only storage abstraction and hash-reverified before terminal persistence.
- Only `success` may obtain automatic initial activation; `partial` only through an explicit audited activation; `failed` is never selectable.
- A later `success` or `partial` never replaces any existing active selection automatically.
- Terminal result metadata, blocks, gaps, audit event, and any initial active selection commit atomically. A DB failure leaves no terminal `success`/`partial` with partial children.
- Explicit activation locks and validates the candidate result, target `PaperVersion`, and current selection before one atomic pointer update.
- Terminal rows and child evidence are never patched/deleted; a correction is a new result. Failed diagnostic fragments are not exposed through normal ordered-block reads.

### Parser-enforced

- Direct OOXML traversal is the only source of natural paragraph order/identity.
- Natural paragraphs become text blocks without semantic split/merge/reorder; visual line breaks do not create blocks.
- Known unsupported structures become explicit gaps; unknown main-body structures cannot silently produce `success`.
- Page/bbox is unavailable in WDV1-003 and is never manufactured.

## 8. Transaction design

### 8.1 Intent reservation and terminalization

1. In a short transaction, lock the existing idempotency key if present. If it is a matching replay, return its result. Otherwise validate the finalized `PaperVersion`, create the idempotency key and a `processing` `SourceProcessingResult` identity together, and commit the reservation.
2. Read source bytes through the future read-only storage boundary, recompute SHA-256, and run T1 outside the final database transaction. No source content enters logs or the database beyond permitted block text in a terminal usable result.
3. In one terminal transaction, lock the `PaperVersion` row (`SELECT … FOR UPDATE`) before reading/updating its selection; lock the reserved result; insert all blocks and gaps; set the terminal status/metadata; append the safe audit event; and, only for initial `success`, insert the active selection if absent. Commit once.

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
SCHEMA + TRANSACTION DESIGN = READY FOR REVIEW

IMPLEMENTATION CODE
= NOT STARTED
```
