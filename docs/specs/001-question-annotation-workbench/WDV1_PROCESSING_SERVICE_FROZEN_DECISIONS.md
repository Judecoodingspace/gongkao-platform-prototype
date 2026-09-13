# WDV1 Processing Service Frozen Decisions

**状态：APPROVED / FROZEN（产品决策基线）。**

```text
PROCESSING_SERVICE_FROZEN_DECISIONS = APPROVED / FROZEN

PROCESSING SERVICE FROZEN DECISIONS ONLY

IMPLEMENTATION CONTRACT = NOT YET APPROVED
IMPLEMENTATION PLAN = NOT YET AUTHORIZED
PROCESSING SERVICE IMPLEMENTATION = NOT AUTHORIZED
API = NOT AUTHORIZED
FRONTEND = NOT AUTHORIZED
WDV1-004 = NOT AUTHORIZED
```

本文冻结 **Processing Service 的产品 / 服务行为**。它授权的唯一下一阶段是 `PROCESSING_SERVICE_IMPLEMENTATION_CONTRACT_DRAFT`，除此之外不授权任何 implementation、API、前端、视觉预览、OCR、schema 变更或 WDV1-004 工作。

---

## 1. Status

- 本文档状态：**APPROVED / FROZEN**，由 Product Owner re-review 批准。
- 本文档只冻结 **Processing Service 的产品 / 服务行为**。
- 本文档**不授权** Implementation Contract、Implementation Plan、Processing Service 实现、API / OpenAPI、React / 前端、视觉预览、OCR、图像提取、表格重建、公式转换或 WDV1-004。
- 本文档**不规定** SQLAlchemy 写法、事务边界、锁、类 / 函数名、FastAPI endpoint、request hash 算法、worker / queue 架构等技术实现细节。
- 本切片稳定名称：**Processing Service**。不引入新的 STEP 编号（如 4.4C）。

## 2. Authority

### 治理仓库

```text
Judecoodingspace/gongkao-platform-prototype
main
```

本文依据的主要权威文件：

```text
docs/specs/001-question-annotation-workbench/WDV1_STEP4_4B_PARSER_FROZEN_DECISIONS.md
docs/specs/001-question-annotation-workbench/WDV1_STEP4_4B_PARSER_IMPLEMENTATION_PLAN.md
docs/specs/001-question-annotation-workbench/WDV1_G08_FROZEN_DECISIONS.md
docs/specs/001-question-annotation-workbench/WDV1_G08_IMPLEMENTATION_CONTRACT.md
docs/specs/001-question-annotation-workbench/WDV1_G08_SCHEMA_TRANSACTION_DESIGN.md
```

### API 仓库当前权威状态

```text
Judecoodingspace/gongkao-question-bank-api
main@85e20755f6069a4446f67417e2eff323b6a41674
```

已完成并闭合的切片：

```text
STEP 4.4A Source Reader = CLOSED
STEP 4.4B Direct OOXML Parser = CLOSED
POST_MERGE_CLOSURE_STATUS = COMPLETE
APPROVED_IMPL_SHA_IN_MAIN = YES
```

当前状态：

```text
PROCESSING_SERVICE_IMPLEMENTED = NO
PROCESSING_SERVICE_AUTHORIZED = NO
WDV1_003_COMPLETE = NO
G08_COMPLETE = NO
WDV1_004_COMPLETE = NO
```

## 3. Objective

Processing Service 当前切片的唯一产品目标是：

> 将一次被系统正式接受的 DOCX 处理意图，转化为一个完整、可追溯、可持久使用的 Processing Result。

本文回答：

- 产品必须表现成什么样；
- 哪些行为允许、哪些行为禁止；
- 什么算 success / partial / failed / 重复 / 可恢复；
- 历史结果如何保留；
- 当前使用结果（active result）如何选择。

本文不回答任何技术实现问题；这些问题全部留给后续 Implementation Contract 与 Implementation Plan。

## 4. Existing frozen semantics that remain authoritative

以下已冻结语义继续有效，本文不覆盖、不重编号、不重新解释：

