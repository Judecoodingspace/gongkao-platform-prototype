# WDV1 Processing API — Idempotency Response Semantics

```text
STATUS =
APPROVED
(TEAM B PROCESSING API IDEMPOTENCY RESPONSE SEMANTICS RE-REVIEW #2 PASS)

API IDEMPOTENCY RESPONSE SEMANTICS =
APPROVED

PROCESSING SERVICE IMPLEMENTATION = NOT AUTHORIZED
PROCESSING API IMPLEMENTATION = NOT AUTHORIZED
IMPLEMENTATION AUTHORIZED = NO
IMPLEMENTATION STARTED = NO
```

---

## 1. Scope and authorities

This document closes the numeric/API semantic prerequisite intentionally deferred by the Processing Service authorities. It freezes only the idempotency response semantics needed for:

- `source_processing:trigger`
- `source_processing.activate`

It does **not** design full routes, OpenAPI schemas, frontend behavior, auth, pagination, worker/queue infrastructure, or new DB state.

### Authorities

```text
Frozen Decisions authority =
1f5e0ea23a235f23193d7821fff4bde8be7a7473

Processing Service Implementation Contract authority =
99433c824efd36ce515742642199a9e50c701e90

Processing Service Implementation Plan authority =
db8acfe38d70e12d2b04ca6a1457d31772c1cf67

API baseline =
Judecoodingspace/gongkao-question-bank-api
main@85e20755f6069a4446f67417e2eff323b6a41674

Historical Plan authority (superseded) =
e197b1371c58408fab2572dc7d434fbbbf5ffd4b
```

This document does **not** change Frozen Decisions, the Processing Service Contract, or the Implementation Plan. It only closes the numeric/API semantic prerequisite those authorities deferred.

---

## 2. Actual code facts inspected

From `src/gongkao_api/modules/idempotency/models.py`:

```text
IdempotencyKey.result_http_status
= NOT NULL SmallInteger

IdempotencyKey.result_row_version
= nullable Integer

unique key =
(actor_id, operation_scope, client_request_id)
```

From `src/gongkao_api/modules/idempotency/repository.py`:

```text
request_hash(value: object) -> str
canonical JSON + SHA-256

lock_by_scope(actor_id, operation_scope, client_request_id) -> IdempotencyKey | None
add(...) -> IdempotencyKey
```

From `src/gongkao_api/api/errors.py`:

```text
IDEMPOTENCY_CONFLICT = HTTP 409
```

From `src/gongkao_api/modules/source_materials/service.py`:

```text
existing pattern:
- accepted successful action creates idempotency binding
- pre-accept DomainRuleViolation does not create a key
- same-key different-hash raises IDEMPOTENCY_CONFLICT
```

Confirmed: no Processing API route exists at API baseline `85e2075`.

---

## 3. Frozen semantics

### D1 — Durable accepted / in-progress idempotency state

For `operation_scope = source_processing:trigger`:

```text
STORED_RESULT_HTTP_STATUS_WHILE_PROCESSING = 202
```

When Transaction A accepts a new processing intent, it creates durable idempotency metadata:

```text
result_resource_type = source_processing_result
result_resource_id     = <reserved result id>
result_http_status     = 202
result_row_version     = NULL
```

Meaning: accepted and durable, but not terminal.

This `202` is the **stored idempotency status** while `execution_state='processing'`. It is NOT a separate HTTP return boundary for the initiating synchronous trigger call.

Canonical Plan orchestration is synchronous and single-call:

```text
Transaction A commit
→ _execute_processing(context)
→ _terminalize(context, outcome)
→ return _to_trigger_result(...)
```

Therefore:

```text
INITIATING_SYNCHRONOUS_TRIGGER_DOES_NOT_RETURN_AT_TRANSACTION_A_BOUNDARY = YES
```

For a normal run that reaches a durable terminal result:

