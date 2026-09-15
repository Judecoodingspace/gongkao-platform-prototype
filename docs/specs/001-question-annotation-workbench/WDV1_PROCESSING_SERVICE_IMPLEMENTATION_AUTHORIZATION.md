# WDV1 Processing Service Implementation Authorization

```text
STATUS =
ISSUED

PROCESSING_SERVICE_IMPLEMENTATION_AUTHORIZED = YES
PROCESSING_API_IMPLEMENTATION_AUTHORIZED = NO

SCHEMA_REDESIGN_AUTHORIZED = NO
MIGRATION_AUTHORIZED = NO
PARSER_MODIFICATION_AUTHORIZED = NO
SOURCE_READER_MODIFICATION_AUTHORIZED = NO
API_ROUTE_IMPLEMENTATION_AUTHORIZED = NO
OPENAPI_MODIFICATION_AUTHORIZED = NO
FRONTEND_IMPLEMENTATION_AUTHORIZED = NO
WORKER_QUEUE_IMPLEMENTATION_AUTHORIZED = NO

IMPLEMENTATION_STARTED = NO
```

---

## 1. Authorization intent

```text
PRODUCT_OWNER_REQUESTED_STAGE =
PROCESSING_SERVICE_IMPLEMENTATION_AUTHORIZATION
```

This document is a restricted governance authorization. It converts the previously approved Processing Service Plan into a formal Git authority for the next implementation stage. It does **not** itself create production code, tests, schema, migration, parser changes, source-reader changes, API routes, OpenAPI changes, or frontend changes.

---

## 2. Exact authority binding

The following four authorities are bound exactly:

```text
FROZEN_DECISIONS_AUTHORITY =
1f5e0ea23a235f23193d7821fff4bde8be7a7473

PROCESSING_SERVICE_CONTRACT_AUTHORITY =
99433c824efd36ce515742642199a9e50c701e90

PROCESSING_SERVICE_IMPLEMENTATION_PLAN_AUTHORITY =
db8acfe38d70e12d2b04ca6a1457d31772c1cf67

PROCESSING_API_IDEMPOTENCY_RESPONSE_SEMANTICS_AUTHORITY =
72172c1a23fd3769f360b73aaf68fc10aa82c954

API_IMPLEMENTATION_BASE_SHA =
85e20755f6069a4446f67417e2eff323b6a41674
```

No shortened SHA, chat-memory substitution, or "latest main" substitution is permitted.

---

## 3. Authorized implementation repository

The only implementation repository authorized by this document is:

```text
Judecoodingspace/gongkao-question-bank-api
```

No implementation work is authorized in `gongkao-platform-prototype` except this authorization document itself.

---

## 4. Authorized implementation branch / worktree contract

The next implementation task MUST create the following branch from the exact baseline:

```text
IMPLEMENTATION_BRANCH =
impl/20260915-wdv1-processing-service

IMPLEMENTATION_BASE_SHA =
85e20755f6069a4446f67417e2eff323b6a41674

IMPLEMENTATION_WORKTREE_NAME =
wdv1_processing_service_implementation

RECOMMENDED_WORKTREE_PATH =
<API_REPO_ROOT>/.worktrees/wdv1_processing_service_implementation
```

This authorization task does NOT create the branch or worktree.

Before any code edit, the next task must verify:

```text
git branch --show-current
git rev-parse HEAD
git status --short
```

Initial implementation worktree must start:

```text
BRANCH = impl/20260915-wdv1-processing-service
BASE_SHA = 85e20755f6069a4446f67417e2eff323b6a41674
WORKTREE_CLEAN = YES
```

Otherwise implementation must STOP.

---

## 5. Authorized production-code file scope

### Authorized NEW files

```text
src/gongkao_api/modules/source_processing/service.py
src/gongkao_api/modules/source_processing/repository.py
tests/services/test_source_processing_service.py
```

### Authorized MODIFY file

```text
src/gongkao_api/core/config.py
```

No other file is authorized for modification by this implementation slice. If implementation discovers that another file must change, it MUST STOP and request scope amendment / Plan reconciliation.

---

## 6. Explicitly untouched implementation files

The following files MUST remain explicitly untouched:

