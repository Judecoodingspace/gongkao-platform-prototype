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
9. The annotator saves the draft or submits it for review.

### Required Capabilities

- File upload entry
- Source block display and selection
- Explanation material display
- Structured question form
- Option editing
- Answer selection
- Difficulty annotation
- Tag and knowledge point selection
- Save draft
- Submit for review
- Source provenance

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
- Important actions need clear feedback.
- Missing fields must be shown before review submission.

### Open Questions

- Should source blocks support multi-selection across pages?
- Should pasted question images be auto-cropped?
- Must explanation material always match the same paper version?
- Who maintains the knowledge point taxonomy?
- Is difficulty first set by the annotator or finalized by the reviewer?

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
9. 标注员保存草稿或提交审核。

### 必需能力

- 文件上传入口
- 原文块展示和选择
- 解析材料展示
- 题目结构化表单
- 选项编辑
- 答案选择
- 难度标注
- 标签和知识点选择
- 保存草稿
- 提交审核
- 来源追溯

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
- 重要操作需要明确反馈。
- 提交审核前必须提示缺失字段。

### 开放问题

- 原文块是否支持跨页多选？
- 题图粘贴后是否需要自动裁剪？
- 解析材料是否必须与题本同版？
- 知识点体系由谁维护？
- 难度由标注员初评还是审核员最终确定？
