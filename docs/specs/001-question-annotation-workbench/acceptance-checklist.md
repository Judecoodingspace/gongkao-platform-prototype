# Acceptance Checklist: Question Annotation Workbench

## English Version

### Prototype Acceptance

- [ ] Stakeholders can identify the four main areas: source paper, explanation material, structured question form, workflow status.
- [ ] Annotator can explain where to upload a source paper.
- [ ] Annotator can explain how to bind a source block to a question.
- [ ] Annotator can find fields for subject, type, knowledge point, year, province, and difficulty.
- [ ] Annotator can find fields for stem, question, options, answer, and explanation.
- [ ] Reviewer can understand where review state and source provenance should appear.

### Functional Acceptance

- [ ] A source paper can be uploaded as a paper version.
- [ ] Source blocks can be displayed in stable order.
- [ ] A question draft can be created from a source block.
- [ ] Draft question can be saved without being visible in the official question bank.
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

### UI Acceptance

- [ ] Workbench supports 1440 x 900 desktop layout.
- [ ] Workbench supports 1366 x 768 laptop layout.
- [ ] Source area and form area scroll independently.
- [ ] Important buttons remain visible during long-form editing.
- [ ] No important text overlaps with controls.
- [ ] Field validation messages are visible and specific.

### Quality Acceptance

- [ ] Unit tests cover question state transitions.
- [ ] Parser adapter has fixture-based tests.
- [ ] Frontend has tests for save draft and submit review.
- [ ] Screenshot check exists for the workbench once production frontend begins.
- [ ] CI runs lint, type check, and tests before merge.

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
- [ ] 草稿题目可以保存，且不会出现在正式题库中。
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

### UI 验收

- [ ] 工作台支持 1440 x 900 桌面布局。
- [ ] 工作台支持 1366 x 768 笔记本布局。
- [ ] 来源区域和表单区域独立滚动。
- [ ] 长表单编辑时重要按钮仍然可见。
- [ ] 重要文字不与控件重叠。
- [ ] 字段校验提示可见且具体。

### 质量验收

- [ ] 单元测试覆盖题目状态流转。
- [ ] 解析器适配器有基于 fixture 的测试。
- [ ] 前端有保存草稿和提交审核测试。
- [ ] 正式前端开始后，为工作台增加截图检查。
- [ ] CI 在合并前运行 lint、类型检查和测试。
