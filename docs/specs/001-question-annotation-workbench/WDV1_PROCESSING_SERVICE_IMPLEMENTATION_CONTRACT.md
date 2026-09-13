# WDV1 Processing Service Implementation Contract

**STATUS = APPROVED（TEAM B CONTRACT RE-REVIEW PASS）。**

本文把已冻结的 `WDV1_PROCESSING_SERVICE_FROZEN_DECISIONS.md`（S1–S10）翻译为系统级技术契约。它不是 Implementation Plan，不授权任何 production code、schema migration、API、frontend 或 WDV1-004 工作。

```text
IMPLEMENTATION CONTRACT = APPROVED
IMPLEMENTATION PLAN = NOT YET CREATED
PROCESSING SERVICE IMPLEMENTATION = NOT AUTHORIZED
API IMPLEMENTATION = NOT AUTHORIZED
FRONTEND = NOT AUTHORIZED
WDV1-004 = NOT AUTHORIZED
```

Contract 的批准仅授权下一阶段 `PROCESSING_SERVICE_IMPLEMENTATION_PLAN_DRAFT`；在 Plan 评审与明确 implementation authorization 之前，不得开始任何 implementation。

### Team B review record

```text
TEAM_B_PROCESSING_SERVICE_CONTRACT_RE_REVIEW_STATUS = APPROVE

P0_FINDINGS = 0
P1_FINDINGS = 0
P2_FINDINGS = 0
P3_FINDINGS = 0

C1_INITIAL_ACTIVE_MAY_TO_MUST = PASS
C2_R2_RUN_ADMISSION_SERIALIZATION_CLOSED = PASS
C3_PERSISTENCE_FAILURE_LIFECYCLE_UNIFIED = PASS
C4_TRANSACTION_A_REQUIRED_PROVENANCE_COMPLETE = PASS
C5_MARKDOWN_TABLE_REPAIRED = PASS

COLLATERAL_SEMANTIC_DRIFT = NONE
NEW_PRODUCT_DECISION_INTRODUCED = NO
SCHEMA_REDESIGN_REQUIRED = NO
MIGRATION_REQUIRED = NO
```

---

## 1. Status and authority

### Governance authority（绑定，不得用聊天记忆替代）

```text
Frozen Decisions:
  docs/specs/001-question-annotation-workbench/WDV1_PROCESSING_SERVICE_FROZEN_DECISIONS.md
  main@1f5e0ea23a235f23193d7821fff4bde8be7a7473

G-08 authorities:
  WDV1_G08_FROZEN_DECISIONS.md
  WDV1_G08_IMPLEMENTATION_CONTRACT.md
  WDV1_G08_SCHEMA_TRANSACTION_DESIGN.md

Parser authorities:
  WDV1_STEP4_4B_PARSER_FROZEN_DECISIONS.md
  WDV1_STEP4_4B_PARSER_IMPLEMENTATION_PLAN.md
```

### API implementation baseline（实际代码检查对象）

```text
Judecoodingspace/gongkao-question-bank-api
main@85e20755f6069a4446f67417e2eff323b6a41674
```

本 Contract 基于对上述 SHA 处真实代码的只读检查（见 §3）。如后续 main 变化，契约映射需重新核对。

## 2. Scope

**In scope**：Processing Service 的不可违反契约——processing intent、lifecycle、source integrity、parser 调用边界、结果持久化映射、终态一致性、active-result、stale/interrupted、并发不变量、失败与诊断安全、provenance、schema 兼容性审计、逻辑服务接口。

**Out of scope（明确禁止作为本契约的依赖）**：题目语义拆分、自动建题/发布、OCR、图像提取、表格重建、公式转换、AI 补 gap、parser fallback、DOCX 修复、来源覆盖、视觉预览、WDV1-004、React、OpenAPI 层、自动最佳结果排序、worker 集群、自动重试调度、复杂异步编排。API HTTP 路由与状态码不在本契约冻结范围。

## 3. Existing implementation baseline（实际代码事实）

以下是对 API `main@85e2075` 的只读检查结论，是契约的代码事实基础：

