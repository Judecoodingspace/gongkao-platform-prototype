# PRD: Civil-Service Exam Question Bank Annotation Platform

## English Version

### 1. Background

The project needs to convert historical civil-service exam papers from Word, PDF, and later other formats into structured questions stored in a question-bank database. Teachers should be able to retrieve questions by year, province, subject, question type, knowledge point, and difficulty for paper assembly.

The current source papers are mainly Word documents. Their formats may be inconsistent, and stems, options, answers, explanations, figures, and source materials may not appear in stable positions. Therefore, the system must not rely on fully automatic parsing to write directly into the official bank. It needs manual extraction, annotation, review, and version tracking.

### 2. Goals

- Support uploading and managing source exam papers.
- Support manual question extraction beside the original source document.
- Support metadata annotation, including question type, difficulty, knowledge point, year, province, and subject.
- Support review workflow to protect question-bank quality.
- Support question-bank versioning and later retrieval for paper assembly.

### 3. User Roles

#### Annotator

Splits questions from source papers and answer materials, then fills structured fields.

#### Reviewer

Checks question content, source provenance, answer, explanation, tags, and difficulty, then approves or rejects the question.

#### Teacher

Searches approved questions and assembles teaching or practice papers.

#### Admin

Manages users, permissions, source papers, taxonomies, releases, and system configuration.

### 4. MVP Scope

#### In Scope

- DOCX source-paper upload records
- Source block display
- Answer and explanation material upload records
- Manual question creation
- Stem, question, options, answer, and explanation input
- Reusable, versioned source materials that can be linked to multiple question versions without duplicating passage text
- Subject, question type, knowledge point, year, province, and difficulty annotation
- Draft, submitted, approved, and rejected states
- Source provenance
- First-pass design for question-bank search fields

#### Out Of Scope

- Fully automatic question extraction directly into the official bank
- Complex online paper-assembly algorithms
- Mobile annotation
- Large-scale OCR for scanned papers
- Training data loop or model fine-tuning
- Commercial billing for institutions

### 5. Core Workflow

1. Admin or annotator uploads a source paper.
2. The system creates a paper version record.
3. The system parses or manually locates source blocks.
4. The annotator selects source blocks in the workbench.
5. The annotator creates a draft question.
6. The annotator fills structured fields.
7. The annotator submits the question for review.
8. The reviewer approves or rejects it.
9. Approved questions become eligible for the question bank.
10. Admin publishes stable question-bank releases by batch.

### 6. Page List

#### MVP Pages

- Task list
- Question annotation workbench
- Review workbench
- Question-bank search page
- Question detail page

#### Later Pages

- Source-paper management
- Taxonomy management
- User and permission management
- Question-bank release management
- Data quality dashboard

### 7. Question Annotation Workbench

The workbench should support:

- Left-side source paper or source block display
- Lower-left answer and explanation material display
- Right-side structured question editing form
- Far-right workflow status
- Source block selection and binding to a question
- Stem, question, options, answer, explanation, and image fields
- Save draft and submit for review

### 8. Question Fields

Basic fields:

- Subject
- Question type
- Knowledge point
- Year
- Province
- Difficulty
- Stem
- Question text
- Options
- Correct answer
- Explanation
- Source
- Status

Extensible fields:

- Score
- Suggested solving time
- Multiple-choice flag
- Image flag
- Quality tags
- Review comments

### 9. Permission Draft

- Annotator: create drafts, edit their own unsubmitted or rejected questions, submit for review.
- Reviewer: view submitted questions, approve, reject, and write review comments.
- Teacher: view released question-bank content, filter questions, export or assemble papers.
- Admin: manage all data and releases.

### 10. Success Metrics

- Annotators can complete question extraction and submission in one workbench.
- Each question can be traced to its source file and source block.
- Reviewers can see question versions and edit history.
- Approved questions can be searched by year, province, subject, type, knowledge point, and difficulty.
- When document parsing fails, the manual workflow still works.

### 11. Risks

- Historical Word files may have inconsistent formats and unstable parsing quality.
- Question type, knowledge point, and difficulty standards may need several rounds of calibration.
- Without versioning, later corrections may contaminate released question-bank data.
- Without review workflow, question quality is uncontrollable.
- Without sufficient source provenance, disputed questions are hard to inspect.

### 12. V1 Pure-Text Pilot

The first runnable workflow accepts text-only questions. A LibreOffice-derived HTML preview provides copyable source text, while a constrained rich-text editor handles text entry and basic formatting. Questions depending on formula images, diagrams, charts, screenshots, image-only options, or mixed text/image layout are deferred to the next workflow stage. This is a delivery boundary, not a removal of the long-term provenance and content-block model.

## 中文版本

### 1. 背景

