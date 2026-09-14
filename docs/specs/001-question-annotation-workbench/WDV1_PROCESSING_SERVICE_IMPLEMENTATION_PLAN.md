# WDV1 Processing Service Implementation Plan

```text
STATUS =
APPROVED
(TEAM B PROCESSING SERVICE IMPLEMENTATION PLAN RE-REVIEW #4 PASS)

IMPLEMENTATION PLAN = APPROVED
PROCESSING SERVICE IMPLEMENTATION = NOT AUTHORIZED
PRODUCTION CODE MODIFICATION = NOT AUTHORIZED
IMPLEMENTATION_AUTHORIZED = NO
IMPLEMENTATION_STARTED = NO

PREVIOUS_TEAM_B_APPROVAL_RECORD =
SUPERSEDED_FOR_IMPLEMENTATION_AUTHORIZATION_BY =
TEAM_B_PROCESSING_SERVICE_IMPLEMENTATION_PLAN_RE_REVIEW_3_REQUEST_CORRECTION

TEAM_B_RE_REVIEW_4_APPROVAL_RECORD =
APPROVED_AND_CANONICALIZED
```

本文是基于已 CLOSED 的 Frozen Decisions、已 canonicalized 的 Implementation Contract 与 API 真实代码的**计划级**文档。它定义文件级、符号级、事务级、测试级的实施方案，但不创建、不修改任何 production code。

---

## §1 Authority and exact baseline

```text
Frozen Decisions authority =
Judecoodingspace/gongkao-platform-prototype
docs/specs/001-question-annotation-workbench/WDV1_PROCESSING_SERVICE_FROZEN_DECISIONS.md
main@1f5e0ea23a235f23193d7821fff4bde8be7a7473

Processing Service Contract authority =
docs/specs/001-question-annotation-workbench/WDV1_PROCESSING_SERVICE_IMPLEMENTATION_CONTRACT.md
main@99433c824efd36ce515742642199a9e50c701e90

API implementation baseline =
Judecoodingspace/gongkao-question-bank-api
main@85e20755f6069a4446f67417e2eff323b6a41674

Corrective Revision base Plan authority =
Judecoodingspace/gongkao-platform-prototype
docs/specs/001-question-annotation-workbench/WDV1_PROCESSING_SERVICE_IMPLEMENTATION_PLAN.md
main@e197b1371c58408fab2572dc7d434fbbbf5ffd4b
```

实际检查：

- Frozen Decisions / Contract authorities 是上文列出的历史不可变 authority。
- Corrective Revision #4 基于 canonical Plan authority
  `e197b1371c58408fab2572dc7d434fbbbf5ffd4b`。
- API baseline 保持
  `85e20755f6069a4446f67417e2eff323b6a41674`。
- API repo 本地 `main@85e20755f6069a4446f67417e2eff323b6a41674`，与 remote 一致；对以下文件做了真实只读检查：`papers/models.py`、`papers/storage.py`、`papers/repository.py`、`papers/service.py`、`source_processing/models.py`、`source_processing/parser.py`、`parser_types.py`、`parser_constants.py`、`idempotency/models.py`、`idempotency/repository.py`、`audit/repository.py`、`source_materials/service.py`、`api/errors.py`、`migrations/versions/0001..0006`、`tests/services/conftest.py`、`tests/migrations/test_source_processing_schema.py`、`tests/services/test_shenlun_services.py`、`tests/services/test_source_processing_parser.py`、`tests/services/fixtures/source_processing.py`、`pyproject.toml`。

## §2 Scope / non-goals

**In scope**：Processing Service orchestration（trigger / transaction / idempotency / admission / integrity / parser 调用 / 持久化 / active selection / stale 分类 / 失败映射 / 读取 / audit）与其单元 + PostgreSQL 16 集成测试。

**Out of scope**：schema redesign、migration、parser 扩展、source-reader 重设计、API 路由 / OpenAPI、frontend、WDV1-004 / 视觉预览、OCR / 图像 / 表格 / 公式、AI 补 gap、语义题目抽取、worker 集群、调度器、自动重试 / 恢复。

## §3 Existing code map

| Concern               | Existing file                                                                          | Existing symbol(s)                                                                                                                                                                             | Reuse / modify / new                                        |
| --------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 来源证据              | `src/gongkao_api/modules/papers/models.py`                                           | `Paper`, `PaperVersion`                                                                                                                                                                    | Reuse（只读字段，不写）                                     |
| PaperVersion 行锁     | `src/gongkao_api/modules/papers/repository.py`                                       | `PaperRepository.lock_version / get_version`                                                                                                                                                 | Reuse（Transaction A 准入串行化的载体）                     |
| 私有来源读取          | `src/gongkao_api/modules/papers/storage.py`                                          | `PrivateSourceReader`, `SourceReadResult(content,size,sha256)`, `SourceReadError('SOURCE_READ_FAILED')`                                                                                  | Reuse（DI 注入 service）                                    |
| 处理结果 schema       | `src/gongkao_api/modules/source_processing/models.py`                                | `SourceProcessingResult`, `DocumentBlock`, `SourceProcessingGap`, `PaperVersionActiveProcessing`                                                                                       | Reuse（不改 ORM）                                           |
| 处理 schema migration | `migrations/versions/0006_m006_source_processing_schema.py`                          | 对应表/CHECK/FK                                                                                                                                                                                | Reuse（不改 migration）                                     |
| Parser                | `src/gongkao_api/modules/source_processing/parser.py`                                | `parse_docx`                                                                                                                                                                                 | Reuse（bytes + ParserConfig boundary）                      |
| Parser 类型/常量      | `parser_types.py`, `parser_constants.py`                                           | `ParseResult`, `ParsedBlockCandidate`, `GapCandidate`, `ParserDiagnostic`, `ParserConfig`, `StatusCandidate`, `GapType`, `SourceRegionKind`, `DiagnosticCode`, `BlockType` | Reuse（DTO 映射输入）                                       |
| Idempotency           | `src/gongkao_api/modules/idempotency/models.py`, `repository.py`                   | `IdempotencyKey`, `IdempotencyRepository.lock_by_scope/add`, `request_hash()`                                                                                                            | Reuse（`operation_scope='source_processing:trigger'` 等） |
| Audit                 | `src/gongkao_api/modules/audit/repository.py`                                        | `AuditRepository.append(...)`                                                                                                                                                                | Reuse（3 个 action code）                                   |
| 领域错误              | `src/gongkao_api/core/errors.py`                                                     | `DomainRuleViolation(code)`                                                                                                                                                                  | Reuse（新 code 字符串仅 service 层使用）                    |
| 配置                  | `src/gongkao_api/core/config.py`                                                     | `Settings`（pydantic-settings）                                                                                                                                                              | Modify（新增 1 个 stale window 字段，见 §10）              |
| Service 风格参照      | `papers/service.py`, `source_materials/service.py`, `questions/service.py`       | frozen dataclass command/result、`Session` 注入、`_within_transaction` 幂等模板、`lock_by_scope` + `request_hash`                                                                      | 遵循 house style                                            |
| 测试基座              | `tests/services/conftest.py`                                                         | `postgres16_service_engine`, `service_session`（PG16 校验 + drop schema + alembic upgrade）                                                                                                | Reuse                                                       |
| Parser 测试基座       | `tests/services/fixtures/source_processing.py`, `test_source_processing_parser.py` | docx fixture builders                                                                                                                                                                          | Reuse（构造 partial/failed 输入）                           |

## §4 Planned file-level changes