| 关注点 | 实际代码事实 |
| --- | --- |
| `PaperVersion` | `src/gongkao_api/modules/papers/models.py`：`id, paper_id, version_number, file_name, file_type, file_hash(64), storage_uri, upload_status, parser_name/version/config(legacy), created_at, created_by`。本契约不写任何 `PaperVersion` 字段。 |
| `SourceProcessingResult` | `src/gongkao_api/modules/source_processing/models.py`：`id, paper_version_id, execution_state`（取值 `processing` / `completed`），`result_status`（`NULL` 或 `success` / `partial` / `failed`），`parser_name, parser_version, parser_config(JSONB), verified_source_hash(NULL或64位), runtime_fingerprint(JSONB), triggered_by, created_at, completed_at, diagnostic_code, diagnostic_metadata(JSONB)`。DB CHECK 强制 lifecycle 一致性。候选键 `UNIQUE(paper_version_id, id)`。 |
| `DocumentBlock` | `processing_result_id, source_order(>0, result 内唯一), block_type('text'), text_original`。 |
| `SourceProcessingGap` | `processing_result_id, source_order(>0), gap_type, source_region_kind, diagnostic_code, before/after_block_source_order(可空)`；`(processing_result_id, source_order)` 有索引。 |
| `PaperVersionActiveProcessing` | `paper_version_id` 为 PK；复合 FK `(paper_version_id, processing_result_id)` 指向 `source_processing_results(paper_version_id, id)`，`ON DELETE RESTRICT`；`selected_at, selected_by`。 |
| Source reading | `modules/papers/storage.py`：`PrivateSourceReader.read(storage_uri) -> SourceReadResult(content, size, sha256)`；`SourceReadError(code='SOURCE_READ_FAILED')`。URI 形如 `private://paper-versions/{id}.docx`；实现类只供开发/受控测试环境。 |
| Idempotency | `modules/idempotency/models.py` + `repository.py`：`IdempotencyKey(actor_id, operation_scope, client_request_id, request_hash(64), result_resource_type, result_resource_id, result_http_status, result_row_version, created_at)`；DB 唯一约束 `uq_idempotency_keys_actor_scope_client_request`；`request_hash()` 对 frozen dataclass command 做 canonical JSON + SHA-256；`lock_by_scope()` 使用 `SELECT ... FOR UPDATE`。 |
| Parser | `modules/source_processing/parser.py`：`parse_docx(bytes) -> ParseResult(blocks, gaps, status_candidate, diagnostics)`；`StatusCandidate` 取值为 `success` / `partial` / `failed`；`ParseResult.status_candidate == failed ⇒ blocks == ()`；diagnostics bounded、source-content-free；namespace-aware 分类；DOCTYPE/ENTITY 拒绝；archive 异常与 parser 异常分类隔离。 |
| 错误协议 | `api/errors.py`：`DomainRuleViolation` + `_DOMAIN_STATUS`（如 `SOURCE_STORAGE_UNAVAILABLE=503`, `IDEMPOTENCY_CONFLICT=409`）。 |
| 现有 service | 已存在 `PaperUploadService`（papers）、questions / source_materials services 使用 idempotency 模式。**不存在任何 Processing Service 实现**。 |

**未发现与治理假设的重大不符**：schema、idempotency、storage reader、parser 行为均与 G-08 Schema Transaction Design 和 STEP 4.4B 冻结语义一致。

## 4. Terminology

- **Processing Intent**：operator 明确触发一次处理的意图，由 `(actor_id, operation_scope='source_processing:trigger', client_request_id)` 标识，并由 `request_hash` 绑定其目标语义。
- **Processing Result**：`source_processing_results` 一行，一个 intent 对应一个 result identity。
- **execution_state**：`processing`（已接受、未终态）或 `completed`（终态）。不是第四来源结构化状态。
- **result_status**：终态语义 `success|partial|failed`；`processing` 期间必须为 NULL。
- **Terminal / terminalization**：transition 到 `completed` 且 result_status、completed_at、证据集合一致提交。
- **Active Selection**：`paper_version_active_processings` 的可变指针；不是质量状态。
- **Stale / Interrupted（产品级分类）**：`execution_state='processing'` 且存在时长超出预期处理窗口的派生分类；不改变 execution_state，不新增 DB 状态。
- **Same Intent Replay**：相同 `(actor, scope, client_request_id)` 且相同 `request_hash` 的请求重放。
- **Explicit Reprocess**：operator 在新的、明确的处理动作中使用新的 `client_request_id` 发起的新 intent。

## 5. Frozen Decision traceability（S1–S10）

