# WDV1 STEP 4.4B — Direct OOXML Text-first Parser Frozen Decisions

**STATUS = APPROVED BY PRODUCT OWNER**

Approved for governance commit and Team A verification. Merge to main and STEP 4.4B Implementation Plan remain NOT AUTHORIZED.

本文收敛 STEP 4.4B — Direct OOXML Text-first Parser 的产品与架构决策。

本文只冻结 Parser slice 的边界与行为语义。

本文：

* 不授权 STEP 4.4B implementation；
* 不授权 Processing Service；
* 不授权 API / OpenAPI / React；
* 不授权 WDV1-004；
* 不改变既有 G-06 / G-07 / G-08 冻结语义；
* 不重新设计 STEP 4.3 schema；
* 不重新设计已完成的 STEP 4.4A Source Reader Boundary。

---

## 1. Authority

### Product / Governance Repo

```text
Judecoodingspace/gongkao-platform-prototype
main@4e6373f719abde7d8fb7701a429f521dac3d1953
```

主要既有 authority：

```text
WDV1_G08_FROZEN_DECISIONS.md
WDV1_G08_IMPLEMENTATION_CONTRACT.md
WDV1_G08_SCHEMA_TRANSACTION_DESIGN.md
WDV1_G08_TECHNICAL_CHOICES.md
WDV1_G08_TEXT_STRUCTURING_TECHNICAL_PRECHECK.md
```

### API Repo

STEP 4.4A closure 后 authoritative main：

```text
Judecoodingspace/gongkao-question-bank-api

main@
f7f49399f05ebf16110d8a1a940f2681f000a32e
```

STEP 4.4A：

```text
CLOSED
```

STEP 4.4B：

```text
IMPLEMENTATION NOT AUTHORIZED
```

---

# 2. Naming clarification

既有 `WDV1_G08_IMPLEMENTATION_CONTRACT.md` 已经存在另一组名为 `P1–P3` 的历史产品决策。

因此本轮讨论期间使用的：

```text
P1–P9
```

在 durable governance artifact 中统一重命名为：

```text
B1–B9
```

其中：

```text
B = STEP 4.4B Parser Decision
```

不得用本文的 B1–B9 覆盖、重解释或重新编号既有 G-08 P1–P3。

---

# 3. STEP 4.4B Objective

STEP 4.4B 的唯一目标是：

> 对已经由上游完成来源身份确认和完整性验证的 DOCX bytes，通过 Direct OOXML traversal，产生稳定、自然段级、有序、可追溯且 fail-visible 的 text-first source structure candidate。

当前核心主路径是：

```text
纯文字申论 DOCX
```

理想正常路径：

```text
verified DOCX bytes
↓
Direct OOXML Parser
↓
ordered natural-paragraph text blocks
+
Gap = 0
↓
success candidate
```

Parser 不负责业务语义判断。

Parser 不判断：

```text
题干
材料
问题
作答要求
答案
知识点
题型
```

---

# B1 — Parser Input / Output Boundary

## Decision

Parser 只消费：

```text
verified DOCX bytes
```

这里的 `verified` 表示：

> 上游 Processing Service 已经完成 actual SHA-256 与 expected `PaperVersion.file_hash` 的比较。

Parser 不负责来源身份或完整性验证。

Parser MUST NOT receive or depend on：

```text
PaperVersion
storage_uri
absolute path
expected source hash
DB session
SQLAlchemy ORM objects
ProcessingResult ORM
HTTP request
actor/user context
```

Parser 不直接读取 private storage。

Parser 不直接写数据库。

## Output

Parser 输出 persistence-agnostic 的 source-structuring candidate，至少表达：

```text
ordered text blocks
Gap evidence
structural reliability / outcome
safe parser diagnostics
```

Parser 输出不得包含：

```text
database IDs
processing_result_id
PaperVersion identity
storage_uri
ORM entities
```

最终 ProcessingResult 的持久化与 terminalization 仍属于 Processing Service。