1. **G-08 Frozen Decisions**
   - 双层派生表示：视觉层与来源结构层互补；原始 DOCX 是唯一权威来源。
   - 自然结构块：`DocumentBlock` 边界来自文档自身自然结构，而非业务语义。
   - 独立处理历史与 active result：同一 `PaperVersion` 可被多次人工触发处理；每次 result 独立、只读保留；首次成功可成为 initial active；后续切换必须明确受控。
   - WDV1-003 text-first 分片与状态语义（success / partial / failed）。
   - WDV1-003 Gap = 当前 text-first 能力边界证据，不是永久不支持分类。

2. **G-08 Implementation Contract（D1–D6、P1–P3）**
   - 只接受已 finalized 的 `PaperVersion`；原始 bytes、hash、storage reference 不可变。
   - parser / service 通过只读私有来源存储抽象取得 bytes。
   - 处理前必须重新计算 SHA-256 并与 `PaperVersion.file_hash` 比对；不一致时返回安全 integrity failure。
   - 每次人工处理形成独立 immutable processing result；历史只读保留。
   - P1：partial 默认 inactive，可显式激活；failed 永远不可 active；后续 success 不自动替换 partial active。
   - P2：无 active 时新 success 自动成为 initial active；已有 active 时新结果默认 inactive。
   - P3：WDV1-003 须交付最小 backend contract（trigger / read result / read blocks / read active / activate）。

3. **STEP 4.4A Source Reader boundary** 与 **STEP 4.4B Parser Frozen Decisions（B1–B9）**
   - bytes-only parser 边界、source_order 规则、自然段级 block、Gap 语义、status 推导、diagnostics 安全与确定性。

4. **G-08 Schema Transaction Design**
   - 既有 schema（DocumentBlock / SourceProcessingGap / SourceProcessingResult）足以承载当前切片；本文不要求任何 schema 重新设计。

## 5. S1–S10 Processing Service Decisions

### S1 — Reprocessing creates a new historical result

- **Decision**：一次明确的 operator 重新处理动作 = 一个新的、独立的 Processing Result。
- **Product rationale**：历史必须完整保留，任何一次处理结果都不应因后续处理而被覆盖或改写。
- **Allowed behavior**：同一 `PaperVersion` 下保留多个独立结果；每个结果拥有自己的 status、usable blocks、gaps、processing metadata 与 traceability 信息；原始 `PaperVersion` 仍是唯一 source artifact。
- **Forbidden behavior**：不得覆盖、改写或删除既有结果；不得把重新处理当作 `PaperVersion` 的新版本；不得把 active result 与历史结果混为一谈。
- **Examples**：`PaperVersion ├─ Result A ├─ Result B └─ Result C (active)`。
- **Relationship to existing authority**：与 G-08 第 3 节“独立处理历史与 active result”一致；不改变 G-06 / G-07 原始 DOCX 不变性。

### S2 — When processing officially starts

- **Decision**：系统正式接受 operator 的处理请求后，operator 必须立即能在处理历史中看到一个 `processing` 状态的记录。
- **Product rationale**：operator 提交后应立即获得“已受理”的可见反馈；submission failure ≠ processing failure。
- **Allowed behavior**：请求被正式接受 → 立即产生可见的 processing 记录 → 最终收敛到 success / partial / failed。
- **Forbidden behavior**：未被正式接受的请求（未到达系统、受理前被拒绝、目标 `PaperVersion` 不存在、请求无效）不得进入处理历史；不得把 reading / hashing / parsing / persisting 等技术子阶段暴露为 operator-facing 状态。
- **Examples**：operator 点击“开始处理”后历史列表立即出现一条 `processing` 记录。
- **Relationship to existing authority**：与 G-08“人工明确触发一次独立处理”一致。

### S3 — Duplicate submission vs explicit reprocessing