| Frozen Decision | Contract Clause(s) | Existing Code / Schema Support | Missing Implementation Obligation |
| --- | --- | --- | --- |
| S1 重处理产生新历史结果 | §6, §7, §11 | `SourceProcessingResult` 独立行 + RESTRICT FK；无 UPDATE/DELETE 路径 | Service 必须只新增、不改写历史；终态后 result 及其 children 只读 |
| S2 正式受理即可见 processing | §6, §7 | lifecycle CHECK（processing ⇒ status/completed_at NULL） | Transaction A 原子创建 result + idempotency 绑定；受理前拒绝不得留痕 |
| S3 重复提交 vs 显式重处理 | §6, §15(R1/R2) | `idempotency_keys` 唯一约束 + `lock_by_scope` + `request_hash` | 实现 reservation 策略与 conflict/replay 语义（含 stale 例外） |
| S4 失败类别与安全诊断 | §12 | `diagnostic_code`/`diagnostic_metadata`(JSONB)；parser bounded diagnostics | 定义四类 contract 失败语义与安全持久化/暴露边界 |
| S5 可追溯性 | §16 | result 行全部 provenance 字段；blocks/gaps 表；active 表 | Service 填充 runtime_fingerprint 等；历史读取逻辑 |
| S6 success/partial/failed 可用性 | §10, §13 | status CHECK；block/gap 表；active 复合 FK | 持久化映射与下游使用不变量（failed 无 usable blocks 等） |
| S7 完成完整性 | §11 | Schema Design §8 两段式事务模型 | 实现 Transaction A/B 与原子性不变量 |
| S8 active 选择规则 | §13 | `PaperVersionActiveProcessing` PK + 复合 FK | 无 active 时 initial activation 为强制（MUST）并与终态原子提交；显式激活校验；无自动替换 |
| S9 中断/陈旧处理 | §14, §15(R5/R6) | 派生分类可行（`processing` + created_at）；无现成策略 | 实现陈旧分类与“不阻塞显式重处理”的不变量；超时数值等留待 Plan |
| S10 范围边界 | §2, §19 | 不适用（治理约束） | 无；任何越权能力不得进入 Plan |

## 6. Processing intent contract（A/B）

- **权威输入**：一次处理尝试的权威输入 = `actor_id` + `client_request_id` + `paper_version_id` + parser 身份（`parser_name` + `parser_version` + canonical `parser_config`）。
- **operation_scope**：固定为 `source_processing:trigger`（沿用 Schema Design §6）。
- **request_hash**：MUST 覆盖 canonical PaperVersion identity + parser name/version + canonical parser config 的规范化表示，输出 64 位十六进制（复用现有 `request_hash()` 机制）。精确 canonicalization 规则留待 Implementation Plan；本契约冻结其必须覆盖的语义内容。
- **同一 intent 重放**：相同 `(actor_id, operation_scope, client_request_id)` 且 `request_hash` 相同 ⇒ MUST 返回同一 Processing Result（无论其处于 `processing` 或 completed），MUST NOT 启动第二次 parser 执行，MUST NOT 创建第二条历史。
- **key 冲突**：相同 key 但 `request_hash` 不同 ⇒ MUST 以安全冲突失败（现有 `IDEMPOTENCY_CONFLICT` 语义），MUST NOT 静默改指 result。
- **显式重处理**：operator 新的明确处理动作 MUST 使用新的 `client_request_id` ⇒ 创建新的独立 Processing Result，即使 DOCX bytes 与配置完全相同。
- **正常进行中阻塞**：同一 `PaperVersion` 存在正常进行中的 `processing` result 时，MUST NOT 为其启动第二个并行 run；replay 被引导回现有 result。
- **PaperVersion 级 run 准入（same-PaperVersion admission control）**：在为某 `PaperVersion` 创建新 Processing Result 之前，Transaction A MUST 建立该 `PaperVersion` 级的准入串行化（与 G-08 Schema Transaction Design 的 `PaperVersion` 行锁权威一致；不冻结具体 SQL/ORM 语法）。在同一串行化决策范围内，服务 MUST 判定：
  1. 存在正常进行中的处理尝试 ⇒ 新 intent MUST NOT 创建另一 Processing Result；
  2. 仅存在 stale/interrupted 尝试（§14）⇒ 显式新 intent MAY 创建新 Processing Result；
  3. 不存在阻塞性处理尝试 ⇒ 显式新 intent MAY 创建新 Processing Result。