| Path                                                                      | Why                                                                                        | Existing symbols affected | New symbols（计划名）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Contract clauses            | Tests                                                |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | ---------------------------------------------------- |
| **NEW** `src/gongkao_api/modules/source_processing/service.py`    | Processing Service 编排（Transaction A/B、完整性、parser 调用、映射、active、stale、读取） | 无                        | `TriggerProcessing`, `ActivateProcessing`, `TriggerProcessingResult`, `ProcessingResultView`, `ProcessingBlockView`, `ProcessingGapView`, `ProcessingService`, `StaleClassifier`（纯函数 `is_stale`）, `_runtime_fingerprint()`, `TriggerProcessingFingerprintPayload`, `ActivateProcessingFingerprintPayload`, `ProcessingExecutionContext`, `ProcessingOutcome`, `_reserve_processing`, `_execute_processing`, `_terminalize`, `_to_trigger_result`, 失败映射内部符号 | §6–§16                   | `tests/services/test_source_processing_service.py` |
| **NEW** `src/gongkao_api/modules/source_processing/repository.py` | 结果/块/gap/active 的受控访问                                                              | 无                        | `SourceProcessingRepository`（写入/锁：`lock_result`, `add_result`, `add_blocks`, `add_gaps`, `lock_active`, `upsert_active`；读：`get_result`, `list_by_paper_version`（ORDER BY `created_at, id`）, `list_processing_attempts`, `list_blocks(result_id)`（ORDER BY `source_order`）, `list_gaps(result_id)`（ORDER BY `source_order, id`）, `count_blocks(result_id)`, `count_gaps(result_id)`, `get_active`）                                                        | §6–§13, §15, §17, §22 | 同 service 测试（PG16）                              |
| **MODIFY** `src/gongkao_api/core/config.py`                       | stale window 配置（见 §10）                                                               | `Settings`              | 字段`processing_stale_window_seconds: int = 900`（env `GONGKAO_PROCESSING_STALE_WINDOW_SECONDS`）                                                                                                                                                                                                                                                                                                                                                                                                       | §14（stale 分类）          | stale 单测（注入 now/window，无需 DB）               |
| **NEW** `tests/services/test_source_processing_service.py`        | 单元 + service + PG16 并发测试                                                             | 无                        | 见 §19/§20 测试清单                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | §15（R1–R10）             | 自身                                                 |

**Explicitly untouched files**：

- `source_processing/models.py`（无 schema 改动）
- `source_processing/parser.py` / `parser_types.py` / `parser_constants.py` / `__init__.py`
- `papers/storage.py` / `papers/models.py` / `papers/repository.py` / `papers/service.py`
- `idempotency/models.py` / `idempotency/repository.py`（复用现签名）
- `audit/repository.py`
- `api/errors.py` / `api/*`（本阶段无 API）
- `migrations/*`、`pyproject.toml`、questions / source_materials / taxonomy / frontend
- 现有测试文件（仅新增测试文件，不改既有测试）

**结论**：无需 schema/migration；`SCHEMA_REDESIGN_REQUIRED = NO`。

## §5 Implementation units

| Unit                                         | 内容                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 落点                                             |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| P1 command / input model                     | `TriggerProcessing(client_request_id, paper_version_id, parser_name, parser_version, parser_config)`、`ActivateProcessing(client_request_id, processing_result_id)` frozen dataclass；`TriggerProcessingFingerprintPayload(paper_version_id, parser_name, parser_version, parser_config)`（trigger request_hash 输入，见 §6）；`ActivateProcessingFingerprintPayload(processing_result_id)`（activate request_hash 输入，见 §14）；`ProcessingExecutionContext(actor_id, client_request_id, processing_result_id, paper_version_id, storage_uri, expected_file_hash, parser_name, parser_version, parser_config)`（Transaction A → parser phase → Transaction B 的 bounded 上下文，parser phase 零 DB，见 §7/§10/§13）；`ProcessingOutcome`（bounded 终态输入，见 §7.1）；内部编排符号 `_reserve_processing(...)`、`_execute_processing(...)`、`_terminalize(...)`、`_to_trigger_result(...)`（见 §7.1） | service.py                                       |
| P2 source-processing repository              | 见 §4                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | repository.py                                    |
| P3 idempotency reservation integration       | replay/conflict/binding + terminal cache 更新                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | service.py（复用`IdempotencyRepository`）      |
| P4 same-PaperVersion admission serialization | PaperVersion 行锁 + 进行中检测 + stale 例外                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | service.py Transaction A                         |
| P5 Transaction A                             | 见 §7                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | service.py`trigger_processing`                 |
| P6 source read + integrity                   | 见 §10                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | service.py parser phase                          |
| P7 parser invocation                         | `parse_docx(content, parser_config=ParserConfig(...))`（canonical config propagation，见 §11）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | service.py                                       |
| P8 ParseResult → persistence mapper         | 见 §12                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | service.py`_map_parse_result()`                |
| P9 Transaction B                             | 见 §13                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | service.py`_terminalize()`                     |
| P10 failure mapping / safe diagnostics       | 见 §15                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | service.py`_failures.py 语义内化于 service`    |
| P11 active-selection operations              | initial / explicit / read（见 §14）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | service.py + repository.py                       |
| P12 stale/interrupted classifier             | 纯函数 + config + 注入 now（见 §9）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | service.py                                       |
| P13 reads                                    | result/history/blocks/gaps/active（见 §22）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | service.py                                       |
| P14 audit integration                        | 3 个 action code（见 §21）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | service.py + AuditRepository                     |
| P15 tests / concurrency qualification        | 见 §18–§20                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | tests/services/test_source_processing_service.py |

## §6 Processing intent & idempotency plan

- `operation_scope`：trigger = `source_processing:trigger`；activate = `source_processing.activate`。
- `request_hash`：复用 `idempotency.repository.request_hash()`（canonical JSON + SHA-256），但**输入为专门的 fingerprint payload**：`TriggerProcessingFingerprintPayload(paper_version_id, parser_name, parser_version, parser_config)`。`client_request_id` 只作为 idempotency key 元组的一维（`actor_id, operation_scope, client_request_id`），**不参与** `request_hash` payload。这样与 Contract §6 一致（hash 覆盖 PaperVersion 身份 + parser 身份/配置语义），且同一 key 换语义载荷才冲突。
- replay：`lock_by_scope` → 命中且 hash 相等 → 返回 `TriggerProcessingResult(replayed=True, processing_result_id=...)`；hash 不等 → `DomainRuleViolation("IDEMPOTENCY_CONFLICT")`。
- **唯一冲突恢复模型（选择 Model A — SAVEPOINT / nested transaction）**：Transaction A 内在创建 reservation 行与 audit **之前**，先用预生成的 `result_id` 在 `session.begin_nested()`（SAVEPOINT）内 `idempotency.add(...)` 并 `flush()`：
  - 若 `uq_idempotency_keys_actor_scope_client_request` 唯一冲突 → **仅回滚 SAVEPOINT**（此时 reservation 行与 audit 尚未创建，不存在 orphan）→ 重新 `lock_by_scope` 读取既有 key → 按 replay/conflict 语义返回；外层事务只保留锁，不产生任何持久化写入。
  - 若无冲突 → 外层事务继续创建 reservation 行（使用同一预生成 `result_id`）与 audit（见 §7），随后提交。
  - 不变量：replay/conflict 胜出的事务绝不留下自己的 reservation/audit；胜出者与失败者的持久化结果各自唯一确定。
- binding（不含 HTTP 数值）：Transaction A 内 `add(result_resource_type="source_processing_result", result_resource_id=<result_id>, result_http_status=IN_PROGRESS_RESPONSE_SEMANTIC, result_row_version=None)`。`IN_PROGRESS_RESPONSE_SEMANTIC` 与终态 `TERMINAL_RESPONSE_SEMANTIC` 的具体数值**不属于本 Plan 决定**，由后续 API 契约层固定（见 §13 与“前置条件”）。
- **前置条件（implementation 授权前必须闭合）**：`PRE_IMPLEMENTATION_PREREQUISITE = PROCESSING_API_IDEMPOTENCY_RESPONSE_SEMANTICS_CLOSURE`。Plan 评审可先于该 API 级前置条件完成；但在合适的 API 契约/治理 authority 固定该响应语义前，不得授权 production implementation。

## §7 Transaction A plan（`trigger_processing`）

事务所有者：`ProcessingService._session`；单 `with self._session.begin()`。

