# Acceptance Checklist: Question Annotation Workbench

## English Version

### Prototype Acceptance

- [ ] Stakeholders can identify the four main areas: source paper, explanation material, structured question form, workflow status.
- [ ] Annotator can explain where to upload a source paper.
- [ ] Annotator can explain how to bind a source block to a question.
- [ ] Annotator can find fields for subject, type, knowledge point, year, province, and difficulty.
- [ ] Annotator can find fields for stem, question, options, answer, and explanation.
- [ ] Reviewer can understand where review state and source provenance should appear.

### V1 Pure-Text Pilot Acceptance

- [ ] The annotator can load a LibreOffice-derived HTML preview for both the paper and explanation material.
- [ ] Source text is selectable and can be copied from the left preview into every right-side text field.
- [ ] Stem, question, options A-D, and explanation support text entry and basic paragraph formatting without image or media controls.
- [ ] Switching question slots preserves the current text draft and its rich-text draft representation.
- [ ] The V1 screen visibly states that formula, diagram, chart, screenshot, image-only option, and mixed-content questions are deferred.
- [ ] When the rich-text library cannot load, editable plain-text controls remain available.
- [ ] The V1 save path does not claim to upload files, create database records, or approve questions.
- [ ] Switching the subject to Shenlun hides objective question type, A-D options, and A-D correct-answer controls.
- [ ] Shenlun mode presents only the five confirmed specialty knowledge points as controlled choices.
- [ ] Shenlun mode presents four distinct text fields: stem body, requirement, question, and reference answer.
- [ ] Shenlun question tabs are grouped by specialty and show the specialty-local question order.

### Functional Acceptance

### Word-Assisted Annotation V1 (requires G-06)

- [ ] A DOCX upload is stored as an immutable paper version with hash and upload outcome.
- [ ] Parser candidates are ordered, text-only, provenance-bearing suggestions and never automatically create or submit a question.
- [ ] An annotator can explicitly fill a Shenlun field from selected source text, inspect its source reference, save, switch, return, and submit.
- [ ] Parser failure preserves the original upload and leaves manual draft entry available.
- [ ] Upload, parser, API, migration, and browser fixtures are sanitized; real paper text is not committed.

- [ ] A source paper can be uploaded as a paper version.
- [ ] Source blocks can be displayed in stable order.
- [ ] A question draft can be created from a source block.
- [ ] Stem, options, and explanation can contain ordered text and image content blocks.
- [ ] Formula or diagram images can be inserted without converting surrounding editable text into a screenshot.
- [ ] Full-region screenshots are available only as an explicit fallback content block.
- [ ] Draft question can be saved without being visible in the official question bank.
- [ ] Previous and next controls move by ordered question slot.
- [ ] A full question list allows jumping to any question slot.
- [ ] Switching question slots preserves the current draft before loading the target slot.
- [ ] Unstarted question slots can be viewed without automatically creating a question draft ID.
- [ ] Draft question can be submitted for review.
- [ ] Submitted question cannot be silently modified without version tracking.
- [ ] Reviewer can approve or reject.
- [ ] Rejection requires a reason.
- [ ] Approved question can be searched by basic metadata.

### Data Acceptance

- [ ] Every question version has a source paper reference.
- [ ] Every approved question version has a review record.
- [ ] Every released question points to a specific question version.
- [ ] Original source text is preserved separately from normalized or edited text.
- [ ] Parser name and parser version are stored when parser output is used.
- [ ] Image content blocks reference stored assets by asset ID rather than embedding binary data in question fields.
- [ ] Text projections remain available for search even when the authoritative content uses mixed content blocks.
- [ ] Source spans can be attached to specific content blocks when block-level provenance is available.
- [ ] A Shenlun question version round-trips `stem_text`, `requirement_text`, `question_text`, and `reference_answer_text` without merging fields or losing paragraph breaks.
- [ ] A Shenlun question version references an immutable `paper_version_id` and stores global, specialty, specialty-local, and source-label ordering provenance.
- [ ] Specialty navigation uses controlled `knowledge_point_id`; `source_topic_label` does not create taxonomy values.
- [ ] Two versions of one question may preserve the same source order, while two question slots in one paper version cannot claim the same global order.
- [ ] Draft writes reject stale `row_version`; submitted and approved versions cannot be patched in place.
- [ ] Shenlun V1 persistence creates no A-D option or correct-answer rows and stores no editor-specific HTML as authoritative content.
- [ ] A reusable source-material body is stored once and exact material versions can be linked in order to multiple question versions.
- [ ] Shenlun submission accepts a blank question-specific stem only when at least one valid source-material version is linked.
- [ ] Historical approved question and material versions remain immutable and discoverable after a correction draft becomes current.