- **两层控制并存**：same-key idempotency（DB 唯一约束 + request_hash）与 same-PaperVersion 准入串行化是两项独立且都必须存在的不变量；前者不替代后者。
- **stale 例外**：既有尝试被产品级分类为 stale/interrupted（§14）后，MUST NOT 再阻塞显式重处理；但重放**同一旧 key** 仍 MUST 返回旧 result（stale 分类不改变 idempotency 归属）。
- **并发安全**：DB 唯一约束 `uq_idempotency_keys_actor_scope_client_request` 是最终防线；service 在唯一冲突时 MUST 重新读取既有 key 并按 replay/conflict 规则处理，MUST NOT 让唯一冲突逃逸为 500 或产生第二条 result。

## 7. Processing lifecycle / state contract（C/D）

- **合法状态**：`processing`（`result_status=NULL`, `completed_at=NULL`）→ `completed`（`result_status ∈ {success, partial, failed}`, `completed_at` 非 NULL）。不存在其他 transition；终态行及其 children MUST 不可变。
- **正式受理（S2）**：Transaction A 在单个事务中完成：取得该 `PaperVersion` 的准入串行化（见 §6 “PaperVersion 级 run 准入”）→ 锁定既有 idempotency key（若存在）→ 校验 `PaperVersion` 存在且 `upload_status='finalized'` → 创建满足全部 reservation-time NOT NULL 约束的 `SourceProcessingResult` 行（见下）→ 立即将 idempotency key 绑定到该 result（resource type `source_processing_result` + 预留的 in-progress 响应语义，见 §11）→ 提交。自提交完成起，该 result MUST 对历史查询可见。
- **Transaction A 创建的 reservation 行 MUST 满足的 schema 要求**：`paper_version_id`（目标 finalized 版本）、`execution_state='processing'`、`result_status=NULL`、`completed_at=NULL`、`parser_name`、`parser_version`、canonical `parser_config`、`runtime_fingerprint`、`triggered_by`、`diagnostic_metadata`（安全、bounded 的初始值，如空对象）；`verified_source_hash=NULL`（来源验证成功前不得写入）；`diagnostic_code=NULL`。不得发明新字段；`runtime_fingerprint` 的生成算法不在本契约冻结。
- **受理前拒绝**：请求未到达、校验失败、目标不存在等**受理前**失败 MUST NOT 创建任何 processing 历史记录（submission failure ≠ processing failure）。
- **受理后失败**：正式受理后，能够被安全、一致持久化的处理失败 MUST 以终态 `failed` 结果保留在历史中，并携带 §12 的安全失败类别。
- **持久化基础设施自身失败的例外**：若终态快照的持久化机制本身失败（无法安全写入 even 一个 `failed` 终态），系统 MUST NOT 伪造或部分持久化一个 completed 结果；Transaction B MUST 完整回滚，reservation 保持 `execution_state='processing'`（未提交可信终态快照），该尝试随后进入 §14 的 stale/interrupted 处理路径。operator 安全类别 INTERNAL_PROCESSING_FAILURE 仅适用于上述失败能够被实际持久化的场景（§12）。
- **operator-facing 状态**：仅暴露 `processing` / `success` / `partial` / `failed` 与 S9 的“处理异常 / 可能已中断”派生提示；技术子阶段 MUST NOT 成为 operator-facing 状态。

## 8. Source read & integrity contract（F）

- **前置条件**：`PaperVersion` MUST 存在且 `upload_status='finalized'`；否则 fail-closed（不产生 success/partial）。
- **读取**：MUST 通过 provider-neutral 的 `PrivateSourceReader.read(storage_uri)` 获取 `SourceReadResult(content, size, sha256)`；MUST NOT 解析/推导本地绝对路径，MUST NOT 把 `storage_uri` 写入日志或诊断。
- **完整性验证**：MUST 用当前读取的 bytes 重新计算 SHA-256 并与 `PaperVersion.file_hash` 比对。MUST NOT 在未重读重算的情况下信任存储 hash；MUST NOT 把未通过验证的 bytes 交给 parser。
- **不匹配（fail-closed）**：MUST NOT 运行 parser；MUST NOT 修改/“修复”/替换来源；结果 MUST 终态 `failed`，类别为 SOURCE_INTEGRITY_FAILURE（§12）。`verified_source_hash` MUST 保持 NULL（不得把不匹配的实际 hash 伪装成已接受 provenance）；验证结论以 `diagnostic_code` / bounded `diagnostic_metadata` 记录。
- **读取失败**：`SourceReadError` ⇒ 终态 `failed`，类别 SOURCE_READ_FAILURE；`verified_source_hash` 为 NULL。
- **验证通过**：`verified_source_hash` MUST 记录本次实际验证通过的 hash（与 `file_hash` 相等），包括后续 parser 失败的场景。