**全局锁顺序（所有 Processing Service 写事务统一遵守，避免 R4 死锁环）**：

```text
GLOBAL_LOCK_ORDER =
PaperVersion
→ ProcessingResult
→ ActiveSelection
```

Transaction A / Transaction B / 显式激活 / 任何 selection 变更均不得按其他顺序获取这些资源锁。顺序：

1. `payload_hash = request_hash(TriggerProcessingFingerprintPayload(paper_version_id=command.paper_version_id, parser_name=command.parser_name, parser_version=command.parser_version, parser_config=command.parser_config))`（`client_request_id` 不参与 payload，见 §6）。
2. `paper_version = PaperRepository.lock_version(command.paper_version_id)`（`SELECT ... FOR UPDATE`；**建立 PaperVersion 级准入串行化**，R2/R4 关键，全局锁顺序第 1 级）；不存在 → `DomainRuleViolation("PAPER_VERSION_NOT_FOUND")`（受理前拒绝，不留历史）。
3. `replay = IdempotencyRepository.lock_by_scope(actor, scope, command.client_request_id)`；命中 → hash 校验 → 返回既有 result 视图（replayed=True）。
4. `paper_version.upload_status != "finalized"` → `DomainRuleViolation("PAPER_VERSION_NOT_FINALIZED")`（受理前拒绝）。
5. **准入检查**：`SourceProcessingRepository.list_processing_attempts(paper_version_id, execution_state='processing')`；
   - 存在**非 stale**（`is_stale(...)` 为 False）→ 新 intent 不创建 result，返回 `TriggerProcessingResult(processing_result_id=<existing>, replayed=False, redirected=True)`；
   - 仅 stale 或无 → 继续。
6. 预生成 `result_id = uuid4()`；按 §6 Model A 在 `session.begin_nested()`（SAVEPOINT）内执行 `IdempotencyRepository.add(...)` + `flush()` 完成 key 绑定；唯一冲突 → 回滚 SAVEPOINT → 重读既有 key → 按 replay/conflict 返回（此时 reservation/audit 尚未创建，无 orphan）。
7. 创建 reservation 行（全部 reservation-time NOT NULL）：`id=result_id`、`paper_version_id`、`execution_state='processing'`、`result_status=None`、`completed_at=None`、`parser_name=command.parser_name`、`parser_version=command.parser_version`、`parser_config=command.parser_config`（canonical JSONB）、`runtime_fingerprint=_runtime_fingerprint()`、`triggered_by=actor_id`、`diagnostic_metadata={}`；`verified_source_hash=None`、`diagnostic_code=None`。`session.flush()`。
8. `AuditRepository.append(action_code="source_processing.accepted", entity_type="source_processing_result", entity_id=result_id, actor_id=actor_id, request_id=command.client_request_id, details={"paper_version_id": str(paper_version_id)})`（DERIVED_TECHNICAL_PLAN）。
9. 构建 `ProcessingExecutionContext(actor_id, client_request_id=command.client_request_id, processing_result_id=result_id, paper_version_id=command.paper_version_id, storage_uri=paper_version.storage_uri, expected_file_hash=paper_version.file_hash, parser_name=command.parser_name, parser_version=command.parser_version, parser_config=command.parser_config)`。`paper_version.storage_uri` 与 `paper_version.file_hash` 在现有 authority 下对该 `PaperVersion` 不可变，因此可在 Transaction A 锁定后安全携带到 parser phase；parser phase 不再重新加载 `PaperVersion`，从而避免 SQLAlchemy autobegin 导致的事务重叠（见 §7.1、§10）。
10. 提交。自提交起该 result 对历史查询可见。

不新增字段、不新增 DB 状态、不写 production code（以上仅计划）。

### §7.1 End-to-end synchronous orchestration（MVP 无 worker / scheduler / queue）

`ProcessingService.trigger_processing(actor_id, command)` 是当前 MVP 的 orchestration owner，同步串起三个阶段：

```text
trigger_processing(actor_id, command)
    |
    +-- result_or_context = _reserve_processing(actor_id, command)
    |      # Transaction A（§7 步骤 1–10，单事务提交）
    |      → replay / redirect：返回 TriggerProcessingResult(...)
    |      → 新 intent：返回 ProcessingExecutionContext
    |
    +-- if isinstance(result_or_context, TriggerProcessingResult):
    |      return result_or_context   # MUST NOT 重跑 parser
    |
    +-- outcome = _execute_processing(context)
    |      # 数据库事务之外；执行零 SQLAlchemy / repository / Session DB 操作
    |      → source_reader.read(context.storage_uri)
    |      → service 重算 content SHA-256（§10）
    |      → 与 context.expected_file_hash 做完整性 / 一致性检查
    |      → 构建 ParserConfig 并调用 parse_docx(...)
    |      → 产出 bounded ProcessingOutcome
    |
    +-- terminal_view = _terminalize(context, outcome)
    |      # Transaction B（§13，单事务提交）
    |      → 返回终态 ProcessingResultView
    |
    +-- return _to_trigger_result(terminal_view, replayed=False, redirected=False)
```

新增内部符号（service.py 内）：`ProcessingOutcome`（bounded：`result_status`、`blocks`、`gaps`、`diagnostic_code`、`diagnostic_metadata`、`verified_source_hash`）、`_reserve_processing(...)`、`_execute_processing(...)`、`_terminalize(...)`、`_to_trigger_result(...)`。

**Public return type discipline**：`ProcessingService.trigger_processing(...)` 在所有分支（new run / replay / redirect）下 MUST 返回 `TriggerProcessingResult`。`ProcessingResultView` 仅作为 Transaction B 内部终态视图与读方法返回类型；不得直接暴露为 `trigger_processing` 的返回类型。

强制规则：

- Transaction A commit 后 parser 才开始；replay 与 redirected/in-progress 均 MUST NOT 重跑 parser；只有新 intent 才继续 `_execute_processing` + `_terminalize`。
- read failure / integrity failure / parser failed / 可安全持久化的内部异常，全部转换为 bounded `ProcessingOutcome` 交给 Transaction B；`_execute_processing` 自身不直接写库。
- Transaction B 持久化失败 → 整体回滚 → reservation 保持 `processing` → 无隐藏重试（见 §13 失败路径）。
- 禁止引入 worker、scheduler、background task、queue。

## §8 R2 same-PaperVersion admission plan

不变量：`at most one normally-in-progress run per PaperVersion`。

- 串行化载体：`PaperRepository.lock_version`（沿用 G-08 Schema Design 的 PaperVersion 行锁权威），保证同一 PaperVersion 上并发 Transaction A 串行进入准入检查。
- 决策（在锁内完成）：正常进行中 → 不创建；仅 stale → MAY 创建；无 → MAY 创建。
- same-key idempotency（唯一约束）与 same-PaperVersion 准入（行锁）是两层独立不变量，二者并存（Contract C2）。
- 测试：见 R2（两线程、两独立 Session、不同 `client_request_id`、同一 PaperVersion）。

## §9 Stale / interrupted MVP plan（P12）

- **最窄 MVP 规则**：`execution_state == 'processing'` 且 `(now - created_at) > processing_stale_window_seconds`。
- **配置落点**：`Settings.processing_stale_window_seconds`（pydantic-settings，env `GONGKAO_PROCESSING_STALE_WINDOW_SECONDS`，默认 `900`）。Service 构造时注入 `now: Callable[[], datetime]`（默认 `lambda: datetime.now(timezone.utc)`）与 window，便于确定性测试。
- **纯函数**：`StaleClassifier.is_stale(*, execution_state, created_at, now, window_seconds) -> bool`（service.py 内 module-level 纯函数；不新增 DB 状态）。
- **使用点**：Transaction A 准入检查（§7.5）；读取视图 `ProcessingResultView.stale_indicator`（§13/§23）；Transaction B 终态不依赖 stale（迟到终态规则见 §14/R6）。
- **禁止**：stale DB enum、heartbeat、lease、scheduler、worker recovery、automatic retry。