- **Decision**：必须区分“同一处理意图的意外重复”与“新的明确重新处理意图”。
- **Product rationale**：意外重复不得污染历史；真实重新处理必须保留历史。
- **Allowed behavior**：
  - 同一已接受意图的重放（双击、网络重试、浏览器 / 客户端重发、同一已接受用户意图的重放）映射到同一个 Processing Result，不得创建重复处理历史。
  - **“不启动第二个并行处理 run”的规则仅适用于：同一 `PaperVersion` 已有一个仍被视为正常进行中的（normally in progress）`processing` 状态结果。** 此时 operator 被引导回现有 in-progress 结果。
  - 上一次处理尝试达到终态（success / partial / failed）后，operator 明确选择 reprocess，才创建新的 Processing Result。
  - **例外（与 S9 衔接）：一旦既有处理尝试按 S9 在产品层被分类为“处理异常 / 可能已中断”，它不再阻止 operator 明确发起新的 reprocessing 意图。** 该明确意图创建新的 Processing Result；旧的中断尝试保留在处理历史中。
- **Forbidden behavior**：
  - 不得为同一意图的意外重放创建重复历史。
  - 在既有尝试仍正常进行中时，不得为同一 `PaperVersion` 启动第二个并行 processing run（当前 MVP）。
  - 本文档不决定：stale 的技术检测方式、是否新增数据库状态、锁机制、并发控制方式、心跳、租约、超时数值、事务机制——这些留给后续 Implementation Contract / Implementation Plan。
- **Examples**：双击“开始处理”只产生一条历史记录；处理中再次点击被引导回进行中的记录；进行中记录被标记为“可能已中断”后，operator 可明确重新处理并产生新记录，旧记录保留。
- **Relationship to existing authority**：与 Implementation Contract 的 processing-intent idempotency（同一人工 intent 的技术重放不创建第二条 result）一致；与 G-08 第 3 节独立处理历史一致。

### S4 — Operator-visible failure categories

- **Decision**：失败的处理尝试必须保留在处理历史中，且 operator 可见的失败信息必须 stable / understandable / actionable / safe。
- **Product rationale**：operator 需要知道失败类别以便采取行动；技术诊断细节留在内部。
- **Allowed behavior**：至少区分四类 operator-facing 失败：
  1. **Source file cannot be read**（来源当前不可用；重试或联系管理员）
  2. **Source integrity verification failed**（来源与记录的原件不一致；停止并调查来源）
  3. **Document cannot be reliably parsed**（当前系统无法建立可信来源结构）
  4. **Internal system processing failed**（系统侧失败；重试或联系管理员）
- **Forbidden behavior**：不得向 operator 暴露 raw exception message、traceback、绝对路径、storage URI、raw XML、DOCX bytes、credentials 或内部实现细节。
- **Examples**：operator 看到“解析失败：文档无法可靠解析”，而不是栈信息。
- **Relationship to existing authority**：与 Implementation Contract 的 integrity failure 语义及 B8 diagnostics 安全要求一致。

### S5 — Processing history traceability

- **Decision**：每个 Processing Result 必须可独立追溯。
- **Product rationale**：operator 审查历史时应能理解处理了哪个来源版本、谁触发、何时、结果如何、有多少可用结构、是否存在 gap、是否为当前 active。
- **Allowed behavior**：默认 operator 历史视图优先展示业务相关信息（time / status / operator / block count / gap count / active indicator）；技术 provenance（parser identity / version、source integrity provenance、processing configuration provenance）必须保留，可出现在 details / admin view / technical traceability section。
- **Forbidden behavior**：不得因存在更新的结果而改写历史记录；技术细节不得主导默认 operator 视图。
- **Examples**：历史列表展示“2026-09-10 07:29，解析成功，120 个块，0 个 gap，当前使用中”。
- **Relationship to existing authority**：与 G-08 第 3 节及 Implementation Contract 的 traceability 元数据要求一致。

### S6 — Meaning and usability of success / partial / failed