## 9. Parser invocation contract（边界）

- **Processing Service 负责**：加载 `PaperVersion`、读取私有来源 bytes、验证完整性、调用 parser、持久化 Result / Blocks / Gaps、应用 active-result 规则、写安全 audit。
- **Parser 负责**：仅对 bytes 做 Direct OOXML 解析并返回 `ParseResult`。Parser MUST NOT 访问 DB、MUST NOT 选择 active result、MUST NOT 修改 `PaperVersion` 或任何持久状态。
- Parser 的 B1–B9 冻结语义（含 `failed ⇒ blocks == ()`、bounded diagnostics）是本契约的输入事实，不得被 service 层重解释。

## 10. ParseResult → persistence contract（G）

- **状态映射（确定性）**：`status_candidate=success ⇒ result_status='success'`；`partial ⇒ 'partial'`；`failed ⇒ 'failed'`。不得叠加、合并或发明中间态。
- **Blocks**：仅 `success` / `partial` 持久化 `DocumentBlock`；按 `source_order` 保序；`block_type='text'`；`text_original` 原样保存（含空自然段的空字符串）。`failed` MUST 持久化 0 条 DocumentBlock。
- **Gaps**：`partial` MUST 持久化全部已知 gap；`success` gap 数为 0；`failed` MAY 持久化 parser 返回的 bounded、可靠 Gap evidence（含 source_order / region kind / before-after），仅作历史与审计，不得使结果可用。
- **诊断**：`failed` 的 `diagnostic_code` MUST 为 §12 四类之一（控制性失败类别）；`diagnostic_metadata` MUST 为 bounded JSONB，不得包含来源正文、raw XML、bytes、路径、URI、credentials、traceback 或原始异常文本。`success` 的 `diagnostic_code` MUST 为 NULL；`partial` MAY 为 NULL（逐 gap 诊断存在于 gap 行）。
- **provenance**：`parser_name` / `parser_version` / `parser_config`（canonical JSONB）与 `runtime_fingerprint`（小型 JSONB：Python 版本、direct-ooxml 实现版本、实际影响本路径的库版本）MUST 在终态时写入。
- **不得**创建任何语义题目实体、SourceSpan、page/bbox 或业务标签。

## 11. Completion / transaction consistency contract（S7）

采用 Schema Design §8 的两段式模型；本契约冻结其不变量：

- **Transaction A（reservation）**：语义同 §7。任何失败不得残留“半受理”状态。
- **Parser phase**：在数据库事务之外执行；来源内容 MUST NOT 进入日志或 DB（终态 success/partial 的 text blocks 除外）。
- **Transaction B（terminalization）**：锁定该 result 与其 `PaperVersion` 行（`FOR UPDATE`）后，在**单个事务**内完成：写入全部 blocks/gaps（按状态规则）→ 设置 `execution_state='completed'`、`result_status`、`completed_at` → 追加安全 audit event → 如需则更新 idempotency 响应缓存元数据 → 当 `success` 且当前无 active selection 时 MUST 同事务插入 initial active selection（无 active 时 initial activation 为强制，见 §13）。一次提交。
- **原子性不变量（任一不满足则整事务回滚，fail-closed）**：
  1. `success` 不得在任何预期 block 未持久化时成为终态；`success` 的已知 gap 必须为 0。
  2. `partial` 必须在全部可信 blocks 与全部已知 gaps 均持久化后才可终态。
  3. `failed` 不得伴随任何 usable DocumentBlock；bounded gap evidence 的存在不改变 failed 语义。
  4. initial active selection 不得指向 failed / 不存在 / 其他 `PaperVersion` 的 result。
  5. `completed_at`、status、children、audit 必须同事务一致。
- **回滚后果**：Transaction B 失败（包括终态快照持久化机制自身失败）⇒ 事务完整回滚，MUST NOT 留下任何终态半成品，MUST NOT 伪造或部分持久化一个 completed（含 `failed`）结果；reservation 保持 `execution_state='processing'`（未提交可信终态快照），交由 §14 stale 策略处理；operator 可在产品层判定中断后显式重处理（新 intent）。
- **idempotency 响应语义**：reservation 使用一个固定的、文档化的 accepted/in-progress 响应含义；终态时可更新缓存元数据到终态响应含义。具体 HTTP 数值属于 API 契约层，本契约只冻结“存在一个稳定 in-progress 含义 + 允许终态缓存更新”的不变量；该数值必须在 implementation 前于 API 契约中固定。