## §10 Source integrity plan（P6）

Parser phase（事务外，且**零 DB 操作**）顺序：

1. 直接使用 `ProcessingExecutionContext` 中在 Transaction A 已捕获的不可变元数据：

   - `context.storage_uri`
   - `context.expected_file_hash`
   - `context.parser_name` / `context.parser_version` / `context.parser_config`

   `_execute_processing()` MUST NOT 调用 `PaperRepository.get_version()`、任何 repository 方法、或任何 SQLAlchemy Session SQL；否则 SQLAlchemy 2.x autobegin 会隐式启动事务，导致后续 `_terminalize()` 的 `with self._session.begin()` 与未提交事务冲突。
2. `source_reader.read(context.storage_uri) -> SourceReadResult`：

   - `SourceReadError` → Transaction B failed：`diagnostic_code='SOURCE_READ_FAILURE'`，`verified_source_hash=None`，parser 不调用。
3. **Service 自行重算内容 hash（信任锚点）**：

   ```text
   SOURCE_INTEGRITY_TRUST_ANCHOR =
   SERVICE_RECOMPUTED_CONTENT_SHA256

   actual_sha256 = hashlib.sha256(read_result.content).hexdigest()
   ```

   `read_result.sha256` 只能作为辅助一致性信号，MUST NOT 作为最终 trust anchor。
4. **一致性守卫（fail-closed）**：`read_result.sha256 != actual_sha256` → Transaction B failed：`diagnostic_code='INTERNAL_PROCESSING_FAILURE'`（安全内部一致性失败），`verified_source_hash=None`，parser MUST NOT 被调用。
5. **完整性比对**：`actual_sha256 != context.expected_file_hash` → Transaction B failed：`diagnostic_code='SOURCE_INTEGRITY_FAILURE'`，`verified_source_hash=None`，parser MUST NOT 被调用（不匹配的实际 hash 不得写入 `verified_source_hash`）。
6. **匹配** → `verified_source_hash = actual_sha256`，继续 parser 调用。
7. 安全：source bytes、`storage_uri`、traceback 不得进入日志 / `diagnostic_metadata` / audit details；`diagnostic_metadata` 仅允许 bounded 键值（如 `error_type`）。
8. 对应测试：bytes 重算值与 `context.expected_file_hash` 不一致 → integrity failure；reader 返回 sha 与 content 重算值不一致 → fail-closed internal consistency failure；重算值匹配 → `verified_source_hash = actual_sha256`。不得修改 Source Reader。
9. **Parser phase DB-free 断言**：单元/集成测试 MUST 验证：

   - Transaction A commit 后 `session.in_transaction() == False`；
   - `_execute_processing(context)` 期间任何 SQLAlchemy / repository / Session DB 访问都使测试失败（可用 monkeypatch/spy）；
   - `_execute_processing` 返回后 `session.in_transaction() == False`；
   - `_terminalize(...)` 可安全进入新的显式 `with self._session.begin()`。

## §11 Parser invocation plan（P7）

- 调用形态（保持 service 边界的 canonical 配置身份）：

  ```text
  parser_config = ParserConfig(
      parser_name=context.parser_name,
      parser_version=context.parser_version,
      canonical_config=context.parser_config,
  )
  parse_result = parse_docx(read_result.content, parser_config=parser_config)
  ```

  即使当前 parser 实现内部忽略 `parser_config`，service 边界 MUST 原样保留并传递 canonical 配置身份；不得修改 parser 实现，不得重解释 B1–B9。
- Parser 保持 persistence-agnostic：不接 Session、不接 storage、不读 PaperVersion、不做 active 选择；不创建第二套 parser authority。
- 意外的 parser 内部异常（非 `ParseResult` 返回）→ 可安全持久化的内部失败：Transaction B failed，`diagnostic_code='INTERNAL_PROCESSING_FAILURE'`（见 §16 边界）；Transaction B 自身持久化失败不属于此类（回滚 + stale 路径）。

## §12 ParseResult → persistence plan（P8 `_map_parse_result`）

| status_candidate | persisted result_status | blocks                                                                                        | gaps                                                                                       | verified_source_hash                 | 其他                                                             |
| ---------------- | ----------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------ | ---------------------------------------------------------------- |
| `success`      | `success`             | 全部`DocumentBlock`（`source_order` 保序、`block_type='text'`、`text_original` 原样） | 0                                                                                          | 已验证 hash                          | `diagnostic_code=None`                                         |
| `partial`      | `partial`             | 全部可靠 blocks                                                                               | 全部已知 gaps（`gap_type/source_order/source_region_kind/diagnostic_code/before/after`） | 已验证 hash                          | `diagnostic_code=None`                                         |
| `failed`       | `failed`              | **0 条 DocumentBlock**                                                                  | MAY 持久化 parser 返回的 bounded reliable gaps（仅历史/审计）                              | 验证成功时写 hash；不匹配场景为 None | `diagnostic_code='DOCUMENT_PARSE_FAILURE'`（或 §16 对应类别） |

映射禁止加入业务语义（无 stem/question/answer 等）。

## §13 Transaction B plan（P9 `_terminalize`）

单 `with self._session.begin()`。终态上下文：`ProcessingExecutionContext`（来自 Transaction A，§7.9），用于定位原始 trigger idempotency key 与 audit `request_id`。锁顺序遵循 §7 GLOBAL_LOCK_ORDER：

1. `PaperRepository.lock_version(context.paper_version_id)`（全局锁顺序第 1 级；与 activation/终态串行）。
2. `SourceProcessingRepository.lock_result(context.processing_result_id)`（第 2 级，FOR UPDATE）。若已 `completed`（重复终态路径/重复调用）→ 直接返回既有终态视图（幂等安全）。
3. 校验 `execution_state == 'processing'` 且 result 属于 `context.paper_version_id`，否则按 2 处理。
4. 按 §12 映射持久化 blocks/gaps（success/partial）或仅 gaps（failed）。
5. 写入 `verified_source_hash`（适用时）、`diagnostic_code` / bounded `diagnostic_metadata`。
6. `execution_state='completed'`、`result_status`、`completed_at=now()`。
7. `AuditRepository.append(action_code="source_processing.terminalized", entity_type="source_processing_result", entity_id=context.processing_result_id, actor_id=context.actor_id, request_id=context.client_request_id, details={"result_status": status, "block_count": n, "gap_count": m})`（DERIVED_TECHNICAL_PLAN；details 不含来源内容）。
8. idempotency terminal cache 更新：`IdempotencyRepository.lock_by_scope(actor_id=context.actor_id, operation_scope='source_processing:trigger', client_request_id=context.client_request_id)` 定位原始 trigger key，将其 `result_http_status` 更新为 `TERMINAL_RESPONSE_SEMANTIC`（缓存元数据更新，不改 result 本体；具体数值由 API 契约层固定，本 Plan 不选择数值，见 §6 前置条件）。
9. `if status == 'success'`：`SourceProcessingRepository.lock_active(context.paper_version_id)`（第 3 级）；无 active 行 → `upsert_active(...)` **MUST 插入 initial active**（同事务）；已有 active → 不动。
10. 一次提交。

**失败路径**：任一步抛异常 → 事务整体回滚；不得伪造/部分持久化 completed（含 failed）；reservation 保持 `processing` → §9 stale 路径；无隐藏 recovery loop。

## §14 Active selection plan（P11）

