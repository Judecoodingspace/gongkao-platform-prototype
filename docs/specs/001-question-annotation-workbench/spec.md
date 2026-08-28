# Spec: Question Annotation Workbench

## English Version

### Summary

Annotators need to view the original paper, answer or explanation materials, and structured question fields on the same page. This workbench is the core entry point for producing question-bank data.

### Users

- Annotator
- Reviewer
- Admin

### User Goals

#### Annotator

- Open an assigned paper task.
- View the source paper and explanation materials.
- Select source blocks and create a question.
- Enter stem, question text, options, answer, explanation, and metadata.
- Create or select reusable source material and link the exact material version to multiple Shenlun question versions.
- Insert text and image/formula/diagram blocks into stem, options, and explanation when the source content is mixed.
- Save a draft or submit it for review.

#### Reviewer

- View question source, fields, and edit history.
- Decide whether the question can enter the question bank.
- Approve or reject the question.

### Primary Workflow

1. The annotator opens the task list.
2. The annotator selects a pending paper.
3. The system opens the annotation workbench.
4. The left side displays source blocks, and the lower-left area displays explanation materials.
5. The annotator selects one or more source blocks.
6. The annotator creates a question draft.
7. The annotator fills the question fields.
8. The system shows field completeness and source-binding status.
9. The annotator can move to another ordered question slot without losing the current draft.
10. The annotator saves the draft or submits it for review.

### Required Capabilities

- File upload entry
- Source block display and selection
- Explanation material display
- Structured question form
- Ordered question slot navigation
- Option editing
- Mixed text/image content block editing for stem, options, and explanation
- Answer selection
- Difficulty annotation
- Tag and knowledge point selection
- Save draft
- Submit for review
- Source provenance
- Reusable source-material creation, versioning, and ordered question-version links for Shenlun

### States

Question states:

- Draft
- Submitted
- Approved
- Rejected
- Archived

Paper states:

- Uploaded
- Parsed
- ParseFailed
- InAnnotation
- Completed

### UX Constraints

- The workbench prioritizes desktop usage.
- Common widths: 1440 x 900, 1366 x 768, and 1280 x 720.
- Source area and question-editing area should scroll independently.
- Editing a question should not lose the current source location.
- Previous and next navigation should follow paper question order, not recent draft order.
- The workbench should provide a full question list for jumping to any question slot.
- Switching away from a question should preserve the current draft state before loading the target slot.
- Important actions need clear feedback.
- Missing fields must be shown before review submission.
- Rich text editors may be used for editing/rendering, but persisted question content should use the platform-owned `content_blocks` structure, not editor-specific HTML or plugin markup.
- Full-region screenshots are allowed only as fallback blocks for content that cannot be split safely; normal text remains editable/searchable text blocks.

### Open Questions

- Should source blocks support multi-selection across pages?
- Should pasted question images be auto-cropped?
- How should inline formula images be resized and aligned relative to surrounding text?
- Must explanation material always match the same paper version?
- Who maintains the knowledge point taxonomy?
- Is difficulty first set by the annotator or finalized by the reviewer?

### Source Preview and Region-Fill POC Decision

The annotation workbench POC uses a continuous page-oriented source preview for parsed `DocumentBlock` data. Text, formula images, diagrams, and other image blocks are placed using their page and bounding-box provenance so the annotator can read them in a layout closer to the source document.

The annotator may click a single block, shift-click multiple blocks, or drag a rectangle across a contiguous region. The selected blocks are ordered by page, top coordinate, and left coordinate, then filled in one operation into the selected destination: stem, question, option A-D, or explanation. Each resulting `ContentBlock` keeps its own `source_span_id`.

`DocumentBlock` remains an atomic provenance and parser-output unit; it is not the required editing unit in the user interface. The source preview may compose many document blocks into one visual region. The POC must not require the annotator to switch between a text-only list and an image-only list to reconstruct the original reading order.

The right-hand editor remains necessary for human correction, deletion, ordering, and review. It is the canonical editing surface for `content_blocks`. Plain text inputs or textareas for stem, options, and explanation are projections for search/completeness or compact display, not a second independent content store.

The POC does not infer final question boundaries or field ownership without human confirmation. Region selection is an operator-assisted binding action, not automatic question extraction.

### V1 Pure-Text Pilot Boundary

The first runnable workbench profile accepts only questions whose stem, question text, A-D options, and explanation are all text. The source-paper and explanation panels use LibreOffice-derived read-only HTML previews so the annotator can select and copy source text.

The right-hand form may use a constrained rich-text editor for paragraph and basic text formatting, but V1 must disable image, video, table, attachment, external-link, and arbitrary-HTML insertion. The editor output is a draft editing representation only; the saved business payload remains platform-owned fields and projections.

Questions containing formula images, diagrams, charts, table screenshots, image-only options, or mixed text/image content are explicitly deferred. The existing `DocumentBlock`, `SourceSpan`, `DocumentAsset`, and `ContentBlock` design remains the later extension path and must not be removed because of this V1 simplification.

For Shenlun, reusable passages such as "Material 1" are stored once as versioned source material and linked to exact question versions. `stem_text` contains only question-specific text. Submission requires requirement, question, and reference answer plus either question-specific stem text or at least one valid material-version link.

## 中文版本

### 概要

标注员需要在同一页面中查看真题原文、解析材料，并把题目拆解为结构化记录。该工作台是整个题库数据生产流程的核心入口。

### 用户

- 标注员
- 审核员
- 管理员

### 用户目标

#### 标注员