项目需要把各省市历年公务员考试真题从 Word、PDF 或后续其他格式中拆解为结构化题目，沉淀到题库数据库中，方便机构老师按年份、省份、科目、题型、知识点、难度等条件抽题组卷。

当前真题来源以 Word 版为主，格式可能不统一，题干、选项、答案、解析、图表和材料位置不一定稳定。因此系统不能依赖全自动解析直接入库，需要人工拆解、标注、审核和版本追溯。

### 2. 目标

- 支持上传和管理历史真题源文件。
- 支持人工在原文旁边拆解题目。
- 支持标注题型、难度、知识点、年份、省份、科目等元数据。
- 支持审核流程，确保入库题目质量。
- 支持题库版本化和后续组卷检索。

### 3. 用户角色

#### 标注员

负责从题本和解析材料中拆出结构化题目，并补全基础字段。

#### 审核员

负责检查题目内容、来源、答案、解析、标签和难度，决定通过或驳回。

#### 机构老师

负责从已审核题库中筛选题目，用于组卷、训练或教学。

#### 管理员

负责管理用户、权限、真题来源、标签体系、发布版本和系统配置。

### 4. MVP 范围

#### 包含

- DOCX 真题上传记录
- 题本原文块展示
- 解析材料上传记录
- 人工创建题目
- 题干、问题、选项、答案、解析录入
- 可被多个题目版本按序引用的版本化共享材料，材料正文只保存一次，不重复复制到每道题中
- 科目、题型、知识点、年份、省份、难度标注
- 草稿、待审核、已通过、已驳回状态
- 来源追溯
- 第一版题库检索字段设计

#### 不包含

- 全自动拆题直接入库
- 复杂在线组卷算法
- 移动端标注
- 大规模 OCR 扫描件处理
- 训练数据闭环和模型微调
- 机构商业化计费

### 5. 核心流程

1. 管理员或标注员上传真题题本。
2. 系统生成题本版本记录。
3. 系统解析或人工定位原文块。
4. 标注员在工作台中选择原文块。
5. 标注员创建题目草稿。
6. 标注员补全题目结构化字段。
7. 标注员提交审核。
8. 审核员通过或驳回。
9. 通过后的题目进入可发布题库。
10. 管理员按批次发布稳定题库版本。

### 6. 页面清单

#### MVP 页面

- 任务列表页
- 人工拆题工作台
- 审核工作台
- 题库检索页
- 题目详情页

#### 后续页面

- 真题文件管理页
- 标签体系管理页
- 用户与权限管理页
- 题库发布版本页
- 数据质量看板

### 7. 人工拆题工作台

工作台需要支持：

- 左侧显示题本原文或原文块。
- 左侧下半区显示解析材料。
- 右侧显示结构化题目编辑表单。
- 最右侧显示当前流程状态。
- 支持选择原文块并绑定到题目。
- 支持题干、问题、选项、答案、解析和图片字段。
- 支持保存草稿和提交审核。

### 8. 题目字段

基础字段：

- 科目
- 题型
- 知识点
- 年份
- 省份
- 难度
- 题干
- 问题
- 选项
- 正确答案
- 解析
- 来源
- 状态

可扩展字段：

- 分值
- 作答时长
- 是否多选
- 是否含图
- 质量标签
- 审核意见

### 9. 权限草案

- 标注员：创建草稿、编辑自己未提交或被驳回的题目、提交审核。
- 审核员：查看待审核题目、通过、驳回、填写审核意见。
- 老师：查看已发布题库、筛选题目、导出或组卷。
- 管理员：管理全部数据和发布版本。

### 10. 成功指标

- 标注员可以在一个工作台完成题目拆解和提交。
- 每道题可以追溯到源文件和源块。
- 审核员可以明确看到题目版本和修改记录。
- 已审核题目可以按年份、省份、科目、题型、知识点、难度检索。
- 文档解析失败时，人工流程仍可继续。

### 11. 风险

- 历年真题 Word 格式不统一，解析质量波动大。
- 题型、知识点和难度标准可能需要多轮校准。
- 如果没有版本化，后续纠错会污染已发布题库。
- 如果没有审核流，题库质量不可控。
- 如果原文追溯不足，后续争议题难以定位。

### 12. V1 纯文本题试行

第一个可运行流程仅处理纯文本题。左侧使用 LibreOffice 衍生 HTML 预览提供可复制原文，右侧使用受限富文本编辑器录入文字和基础格式。依赖公式图、图形、统计图、截图、图片选项或图文混排的题目后置到下一阶段图文工作流。该范围是交付边界，不代表删除长期来源追溯和内容块模型。

申论 V1 采用主观题录入模式：归纳概括、提出对策、综合分析、应用文写作和大作文作为受控知识点；每题保存独有的题干正文、要求、问题和参考答案。申论界面不展示行测类型、A-D 选项或正确答案单选。来源文档中的专项顺序和专项内题序应保留，用于录题导航和追溯。