### UI Acceptance

- [ ] Workbench supports 1440 x 900 desktop layout.
- [ ] Workbench supports 1366 x 768 laptop layout.
- [ ] Source area and form area scroll independently.
- [ ] Current question slot, status, source summary, and completeness are visible near the structured form.
- [ ] Important buttons remain visible during long-form editing.
- [ ] No important text overlaps with controls.
- [ ] Field validation messages are visible and specific.

### Quality Acceptance

- [ ] Unit tests cover question state transitions.
- [ ] Parser adapter has fixture-based tests.
- [ ] Frontend has tests for save draft and submit review.
- [ ] Screenshot check exists for the workbench once production frontend begins.
- [ ] CI runs lint, type check, and tests before merge.
- [ ] API contract tests cover idempotent create, exact four-field round-trip, source-order conflict, stale update, submit completeness, and correction-version immutability.
- [ ] Migration tests upgrade an empty disposable database, verify schema/indexes/seeds, and re-run safely.
- [ ] Migration inspection verifies non-cascading foreign keys and deferred composite current-version ownership constraints.
- [ ] Test startup refuses a non-test environment or a PostgreSQL database whose name does not end in `_test`.
- [ ] Logs, fixtures, migration seeds, and GitHub progress comments contain no private paper or answer text.

## 中文版本

### 原型验收

- [ ] 相关方能够识别四个主要区域：题本原文、解析材料、结构化题目表单、流程状态。
- [ ] 标注员能够说明在哪里上传题本。
- [ ] 标注员能够说明如何把原文块绑定到题目。
- [ ] 标注员能够找到科目、类型、知识点、年份、省份和难度字段。
- [ ] 标注员能够找到题干、问题、选项、答案和解析字段。
- [ ] 审核员能够理解审核状态和来源追溯应该出现在哪里。

### 功能验收

- [ ] 源试卷可以作为一个试卷版本上传。
- [ ] 原文块可以按稳定顺序展示。
- [ ] 可以从原文块创建题目草稿。
- [ ] 题干、选项和解析可以包含有序文本块和图片块。
- [ ] 公式或图形图片可以插入，不需要把周围可编辑文字一起转成截图。
- [ ] 整段区域截图只作为明确的兜底内容块使用。
- [ ] 草稿题目可以保存，且不会出现在正式题库中。
- [ ] 上一题、下一题控件按顺序题位移动。
- [ ] 完整题目列表支持跳转到任意题位。
- [ ] 切换题位前会保留当前草稿，再加载目标题位。
- [ ] 未开始题位可以查看，不会自动生成题目草稿 ID。
- [ ] 草稿题目可以提交审核。
- [ ] 已提交题目不能在没有版本追踪的情况下被静默修改。
- [ ] 审核员可以通过或驳回。
- [ ] 驳回时必须填写原因。
- [ ] 已通过题目可以按基础元数据检索。

### 数据验收