```text
INITIATING_SYNCHRONOUS_TRIGGER_TERMINAL_SUCCESS_HTTP_STATUS = 200
INITIATING_SYNCHRONOUS_TRIGGER_TERMINAL_PARTIAL_HTTP_STATUS = 200
INITIATING_SYNCHRONOUS_TRIGGER_TERMINAL_FAILED_HTTP_STATUS  = 200
```

The stored `202` is used for:

- same-key replay while still processing;
- the durable idempotency state after a Transaction B infrastructure failure (the reservation remains `processing`).

### D2 — Same-intent replay while processing

Same key + same hash + result still `processing`:

```text
HTTP                = 202
same processing_result_id
replayed            = true
parser rerun        = NO
new result          = NO
```

The replay reconstructs the response from the current `Processing Result`. The idempotency table stores no serialized response body.

### D3 — Trigger terminal

After Transaction B commits:

```text
execution_state = completed
result_status   ∈ {success, partial, failed}

TRIGGER_TERMINAL_HTTP_STATUS = 200
```

The same idempotency key is updated:

```text
result_http_status: 202 → 200
result_resource_id: unchanged
```

Freeze:

```text
success → HTTP 200
partial → HTTP 200
failed  → HTTP 200
```

A durable terminal `failed` result is a completed domain outcome, not automatically a transport failure.

### D4 — Terminal replay

Same key + same hash after terminalization:

```text
HTTP       = 200
same result
replayed   = true
parser rerun = NO
```

### D5 — Transaction B infrastructure failure

If terminal snapshot persistence fails:

```text
Transaction B rollback
reservation remains processing
```

Freeze:

```text
DO NOT cache 500
DO NOT change key to terminal
DO NOT fabricate failed result

existing key remains:
result_http_status = 202
result_resource_id = original reservation
```

Same-key replay still returns that original result. Stale/interrupted classification is derived and does not change ownership.

### D6 — Persisted processing failures

For safely persisted:

```text
SOURCE_READ_FAILURE
SOURCE_INTEGRITY_FAILURE
DOCUMENT_PARSE_FAILURE
INTERNAL_PROCESSING_FAILURE
```

freeze:

```text
result_status = failed
HTTP          = 200
```

Do not map these durable result outcomes to cached 4xx/5xx.

### D7 — Same key, different request hash

Freeze existing:

```text
IDEMPOTENCY_CONFLICT = HTTP 409
```

Behavior:

```text
no new result
no parser
no key overwrite
no result-resource reassignment
```

### D8 — Pre-accept rejection

For target-not-found, not-finalized, other pre-accept domain/validation rejection, and same-key hash conflict:

```text
NO new Processing Result
NO accepted audit
NO new idempotency result binding
```

Auth/authentication behavior is out of scope for this semantics closure.

Do not invent cached `result_http_status` for rejected requests.

Generic pre-accept rejection HTTP status:

```text
PRE_ACCEPT_GENERIC_HTTP_STATUS =
NOT_FROZEN_BY_THIS_CLOSURE
```

The only concrete error HTTP status already frozen in this closure is:

```text
IDEMPOTENCY_CONFLICT = HTTP 409
```

### D9 — Same PaperVersion normal-run admission redirect

Approved Plan semantics:

```text
different new intent
+ same PaperVersion
+ normal in-progress result
→ no second result
→ redirected = true to existing result
```

Freeze:

```text
ADMISSION_REDIRECT_HTTP_STATUS = 202

processing_result_id = existing result
execution_state      = processing
redirected           = true
replayed             = false
```

The new intent is **not** formally accepted as a new Processing Result, therefore:

```text
ADMISSION_REDIRECT_CREATES_NEW_IDEMPOTENCY_KEY = NO
```

A later retry after the blocking run terminalizes may be evaluated anew because the earlier redirected request was never accepted.

### D10 — Successful explicit activation

For:

```text
operation_scope = source_processing.activate
```

Activation is synchronous and has no durable in-progress state.

Freeze:

```text
ACTIVATE_TERMINAL_HTTP_STATUS = 200

result_resource_type = source_processing_result
result_resource_id   = <activated result id>
result_http_status   = 200
result_row_version   = NULL
```