- **initial activation**：仅 Transaction B success 分支，且无 active 时 MUST 插入（R3 由 PaperVersion 行锁串行化保证“双 success 终态”只有一个插入）。
- **explicit activation**（`activate_processing_result(actor_id, command: ActivateProcessing) -> ProcessingResultView`，scope `source_processing.activate`，完整 idempotency lifecycle）。`client_request_id` 只作 key 维度，fingerprint payload 为 `ActivateProcessingFingerprintPayload(processing_result_id)`，与 §6 同一 hash 纪律。**选择 Option A**（命令只含 `processing_result_id`）。整个激活是一个显式外事务 `with self._session.begin():`。

  **A. Existing-key replay / conflict gate**

  进入外事务后立即：

  ```text
  payload_hash = request_hash(
      ActivateProcessingFingerprintPayload(
          processing_result_id=command.processing_result_id
      )
  )

  existing = IdempotencyRepository.lock_by_scope(
      actor_id=actor_id,
      operation_scope='source_processing.activate',
      client_request_id=command.client_request_id,
  )
  ```

  - 若 `existing` 存在：
    - `existing.request_hash != payload_hash` → `DomainRuleViolation("IDEMPOTENCY_CONFLICT")`，外层事务回滚，**无 mutation、无 audit**。
    - `existing.request_hash == payload_hash` → **MUST NOT** 再次执行 active-selection mutation，**MUST NOT** 追加第二条 `active_changed` audit；读取/重构 originally bound `ProcessingResultView` 并返回。
    - 额外 fail-closed 校验：`existing.result_resource_type == 'source_processing_result'` 且 `existing.result_resource_id == command.processing_result_id`；不一致则回滚并视为内部状态错误。

  **B. Absent key：SAVEPOINT unique-race gate**

  若 `existing` 不存在，使用与 trigger 相同的 SAVEPOINT 原则，在激活 mutation 之前预绑定候选 key：

  ```text
  session.begin_nested()
      IdempotencyRepository.add(
          actor_id=actor_id,
          operation_scope='source_processing.activate',
          client_request_id=command.client_request_id,
          request_hash_value=payload_hash,
          result_resource_type='source_processing_result',
          result_resource_id=command.processing_result_id,
          result_http_status=ACTIVATE_TERMINAL_RESPONSE_SEMANTIC,  # 数值由 API 语义闭包固定
          result_row_version=None,
      )
      flush()
  ```

  - 若唯一冲突 → 仅回滚 SAVEPOINT → 重新 `lock_by_scope` 读取既有 key：
    - same hash → 按 replay 返回 originally bound view，无 mutation，无 audit；
    - different hash → `IDEMPOTENCY_CONFLICT`。
  - 无冲突 → SAVEPOINT 成功，继续同一外事务执行后续 mutation。

  **C. Only the unique-key winner continues activation mutation**

  在 idempotency gate 成功后，**同一外事务**内继续：

  ```text
  candidate_hint = SourceProcessingRepository.get_result(command.processing_result_id)
      # plain SELECT, no FOR UPDATE
  if candidate_hint is None:
      → DomainRuleViolation("PROCESSING_RESULT_NOT_ACTIVATABLE")

  paper_version_id = candidate_hint.paper_version_id

  PaperRepository.lock_version(paper_version_id)            # lock class 1

  candidate = SourceProcessingRepository.lock_result(command.processing_result_id)
      # lock class 2

  revalidate:
      candidate 仍存在
      candidate.paper_version_id == paper_version_id
      candidate.execution_state == 'completed'
      candidate.result_status ∈ {'success', 'partial'}
      # failed / 跨版本 / 非终态 → NOT_ACTIVATABLE

  SourceProcessingRepository.lock_active(paper_version_id)  # lock class 3

  upsert_active(processing_result_id, selected_at=now, selected_by=actor_id)
      # 锁内原地更新或 delete+insert；指针可变，不触碰 result/blocks/gaps

  AuditRepository.append(
      action_code="source_processing.active_changed",
      actor_id=actor_id,
      request_id=command.client_request_id,
      ...)
      # DERIVED_TECHNICAL_PLAN
  ```

  全局行锁顺序仍为 `PaperVersion → ProcessingResult → ActiveSelection`；idempotency gate 是操作级 gate，不替代也不改变该 domain lock order。

  **D. Rejected activation**

  若后续 activation validation 失败（candidate missing、cross-PaperVersion、non-terminal、failed、not activatable），外层事务 MUST 完整回滚，包括：

  - 无 durable activation idempotency key；
  - 无 `active_changed` audit；
  - 无 active selection mutation。

  因此 `rejected activation → no durable successful activation idempotency binding`。

  注：`GLOBAL_LOCK_ORDER` 约束的是**行锁获取顺序**；它并不禁止同一显式事务内更早的 plain SELECT。
- **active read**：`get_active_processing(paper_version_id)` → view；partial active 必须携带 `result_status='partial'` 与 gaps 可见。
- 锁顺序统一为 §7 GLOBAL_LOCK_ORDER（PaperVersion → ProcessingResult → ActiveSelection），Transaction B 与显式激活均按此顺序，避免死锁环；禁止 best-result ranking。

## §15 Failure taxonomy plan（P10）

| 类别                            | detection site                                                             | persisted fields                                                                                             | bounded metadata 允许                                                              | 禁止                          |
| ------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- | ----------------------------- |
| `SOURCE_READ_FAILURE`         | `PrivateSourceReader.read` 抛 `SourceReadError`                        | `result_status='failed'`, `diagnostic_code`, `verified_source_hash=None`                               | `error_type`                                                                     | bytes/URI/path/traceback      |
| `SOURCE_INTEGRITY_FAILURE`    | hash 比对                                                                  | 同上；**不匹配实际 hash 不写入 `verified_source_hash`**                                              | `error_type`                                                                     | 实际 mismatch hash 伪装、正文 |
| `DOCUMENT_PARSE_FAILURE`      | `ParseResult.status_candidate == 'failed'`（含 archive/unsafe/结构失败） | `result_status='failed'`, `diagnostic_code`, bounded gap evidence, 验证成功时的 `verified_source_hash` | parser`ParserDiagnostic.code/stage/structure_kind/bounded_metadata`（B8 已约束） | raw XML / source text         |
| `INTERNAL_PROCESSING_FAILURE` | 非上述且**可安全持久化**的 service 内部异常                          | `result_status='failed'`, `diagnostic_code`                                                              | `error_type`（`type(exc).__name__`）                                           | 异常 message / traceback      |

**边界**：终态快照持久化机制自身失败（Transaction B 抛错）≠ INTERNAL_PROCESSING_FAILURE 行；此时整体回滚、保持 `processing`、走 stale 路径（Contract C3）。

## §16 Runtime provenance plan

- `parser_name` / `parser_version`：由 command 注入（默认建议沿用 `ParserConfig` 默认 `wdv1-direct-ooxml` / `4.4b.1`；由调用方在 Plan 实施时以受控配置提供）。
- `parser_config`：canonical JSONB（dict 原样，JSON 序列化排序由 jsonb 语义保证）。
- `runtime_fingerprint`：`{"python": platform.python_version(), "parser": "wdv1-direct-ooxml@<version>", "sqlalchemy": <version>, "psycopg": <version>}`——最小、bounded、deterministic；**禁止** `pip freeze` dump；实现时以模块级常量/导入元数据构建，单测断言键集合稳定。
- `verified_source_hash`：见 §10。
- `triggered_by` / `created_at` / `completed_at` / diagnostics：见 §7/§13/§15。

## §17 Seven logical service interfaces（planned symbols）

