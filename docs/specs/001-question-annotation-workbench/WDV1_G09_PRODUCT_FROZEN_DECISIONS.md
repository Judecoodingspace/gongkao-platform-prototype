# WDV1 G-09 Pure-Text Question Annotation E2E — Product Frozen Decisions

```text
PRODUCT_DECISIONS = FROZEN
IMPLEMENTATION_AUTHORIZED = NO
```

These decisions are the product authority for the WDV1 G-09 pure-text question-annotation end-to-end slice. They do not authorize an implementation plan, migration, backend or frontend implementation, or merge.

## FD-01 — 本轮 E2E 目标

```text
成套 DOCX 资料导入
→ Processing
→ 题本详情
→ 开始拆题
→ 查看题本 / 解析
→ 选择来源
→ 填入结构化字段
→ 人工编辑
→ 自动/手动保存
→ 逐题拆解
→ 退出 / 恢复
→ 完成本卷拆题
```

最终状态仅为 `已完成拆题`，不等于审核通过或题库发布。

## FD-02 — 导入单位是一套试卷资料包

V1 一套资料包含：

- 题本 DOCX；
- 解析 DOCX；
- 年份；
- 地区；
- 科目；
- 考试类型。

题本与解析在导入时绑定。第一轮只要求单套资料导入；批量导入后续再做。

## FD-03 — 上传不发生在拆题工作台

正式流程：

```text
导入资料包 → 保存两个来源 → Processing → 题本详情 → 开始拆题
```

正式工作台不再手工选择 DOCX / HTML / JSON。

## FD-04 — 题本详情页是入口

上传/处理后先进入题本详情，用户明确点击 `开始拆题` 或 `继续拆题` 才进入 workbench。

## FD-05 — Processing 用户状态

```text
success → 处理完成 → 可以拆题
partial → 部分内容无法可靠读取 → 缺口可见 → 仍允许拆题
failed  → 处理失败 → 本版禁止进入拆题工作台 → 只能重新处理
```

不提供 failed 情况下的完全人工录题模式。

## FD-06 — 两个来源共同决定 readiness

```text
题本 = success/partial
且
解析 = success/partial
→ 可拆题
```

任一来源 `failed` → 整套资料暂不能开始正式拆题。

必须与已有 Processing Service 的 immutable history、active result、success initial activation、partial explicit activation、failed never active 兼容。

**不得自动激活 partial 来绕过旧 invariant。** 若需要 adoption，Contract 必须设计成明确、可审计的 actor intent。

## FD-07 — 题本级拆题状态

```text
未开始
进行中
已完成
```

V1 不提前识别总题数。进行中只显示 `已创建 X 道题`；完成后可显示 `共拆出 X 道题`。

## FD-08 — 高保真是 UI baseline

`prototypes/question-bank-prototype/` 是 UI / interaction baseline。

保留：左侧来源区、中央结构化录题区、当前题、上一题/下一题、题目列表、保存草稿、保存并录下一题、预览位置。

修改：删除 POC 文件选择；source 自动加载；不预生成整卷题位。

延后：正式图文混排、复杂图片/公式/截图、review workflow。

Prototype JS 不得直接作为生产业务逻辑。

## FD-09 — 题本/解析显示采用方案 C

默认：

```text
[题本] [解析] [对照查看]
```

单个大阅读区；可切换；需要核对时开启对照模式。题本与解析保持独立 source identity。

## FD-10 — 不向 annotator 暴露技术概念

UI 不展示 ProcessingResult、DocumentBlock ID、Gap ID、parser config、storage URI 等内部概念。

## FD-11 — 题目动态创建

不预生成第1题～第N题。

```text
开始第1题
→ 保存并录下一题
→ 第2题
→ 第3题...
```

题目列表随人工拆题增长。

## FD-12 — 换题不换来源

同一套资料中从第1题到第2题，左侧仍保持同一套题本与解析。

## FD-13 — Shenlun V1 四字段

```text
stem_text
requirement_text
question_text
reference_answer_text
```

四字段独立 round-trip；不创建 A-D options / correct answer；既有五类申论专项知识点规则继续有效（无冲突时）。

## FD-14 — Source → Field

可选择一个或多个来源段落，再明确填入：题干、要求、问题、参考答案。

题本优先展示题干/要求/问题；解析优先展示参考答案，但仅是 UI 优先级，不是数据层限制。