Same-key same-hash replay:

```text
HTTP     = 200
previously successful activation target
(current active pointer may have changed)
no duplicate activation mutation
no duplicate active_changed audit
return / reconstruct originally bound ProcessingResultView
```

Freeze:

```text
ACTIVATION_REPLAY_REPLAYED_RESPONSE_FIELD_REQUIRED = NO
ACTIVATION_REPLAY_REAPPLIES_MUTATION = NO
ACTIVATION_REPLAY_DUPLICATE_AUDIT = NO
ACTIVATION_REPLAY_RETURNS_ORIGINALLY_BOUND_RESULT = YES
ACTIVATION_REPLAY_TARGET_MUST_STILL_BE_ACTIVE = NO
```

### D11 — Activation rejection / rollback

For not-found, cross-PaperVersion, non-terminal, failed, or other activation validation failure:

```text
no durable successful activation idempotency binding
```

The canonical Plan requires the outer transaction to roll back the pre-bound key together with the failed validation/mutation.

Generic activation rejection HTTP status:

```text
ACTIVATION_REJECTION_GENERIC_HTTP_STATUS =
NOT_FROZEN_BY_THIS_CLOSURE
```

Same-key different-hash conflict remains:

```text
IDEMPOTENCY_CONFLICT = HTTP 409
```

---

## 4. `result_row_version`

Freeze:

```text
TRIGGER_RESULT_ROW_VERSION = NULL
ACTIVATE_RESULT_ROW_VERSION = NULL
```

Do not invent Processing Result row-version semantics in the idempotency layer.

---

## 5. Replay reconstruction rule

```text
IdempotencyKey does NOT store a serialized response body.
```

Replay path:

```text
key
→ result_resource_id
→ current Processing Result read
→ response reconstruction
```

For trigger, the referenced result may evolve:

```text
processing → terminal
```

Therefore this metadata transition is intentional:

```text
result_http_status:
202 → 200
```

while `result_resource_id` remains immutable.

---

## 6. Authoritative response matrix

| #  | Operation | Situation                                | Domain state                                                                      | Accepted as new intent/action? | Durable idempotency binding?                    | Stored result_http_status | Resource identity behavior                  | Parser / mutation replay?                  | HTTP                                                        |
| -- | --------- | ---------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------ | ----------------------------------------------- | ------------------------- | ------------------------------------------- | ------------------------------------------ | ----------------------------------------------------------- |
| 1  | trigger   | durable accepted/in-progress reservation | execution_state='processing'                                                      | YES                            | create                                          | 202                       | new processing_result_id                    | orchestration continues; parser MAY run once if reached; never replayed | NONE at Transaction A boundary                              |
| 2  | trigger   | same-key replay while processing         | execution_state='processing'                                                      | NO (reuse)                     | reuse existing                                  | 202                       | same processing_result_id                   | NO                                         | 202                                                         |
| 3  | trigger   | terminal success                         | execution_state='completed', result_status='success'                              | NO (terminal update)           | update existing                                 | 200                       | same processing_result_id                   | NO                                         | 200                                                         |
| 4  | trigger   | terminal partial                         | execution_state='completed', result_status='partial'                              | NO                             | update existing                                 | 200                       | same processing_result_id                   | NO                                         | 200                                                         |
| 5  | trigger   | terminal failed                          | execution_state='completed', result_status='failed'                               | NO                             | update existing                                 | 200                       | same processing_result_id                   | NO                                         | 200                                                         |
| 6  | trigger   | terminal replay                          | execution_state='completed'                                                       | NO (reuse)                     | reuse existing                                  | 200                       | same processing_result_id                   | NO                                         | 200                                                         |
| 7  | trigger   | Transaction B infrastructure failure     | execution_state='processing' remains                                              | NO                             | keep existing                                   | 202 (unchanged)           | same reservation id                         | NO (reservation stays processing)          | 202 on replay; initiating transport failure NOT_FROZEN_HERE |
| 8  | trigger   | idempotency conflict                     | N/A (no mutation)                                                                 | NO                             | no overwrite                                    | unchanged                 | no new result, existing key untouched       | NO                                         | 409                                                         |
| 9  | trigger   | pre-accept rejection                     | N/A (no durable result)                                                           | NO                             | NO binding                                      | N/A                       | no result created                           | NO                                         | NOT_FROZEN_BY_THIS_CLOSURE                                  |
| 10 | trigger   | same-PaperVersion admission redirect     | existing normal in-progress run                                                   | NO new intent                  | no new key                                      | N/A                       | redirected to existing processing_result_id | NO                                         | 202                                                         |
| 11 | activate  | successful activation                    | active selection changed                                                          | YES                            | create                                          | 200                       | activated processing_result_id              | action once                                | 200                                                         |
| 12 | activate  | same-key replay                          | previously successful activation target (current active pointer may have changed) | NO (reuse)                     | reuse existing                                  | 200                       | same originally bound processing_result_id  | NO mutation / NO duplicate audit           | 200                                                         |
| 13 | activate  | idempotency conflict                     | different target/hash                                                             | NO                             | no overwrite                                    | unchanged                 | no new activation                           | NO                                         | 409                                                         |
| 14 | activate  | rejection / rollback                     | validation failure                                                                | NO                             | key rolled back (no durable successful binding) | N/A                       | no active selection mutation                | NO                                         | NOT_FROZEN_BY_THIS_CLOSURE                                  |