```text
src/gongkao_api/modules/source_processing/models.py

src/gongkao_api/modules/source_processing/parser.py
src/gongkao_api/modules/source_processing/parser_types.py
src/gongkao_api/modules/source_processing/parser_constants.py
src/gongkao_api/modules/source_processing/__init__.py

src/gongkao_api/modules/papers/storage.py
src/gongkao_api/modules/papers/models.py
src/gongkao_api/modules/papers/repository.py
src/gongkao_api/modules/papers/service.py

src/gongkao_api/modules/idempotency/models.py
src/gongkao_api/modules/idempotency/repository.py

src/gongkao_api/modules/audit/repository.py

src/gongkao_api/api/errors.py
src/gongkao_api/api/**

migrations/**
frontend/**
```

Also forbidden: any parser/schema/source-reader/API-route/OpenAPI changes.

---

## 7. Authorized implementation units

Implementation is limited to the canonical Plan's approved units:

```text
P1  command / input / internal DTO models
P2  SourceProcessingRepository
P3  idempotency reservation integration
P4  same-PaperVersion admission serialization
P5  Transaction A
P6  source read + service-side integrity verification
P7  parser invocation through existing parser boundary
P8  ParseResult -> persistence mapping
P9  Transaction B
P10 failure mapping / bounded safe diagnostics
P11 active-selection operations
P12 stale/interrupted classifier
P13 read-side service methods
P14 audit integration
P15 tests / concurrency qualification
```

P6/P7 authorize **calling/reusing** Source Reader / Parser. They do NOT authorize modifying Source Reader / Parser.

---

## 8. Response semantics frozen for implementation

The implementation MUST bind to the canonical semantics authority and MUST NOT reinterpret the following constants:

```text
STORED_RESULT_HTTP_STATUS_WHILE_PROCESSING = 202

PROCESSING_REPLAY_HTTP_STATUS = 202

TRIGGER_TERMINAL_HTTP_STATUS = 200

TERMINAL_SUCCESS_HTTP_STATUS = 200
TERMINAL_PARTIAL_HTTP_STATUS = 200
TERMINAL_FAILED_HTTP_STATUS = 200
TERMINAL_REPLAY_HTTP_STATUS = 200

TXB_INFRA_FAILURE_CACHED_STATUS_CHANGE = NO
TXB_INFRA_FAILURE_EXISTING_STATUS_REMAINS = 202
TXB_INFRA_FAILURE_CACHES_500 = NO

IDEMPOTENCY_CONFLICT_HTTP_STATUS = 409

ADMISSION_REDIRECT_HTTP_STATUS = 202
ADMISSION_REDIRECT_CREATES_NEW_IDEMPOTENCY_KEY = NO

ACTIVATE_TERMINAL_HTTP_STATUS = 200

TRIGGER_RESULT_ROW_VERSION = NULL
ACTIVATE_RESULT_ROW_VERSION = NULL
```

---

## 9. Frozen architectural constraints

### Synchronous MVP

```text
worker = NO
scheduler = NO
background task = NO
queue = NO
automatic retry loop = NO
```

### Orchestration

```text
Transaction A
→ DB-free parser phase
→ Transaction B
```

### Parser phase

```text
_execute_processing(context)
MUST perform zero repository / SQLAlchemy / Session DB operations
```

### Global row-lock order

```text
PaperVersion
→ ProcessingResult
→ ActiveSelection
```

### Source integrity trust anchor

```text
SERVICE_RECOMPUTED_CONTENT_SHA256
```

Reader-provided SHA is auxiliary only.

### Failed parser result

```text
failed result
→ zero usable DocumentBlock
→ bounded gap evidence MAY remain
```

### Transaction B persistence failure

```text
rollback
→ reservation remains processing
→ no fabricated terminal failed result
→ no cached 500
```

---

## 10. Authorized test scope

Implementation is authorized and required to add:

```text
tests/services/test_source_processing_service.py
```

The implementation must execute targeted tests required by the canonical Plan, including:

```text
unit/service behavior tests

PostgreSQL 16 integration tests

R1a same-key replay concurrency
R1b SAVEPOINT unique-race conflict recovery
R2 same-PaperVersion admission serialization
R3 initial-active race / exactly-one active
R4 lock-order/deadlock-sensitive activation/terminalization cases
R5 stale classification
R6 late terminalization behavior
R7 source integrity / reader-hash consistency
R8 Transaction B persistence rollback behavior
R9 failed-result zero-block invariant / bounded gaps
R10 read-side / history / active behavior
```