| Capability                 | Planned symbol                                                                 | Input             | Return DTO                                                                               | Repository calls                                                                                                                  | Error modes                                      | Tests                                 |
| -------------------------- | ------------------------------------------------------------------------------ | ----------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ------------------------------------- |
| trigger_processing         | `ProcessingService.trigger_processing(actor_id, command: TriggerProcessing)` | command dataclass | `TriggerProcessingResult(processing_result_id, execution_state, replayed, redirected)` | `PaperRepository.lock_version`, `IdempotencyRepository.*`, `SourceProcessingRepository.list_processing_attempts/add_result` | NOT_FOUND / NOT_FINALIZED / IDEMPOTENCY_CONFLICT | service+PG16 R1/R2                    |
| get_processing_result      | `.get_processing_result(result_id)`                                          | result_id         | `ProcessingResultView`（status/counts/active/stale/category）                          | `get_result`, `count_blocks`, `count_gaps`, `get_active`                                                                  | NOT_FOUND                                        | read 单测                             |
| list_processing_results    | `.list_processing_results(paper_version_id)`                                 | version_id        | `list[ProcessingResultView]`（ORDER BY `created_at, id`）                            | `list_by_paper_version`                                                                                                         | NOT_FOUND(version)                               | read 单测                             |
| get_processing_blocks      | `.get_processing_blocks(result_id)`                                          | result_id         | `list[ProcessingBlockView]`（ORDER BY `source_order`；failed → []）                 | `list_blocks`                                                                                                                   | NOT_FOUND                                        | read 单测（failed 空集断言）          |
| get_processing_gaps        | `.get_processing_gaps(result_id)`                                            | result_id         | `list[ProcessingGapView]`（ORDER BY `source_order, id`；含 failed bounded evidence） | `list_gaps`                                                                                                                     | NOT_FOUND                                        | read 单测                             |
| get_active_processing      | `.get_active_processing(paper_version_id)`                                   | version_id        | `ProcessingResultView / None`                                                          | `get_active` + result join                                                                                                      | NOT_FOUND(version)                               | read 单测（partial active 携带 gaps） |
| activate_processing_result | `.activate_processing_result(actor_id, command: ActivateProcessing)`         | command           | `ProcessingResultView`                                                                 | 锁链（§14）                                                                                                                      | NOT_ACTIVATABLE 等                               | service+PG16 R4/R6                    |

不定义 HTTP routes / OpenAPI。

## §18 R1–R10 implementation + test matrix

| Race                                                           | Implementation mechanism                                                                                                                            | Test type                                                                                     | Deterministic setup                               | Required assertion                                                                                                                                                                                                       |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| R1a 同 PaperVersion + 同 key 重放                              | PaperVersion 行锁串行化两个 Transaction A；winner 建 key + reservation；第二调用方随后在`lock_by_scope` 看到既有 key                              | PG16 集成（线程×2，各持 Session；同 actor/scope/`client_request_id`/PaperVersion/payload） | 同 key 双线程 trigger                             | PaperVersion 锁使双方不可能同时越过“key 不存在”；hash 相同 → 第二调用方 replay；恰好 1 个 result、1 个 key；parser 至多执行一次；无 orphan；无 500                                                                    |
| R1b 唯一键冲突恢复资格（SAVEPOINT 真实触发）                   | 不同 PaperVersion（行锁互不阻塞）+ 同 actor/scope/`client_request_id`；`paper_version_id` 进入 hash payload ⇒ 双方 hash 不同                   | PG16 集成（线程×2，各持 Session；Barrier/Event 在 SAVEPOINT 的 add+flush 前确定性对齐）      | 双方并发到达 idempotency insert                   | 一方赢得唯一 key；失败方在 SAVEPOINT 内得到唯一冲突 → 仅回滚 SAVEPOINT → 重读既有 key → hash 不同 →`IDEMPOTENCY_CONFLICT`；恰好 1 个持久化 key、1 个持久化 result；失败方无 reservation、无 accepted audit；无 500 |
| R2 同 Paper 不同 intent                                        | PaperVersion 行锁准入（§7.2/§7.5）                                                                                                                | PG16 集成（线程×2 + Barrier）                                                                | 不同`client_request_id` 双线程 trigger          | 恰好 1 个 result；另一线程 redirected=True                                                                                                                                                                               |
| R3 并发首次 success                                            | Transaction B PaperVersion 锁 + initial insert                                                                                                      | PG16 集成（预置两个 processing reservation，线程×2 终态 success）                            | barrier 对齐`_terminalize`                      | 恰好 1 个 active；另一 success inactive                                                                                                                                                                                  |
| R4 activation vs terminalization                               | 统一 §7 GLOBAL_LOCK_ORDER（PaperVersion → ProcessingResult → ActiveSelection），Transaction B 与激活同序取锁                                     | PG16 集成（线程：终态 success/partial × 显式激活；Barrier 对齐锁竞争点）                     | 确定性并发同步                                    | 无死锁；结果可串行化；active 指针绝不指向非终态/失败 result                                                                                                                                                              |
| R5 stale A + 新 B                                              | 准入 stale 例外（注入 now 使 A stale）                                                                                                              | service 集成                                                                                  | A reservation（伪造 created_at 旧值）→ B trigger | B 创建成功；A 保留 processing                                                                                                                                                                                            |
| R6 A 迟到终态于 B 后                                           | Transaction B 时点 activation 决策                                                                                                                  | PG16 集成                                                                                     | B 已 success+active；A 后终态 success             | A inactive；active 仍为 B；另有子用例：无 active 时 A MUST initial active                                                                                                                                                |
| R7 来源在 Transaction A 捕获的 expected_file_hash→read 间损坏 | 每次尝试重读重算（§10）；expected_file_hash 在 Transaction A 锁定 PaperVersion 时捕获，parser phase 用该不可变值与 freshly read bytes 重算结果比对 | service（fault injection：storage.read 返回篡改内容）                                         | 注入 mismatch                                     | failed + SOURCE_INTEGRITY_FAILURE + verified_source_hash=None + parser 未被调用                                                                                                                                          |
| R8 parser 后持久化失败                                         | Transaction B 回滚                                                                                                                                  | PG16（fault injection：`add_blocks` 抛 SQLAlchemyError）                                    | 注入失败                                          | 事务回滚；result 仍`processing`；无 children；无 completed 行                                                                                                                                                          |
| R9 partial blocks 成功 gaps 失败                               | 同事务原子性                                                                                                                                        | PG16（fault injection：`add_gaps` 抛错）                                                    | partial 输入 + 注入                               | 回滚后无 blocks 无 gaps，result 非 completed                                                                                                                                                                             |
| R10 success 终态 + initial active 失败                         | initial insert 同事务                                                                                                                               | PG16（fault injection：`upsert_active` 抛错）                                               | success 输入 + 注入                               | 回滚；无 completed success；无 active；reservation 保持 processing                                                                                                                                                       |

并发测试要求：PostgreSQL 16（沿用 `postgres16_service_engine`）、独立 `sessionmaker` Sessions、线程 + `threading.Barrier/Event` 同步；**不得**用 SQLite 声称 row-lock 语义。

## §19 Test architecture

### Unit（无 DB，`tests/services/test_source_processing_service.py` 内独立 class）

- `StaleClassifier`：边界（恰好等于 window 不算 stale / 超一秒算 stale；`completed` 永不算 stale）。
- `_runtime_fingerprint()`：键集合稳定、不含环境噪声。
- `_map_parse_result`：复用 `tests/services/fixtures/source_processing.py` 的 docx fixtures，分别构造 success/partial/failed `ParseResult`，断言行映射（failed → 0 blocks、保留 bounded gaps）。
- diagnostic 映射：四类失败的 `diagnostic_code` 与 metadata 白名单。
- `request_hash` 覆盖语义（fingerprint payload 纪律）：`TriggerProcessingFingerprintPayload` 中 `paper_version_id` / `parser_name` / `parser_version` / `parser_config` 任一变化 → hash 变；`client_request_id` 不在 payload 中，变化不影响 hash（它只作为 idempotency key 元组一维；同一 key 换 payload 才触发 conflict）。
- **parser phase DB-free**：断言 Transaction A commit 后 `session.in_transaction() == False`；`_execute_processing(context)` 期间任何 Session SQL / repository 调用都使测试失败（monkeypatch/spy）；返回后 `session.in_transaction() == False`；`_terminalize(...)` 可安全进入新的 `with self._session.begin()`。

### Service（PG16，`service_session` fixture）

- trigger → 成功终态（success：blocks、无 gaps、initial active）。
- partial：blocks+gaps 完整、inactive。
- parser failed：0 blocks、bounded gaps、SOURCE→`DOCUMENT_PARSE_FAILURE` 类别、never active。
- source read failed / hash mismatch（注入）。
- replay / conflict / reprocess（新 intent 产生新 result）。
- **trigger 返回类型一致性**：所有 `trigger_processing(...)` 分支（new terminal success/partial/failed、same-key replay processing、same-key replay terminal、admission redirect）MUST 返回 `TriggerProcessingResult`；不得直接返回 `ProcessingResultView`。
- 显式激活：partial 激活成功；failed/跨版本/非终态拒绝。
- reads：history 顺序、blocks 保序、gaps、active 视图、stale_indicator（注入 now）、failed blocks 空集。
- 幂等模板：replay 时 `replayed=True`。