## FD-15 — 多来源按原文顺序

一个 field 可绑定多个 source blocks；填入顺序必须按原文顺序，不得语义重排。

## FD-16 — 默认追加，显式替换

field 为空：直接填入。

field 非空：默认 append；另提供 explicit replace。

replace 是破坏性操作，UI 必须确认。

Backend 必须保证：**普通 fill 不能静默覆盖非空 human content。**

Contract 必须定义 append/replace 对 text、ordered provenance、history/audit、stale provenance、optimistic concurrency 的影响。

## FD-17 — 人工编辑不解除 provenance

```text
source text → fill → human edit
```

human edit 后仍保留原始来源关系。不得回写 `DocumentBlock`。

## FD-18 — Partial gap 必须可见

partial gap 不得静默丢失，也不得伪装成连续原文。UI 获得安全、人类可理解的 gap marker/evidence；不得泄露 traceback/private path。

## FD-19 — 保存采用方案 C

```text
autosave + manual save
```

UI 状态：正在保存 / 已保存 / 保存失败。

保留 `保存草稿`、`保存并录下一题`。

Autosave 不是 last-write-wins；Contract 必须设计 concurrency semantics。

## FD-20 — 保存并录下一题

```text
保存当前题成功
→ 才进入/创建下一题
```

必须处理 idempotency、double click、network retry、question ordering、duplicate next-question creation。

## FD-21 — Resume 以最后编辑为准

重新进入进行中的资料 → 回到最后编辑题，不是最后浏览题。只浏览不得更新 work-progress pointer。

## FD-22 — Resume 内容

恢复：最后编辑题、已保存四字段、provenance、上次 source tab。

本轮不要求恢复：temporary block selection、popover、pending replace confirmation、exact scroll offset。

## FD-23 — Save failure

有未成功保存内容时离开，UI 必须能提示：继续编辑 / 重试保存 / 仍然离开。

Contract 区分 server truth 与 frontend ephemeral state。

## FD-24 — 完成本卷硬校验

每一道已创建的申论题都必须具有：题干、要求、问题、参考答案。

缺任意字段 → 不允许完成，并能返回 `第X题：缺少Y`。

## FD-25 — Hard blockers vs soft warnings

Hard blockers：

- 四字段缺失；
- server-side known unsaved/failed state（若存在）；
- 完成本卷事务冲突/失败。

Soft warnings：

- source processing 为 partial；
- 存在 gap；
- 某字段有人工内容但无 source binding。

Soft warning 可由 annotator 明确确认后继续完成。

## FD-26 — 完成本卷需要显式确认

通过 hard validation 后，只有用户明确确认才进入 completed。

## FD-27 — Completed 默认只读，可显式 reopen

`已完成拆题` 默认 read-only。

用户执行 `重新编辑` 后才切回 `进行中`。Contract 必须定义 auditable completed → in_progress transition。

## FD-28 — 本轮不包括审核

本轮不实现 submit review、reviewer workbench、approve/reject、publish/release。

旧 acceptance checklist 中 G-09 的 submit 范围由本 FD 明确 supersede。

## FD-29 — 完整用户链路

```text
导入一套资料
├─ 题本 DOCX
└─ 解析 DOCX
        ↓
Processing
        ↓
题本详情
        ↓
开始拆题
        ↓
[题本] [解析] [对照查看]
        ↓
选择来源块
        ↓
填入四字段
        ↓
人工编辑
        ↓
autosave / manual save
        ↓
保存并录下一题
        ↓
重复逐题拆解
        ↓
中途退出
        ↓
回到最后编辑题
        ↓
完成本卷
        ↓
hard validation + soft warning
        ↓
confirm
        ↓
已完成拆题
```

## Continuing invariants

Unless an FD above explicitly supersedes an older product behavior, the following remain binding: original DOCX and `PaperVersion` provenance are immutable; `ProcessingResult` history is immutable; active selection remains independent; partial is never automatically activated and failed is never active; field provenance identifies an exact processing result and exact document block; parser output never assigns question semantics; private source content and paths never enter logs or Git; PostgreSQL 16 and disposable-test-database guards remain mandatory; provenance history uses no cascade deletion; and this slice must not weaken future submitted/approved immutability.

```text
NEXT_STAGE = TEAM B CONTRACT REVIEW
```