## 12. Failure & diagnostics contract（S4）

### Contract 级失败分类（语义冻结；名称可沿用仓库既有约定）

| Contract 类别 | 触发条件 | operator 语义（Frozen S4） |
| --- | --- | --- |
| SOURCE_READ_FAILURE | `PrivateSourceReader` 抛 `SourceReadError` / 读取不可用 | 来源当前不可用；重试或联系管理员 |
| SOURCE_INTEGRITY_FAILURE | 重算 SHA-256 ≠ `PaperVersion.file_hash` | 来源与记录原件不一致；停止并调查来源 |
| DOCUMENT_PARSE_FAILURE | parser 返回 `failed`（含 unsafe XML / 结构不可靠） | 当前系统无法建立可信来源结构 |
| INTERNAL_PROCESSING_FAILURE | 上述之外的、能够被安全持久化的 service 内部异常（如 parser 调用失败、终态写入前的业务内失败） | 系统侧失败；重试或联系管理员 |

- **持久化机制自身失败的分类边界**：若终态快照的持久化机制本身失败，系统不因此产生一个 terminal `failed` 行（Transaction B 完整回滚，reservation 保持 `processing`，见 §7 / §11）；INTERNAL_PROCESSING_FAILURE 作为已持久化 `failed` 结果的类别，仅适用于失败被实际、安全写入的场景。
- 持久化侧 MUST 只保存 `diagnostic_code` + bounded `diagnostic_metadata`；operator 可见表达 MUST 只来自上表类别；原始异常 message、traceback、绝对路径、`storage_uri`、raw XML、DOCX bytes、credentials、内部实现细节 MUST NOT 出现在 operator 响应、日志或 DB 诊断中。
- parser 诊断（B8）已有更严格规则的，从其规则。
- `failed` result MUST 保留失败历史与安全类别；永远不得通过普通读取路径暴露 usable blocks。

## 13. Active-result contract（S8 / G-08 P1·P2）

- **结构不变量**：每个 `PaperVersion` 至多一行 active selection（PK 保证）；复合 FK 保证 target 属于同一 `PaperVersion`（跨版本指向被 DB 拒绝）。
- **无 active 时**：若 `PaperVersion` 无 active result，新 `success` 终态 MUST 自动成为 initial active result，且 initial active selection MUST 与该 success 的 Transaction B 原子提交；新 `partial` MUST 保持 inactive，可后续显式采纳；`failed` MUST 永远不能 active。
- **已有 active 时**：后续 `success` / `partial` MUST 默认 inactive，不得静默替换；后续 `failed` MUST 不影响现有 active。
- **显式激活**：单一事务内锁定 `PaperVersion`、现有 selection 行与候选 result；候选 MUST 满足：属于该 `PaperVersion`、`execution_state='completed'`、`result_status ∈ {success, partial}`。以下情况 MUST 拒绝：failed result、其他 `PaperVersion` 的 result、不存在的 result、非终态 result。
- 切换 selection 只改指针 + `selected_at`/`selected_by` + audit；MUST NOT 修改 result、blocks、gaps、parser 元数据。
- 系统 MUST NOT 实现任何“最佳结果”自动推断。

## 14. Stale / interrupted processing contract（S9 / C1）

- **派生分类**：`execution_state='processing'` 且存在时长超过预期处理窗口 ⇒ 产品层分类为“处理异常 / 可能已中断”。窗口数值、检测机制（定时任务 / 惰性计算 / 心跳 / 租约）**不在本契约冻结**，留待 Implementation Plan；不得据此新增 DB 状态或自动恢复机制。
- **分类效果**：
  - 旧尝试保留为历史，不得删除或覆盖；
  - 旧尝试不再阻塞 operator 使用**新 intent**（新 `client_request_id`）显式重处理；新 intent 创建新 Processing Result；
  - 旧 key 的 replay 仍返回旧 result（idempotency 归属不变）。
- **迟到终态**：旧尝试之后产生迟到终态 MAY 持久化（Transaction B 规则不变）；MUST NOT 自动替换当前 active；MUST NOT 使更新 intent 产生的结果失效或被抢占。
- 当前 MVP MUST NOT 实现自动恢复、自动续跑、自动重试循环、后台调度或 worker 编排。

## 15. Concurrency / race invariants（R1–R10）

