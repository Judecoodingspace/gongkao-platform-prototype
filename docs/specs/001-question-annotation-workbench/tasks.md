# Tasks: Question Annotation Workbench

## English Version

### Phase 0: Product Validation

- [ ] Review `docs/PRD.md` with stakeholders.
- [ ] Review `prototypes/question-bank-prototype/index.html` with senior students.
- [ ] Collect feedback from at least one future annotator.
- [ ] Decide whether difficulty is set by the annotator, reviewer, or both.
- [ ] Decide the first taxonomy for subject, question type, and knowledge point.
- [x] Define the V1 pure-text question boundary: text-only stem, question, options, and explanation; mixed-content questions are deferred.
- [x] Add a V1 prototype route using LibreOffice-derived HTML preview and constrained rich-text editing.
- [ ] Validate V1 with an annotator using at least one text-only paper and record copy/paste cleanup observations without committing source content.
- [ ] Decide the V2 mixed-content entry criteria before enabling image import in the production workbench.
- [x] Define Shenlun V1 as a subjective-question mode with specialty knowledge points and no A-D option/answer workflow.
- [x] Add specialty-grouped navigation to the static prototype while preserving stable global question-slot identity.

### Phase 1: Design Baseline

- [ ] Convert the temporary HTML prototype into a Figma high-fidelity prototype.
- [ ] Create frames for 1440 x 900, 1366 x 768, and 1280 x 720.
- [ ] Add states for draft, submitted, rejected, and approved.
- [ ] Add field validation states.
- [ ] Add reviewer view.

### Phase 2: Technical Foundation

- [x] Decide frontend stack.
- [x] Decide backend stack.
- [x] Decide database and migration tool.
- [ ] Decide file storage strategy.
- [ ] Decide first parser POC approach.
- [ ] Create real application repository structure.
- [ ] Add CI checks.

### Shenlun V1 Persistence Runbook

- [x] `SHV1-001` Review and approve gate `G-01`; record exact stack and runtime versions in `plan.md`.
- [x] `SHV1-002` Review and approve gate `G-02`; resolve every open contract question without changing field names in implementation code first.
- [x] `SHV1-003` Review and approve gate `G-03`; create/reuse a dedicated GitHub issue and record the reviewed migration boundary.
- [x] `SHV1-004` Scaffold only the approved backend, migration, and test structure; add no frontend persistence yet.
- [x] `SHV1-005` Implement migrations `M-001` through `M-005` from `migration-plan.md` with sanitized reference seeds only.
- [x] `SHV1-006` Add migration upgrade, schema inspection, idempotent seed, and disposable-database recovery tests.
- [x] `SHV1-007` Implement domain/service transactions for draft create, optimistic-lock patch, submit, and correction-version creation.
- [x] `SHV1-008` Implement the endpoints and errors in `api-contract.md`; do not add review endpoints or mixed-content payloads in this slice.
- [x] `SHV1-009` Add all required contract tests, including exact four-field round-trip, source-order conflict, stale update, and immutable submitted version.
- [x] `SHV1-010` Complete gate `G-04`; record migration commands, test counts, rollback notes, and limitations in the GitHub issue.
- [x] `SHV1-011` Convert the approved static behavior into the selected production frontend and wire save/reload/submit using plain-text payloads.
- [x] `SHV1-012` Complete gate `G-05` with sanitized end-to-end fixtures, interaction tests, screenshot checks, and an issue completion note.

Tasks are dependency ordered. Terra must not begin `SHV1-004` before `SHV1-001` through `SHV1-003` are approved, `SHV1-011` before `SHV1-010`, or mark a task complete without the checks named in that task.

### Phase 3: Document Import

- [x] `WDV1-001` Approve `G-06` Word design; see `WDV1_G06_FROZEN_DECISIONS.md`.
- [x] `WDV1-002` Implement G-07 raw DOCX intake/version finalization; do not recreate existing `papers` or `paper_versions`; see `WDV1_G07_ACCEPTANCE_REPORT.md`.
- [ ] `WDV1-003` Implement the G-08 Shenlun text-first source-structuring foundation: independent processing history and natural-paragraph ordered text blocks, without business-semantic inference; this alone does not pass G-08.
- [ ] `WDV1-004` Implement G-08 visual preview, visual/source linking, image/other reliable evidence, and the remaining visible partial-structuring behavior.
- [ ] `WDV1-005` Implement G-09 explicit multi-block field fill and field-to-block provenance.
- [ ] `WDV1-006` Complete G-09 browser acceptance with sanitized DOCX fixtures.

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

- [x] 确定前端技术栈。
- [x] 确定后端技术栈。
- [x] 确定数据库和迁移工具。
- [ ] 确定文件存储策略。
- [ ] 确定第一版解析器 POC 方案。
- [ ] 创建正式应用仓库结构。
- [ ] 增加 CI 检查。

### 申论 V1 持久化执行清单

- [x] `SHV1-001` 评审并批准 `G-01`，在 `plan.md` 记录准确技术栈和运行时版本。
- [x] `SHV1-002` 评审并批准 `G-02`，先解决契约问题，不得先在实现代码中自行改字段名。
- [x] `SHV1-003` 评审并批准 `G-03`，创建或复用专用 GitHub issue，记录已评审的迁移边界。
- [x] `SHV1-004` 只搭建已批准的后端、迁移和测试结构，暂不连接前端持久化。
- [x] `SHV1-005` 按 `migration-plan.md` 实现 `M-001` 至 `M-005`，只能加入脱敏的受控种子数据。
- [x] `SHV1-006` 增加迁移升级、schema 检查、种子幂等和一次性测试数据库恢复测试。
- [x] `SHV1-007` 实现草稿创建、乐观锁更新、提交和新建修订版本的领域服务事务。
- [x] `SHV1-008` 实现 `api-contract.md` 中的端点和错误；本切片不得扩展审核端点或图文 payload。
- [x] `SHV1-009` 增加全部契约测试，包括四字段原样往返、来源顺序冲突、过期更新和已提交版本不可变。
- [x] `SHV1-010` 完成 `G-04`，在 GitHub issue 记录迁移命令、测试数量、回滚说明和已知限制。
- [x] `SHV1-011` 将已确认的静态交互迁移到选定正式前端，并用纯文本 payload 接通保存、重载和提交。
- [x] `SHV1-012` 用脱敏端到端 fixture、交互测试、截图检查和 issue 完成记录通过 `G-05`。

以上任务按依赖排序。Terra 不得在 `SHV1-001` 至 `SHV1-003` 未批准时开始 `SHV1-004`，不得在 `SHV1-010` 前开始 `SHV1-011`，也不得在未执行任务所列检查时将其标记完成。

### 阶段 3：文档导入

- [x] `WDV1-001` 批准 `G-06` Word 设计；见 `WDV1_G06_FROZEN_DECISIONS.md`。
- [x] `WDV1-002` 实现 G-07 原始 DOCX 进入系统和来源版本定稿；不得重建已有 `papers` 或 `paper_versions`；见 `WDV1_G07_ACCEPTANCE_REPORT.md`。
- [ ] `WDV1-003` 实现 G-08 申论 text-first 来源结构化基础：独立处理历史、自然段级有序文字块，且无业务语义推断；完成本项不等于 G-08 通过。
- [ ] `WDV1-004` 实现 G-08 视觉预览、视觉/来源联动、图片/其他可靠证据及其余可见的部分结构化失败行为。
- [ ] `WDV1-005` 实现 G-09 明确多块填入和字段到块来源关系。
- [ ] `WDV1-006` 用脱敏 DOCX fixture 完成 G-09 浏览器验收。

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