### Activation idempotency tests（PG16 / service）

| #  | Scenario                       | Setup                                                                          | Required assertion                                                                                                                            |
| -- | ------------------------------ | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| A1 | same-key same-hash replay      | first activation succeeds；replay with same`client_request_id` + same target | no second mutation；exactly one activation idempotency key；exactly one`active_changed` audit；returns same target `ProcessingResultView` |
| A2 | same-key different target      | same`client_request_id`，different `processing_result_id`                  | `IDEMPOTENCY_CONFLICT`；no new mutation；existing key unchanged                                                                             |
| A3 | concurrent same-key activation | PG16，2 independent Sessions，Barrier/Event around SAVEPOINT insert/flush      | one durable activation key；one semantic active-selection mutation；one`active_changed` audit；other caller resolves as replay；no 500      |
| A4 | activation validation failure  | candidate failed / nonterminal / cross-PaperVersion / not-activatable          | outer transaction rollback；no durable activation idempotency key；no audit；active selection unchanged                                       |

### PostgreSQL integration（并发）

- R1–R10（见 §18 表）。

### Regression gates（来自仓库真实配置）

```powershell
python -m pytest tests/services/test_source_processing_parser.py -q
python -m pytest tests/services/test_source_processing_service.py -q
python -m pytest -q
ruff check src tests
mypy src
```

测试数据库环境沿用现有约定：`GONGKAO_APP_ENV=test`、`GONGKAO_DATABASE_URL=postgresql+psycopg://...@<host>:<port>/<disposable_test_db>`（PG16 校验已在 `tests/services/conftest.py` / `tests/migrations/conftest.py` 中内建）。

## §20 Fault injection plan

确定性注入（monkeypatch/替身，不污染 production 语义）：

| 注入点                                    | 方式                                         | 验证语义                                             |
| ----------------------------------------- | -------------------------------------------- | ---------------------------------------------------- |
| Source Reader error                       | 替身 reader 抛`SourceReadError`            | failed + SOURCE_READ_FAILURE + parser 未调用         |
| hash mismatch                             | 替身 reader 返回篡改 bytes                   | failed + SOURCE_INTEGRITY_FAILURE + hash=None        |
| parser exception                          | monkeypatch`parse_docx`                    | failed + INTERNAL_PROCESSING_FAILURE（可持久化路径） |
| block insert failure                      | monkeypatch`add_blocks` 抛 SQLAlchemyError | 全回滚 + reservation 保持 processing                 |
| gap insert failure                        | monkeypatch`add_gaps`                      | 同 R9                                                |
| audit insert failure                      | monkeypatch`AuditRepository.append`        | 同回滚（无终态半成品）                               |
| active-selection insert failure           | monkeypatch`upsert_active`                 | R10 回滚                                             |
| idempotency terminal-cache update failure | monkeypatch key 更新                         | Transaction B 回滚，不留半终态                       |

## §21 Audit-event plan

复用 `AuditRepository.append`（entity_type=`source_processing_result`）：

| Event                    | action_code                          | details（bounded）                                               | 标记                   |
| ------------------------ | ------------------------------------ | ---------------------------------------------------------------- | ---------------------- |
| processing accepted      | `source_processing.accepted`       | `paper_version_id`                                             | DERIVED_TECHNICAL_PLAN |
| processing terminalized  | `source_processing.terminalized`   | `result_status`, `block_count`, `gap_count`                | DERIVED_TECHNICAL_PLAN |
| active selection changed | `source_processing.active_changed` | `previous_processing_result_id?`, `new_processing_result_id` | DERIVED_TECHNICAL_PLAN |

details 中禁止 source text / URI / traceback / raw bytes。

## §22 Read-side plan

`ProcessingResultView` 组装字段：`processing_result_id`, `paper_version_id`, `execution_state`, `result_status`, `diagnostic_code`（=operator 安全类别）, `block_count`（`count_blocks` 聚合）, `gap_count`（`count_gaps` 聚合）, `is_active`, `stale_indicator`（注入 now + window）, `triggered_by`, `created_at`, `completed_at`。规则：failed → blocks 视图空集、gap 视图可见（bounded evidence）；partial active → 同视 `result_status='partial'` + gaps；读取确定性顺序：blocks `ORDER BY source_order`、gaps `ORDER BY source_order, id`、history `ORDER BY created_at, id`；不设计 frontend。

## §23 Schema compatibility recheck

| 计划义务                                   | 分类                                                             |
| ------------------------------------------ | ---------------------------------------------------------------- |
| S1 独立历史/终态不可变/children 归属       | SUPPORTED_WITH_SERVICE_LOGIC                                     |
| S2 受理即可见 reservation（Transaction A） | SUPPORTED_WITH_SERVICE_LOGIC                                     |
| S3 replay/conflict/reservation             | SUPPORTED_WITH_SERVICE_LOGIC                                     |
| S4 安全诊断                                | SUPPORTED_WITH_SERVICE_LOGIC                                     |
| S5 provenance                              | SUPPORTED（schema）+ SERVICE_LOGIC（fingerprint 填充）           |
| S6/S7 终态一致性与映射                     | SUPPORTED_WITH_SERVICE_LOGIC                                     |
| S8 active 不变量                           | SUPPORTED（PK + 复合 FK）+ SERVICE_LOGIC                         |
| S9 stale/interrupted 分类                  | DERIVABLE（`processing` + `created_at` + 注入 clock/window） |
| R1–R10 并发                               | SUPPORTED_WITH_SERVICE_LOGIC（行锁 + 唯一约束 + 事务边界）       |

```text
SCHEMA_GAP = NONE
SCHEMA_REDESIGN_REQUIRED = NO
MIGRATION_REQUIRED = NO
```

## §24 Implementation ordering（dependency-aware）

| Step                              | Files / symbols                                                                               | Preconditions | Tests                                          | Exit criteria                                               |
| --------------------------------- | --------------------------------------------------------------------------------------------- | ------------- | ---------------------------------------------- | ----------------------------------------------------------- |
| I1 repository/read infrastructure | `repository.py`（全部查询/锁方法）                                                          | 无            | repository 级 PG16 冒烟（插入/锁/查询）        | 方法可用、锁行为正确                                        |
| I2 stale + provenance helpers     | `StaleClassifier`, `_runtime_fingerprint`, `Settings` 字段                              | I1            | 单测                                           | 分类/指纹确定性                                             |
| I3 Transaction A / trigger        | `TriggerProcessing`, `trigger_processing`, admission, idempotency binding, accepted audit | I1, I2        | service trigger + R1/R2                        | reservation 原子、replay/conflict/redirect 正确             |
| I4 source integrity + parser      | parser phase（§10/§11）                                                                     | I3            | 注入 read/mismatch/parser 异常                 | 三类失败终态正确、hash 语义正确                             |
| I5 mapper + Transaction B         | `_map_parse_result`, `_terminalize`                                                       | I4            | success/partial/failed 持久化；R8/R9/R10 fault | 终态原子、映射保序                                          |
| I6 active selection               | `lock_active/upsert_active`, `activate_processing_result`                                 | I5            | R3/R4/R6；激活拒绝路径                         | initial/explicit 正确                                       |
| I7 read-side                      | 6 个读方法 + view 组装                                                                        | I5, I6        | read 单测                                      | failed 空 blocks、partial active 可见 gaps、stale_indicator |
| I8 failure/audit integration      | 失败映射收口、audit events                                                                    | I3–I6        | 注入 audit 失败回滚                            | 事件完整且 bounded                                          |
| I9 concurrency qualification      | R1–R10 线程矩阵                                                                              | I3–I8        | PG16 并发测试全绿                              | 竞态不变量全部验证                                          |
| I10 full regression               | §19 gates                                                                                    | I9            | 全部命令通过                                   | Plan 验收门槛达成                                           |