- **Decision**：三种结果状态由 operator 下一步被允许做什么来定义。
- **Product rationale**：partial = 可用但必须显式知晓 gap；failed = 不可作为来源结构使用。
- **Allowed behavior**：
  - **success（解析成功）**：在当前能力边界内可信且完整；可用于下游人工拆题；可成为 active；无需额外 gap 确认。
  - **partial（解析部分完成）**：发出的可用结构可信，但存在明确已知 gap；可用于下游人工工作，但必须带可见 gap 提醒；operator 可查看 gap；采纳为 active 前必须做出知情选择；不得以 success 的方式呈现。
  - **failed（解析失败）**：
    - 该次处理尝试未建立足够可信的来源结构；
    - 不得用于下游人工拆题；
    - 不得成为 active；
    - 仅可查看失败信息（S4 的安全失败类别）；
    - 此后 operator 可：**明确重新处理同一个不可变的 `PaperVersion`**；或者，**若来源文件本身错误 / 损坏、确需更正来源，则使用既有 source-version 工作流创建 / 使用一个新的、正确的 `PaperVersion`**。
    - **不可变来源语义（必须明确）**：既有 `PaperVersion` 的 bytes 不会被静默编辑；既有来源 hash 不会被重写；既有来源 artifact 不会被原地替换；历史来源版本保持保留。
    - 本文档不设计 `PaperVersion` 创建 API 或上传流程。
- **Forbidden behavior**：不得把 partial 呈现为 success；不得把 failed 作为可用 source structure 或 active；不得暗示可以原地修改既有 `PaperVersion`。
- **Examples**：partial 结果在列表中带 gap 数量与“部分完成”标签。
- **Relationship to existing authority**：与 G-08 第 6 节状态语义及 P1 / P2 完全一致；与 G-06 / G-07 原始 DOCX 不变性一致。

### S7 — Completion integrity

- **Decision**：处理结果不能因为 parser 逻辑返回就被视为完成；终态结果必须构成一个完整、内部一致的产品结果。
- **Product rationale**：success / partial / failed 必须是完整结果，而不是部分落盘的中间态。
- **Allowed behavior**：终态 = final outcome + usable source structure + gap evidence + 必要 failure / diagnostic 信息 + history / provenance 信息。success 不得在 usable content 只保存了一部分时显示为完成；partial 必须包含全部可信可用内容与全部已知相关 gap；failed 必须保留失败历史与安全可操作类别，且不得把不可信内容暴露为可用 source structure。
- **Forbidden behavior**：当完整产品结果无法一致形成时，不得告诉 operator 该次尝试已成功或部分完成。
- **failed 中 usable Blocks 与可靠 bounded Gap evidence 的区分（与已批准 Parser 行为一致）**：
  - usable Blocks 不得提供给下游人工拆题工作；
  - failed 永远不得被视为“部分可用”的来源结果（failed ≠ partial）；
  - 若系统仍能可靠识别 bounded 的 gap / location evidence，该 Gap evidence 可保留在历史结果中，仅用于解释与审计；
  - 保留该 Gap evidence **不**使结果变为可用，也**不**把 failed 变成 partial。
- **关键语义**：failed → 无可供下游使用的 Blocks；failed → 可保留安全、有界、可靠的 Gap evidence 用于历史 / 诊断；failed → 仍为 failed；failed → 永远不能 active。
- **Examples**：gap 信息丢失的 partial 不是合法完成的 partial。
- **Relationship to existing authority**：与 STEP 4.4B parser 的 fail-visible / failed 不暴露 usable blocks 语义一致；不规定事务实现方式；不改变 Parser 已冻结的 B1–B9 行为；不引入新的 Gap 类别。

### S8 — Active result selection

- **Decision**：active result = 当前默认用于下游工作的 processing result；不代表 latest / best / 最高分 / 自动偏好。
- **Product rationale**：newer ≠ automatically adopted；系统不得自动推断哪个历史结果“最好”。
- **Allowed behavior**：
  - 无 active：新 success 自动成为 initial active；新 partial 不自动 active，operator 查看 gap 后可显式采纳；新 failed 永远不能 active。
  - 已有 active：后续 success / partial 不得静默替换；后续 failed 不得影响当前 active；任何切换必须是明确的 operator 决策。
- **Forbidden behavior**：不得静默替换 active；不得自动选择“最优”结果。
- **Examples**：首次解析成功后该结果自动成为当前使用结果；再次解析成功后仍需人工切换。
- **Relationship to existing authority**：与 G-08 第 3 节、P1、P2 完全一致。

