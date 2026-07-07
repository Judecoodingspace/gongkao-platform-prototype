# Tasks: Question Annotation Workbench

## English Version

### Phase 0: Product Validation

- [ ] Review `docs/PRD.md` with stakeholders.
- [ ] Review `prototypes/question-bank-prototype/index.html` with senior students.
- [ ] Collect feedback from at least one future annotator.
- [ ] Decide whether difficulty is set by the annotator, reviewer, or both.
- [ ] Decide the first taxonomy for subject, question type, and knowledge point.

### Phase 1: Design Baseline

- [ ] Convert the temporary HTML prototype into a Figma high-fidelity prototype.
- [ ] Create frames for 1440 x 900, 1366 x 768, and 1280 x 720.
- [ ] Add states for draft, submitted, rejected, and approved.
- [ ] Add field validation states.
- [ ] Add reviewer view.

### Phase 2: Technical Foundation

- [ ] Decide frontend stack.
- [ ] Decide backend stack.
- [ ] Decide database and migration tool.
- [ ] Decide file storage strategy.
- [ ] Decide first parser POC approach.
- [ ] Create real application repository structure.
- [ ] Add CI checks.

### Phase 3: Document Import

- [ ] Create `paper` and `paper_version` schema.
- [ ] Create upload endpoint.
- [ ] Store uploaded file metadata.
- [ ] Create parser adapter interface.
- [ ] Implement first DOCX parser POC.
- [ ] Store document blocks with source provenance.

### Phase 4: Annotation Workbench

- [ ] Render paper source blocks.
- [ ] Render explanation blocks.
- [ ] Select source block.
- [ ] Create question draft from source block.
- [ ] Edit stem, question, options, answer, explanation, and metadata.
- [ ] Save draft.
- [ ] Submit for review.
- [ ] Show field completeness and provenance status.

### Phase 5: Review

- [ ] Create reviewer queue.
- [ ] Show source provenance next to question fields.
- [ ] Approve question.
- [ ] Reject question with required reason.
- [ ] Record review history.

### Phase 6: Question Bank Release

- [ ] Create approved question search.
- [ ] Add filters for province, year, subject, type, knowledge point, and difficulty.
- [ ] Create release snapshot model.
- [ ] Add release item table.
- [ ] Make released questions stable and traceable.

## 中文版本

### 阶段 0：产品验证

- [ ] 和项目相关方评审 `docs/PRD.md`。
- [ ] 和师兄/同组成员评审 `prototypes/question-bank-prototype/index.html`。
- [ ] 至少收集一位未来标注员的反馈。
- [ ] 确认难度由标注员、审核员，还是两者共同确定。
- [ ] 确认科目、题型和知识点的第一版分类体系。

### 阶段 1：设计基线

- [ ] 将临时 HTML 原型转换为 Figma 高保真原型。
- [ ] 创建 1440 x 900、1366 x 768、1280 x 720 画板。
- [ ] 增加草稿、待审核、已驳回、已通过状态。
- [ ] 增加字段校验状态。
- [ ] 增加审核员视角。

### 阶段 2：技术基础

- [ ] 确定前端技术栈。
- [ ] 确定后端技术栈。
- [ ] 确定数据库和迁移工具。
- [ ] 确定文件存储策略。
- [ ] 确定第一版解析器 POC 方案。
- [ ] 创建正式应用仓库结构。
- [ ] 增加 CI 检查。

### 阶段 3：文档导入

- [ ] 创建 `paper` 和 `paper_version` schema。
- [ ] 创建上传接口。
- [ ] 存储上传文件元数据。
- [ ] 创建解析器适配器接口。
- [ ] 实现第一版 DOCX 解析器 POC。
- [ ] 存储带来源追溯信息的文档块。

### 阶段 4：拆题工作台

- [ ] 渲染题本原文块。
- [ ] 渲染解析材料块。
- [ ] 选择原文块。
- [ ] 从原文块创建题目草稿。
- [ ] 编辑题干、问题、选项、答案、解析和元数据。
- [ ] 保存草稿。
- [ ] 提交审核。
- [ ] 展示字段完整度和来源追溯状态。

### 阶段 5：审核

- [ ] 创建审核队列。
- [ ] 在题目字段旁展示来源追溯。
- [ ] 审核通过题目。
- [ ] 驳回题目并要求填写原因。
- [ ] 记录审核历史。

### 阶段 6：题库发布

- [ ] 创建已审核题目检索。
- [ ] 增加省份、年份、科目、题型、知识点和难度筛选。
- [ ] 创建发布快照模型。
- [ ] 增加发布条目表。
- [ ] 保证已发布题目稳定且可追溯。