| # | 场景 | 必须成立的不变量 | 允许结果 | 禁止结果 |
| --- | --- | --- | --- | --- |
| R1 | 双击 / 同 intent 重放 | 唯一约束 + reservation 使同 key 只对应一个 result | 并发一方成功建立 reservation，另一方按 replay 返回同一 result | 两条 result、两次 parser 执行 |
| R2 | 同 PaperVersion、不同 intent 并发申请 processing run | Transaction A 的 PaperVersion 级准入串行化（§6）使同版本 run 准入决策串行化；正常进行中只能有一个 run | 在串行化决策内：遇正常进行中 ⇒ 新 intent 不创建 result 并被引导回现有 result；遇仅 stale/无阻塞 ⇒ 新 intent MAY 创建 result | 同一 PaperVersion 在正常进行中时并发产生第二个 Processing Result / 第二个 parser 执行 |
| R3 | 无 active + 两个 success 同时终态 | `PaperVersion` 行锁串行化 Transaction B；initial selection 仅插入一次，且无 active 时 success MUST initial activate | 第一个 success 成为 initial active；第二个保持 inactive | 两个 active、双 success 互相覆盖；success 终态时无 active 却未 initial activate |
| R4 | 显式激活与另一终态并发 | 激活事务锁定 PaperVersion + selection + 候选；终态事务同样持 PaperVersion 锁 | 串行后各自按规则提交 | 激活指向非终态/失败结果；半成品终态可见 |
| R5 | stale A + 显式重处理 B | B 使用新 key ⇒ 新 result；A 保留 processing | A、B 两条历史并存 | 因 A 的存在拒绝 B；或 A 被删除 |
| R6 | A 迟到终态于 B 之后 | 迟到终态按 Transaction B 规则提交；activation 取决于 A 终态时点的 active 状态：无 active 且 A 为 success ⇒ A MUST initial activate；已有 active ⇒ A MUST 保持 inactive | A 依上述规则成为 initial active 或 inactive 历史 | A 自动替换 B 的 active；A 使 B 失效；无 active 时 success 未 initial activate |
| R7 | 元数据读取与读取之间来源损坏 | 每次尝试 MUST 重读重算 hash；不匹配 ⇒ integrity failure | 安全 failed + SOURCE_INTEGRITY_FAILURE | 用缓存 metadata 直接信任；parser 消费损坏 bytes |
| R8 | parser 返回后持久化失败（含终态快照持久化机制自身失败） | Transaction B 完整回滚，无终态行；不得伪造/部分持久化 completed（含 failed）结果 | reservation 保持 `processing`，走 §14 stale 路径 | 终态 result 缺 children；blocks 落盘但 result 未 completed；出现部分持久化的 `failed` 行 |
| R9 | partial 的 blocks 成功、gaps 失败 | §11 原子性不变量 2 | 整事务回滚，无 partial 半成品 | 丢失 gaps 的“partial” |
| R10 | success 已持久化但 initial selection 失败 | §11 原子性不变量 4/5（同事务；无 active 时 success MUST initial activate） | 整事务回滚，result 未终态 | success 无 active 却被当作完成；无 active 时 success 未 initial activate；active 指向不存在 result |

## 16. Provenance / traceability contract（S5）

| Provenance 项 | 分类 |
| --- | --- |
| `paper_version_id` | ALREADY STORED（result 行） |
| `triggered_by` | ALREADY STORED |
| `created_at` / `completed_at` | ALREADY STORED |
| `parser_name` / `parser_version` / `parser_config` | ALREADY STORED（service 负责写入） |
| `verified_source_hash` | ALREADY STORED（语义见 §8） |
| `runtime_fingerprint` | ALREADY STORED（REQUIRES IMPLEMENTATION WIRING：填充策略） |
| `result_status` / `diagnostic_code` / `diagnostic_metadata` | ALREADY STORED |
| block count / gap count | DERIVABLE（blocks/gaps 表聚合） |
| active 关系 + `selected_at` / `selected_by` | ALREADY STORED |
| operator 历史视图字段 | REQUIRES IMPLEMENTATION WIRING（读取层组装，不新增列） |

注：上表 ALREADY STORED 指 schema 字段已存在；其中 `parser_name` / `parser_version` / `parser_config` / `runtime_fingerprint` / `diagnostic_metadata` 的值 MUST 在 Transaction A 创建 reservation 行时即按 §7 填充（schema 存在 ≠ 值可延迟到终态才写入）。

**SCHEMA GAP：NONE。**