### S9 — Interrupted / stale processing

- **Decision**：Processing Result 不得永久以 `processing` 状态面向 operator。
- **Product rationale**：被接受但长时间未达到终态的尝试，operator 必须能理解其可能已中断，并被允许重新处理。
- **Allowed behavior**：
  - 超过合理处理窗口未达终态 → operator 可见“处理异常 / 可能已中断”（S9 的产品层分类）。
  - 被中断的尝试保留在处理历史中，不得删除或覆盖。
  - **被分类为“处理异常 / 可能已中断”的尝试，不再阻止 operator 明确发起新的 reprocessing 意图（与 S3 衔接）。** operator 明确重新处理后，创建新的 Processing Result；旧的中断尝试保留在历史中。
  - 若旧的中断尝试之后产生迟到终态：可作为历史结果保留，但不得自动替换当前 active result，也不得干扰更新的、由 operator 发起的处理尝试。
- **Forbidden behavior**：当前 MVP 不要求自动恢复、自动续跑、自动重试循环、后台重试调度器或 worker 恢复编排；本文档不决定 stale 检测的技术机制、超时数值、锁、心跳、租约、事务或并发控制方式。
- **Examples**：一条 `processing` 记录超过窗口后显示“可能已中断”；operator 明确点击重新处理 → 产生新记录；旧记录保留在历史列表中。
- **Relationship to existing authority**：不与任何已冻结语义冲突；与 S3 的并行处理限制规则相互衔接（正常进行中 → 阻塞；产品层判定为中断后 → 不再阻塞明确重新处理）。

### S10 — Processing Service scope boundary

- **Decision**：当前 Processing Service 的职责限于 S1–S9 所列；其余一律显式排除。
- **Product rationale**：保持切片最小且诚实，不允许视觉预览等需求扩大本切片范围。
- **Allowed behavior（职责内）**：接受处理意图；维护处理历史；操作正确的来源版本；验证来源完整性；调用已批准 parser；记录 success / partial / failed；保存可信 Blocks / Gaps / 失败信息；应用已冻结的 active-result 规则。
- **Forbidden behavior（职责外）**：
  - 自动业务语义识别（题干 / 材料 / 问题 / 作答要求 / 答案 / 知识点 / 题型）；
  - 自动创建 / 提交 / 发布正式题目；
  - OCR、图像内容提取、复杂表格重建、公式转换；
  - AI 补 gap、parser fallback chain、自动 DOCX 修复、来源替换；
  - 自动“最佳结果”选择；
  - 复杂后台任务队列、worker 集群、自动重试、自动恢复调度、优先级调度；
  - API / OpenAPI、React / operator frontend、视觉预览、WDV1-004；
  - 不得为让处理成功而修改或替换原始来源文件。
- **Examples**：API 与前端是未来必需的 E2E 层，但不属于本 Processing Service 切片。
- **Relationship to existing authority**：与 G-08、STEP 4.4A / 4.4B 的范围边界一致。

### Product flow（S1–S10 共同定义）

```text
Operator explicitly requests processing
        ↓
System formally accepts intent
        ↓
Visible Processing Result = processing
        ↓
Use the correct source version
        ↓
Verify source integrity
        ↓
Invoke approved Parser
        ↓
Obtain: success / partial / failed
        ↓
Form a complete historical Processing Result
        ↓
Apply active-result rules
        ↓
Operator may:
- continue downstream manual work
- inspect gaps
- inspect failure
- explicitly reprocess
- explicitly switch active result where allowed
```

该流程只描述产品行为，不描述实现机制。

## 6. Operator-visible state model

| Operator-facing 状态 / 概念 | 含义 | operator 可以做什么 |
| --- | --- | --- |
| `processing`（处理中） | 请求已被正式接受，正在收敛到终态 | 查看进度；等待；不被允许对同一 `PaperVersion` 并行发起第二次处理 |
| `success`（解析成功） | 当前能力边界内可信且完整 | 用于下游人工工作；可成为 active |
| `partial`（解析部分完成） | 可用结构可信，但存在明确 gap | 带 gap 感知使用；可查看 gap；可显式采纳为 active |
| `failed`（解析失败） | 未建立足够可信的来源结构 | 查看失败类别；重新处理或经 source-version 工作流使用新 `PaperVersion`；不可使用、不可 active |
| 处理异常 / 可能已中断 | 已接受但超过合理窗口未达终态（S9） | 理解为可能中断；明确重新处理；历史保留 |