Do NOT replace PostgreSQL 16 concurrency qualification with SQLite. Implementation may run existing regression tests read-only. It may NOT modify existing tests outside the one new authorized test file merely to make failures disappear. If existing tests expose a conflict requiring changes outside scope, STOP and request governance review.

---

## 11. Static / quality verification

The implementation stage MAY run repository-standard non-mutating quality checks such as:

```text
pytest
ruff
mypy / type checker if already configured
```

Do not add dependencies or modify `pyproject.toml` unless separately authorized. No dependency upgrade is authorized.

---

## 12. Stop conditions

Implementation MUST stop if any of the following occurs:

```text
S1  wrong repository / branch / worktree
S2  implementation branch not based on exact API baseline 85e20755...
S3  authority SHA mismatch
S4  canonical semantics cannot be implemented without reinterpretation
S5  need to modify any file outside the authorized 4-file scope
S6  schema redesign appears necessary
S7  migration appears necessary
S8  parser modification appears necessary
S9  source reader modification appears necessary
S10 API route / OpenAPI modification appears necessary
S11 worker / scheduler / queue / background execution becomes necessary
S12 new product decision becomes necessary
S13 existing Contract / Plan inconsistency is discovered
S14 PG16 concurrency qualification cannot be performed
S15 implementation would require hidden retry / recovery behavior
S16 implementation would require changing the frozen 200/202/409 semantics
S17 implementation would require changing global lock order
S18 implementation would require modifying existing test files to conceal failures
```

On stop:

```text
IMPLEMENTATION_STATUS =
BLOCKED_REQUIRES_GOVERNANCE_REVIEW
```

No self-amendment.

---

## 13. Commit / push policy for future implementation

During the next implementation stage:

- commits occur only on the registered implementation branch;
- no direct production-code commit to API `main`;
- no force push;
- no merge to main without independent review;
- exact candidate SHA must be reported;
- worktree must be clean at handoff;
- implementation evidence must record changed files and test results.

This authorization task itself does NOT create implementation commits.

---

## 14. Implementation completion handoff requirements

The future implementation task ends with:

```text
PROCESSING_SERVICE_IMPLEMENTATION_STATUS =
CANDIDATE_COMPLETE
```

and must report at minimum:

```text
IMPLEMENTATION_BRANCH
IMPLEMENTATION_WORKTREE
IMPLEMENTATION_BASE_SHA
CANDIDATE_SHA

CHANGED_FILES

AUTHORIZED_FILE_SCOPE_COMPLIANCE = PASS / FAIL
PRODUCTION_CODE_SCOPE = PASS / FAIL
TEST_SCOPE = PASS / FAIL

TARGETED_TEST_RESULT
PG16_CONCURRENCY_TEST_RESULT
REGRESSION_TEST_RESULT
STATIC_CHECK_RESULT

FROZEN_DECISIONS_CHANGED = NO
CONTRACT_CHANGED = NO
IMPLEMENTATION_PLAN_CHANGED = NO
SEMANTICS_CHANGED = NO

SCHEMA_CHANGED = NO
MIGRATION_CHANGED = NO
PARSER_CHANGED = NO
SOURCE_READER_CHANGED = NO
API_CHANGED = NO
FRONTEND_CHANGED = NO

MERGE_PERFORMED = NO

NEXT_AUTHORIZED_STAGE =
TEAM_B_PROCESSING_SERVICE_IMPLEMENTATION_REVIEW
```

Implementation candidate completion does NOT authorize merge.

---

## 15. Authorization issuance state

```text
PROCESSING_SERVICE_IMPLEMENTATION_AUTHORIZATION =
ISSUED

PROCESSING_SERVICE_IMPLEMENTATION_AUTHORIZED =
YES

PROCESSING_API_IMPLEMENTATION_AUTHORIZED =
NO

IMPLEMENTATION_STARTED =
NO

IMPLEMENTATION_BASE_SHA =
85e20755f6069a4446f67417e2eff323b6a41674

IMPLEMENTATION_BRANCH =
impl/20260915-wdv1-processing-service

NEXT_AUTHORIZED_STAGE =
PROCESSING_SERVICE_IMPLEMENTATION_EXECUTION
```
