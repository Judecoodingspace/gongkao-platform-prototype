# Project Constitution

## English Version

### Purpose

Build a maintainable platform that converts historical civil-service exam papers into a reviewed, searchable, and versioned question bank.

### Principles

#### 1. Source Provenance Is Mandatory

Every structured question must be traceable back to its source paper, paper version, and source location when available.

Minimum provenance:

- Source paper
- Paper version
- Source block or page reference
- Annotator
- Review record

#### 2. Human Review Comes Before Official Entry

AI, OCR, document parsing, or heuristic extraction can only produce draft data. Draft data must be reviewed by a human before it becomes part of the official question bank.

#### 3. Version Instead Of Overwriting

Approved question content must not be overwritten in place. Changes create a new question version with editor, timestamp, reason, and diff when possible.

#### 4. Preserve Original Text

Original source text must be preserved. Normalized or corrected text should be stored separately with an edit record.

#### 5. Make Quality Visible

Each question should have visible status, completeness, source confidence, review state, and release state.

#### 6. Keep Workflows Auditable

Important actions must be auditable:

- Uploading a paper
- Parsing a paper
- Creating or editing a question
- Submitting for review
- Approving or rejecting
- Publishing to a dataset release

#### 7. Prefer Small, Verifiable Delivery

Each implementation slice should have acceptance criteria and runnable checks. Avoid vague, all-in-one AI coding tasks.

### Non-Goals For The Initial MVP

- Fully automatic paper-to-question extraction without human review
- Public question marketplace
- Complex adaptive testing
- Mobile-first annotation
- Large-scale model training pipeline
- Multi-tenant billing or commercial SaaS management

## 中文版本

### 目标

建设一个长期可维护的平台，将历年公务员考试真题转换为经过审核、可检索、可版本化管理的题库。

### 原则

#### 1. 来源追溯是强制要求

每一道结构化题目都必须能够追溯到来源试卷、试卷版本，以及在条件允许时追溯到具体的来源位置。

最低追溯信息包括：

- 来源试卷
- 试卷版本
- 来源原文块或页码引用
- 标注员
- 审核记录

#### 2. 正式入库前必须人工审核

AI、OCR、文档解析或启发式抽取只能生成草稿数据。草稿数据必须经过人工审核后，才能成为正式题库的一部分。

#### 3. 使用版本化，而不是覆盖

已审核通过的题目内容不得原地覆盖修改。修改时应创建新的题目版本，并尽可能记录编辑人、时间、原因和差异。

#### 4. 保留原始文本

来源原文必须被保留。规范化文本或人工修正文案应单独存储，并保留编辑记录。

#### 5. 让质量状态可见

每道题都应该能看到状态、字段完整度、来源可信度、审核状态和发布状态。

#### 6. 工作流必须可审计

重要动作都需要可审计：

- 上传试卷
- 解析试卷
- 创建或编辑题目
- 提交审核
- 审核通过或驳回
- 发布到题库版本

#### 7. 优先小步、可验证交付

每个实现切片都应该有验收标准和可运行检查。避免把模糊、庞大的“一次性 AI 编程任务”直接交给 Codex 或 Claude。

### 初始 MVP 不做什么

- 无人工审核的全自动拆题入库
- 公开题目交易市场
- 复杂自适应测评
- 移动端优先标注
- 大规模模型训练流水线
- 多租户计费或商业 SaaS 管理