---

# B2 — `source_order` Semantics

`source_order` 表示：

> 由 Direct OOXML traversal 得出的 deterministic source-relative main-body structural order。

它不是：

```text
数据库插入顺序
DocumentBlock 数组 index
前端显示排序
AI 推断阅读顺序
业务语义顺序
PDF page order
```

对于 main-body body-level structure：

```text
source_order
= authoritative w:body traversal position
```

因此 text block 的 `source_order` 不要求连续。

例如：

```text
1 paragraph
2 paragraph
3 table Gap
4 paragraph
```

对应 text blocks 可以是：

```text
1, 2, 4
```

paragraph 内部 unsupported structure 可以与所属 paragraph 共享 `source_order`，并通过：

```text
source_region_kind = within_paragraph
```

表达位置。

---

# B3 — Paragraph → DocumentBlock

WDV1-003 的文字结构边界来自 DOCX natural paragraph。

原则：

```text
one supported natural paragraph
→ at most one DocumentBlock
```

不得因为以下原因拆分 paragraph：

```text
句号
分号
冒号
句子边界
manual line break
tab
hyperlink
视觉换行
业务语义
```

相邻 paragraph 不得自动 merge。

Heading paragraph 可以作为普通文字来源结构保留，但不得被解释为业务类型。

## Mixed paragraph

如果一个 paragraph 同时包含：

```text
supported visible text
+
unsupported content
```

则：

```text
one DocumentBlock
+
one or more Gap records
```

unsupported content 不产生额外 fake text block。

## Unsupported-only paragraph

如果一个 paragraph 没有可用 supported textual payload，只包含 unsupported content：

```text
DO NOT create a fake empty text block
only to satisfy a one-paragraph-one-block rule
```

应通过 Gap 明确保存当前能力缺口。

这不影响 genuine empty paragraph 的保留规则。

---

# B4 — Empty Paragraph Handling

真正的 empty paragraph 指：

```text
authoritative main-body paragraph
+
no reconstructed supported textual payload
+
no detected unsupported/content-bearing structure
```

这种 paragraph 必须保留：

```text
text_original = ""
```

Parser 不得通过：

```text
strip()
trim()
normalization
```

决定一个 paragraph 是否为空。

因此以下来源结构不能因为“视觉上没有普通字符”就被静默合并：

```text
whitespace-only
tab-only
manual-break-only
```

其具体 authoritative string reconstruction policy 由 STEP 4.4B Implementation Plan 定义并测试，但不得违背来源保真原则。

如果：

```text
reconstructed text = ""
BUT
unsupported/content-bearing structure exists
```

则它不是 genuine empty paragraph。

未知且可能承载内容的结构也不得被当作普通 empty paragraph。

---

# B5 — Unsupported Structure → Gap

`SourceProcessingGap` 的含义是：

> 当前 ProcessingResult 的 source-structuring capability boundary。

它不是：

```text
Word 无法显示该内容
```

也不是：

```text
该内容永久不支持
```

更准确地说：

> 当前 WDV1-003 尚不能把这个来源对象建模为 usable / traceable source object。

## Gap occurrence

每个在当前 scope 内、能够可靠区分的 unsupported source occurrence 必须 fail-visible。

不同可靠来源位置的 unsupported occurrence 不得合并成一个 document-level summary Gap。

一个已经识别出的 unsupported container 不应因为其内部多个 OOXML implementation nodes 而重复产生大量 Gap。

原则：

```text
one reliably distinguishable unsupported occurrence
→ one Gap
```

## Location

Body-level unsupported object：

```text
own source_order
```

Within-paragraph unsupported object：

```text
paragraph source_order
+
source_region_kind = within_paragraph
```

## Known vs unknown

已知但当前不支持的结构使用受控类型，例如：

```text
table
drawing
omml
textbox
embedded_object
```

能够可靠定位但无法识别类型的 in-scope structure：

```text
gap_type = unknown
```