补充规则：

- 未被正式接受的提交失败不进入处理历史（S2）。
- 失败信息的 operator 表达只能是 S4 的安全类别，技术诊断留在内部受控视图。
- 技术子阶段（reading / hashing / parsing / persisting）不作为 operator-facing 状态暴露。

## 7. Historical result / active result product semantics

- **历史结果**：独立、只读、不可覆盖；每个结果有自己的 status、usable blocks、gaps、processing metadata 与 traceability；重新处理只新增，不改写。
- **active result**：
  - 无 active + 新 success → 自动成为 initial active；
  - 无 active + 新 partial → 默认 inactive，可显式采纳；
  - 新 failed → 永远不能 active；
  - 已有 active 时，任何后续结果默认 inactive，切换必须明确、受控；
  - 任一 `PaperVersion` 同时最多一个 active result（与 G-08 P1 / P2 一致）。
- **迟到终态的中断尝试**：保留为历史；不自动替换 active；不干扰新的处理。

## 8. Explicit non-goals

本切片明确不做：

- Processing Service 实现本身（本文通过后仍需 Implementation Contract → Implementation Plan → 明确授权）；
- API / OpenAPI、React / operator frontend；
- 视觉预览、visual / source linking、WDV1-004；
- OCR、图像提取、复杂表格重建、公式转换；
- AI 语义推断、自动建题 / 提交 / 发布、字段填入、SourceSpan；
- 自动“最佳结果”选择；
- 后台任务队列 / worker 集群 / 自动重试 / 自动恢复调度 / 优先级调度；
- 修改或替换原始来源文件；
- schema 重新设计或 migration。

## 9. Deferred technical decisions

以下事项**明确留给** Implementation Contract 与后续 Implementation Plan，本文不冻结：

- service function signatures
- ORM loading pattern
- database locks
- transaction boundaries
- request_hash algorithm
- idempotency-key storage mechanism
- timeout value
- stale-detection mechanism
- runtime fingerprint representation
- diagnostic persistence schema details
- specific endpoint routes
- HTTP status codes
- background worker architecture
- specific test fixture implementation

## 10. Stop conditions

出现以下任一情况必须停止并回到治理评审，不得自行发明产品行为绕过：

- S1–S10 与已冻结的高层产品决策冲突；
- 既有 schema 无法在不重新设计的前提下表达本文冻结的产品行为；
- 实施这些决策需要 WDV1-004 或视觉预览；
- 实施需要 OCR / 图像 / 表格 / 公式能力；
- 关键产品决策仍存在歧义。

## 11. Next governance stage

本文档获批后，唯一被授权的下一阶段：

```text
PROCESSING_SERVICE_IMPLEMENTATION_CONTRACT_DRAFT
```

治理顺序：

```text
Frozen Decisions
→ Implementation Contract
→ Contract Review
→ Implementation Plan
→ Plan Review
→ Explicit Implementation Authorization
```

本文档的批准不授权 Implementation Contract 之外的任何工作。

## Final summary

```text
FROZEN_DECISIONS_APPROVED = YES

PROCESSING_SERVICE_FROZEN_DECISIONS = APPROVED / FROZEN
IMPLEMENTATION_CONTRACT = NOT YET APPROVED
IMPLEMENTATION_PLAN = NOT YET AUTHORIZED
PROCESSING_SERVICE_IMPLEMENTATION = NOT AUTHORIZED
API = NOT AUTHORIZED
FRONTEND = NOT AUTHORIZED
WDV1-004 = NOT AUTHORIZED

NEXT_AUTHORIZED_STAGE =
PROCESSING_SERVICE_IMPLEMENTATION_CONTRACT_DRAFT
```