---

## 7. Domain vs transport separation

```text
ProcessingResult.result_status != HTTP status
```

- `success|partial|failed` are domain outcomes.
- `200|202|409|...` are transport/request semantics.

A durable failed Processing Result is not equivalent to HTTP 500.

---

## 8. Compatibility audit

```text
202 fits SmallInteger      = YES
200 fits SmallInteger      = YES
409 already maps IDEMPOTENCY_CONFLICT = YES
result_row_version = NULL is valid = YES

SCHEMA_COMPATIBILITY                = PASS
SCHEMA_REDESIGN_REQUIRED            = NO
MIGRATION_REQUIRED                  = NO
IDEMPOTENCY_MODEL_CHANGE_REQUIRED   = NO
IDEMPOTENCY_REPOSITORY_CHANGE_REQUIRED = NO
PROCESSING_ROUTE_REQUIRED_FOR_THIS_CLOSURE = NO
OPENAPI_CHANGE_REQUIRED_FOR_THIS_CLOSURE = NO
```

No new repository APIs are required by this semantics closure.

---

## 9. Traceability

| Semantic                 | Frozen Decisions | Contract  | Plan     |
| ------------------------ | ---------------- | --------- | -------- |
| D1 accepted/in-progress  | S2               | §7, §11 | §6, §7 |
| D2 same-intent replay    | S3               | §6       | §6, R1a |
| D3 terminal              | S6, S7           | §11      | §13     |
| D4 terminal replay       | S3               | §6       | §6, R1a |
| D5 Tx B infra failure    | S7, S9           | §7, §11 | §13, R8 |
| D6 persisted failures    | S4, S6           | §12      | §15     |
| D7 key hash conflict     | S3               | §6       | §6, R1b |
| D8 pre-accept rejection  | S2               | §7       | §7      |
| D9 admission redirect    | S3               | §6       | §7, R2  |
| D10 activation success   | S8               | §13      | §14     |
| D11 activation rejection | S8               | §13      | §14     |

```text
This document does NOT change Frozen Decisions.
This document does NOT change Processing Service Contract.
This document does NOT change Implementation Plan.
It only closes the numeric/API semantic prerequisite intentionally deferred by those authorities.
```

---

## 10. Stop conditions

This draft must be rejected back to governance if actual inspection proves any of:

- schema cannot represent 202/200;
- Contract requires terminal failed to be an HTTP error;
- activation requires durable in-progress state;
- an authority already freezes conflicting numbers;
- new DB state/table is required;
- Processing Service semantics must change.

None of the above were found.

---

## 11. Self-audit

```text
TRIGGER_TERMINAL_HTTP_STATUS        = 200
ADMISSION_REDIRECT_HTTP_STATUS      = 202
ACTIVATE_TERMINAL_HTTP_STATUS       = 200
IDEMPOTENCY_CONFLICT_HTTP_STATUS    = 409

STORED_RESULT_HTTP_STATUS_WHILE_PROCESSING = 202

INITIATING_SYNCHRONOUS_TRIGGER_DOES_NOT_RETURN_AT_TRANSACTION_A_BOUNDARY = PASS

INITIATING_SYNCHRONOUS_TRIGGER_TERMINAL_SUCCESS_HTTP_STATUS = 200
INITIATING_SYNCHRONOUS_TRIGGER_TERMINAL_PARTIAL_HTTP_STATUS = 200
INITIATING_SYNCHRONOUS_TRIGGER_TERMINAL_FAILED_HTTP_STATUS  = 200

TRIGGER_PROCESSING_REPLAY_202       = PASS
TERMINAL_SUCCESS_HTTP_STATUS        = 200
TERMINAL_PARTIAL_HTTP_STATUS        = 200
TERMINAL_FAILED_HTTP_STATUS         = 200
TERMINAL_REPLAY_200                 = PASS
PROCESSING_REPLAY_HTTP_STATUS       = 202

TXB_INFRA_FAILURE_CACHED_STATUS_CHANGE  = NO
TXB_INFRA_FAILURE_EXISTING_STATUS_REMAINS = 202
TXB_INFRA_FAILURE_CACHES_500        = NO
TXB_INFRA_FAILURE_INITIATING_HTTP_STATUS =
NOT_FROZEN_BY_THIS_CLOSURE

IDEMPOTENCY_CONFLICT_409            = PASS
PRE_ACCEPT_REJECTION_CACHED         = NO
PRE_ACCEPT_GENERIC_HTTP_STATUS      =
NOT_FROZEN_BY_THIS_CLOSURE
ADMISSION_REDIRECT_HTTP_202         = PASS
ADMISSION_REDIRECT_CREATES_NEW_IDEMPOTENCY_KEY = NO

ACTIVATION_SUCCESS_200              = PASS
ACTIVATION_REPLAY_200               = PASS
ACTIVATION_CONFLICT_409             = PASS
ACTIVATION_REJECTION_DURABLE_KEY    = NO
ACTIVATION_REJECTION_GENERIC_HTTP_STATUS =
NOT_FROZEN_BY_THIS_CLOSURE

ACTIVATION_REPLAY_REPLAYED_RESPONSE_FIELD_REQUIRED = NO
ACTIVATION_REPLAY_REAPPLIES_MUTATION = NO
ACTIVATION_REPLAY_DUPLICATE_AUDIT = NO
ACTIVATION_REPLAY_RETURNS_ORIGINALLY_BOUND_RESULT = YES
ACTIVATION_REPLAY_TARGET_MUST_STILL_BE_ACTIVE = NO

TRIGGER_RESULT_ROW_VERSION          = NULL
ACTIVATE_RESULT_ROW_VERSION         = NULL

RESULT_STATUS_HTTP_STATUS_SEPARATION = PASS

SCHEMA_COMPATIBILITY                = PASS
SCHEMA_REDESIGN_REQUIRED            = NO
MIGRATION_REQUIRED                  = NO
IDEMPOTENCY_MODEL_CHANGE_REQUIRED   = NO
IDEMPOTENCY_REPOSITORY_CHANGE_REQUIRED = NO
PROCESSING_ROUTE_REQUIRED_FOR_THIS_CLOSURE = NO
OPENAPI_CHANGE_REQUIRED_FOR_THIS_CLOSURE = NO

NEW_PRODUCT_DECISION_INTRODUCED     = NO
FROZEN_DECISIONS_CHANGED            = NO
CONTRACT_SEMANTICS_CHANGED          = NO
IMPLEMENTATION_PLAN_CHANGED         = NO

PRODUCTION_CODE_MODIFIED            = NO
PROCESSING_SERVICE_IMPLEMENTATION   = NOT AUTHORIZED
PROCESSING_API_IMPLEMENTATION       = NOT AUTHORIZED
IMPLEMENTATION_AUTHORIZED           = NO
IMPLEMENTATION_STARTED              = NO

COMMIT_PERFORMED = NO
PUSH_PERFORMED   = NO

PRE_IMPLEMENTATION_PREREQUISITE =
PROCESSING_API_IDEMPOTENCY_RESPONSE_SEMANTICS_CLOSURE

PRE_IMPLEMENTATION_PREREQUISITE_STATUS =
SATISFIED

NEXT_AUTHORIZED_STAGE =
PROCESSING_SERVICE_IMPLEMENTATION_AUTHORIZATION
```