## 17. Schema compatibility audit

| 契约义务 | 分类 |
| --- | --- |
| S1 独立历史 / 终态不可变 / children 归属 | SUPPORTED_BY_EXISTING_SCHEMA_WITH_SERVICE_WIRING |
| S2 受理即可见 reservation | SUPPORTED_BY_EXISTING_SCHEMA_WITH_SERVICE_WIRING（idempotency 响应语义需实现层固定，见 §11） |
| S3 replay / conflict / reservation | SUPPORTED_BY_EXISTING_SCHEMA_WITH_SERVICE_WIRING（唯一约束 + request_hash + 两段式绑定） |
| S4 安全诊断 | SUPPORTED_BY_EXISTING_SCHEMA_WITH_SERVICE_WIRING |
| S5 provenance | SUPPORTED_BY_EXISTING_SCHEMA_WITH_SERVICE_WIRING（runtime_fingerprint 填充） |
| S6 / S7 终态一致性与映射 | SUPPORTED_BY_EXISTING_SCHEMA_WITH_SERVICE_WIRING |
| S8 active 不变量 | SUPPORTED_BY_EXISTING_SCHEMA（PK + 复合 FK）+ SERVICE_WIRING |
| S9 stale/interrupted 派生分类 | DERIVABLE（`processing` + `created_at`）；策略与窗口留待 Plan |
| 并发控制（R1–R10） | SUPPORTED_BY_EXISTING_SCHEMA_WITH_SERVICE_WIRING（行锁 + 唯一约束 + 事务边界） |

```text
SCHEMA_REDESIGN_REQUIRED = NO
MIGRATION_REQUIRED = NO
```

## 18. Required logical service interfaces（不规定代码名与路由）

最小逻辑能力集（与 G-08 P3 对齐，不超出 Frozen Decisions 需求）：

1. `trigger_processing` — 受理 intent，返回 result identity（replay 返回同一 identity）。
2. `get_processing_result` — 读取单个 result 的业务视图（status、计数、active 指示、安全失败类别）。
3. `list_processing_results` — 按 PaperVersion 读取处理历史。
4. `get_processing_blocks` — 按稳定 `source_order` 读取指定 result 的 text blocks（`failed` 返回空集）。
5. `get_processing_gaps` — 读取指定 result 的 gap evidence（含 failed 的 bounded evidence）。
6. `get_active_processing` — 读取当前 active result（partial 必须同视携带 gap evidence）。
7. `activate_processing_result` — 显式、受控切换 active（校验规则见 §13）。

不定义 HTTP method / path / status code；不定义前端行为。

## 19. Explicit non-goals

同 Frozen Decisions S10 + 本契约 §2 Out of scope。特别重申：不得实现题目语义识别、自动建题 / 发布、OCR、图像 / 表格 / 公式能力、AI 补 gap、parser fallback、DOCX 修复、来源覆盖、视觉预览、WDV1-004、React、OpenAPI 层、最佳结果排序、worker 集群、自动重试 / 恢复调度。

## 20. Stop conditions

出现以下任一情况，Contract 评审 / 后续 Plan MUST STOP 并回到治理：与 G-08 或 Frozen Decisions 冲突；实际代码与治理假设重大不符；需要 schema 重设计才能表达 S1–S10；S3/S9 语义需要新的未决议产品决策；failed/partial 语义与 parser B1–B9 冲突；active 规则与既有 authority 冲突；需要 API / 前端 / 视觉预览能力才能满足契约；需要新的产品决策。

## 21. Verification obligations for the future Implementation Plan

Plan MUST 规定（本契约不规定其具体实现）覆盖以下验证：§15 R1–R10 各有对应并发 / 集成测试；source integrity 匹配与不匹配；四类失败的持久化与安全暴露；idempotency replay / conflict / reservation 生命周期；stale 分类与新 intent 共存及迟到终态；active 初始激活、显式激活拒绝路径（failed / 跨版本 / 非终态）；Transaction B 回滚不产生半成品；parser 边界（无 DB 访问）；synthetic fixtures 不扩大能力范围。

## 22. Next governance stage

```text
NEXT_AUTHORIZED_STAGE =
PROCESSING_SERVICE_IMPLEMENTATION_PLAN_DRAFT
```

Contract 已获 Team B re-review 批准（APPROVE）。Implementation Plan 现在可以起草；但 implementation 本身在 Plan 评审与明确 implementation authorization 之前仍为 NOT AUTHORIZED。