如果 unknown structure 导致无法确认现有 blocks / order 是否仍然可信，则不能仅作为普通 partial Gap 处理，应进入 `failed` 路径。

## Out-of-scope stories

当前不自动把以下 Word stories 作为 WDV1-003 Gap：

```text
header
footer
footnote
endnote
```

它们当前属于：

```text
out of scope
```

而不是：

```text
in-scope unsupported content
```

---

# B6 — Known Non-text Structures: Current Behavior

WDV1-003 对以下结构统一采用：

```text
DETECTED BUT NOT MODELED
→ GAP-ONLY
```

当前包括：

```text
table
drawing / image
OMML formula
textbox
embedded object
```

Parser MUST NOT 在 STEP 4.4B 中：

```text
把 table cell text 伪装成 paragraph DocumentBlock
把 textbox text 伪装成 main-body paragraph
提取 image asset
执行 OCR
重建 table semantics
把 OMML 转 LaTeX / MathML
恢复 visual layout
分析 image alt-text 为正式来源正文
建立 ImageSource / FormulaSource / TableSource
```

如果 surrounding text 与 source order 仍然可靠：

```text
Gap
→ partial candidate
```

如果无法确认剩余文字或顺序可靠：

```text
→ failed candidate
```

未来 image / table / formula 的正式来源建模必须通过新的 reviewed additive slice 完成。

历史 ProcessingResult 不因未来 parser capability 升级而重写。

---

# B7 — Result Status Derivation

三态必须机械推导，不得依赖开发者主观判断、百分比或 AI confidence。

## `success`

必须同时满足：

```text
main-body traversal reliable
paragraph text reconstruction reliable
source order reliable
Gap count = 0
no unknown-loss risk
```

## `partial`

必须满足：

```text
one or more explicit Gaps exist
AND
all emitted text blocks remain trustworthy
AND
their source order remains trustworthy
AND
missing/unmodeled region can be reliably bounded
```

## `failed`

出现以下任一情况时必须 failed：

```text
trustworthy block set cannot be established
source order cannot be established
unknown content loss may exist
reliable Gap boundary cannot be established
parser cannot establish current-result structural integrity
```

硬规则：

```text
Gap > 0
→ status MUST NOT be success
```

但：

```text
Gap = 0
```

不自动意味着：

```text
success
```

因为 traversal / reconstruction / completeness 仍可能不可靠。

不得使用：

```text
解析成功百分比
block 数量百分比
confidence score
AI risk score
```

决定三态。

Reader failure 或 source-integrity mismatch 可以由 Processing Service 直接产生 `failed`，且 Parser 不运行。

---

# B8 — Parser Diagnostics Boundary

Parser diagnostics 必须：

```text
structured
bounded
machine-readable
source-content-free
```

必须使用 stable controlled diagnostic classification。

允许的 diagnostics 应以结构信息为主，例如：

```text
parser stage
structure kind
source order
source region kind
bounded counts
```

具体 diagnostic code 全集不在本文冻结，由 Implementation Plan 提出并经 review 后实施。

Diagnostics MUST NOT persist：

```text
source text
raw XML
DOCX bytes
image/asset bytes
storage_uri
absolute path
credentials
arbitrary exception messages
unsanitized traceback
```

Gap diagnostic 只是解释：

```text
current capability boundary
```

不自动意味着：

```text
parser failed
```

Parser 只负责 parser-owned diagnostics。

以下仍属于其他层：

```text
Reader failure
source integrity mismatch
processing lifecycle failure
database transaction failure
```

Internal diagnostic code 不自动等于 user-visible error message。

正常 `success` 不应人为制造无意义 diagnostic noise。

---

# B9 — Deterministic Parsing

在以下条件相同的情况下：

```text
source SHA-256
parser name/version
canonical parser config
supported runtime fingerprint
```

Parser 必须产生相同的 semantic source-structuring result。

必须稳定的内容包括：