---

## 12. Team B Re-review #2 approval record

```text
TEAM_B_PROCESSING_API_IDEMPOTENCY_RESPONSE_SEMANTICS_RE_REVIEW_2_STATUS =
APPROVE

FROZEN_DECISIONS_AUTHORITY =
1f5e0ea23a235f23193d7821fff4bde8be7a7473

CONTRACT_AUTHORITY =
99433c824efd36ce515742642199a9e50c701e90

IMPLEMENTATION_PLAN_AUTHORITY =
db8acfe38d70e12d2b04ca6a1457d31772c1cf67

API_BASELINE =
85e20755f6069a4446f67417e2eff323b6a41674

P0_FINDINGS = 0
P1_FINDINGS = 0
P2_FINDINGS = 0
P3_FINDINGS = 0

P2_1_STALE_TRIGGER_NEW_ACCEPTED_202_REMOVED = PASS
P2_1_AMBIGUOUS_TRIGGER_IN_PROGRESS_FIELD_RESOLVED = PASS
P2_1_STORED_202_SEMANTIC_PRESERVED = PASS
P2_1_PROCESSING_REPLAY_202_PRESERVED = PASS
P2_1_SYNC_TERMINAL_200_PRESERVED = PASS

P3_1_MATRIX_ROW1_PARSER_ALWAYS_ONCE_REMOVED = PASS
P3_1_MATRIX_ROW1_PARSER_AT_MOST_ONCE_IF_REACHED = PASS
P3_1_MATRIX_ROWS_2_TO_14_UNCHANGED = PASS

ONLY_REV2_MECHANICAL_DELTA_PRESENT = PASS
AUTHORITY_REBIND_UNCHANGED = PASS

SCHEMA_COMPATIBILITY = PASS
SCHEMA_REDESIGN_REQUIRED = NO
MIGRATION_REQUIRED = NO

NEW_PRODUCT_DECISION_INTRODUCED = NO
FROZEN_DECISIONS_CHANGED = NO
CONTRACT_SEMANTICS_CHANGED = NO
IMPLEMENTATION_PLAN_CHANGED = NO

TEAM_B_REVIEW_VERDICT = APPROVE
```

---

## 13. Canonicalization status

```text
API IDEMPOTENCY RESPONSE SEMANTICS = APPROVED

PROCESSING SERVICE IMPLEMENTATION = NOT AUTHORIZED
PROCESSING API IMPLEMENTATION = NOT AUTHORIZED
IMPLEMENTATION AUTHORIZED = NO
IMPLEMENTATION STARTED = NO

PRE_IMPLEMENTATION_PREREQUISITE =
PROCESSING_API_IDEMPOTENCY_RESPONSE_SEMANTICS_CLOSURE

PRE_IMPLEMENTATION_PREREQUISITE_STATUS =
SATISFIED

NEXT_AUTHORIZED_STAGE =
PROCESSING_SERVICE_IMPLEMENTATION_AUTHORIZATION
```