- 打开待处理真题任务。
- 查看题本原文和解析材料。
- 选择原文块并创建题目。
- 录入题干、问题、选项、答案、解析和元数据。
- 创建或选择可复用来源材料，并把准确材料版本关联到多个申论题目版本。
- 当来源内容混有文字、公式图片或图形时，可以在题干、选项和解析中插入文本块与图片块。
- 保存草稿或提交审核。

#### 审核员

- 查看题目来源、字段和修改记录。
- 判断题目是否可以入库。
- 通过或驳回题目。

### 主流程

1. 标注员进入任务列表。
2. 标注员选择一份待处理真题。
3. 系统打开拆题工作台。
4. 左侧显示题本原文块，左下显示解析材料。
5. 标注员选择一个或多个原文块。
6. 标注员创建题目草稿。
7. 标注员补全题目字段。
8. 系统提示字段完整度和来源绑定情况。
9. 标注员可以切换到其他顺序题位，且不丢失当前草稿。
10. 标注员保存草稿或提交审核。

### 必需能力

- 文件上传入口
- 原文块展示和选择
- 解析材料展示
- 题目结构化表单
- 顺序题位导航
- 选项编辑
- 题干、选项和解析的图文内容块编辑
- 答案选择
- 难度标注
- 标签和知识点选择
- 保存草稿
- 提交审核
- 来源追溯
- 申论共享材料的创建、版本化和题目版本有序关联

### 状态

题目状态：

- Draft，草稿
- Submitted，待审核
- Approved，已通过
- Rejected，已驳回
- Archived，已归档

试卷状态：

- Uploaded，已上传
- Parsed，已解析
- ParseFailed，解析失败
- InAnnotation，标注中
- Completed，已完成

### 体验约束

- 工作台优先支持桌面端。
- 常见宽度：1440 x 900、1366 x 768、1280 x 720。
- 原文区域和题目编辑区域需要独立滚动。
- 题目编辑时不应丢失当前原文定位。
- 上一题、下一题应按试卷题号顺序切换，而不是按最近草稿顺序切换。
- 工作台需要提供完整题目列表，支持跳转到任意题位。
- 切换题位前应保留当前草稿状态，再加载目标题位。
- 重要操作需要明确反馈。
- 提交审核前必须提示缺失字段。
- 富文本编辑器可以用于编辑和渲染，但题目内容持久化应使用平台自有的 `content_blocks` 结构，不绑定某个编辑器 HTML 或插件标记。
- 整段截图只作为无法安全拆分内容的兜底内容块；常规文字仍应保存为可编辑、可检索的文本块。

### 开放问题

- 原文块是否支持跨页多选？
- 题图粘贴后是否需要自动裁剪？
- 行内公式图片相对周围文字的缩放和对齐规则是什么？
- 解析材料是否必须与题本同版？
- 知识点体系由谁维护？
- 难度由标注员初评还是审核员最终确定？

### 来源预览与区域填入 POC 决策

当前工作台 POC 改用连续页面来源预览展示解析得到的 `DocumentBlock`。文本、公式图片、图形和其他图片块根据页面号及来源坐标排列，尽量还原接近原 DOCX/PDF 的阅读顺序和视觉关系。

标注员可以点击单个块、按住 Shift 多选，或在页面上拖动框选连续区域。系统按页码、顶部坐标、左侧坐标对选中块排序，然后一次性填入题干、问题、选项 A-D 或解析。生成的每个 `ContentBlock` 都必须保留对应的 `source_span_id`。

`DocumentBlock` 仍是解析器输出和来源追溯的原子单位，但不再作为界面上强制的逐块操作单位。连续来源预览可以把多个文档块组成一个视觉区域，标注员不应为了恢复原始阅读顺序而在文本块和图片块列表之间来回切换。

右侧编辑区仍然必要，用于人工修正、删除、调整顺序和审核；它是 `content_blocks` 的权威编辑入口。题干、选项和解析旁的普通输入框或文本域只能作为纯文本投影、检索和完整度展示，不应形成第二套独立内容数据。

本 POC 不自动确定最终题目边界或字段归属。区域选择只是操作员确认后的来源绑定动作，不等同于自动拆题。

### V1 纯文本题试行边界

第一个可运行工作台仅接收题干、问题、A-D 选项和解析均为文字的题目。题本与解析区使用 LibreOffice 衍生的只读 HTML 预览，使标注员可以选中并复制原文。

右侧可以使用受限富文本编辑器处理段落和基础文字格式，但 V1 必须关闭图片、视频、表格、附件、外链和任意 HTML 插入。编辑器输出只用于前端草稿编辑；保存的业务数据仍应是平台自有字段及其文本投影。

含公式图片、图形、统计图、表格截图、纯图片选项或图文混排内容的题目明确后置。既有的 `DocumentBlock`、`SourceSpan`、`DocumentAsset` 和 `ContentBlock` 设计保留为后续扩展路径，不能因 V1 简化而删除。

申论中的“材料 1”等可复用长材料只保存一次，并以版本化来源材料关联到准确题目版本。`stem_text` 只保存该题独有文字。提交时，“要求”“问题”“参考答案”必须非空，同时“题目独有题干”与“有效共享材料版本关联”至少存在一项。

### 申论 V1 专项导航与字段规则

当科目为申论时，工作台进入主观题模式：隐藏客观题类型、A-D 选项和正确答案单选；将字段拆分为“题干正文”“要求”“问题”“参考答案”。

已确认的“归纳概括、提出对策、综合分析、应用文写作、大作文”作为受控知识点选择，而不是另一套自由文本专题。右侧题位按专项分组展示，题目身份仍保持全局稳定 ID；来源顺序同时记录专题顺序和专项内题序。上一题、下一题优先在当前专项内移动，跨边界时明确进入相邻专项。