## §25 Future implementation branch / worktree proposal（仅提议）

```text
BRANCH_PROPOSAL = impl/20260913-wdv1-processing-service
WORKTREE_PROPOSAL = dedicated worktree for implementation

BRANCH_CREATED = NO
WORKTREE_CREATED = NO
```

未经后续明确授权，不创建分支/worktree。

## §26 Stop conditions

若真实实施需要以下任一项，STOP 并回到治理：改 S1–S10、改 approved Contract、改 Parser B1–B9、改 G-08、schema/migration、新 DB state、新 stale 产品语义、新自动 retry/recovery、需要 API/frontend/WDV1-004 才能解决当前 service 语义、需要新的产品决策。本 Plan 不擅自解决治理冲突。

---

## §A1 Plan self-audit

```text
PLAN_BINDS_FROZEN_DECISIONS_SHA = YES
PLAN_BINDS_CONTRACT_SHA = YES
PLAN_BINDS_API_BASELINE_SHA = YES

ACTUAL_API_CODE_INSPECTED = YES
ACTUAL_TEST_ARCHITECTURE_INSPECTED = YES
ACTUAL_TRANSACTION_CONVENTIONS_INSPECTED = YES

FILE_LEVEL_CHANGESET_DEFINED = YES
SYMBOL_LEVEL_PLAN_DEFINED = YES

TRANSACTION_A_PLAN_DEFINED = YES
R2_RUN_ADMISSION_PLAN_DEFINED = YES
SOURCE_INTEGRITY_PLAN_DEFINED = YES
PARSER_BOUNDARY_PLAN_DEFINED = YES
PERSISTENCE_MAPPING_PLAN_DEFINED = YES
TRANSACTION_B_PLAN_DEFINED = YES
ACTIVE_SELECTION_PLAN_DEFINED = YES
STALE_CLASSIFICATION_PLAN_DEFINED = YES
FAILURE_MAPPING_PLAN_DEFINED = YES
PROVENANCE_PLAN_DEFINED = YES
READ_SIDE_PLAN_DEFINED = YES
AUDIT_EVENT_PLAN_DEFINED = YES

R1_R10_TEST_MATRIX_DEFINED = YES
FAULT_INJECTION_PLAN_DEFINED = YES
POSTGRESQL_CONCURRENCY_TEST_REQUIREMENTS_DEFINED = YES
REGRESSION_GATE_PLAN_DEFINED = YES

NEW_PRODUCT_DECISION_INTRODUCED = NO
CONTRACT_SEMANTICS_CHANGED = NO
FROZEN_DECISIONS_CHANGED = NO

PRODUCTION_CODE_MODIFIED = NO
IMPLEMENTATION_STARTED = NO
```

---

## §A2 Team B approval history

```text
TEAM_B_PROCESSING_SERVICE_IMPLEMENTATION_PLAN_RE_REVIEW_2_STATUS =
APPROVE

P0_FINDINGS = 0
P1_FINDINGS = 0
P2_FINDINGS = 0

C1_SERVICE_CONTENT_SHA256_RECOMPUTATION = PASS
C2_END_TO_END_SYNCHRONOUS_ORCHESTRATION = PASS
C3_R1_SAVEPOINT_TEST_DESIGN_FEASIBLE = PASS
C4_ACTIVATION_TRANSACTION_BOUNDARY_CLOSED = PASS
C5_SYMBOL_INVENTORY_COMPLETE = PASS

SCHEMA_COMPATIBILITY = PASS
SCHEMA_REDESIGN_REQUIRED = NO
MIGRATION_REQUIRED = NO

NEW_PRODUCT_DECISION_INTRODUCED = NO
CONTRACT_SEMANTICS_CHANGED = NO
FROZEN_DECISIONS_CHANGED = NO

NOTE =
This approval record is retained for history but is
SUPERSEDED_FOR_IMPLEMENTATION_AUTHORIZATION_BY =
TEAM_B_PROCESSING_SERVICE_IMPLEMENTATION_PLAN_RE_REVIEW_4_APPROVAL
(Corrective Revision #4 has been approved and canonicalized).
```

---

## §A3 Team B Re-review #4 final approval record

```text
TEAM_B_PROCESSING_SERVICE_IMPLEMENTATION_PLAN_RE_REVIEW_4_STATUS =
APPROVE

BASE_PLAN_AUTHORITY =
e197b1371c58408fab2572dc7d434fbbbf5ffd4b

FROZEN_DECISIONS_AUTHORITY =
1f5e0ea23a235f23193d7821fff4bde8be7a7473

CONTRACT_AUTHORITY =
99433c824efd36ce515742642199a9e50c701e90

API_BASELINE =
85e20755f6069a4446f67417e2eff323b6a41674

M1_PARSER_INVOCATION_USES_CONTEXT = PASS
M1_STALE_RESERVATION_PARSER_REFERENCE_REMOVED = PASS

M2_BASE_PLAN_AUTHORITY_PRESENT = PASS
M2_STALE_GOVERNANCE_HEAD_WORDING_RESOLVED = PASS

M3_PARSER_CODE_MAP_WORDING_SYNCED = PASS
M4_IMPLEMENTATION_UNIT_SECTION_REFERENCES_SYNCED = PASS

C1_PARSER_PHASE_DB_FREE = PASS
C1_PROCESSING_CONTEXT_SOURCE_METADATA_COMPLETE = PASS
C1_SESSION_AUTOBEGIN_GAP_CLOSED = PASS

C2_TRIGGER_PUBLIC_RETURN_TYPE_UNIFIED = PASS
C2_ALL_TRIGGER_BRANCHES_RETURN_TRIGGER_PROCESSING_RESULT = PASS

C3_ACTIVATION_IDEMPOTENCY_GATE_DEFINED = PASS
C3_ACTIVATION_SAVEPOINT_RACE_RECOVERY_DEFINED = PASS
C3_ACTIVATION_REPLAY_NO_DUPLICATE_MUTATION = PASS
C3_ACTIVATION_REPLAY_NO_DUPLICATE_AUDIT = PASS
C3_ACTIVATION_REJECTION_ROLLS_BACK_KEY = PASS
C3_ACTIVATION_CONCURRENCY_TEST_DEFINED = PASS

GLOBAL_LOCK_ORDER =
PaperVersion → ProcessingResult → ActiveSelection

R1_R10_CORE_SEMANTICS_PRESERVED = PASS
STALE_MODEL_PRESERVED = PASS

P0_FINDINGS = 0
P1_FINDINGS = 0
P2_FINDINGS = 0
P3_FINDINGS = 0

SCHEMA_COMPATIBILITY = PASS
SCHEMA_REDESIGN_REQUIRED = NO
MIGRATION_REQUIRED = NO

NEW_PRODUCT_DECISION_INTRODUCED = NO
FROZEN_DECISIONS_CHANGED = NO
CONTRACT_SEMANTICS_CHANGED = NO
PARSER_AUTHORITY_CHANGED = NO
SOURCE_READER_AUTHORITY_CHANGED = NO

TEAM_B_REVIEW_VERDICT =
APPROVE
```

---

```text
IMPLEMENTATION PLAN = APPROVED
IMPLEMENTATION = NOT AUTHORIZED
IMPLEMENTATION_AUTHORIZED = NO
IMPLEMENTATION_STARTED = NO

PRE_IMPLEMENTATION_PREREQUISITE =
PROCESSING_API_IDEMPOTENCY_RESPONSE_SEMANTICS_CLOSURE

NEXT_AUTHORIZED_STAGE =
PROCESSING_API_IDEMPOTENCY_RESPONSE_SEMANTICS_CLOSURE

Production implementation MUST NOT begin until the
PROCESSING_API_IDEMPOTENCY_RESPONSE_SEMANTICS_CLOSURE
is completed under its own governance authority.
```
