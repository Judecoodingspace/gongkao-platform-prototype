# Plan: Question Annotation Workbench

## English Version

### Product Approach

First make the manual workflow reliable. Document parsing and AI assistance should improve efficiency but must not become the source of truth in the MVP.

### Candidate Architecture

#### Frontend

Candidate stack:

- React
- TypeScript
- Ant Design or a similar enterprise UI system
- Playwright for critical-flow screenshots

Rationale:

- The workbench is a dense enterprise form and workflow page.
- Ant Design style fits task-oriented middle-platform products.
- React makes later componentization straightforward.

#### Backend

Candidate stack options:

- FastAPI with Python
- NestJS with TypeScript
- Django with Python

Decision pending.

Important backend capabilities:

- File upload and storage metadata
- Parser adapter interface
- Question CRUD with versioning
- Review workflow
- Search API
- Role-based access control

#### Database

Candidate:

- PostgreSQL

Rationale:

- The structured question data has clear relationships.
- PostgreSQL supports transactions, indexes, JSONB extension fields, and full-text search extensions.
- It fits audit and version-table design.

#### Document Parsing

Candidate parser POC:

- Docling for DOCX/PDF conversion and structured extraction
- Keep a `DocumentParser` adapter boundary

Fallback:

- For simple DOCX, evaluate `python-docx` or similar lighter tools.

Rule:

- Business code must depend on the adapter interface, not directly on one parser implementation.

### Suggested Modules

```text
apps/
  web/
  api/
packages/
  shared-domain/
  parser-adapters/
docs/
prototypes/
tests/
```

This layout is not final. Do not create it until the stack decision is made.

### First Implementation Slice

1. Create minimal project app structure.
2. Define database schema for paper, paper version, document block, question, question version, and review record.
3. Add DOCX upload endpoint.
4. Store uploaded file metadata.
5. Parse or mock document blocks.
6. Render source blocks in the workbench.
7. Create one draft question linked to a source block.
8. Submit draft question for review.

### Key Risks

- Word documents may have inconsistent styles and hidden formatting.
- Parser output may not map cleanly to visual source positions.
- Data model can become unstable if versioning is added too late.
- High-density UI may become hard to use without real annotator feedback.

### Verification Strategy

- Unit tests for parser adapter output.
- API tests for question state transitions.
- Database migration tests.
- Frontend interaction tests for draft save and submit.
- Screenshot checks for the annotation workbench.

## 中文版本

### 产品策略

先以人工流程跑通为主，文档解析和 AI 辅助只作为提高效率的手段。MVP 不追求全自动拆题。

### 候选架构

#### 前端

候选技术栈：

- React
- TypeScript
- Ant Design 或类似企业级 UI 系统
- Playwright 用于关键流程截图验证

理由：

- 工作台是高密度表单和中后台页面。
- Ant Design 风格适合任务型中台。
- React 生态便于后续组件化。

#### 后端

候选技术栈：

- Python FastAPI
- TypeScript NestJS
- Python Django

待决策。

重要后端能力：

- 文件上传和存储元数据
- 解析器适配器接口
- 带版本化的题目 CRUD
- 审核工作流
- 检索 API
- 基于角色的访问控制

#### 数据库

候选：

- PostgreSQL

理由：

- 结构化题目数据关系明确。
- 支持事务、索引、JSONB 扩展字段和全文检索扩展。
- 适合后续审计和版本表设计。

#### 文档解析

候选解析器 POC：

- 使用 Docling 做 DOCX/PDF 转换和结构化抽取。
- 保留 `DocumentParser` 适配器边界。

兜底方案：

- 对于简单 DOCX，评估 `python-docx` 或类似轻量工具。

规则：

- 业务代码必须依赖适配器接口，而不是直接依赖某个解析器实现。

### 建议模块

```text
apps/
  web/
  api/
packages/
  shared-domain/
  parser-adapters/
docs/
prototypes/
tests/
```

该布局尚未最终确定。在技术栈决策前，不要创建正式应用结构。

### 第一段实现切片

1. 创建最小项目应用结构。
2. 定义 paper、paper version、document block、question、question version 和 review record 的数据库 schema。
3. 增加 DOCX 上传接口。
4. 存储上传文件元数据。
5. 解析或模拟文档块。
6. 在工作台渲染原文块。
7. 创建一条绑定原文块的题目草稿。
8. 提交题目草稿进入审核。

### 关键风险

- Word 文档样式和隐藏格式可能不统一。
- 解析器输出可能无法稳定映射到可视化来源位置。
- 如果版本化太晚加入，数据模型会变得不稳定。
- 高密度 UI 如果缺少真实标注员反馈，可能难用。

### 验证策略

- 解析器适配器输出单元测试。
- 题目状态流转 API 测试。
- 数据库迁移测试。
- 保存草稿和提交审核的前端交互测试。
- 拆题工作台截图检查。