- [ ] 每个题目版本都有来源试卷引用。
- [ ] 每个已通过题目版本都有审核记录。
- [ ] 每个已发布题目都指向具体题目版本。
- [ ] 原始来源文本与规范化或编辑后的文本分开保存。
- [ ] 使用解析器输出时，必须存储解析器名称和版本。
- [ ] 图片内容块通过资源 ID 引用已存储资源，不把二进制数据嵌入题目字段。
- [ ] 即使权威内容使用图文内容块，也保留可搜索的纯文本投影。
- [ ] 当具备块级来源时，可以把来源片段绑定到具体内容块。
- [ ] 申论题目版本可以原样往返 `stem_text`、`requirement_text`、`question_text` 和 `reference_answer_text`，不合并字段且不丢失段落换行。
- [ ] 申论题目版本引用不可变的 `paper_version_id`，并保存全局顺序、专项顺序、专项内题序和原文专项标题快照。
- [ ] 专项导航使用受控 `knowledge_point_id`；`source_topic_label` 不会创建知识点。
- [ ] 同一道题的两个版本可以保留相同来源顺序，同一试卷版本的两个题位不能占用同一个全局顺序。
- [ ] 草稿写入会拒绝过期 `row_version`；已提交和已通过版本不能原地 PATCH。
- [ ] 申论 V1 持久化不创建 A-D 选项或正确答案记录，也不把编辑器专用 HTML 作为权威数据。
- [ ] 一份共享材料正文只保存一次，多个题目版本可以按序关联准确的材料版本。
- [ ] 只有在至少关联一个有效共享材料版本时，申论提交才允许题目独有 `stem_text` 为空。
- [ ] 修订草稿成为当前版本后，历史已通过题目和材料版本仍不可变且可检索。

### UI 验收

- [ ] 工作台支持 1440 x 900 桌面布局。
- [ ] 工作台支持 1366 x 768 笔记本布局。
- [ ] 来源区域和表单区域独立滚动。
- [ ] 当前题位、状态、来源摘要和完整度显示在结构化表单附近。
- [ ] 长表单编辑时重要按钮仍然可见。
- [ ] 重要文字不与控件重叠。
- [ ] 字段校验提示可见且具体。

### 质量验收

- [ ] 单元测试覆盖题目状态流转。
- [ ] 解析器适配器有基于 fixture 的测试。
- [ ] 前端有保存草稿和提交审核测试。
- [ ] 正式前端开始后，为工作台增加截图检查。
- [ ] CI 在合并前运行 lint、类型检查和测试。
- [ ] API 契约测试覆盖幂等创建、四字段原样往返、来源顺序冲突、过期更新、提交完整度和修订版本不可变。
- [ ] 迁移测试可升级空的一次性数据库、核对 schema/索引/种子，并可安全重复执行。
- [ ] 迁移检查验证外键不级联删除，并验证延迟的复合当前版本归属约束。
- [ ] 测试启动会拒绝非测试环境或数据库名不以 `_test` 结尾的 PostgreSQL 数据库。
- [ ] 日志、fixture、迁移种子和 GitHub 进度评论不含私有试卷或答案正文。

### 连续来源预览与区域填入 POC 验收

- [ ] 连续页面预览中，文本、公式图片和普通图片可以在同一页面视觉区域内同时查看。
- [ ] 标注员可以通过点击、多选或拖动框选一个包含文字和图片的来源区域。
- [ ] 框选区域可以一次性指定填入题干、问题、选项 A-D 或解析。
- [ ] 填入结果按页面阅读顺序生成混合 `ContentBlock`，不要求在文本块和图片块筛选器之间往返操作。
- [ ] `DocumentBlock` 可以按页面号和来源坐标组成连续页面视图，同时保留原子块来源信息。
- [ ] 区域填入生成的每个内容块都保留其来源 `source_span_id`，且不会把多个来源块错误合并成一个无来源截图。
- [ ] 题干、选项和解析的纯文本投影由 `content_blocks` 派生，不形成第二套独立可编辑真相。
- [ ] 来源预览不以文本块列表和图片块列表作为主要阅读界面；常见桌面宽度下，来源页面、选择工具栏和右侧编辑区不发生遮挡或重叠。
- [ ] 公式图片在未单独切换到“图片块”筛选器时，也能与相邻文本一起显示。
- [ ] 右侧录题区不要求操作员针对每个来源块单独点击“填入”；一次区域填入即可完成混合内容初始录入。