```text
DocumentBlock count
DocumentBlock.text_original
DocumentBlock.source_order
DocumentBlock.block_type

Gap count
Gap type
Gap structural location/order

structural outcome/status candidate
stable diagnostic classification
```

以下 run-instance metadata 不要求相同：

```text
ProcessingResult UUID
DocumentBlock UUID
Gap UUID
created_at
completed_at
other per-run identity metadata
```

Parser 行为不得依赖：

```text
random values
network access
current time/date
local absolute file path
database insertion order
uncontrolled locale/environment state
```

本文要求的是：

```text
semantic determinism
```

不是整个 database snapshot 或 serialized JSON byte-identical。

Parser capability、config 或 supported runtime 发生受控版本变化后，结果可以不同；这种变化必须通过新的 parser metadata / ProcessingResult 留下历史，而不是重写旧结果。

---

# 4. Deliberately Deferred Decisions

为了避免对当前“纯文字申论 DOCX”主路径过度设计，以下内容不在 STEP 4.4B Frozen Decisions 中冻结：

```text
ImageSource schema
TableSource schema
FormulaSource schema
统一 SourceItem schema
图片 relationship / asset extraction
OCR
table cell / row / column model
nested table semantics
textbox reading-order recovery
OMML → LaTeX / MathML
image alt-text provenance
visual preview
page / bbox
PDF / LibreOffice / PyMuPDF
完整 OOXML 标准覆盖
完整 diagnostic-code enum
tab / break 的具体 Python string 编码细节
privileged debug mode
```

这些内容只有在真实产品需求出现后，才能通过新的 bounded slice 单独评审。

---

# 5. Consistency Findings

## Existing-authority compatibility

B1–B9 必须继续服从既有规则：

```text
raw DOCX remains immutable source evidence

Direct OOXML traversal
= authoritative structural truth

Parser
≠ business-semantic classifier

non-text main-body structure
= fail-visible

historical ProcessingResult
= immutable

future parser capability upgrade
= new ProcessingResult
NOT historical rewrite
```

## No schema redesign

本文不要求修改已经批准的 STEP 4.3 schema。

当前：

```text
DocumentBlock
+
SourceProcessingGap
+
SourceProcessingResult
```

足以承载 STEP 4.4B text-first parser candidate。

若 implementation 发现必须改变 schema 才能满足本文：

```text
STOP
RETURN TO DESIGN REVIEW
```

不得由 implementation agent 自行扩 schema。

---

# 6. Over-design Guard

STEP 4.4B 的设计原则是：

> Build the minimum honest text-first parser, not a general Word-processing platform.

中文：

> 建立“最小但诚实”的纯文字来源解析器，而不是提前实现一个通用 Word 解析平台。

当前最重要的是：

```text
纯文字 DOCX
→ stable blocks
→ Gap = 0
→ success
```

以及：

```text
意外出现当前不支持结构
→ detect
→ fail-visible
→ never silently claim success
```

而不是现在解决所有复杂 DOCX。

---

# 7. Gate

当前本文状态：

```text
STEP 4.4B DECISION CONSOLIDATION = COMPLETE

CONSISTENCY AUDIT = PASS
WITH CONSOLIDATION CLARIFICATIONS

OVER-DESIGN AUDIT = PASS
AFTER SCOPE REDUCTION

STEP 4.4B FROZEN DECISIONS =
CANDIDATE FOR PRODUCT OWNER APPROVAL

STEP 4.4B IMPLEMENTATION PLAN =
NOT YET AUTHORIZED

STEP 4.4B IMPLEMENTATION =
NOT AUTHORIZED
```

Product Owner 明确批准本文后，下一步只能进入：

```text
WRITE FROZEN DECISIONS TO GOVERNANCE REPO
→ commit
→ push
→ STOP
→ Team A verification
```

在 Frozen Decisions 的 GitHub authority 被确认之前，不得开始 STEP 4.4B Implementation Plan。

在 Implementation Plan 被独立审查和 Product Owner 批准之前，不得开始 Parser implementation。
