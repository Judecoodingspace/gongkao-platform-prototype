# Plan: Question Annotation Workbench

## English Version

### G-01 Approved Technology Baseline (2026-08-23)

The following baseline is approved for the Shenlun V1 persistence slice:

- Web: React 19, TypeScript 5.7, and Ant Design 5, built with Node.js 22 LTS and npm 10.
- API: CPython 3.12, FastAPI, Pydantic, SQLAlchemy 2.x, and Alembic 1.x; dependencies are managed by uv with `pyproject.toml` and an exact `uv.lock`.
- Database: PostgreSQL 16.
- Verification: Pytest for backend/migration/API tests and Playwright for production-web interaction and screenshot tests.

Use versions compatible with these approved major versions and pin exact dependency versions in generated lockfiles. Do not use the Python 3.13 DOCX POC environment as the production API runtime, because parser and ML dependency behavior in that environment is not the production application contract.

### V1 Pure-Text Pilot Addendum

The next prototype slice validates the operational loop for text-only questions before the production application implementation begins. It uses LibreOffice-derived HTML as the copyable source preview and a constrained rich-text editor for stem, question text, options, and explanation. Images, video, tables, attachments, links, arbitrary HTML insertion, and mixed-content questions are out of scope.

The editor HTML is a prototype draft representation, not the future database contract. `DocumentParser`, `DocumentBlock`, `SourceSpan`, `DocumentAsset`, and `ContentBlock` remain the planned V2 route for mixed-content questions.

### Product Approach

First make the manual workflow reliable. Document parsing and AI assistance should improve efficiency but must not become the source of truth in the MVP.

### Approved Shenlun V1 Architecture

#### Frontend

Selected stack:

- React
- TypeScript
- Ant Design or a similar enterprise UI system
- Playwright for critical-flow screenshots

Rationale:

- The workbench is a dense enterprise form and workflow page.
- Ant Design style fits task-oriented middle-platform products.
- React makes later componentization straightforward.

#### Backend

Selected stack:

- FastAPI with Python
- Pydantic
- SQLAlchemy 2.x
- Alembic 1.x

Important backend capabilities:

- File upload and storage metadata
- Parser adapter interface
- Question CRUD with versioning
- Review workflow
- Search API
- Role-based access control

#### Database

Selected:

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

This layout is the approved repository direction. `SHV1-004` begins with the API, migration, and backend-test portions only; the production web application begins after `G-04`.

### First Implementation Slice

1. Scaffold the approved FastAPI, Alembic, and backend test structure.
2. Implement migrations `M-001` through `M-005`, including reusable source materials and exact question-version links.
3. Implement transactional draft/material create, patch, submit, and correction-version services.
4. Implement the approved API contract and errors.
5. Pass migration and API contract tests to complete `G-04`.
6. Begin React persistence wiring only after `G-04`.

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

### Shenlun V1 Persistence Execution Gates

The executable contract is split between:

- [`data-model.md`](./data-model.md): entity ownership, versioning, and source-order semantics;
- [`api-contract.md`](./api-contract.md): framework-neutral request, response, validation, concurrency, and transaction behavior;
- [`migration-plan.md`](./migration-plan.md): PostgreSQL mapping, migration order, recovery, and verification.
- [`g02-g03-review.md`](./g02-g03-review.md): approved gate decisions, resolved findings, and implementation entry criteria.

No implementation agent may skip these gates:

- `G-01 Stack`: stakeholders explicitly select frontend, backend, database, ORM, migration tool, package manager, and supported runtime versions. The current candidate list is not a decision.
- `G-02 Contract` (`approved 2026-08-28`): four Shenlun fields, reusable versioned source materials, five controlled knowledge points, source-order semantics, API endpoints, immutable-version behavior, idempotency, and optimistic locking are fixed in the contract.
- `G-03 Migration` (`approved 2026-08-28`): SQL naming, non-cascading FK behavior, deferred current-version ownership FKs, indexes, deterministic seeds, disposable PostgreSQL test database, backup, and rollback policy are fixed in the migration plan.
- `G-04 Backend acceptance` (`approved 2026-08-31`): migrations and backend contract tests pass before frontend persistence wiring begins.
- `G-05 End-to-end acceptance`: the production frontend can save, reload, switch, submit, and conflict-test sanitized drafts without bypassing human review.

Terra must execute tasks `SHV1-001` through `SHV1-012` in `tasks.md` in order. It must stop at any unapproved gate, preserve unrelated worktree changes, and record each implementation checkpoint in the relevant GitHub issue with no private paper content.

## 中文版本

### 产品策略

先以人工流程跑通为主，文档解析和 AI 辅助只作为提高效率的手段。MVP 不追求全自动拆题。

### G-01 已批准技术基线（2026-08-23）

申论 V1 持久化切片使用以下已批准基线：

- Web：React 19、TypeScript 5.7、Ant Design 5；运行于 Node.js 22 LTS 和 npm 10。
- API：CPython 3.12、FastAPI、Pydantic、SQLAlchemy 2.x、Alembic 1.x；依赖使用 uv、`pyproject.toml` 和精确 `uv.lock` 管理。
- 数据库：PostgreSQL 16。
- 验证：后端、迁移和 API 使用 Pytest；正式 Web 交互和截图使用 Playwright。

依赖版本必须与以上已批准主版本兼容，并在生成的 lockfile 中锁定精确版本。DOCX POC 使用的 Python 3.13 环境不作为生产 API 运行时，因为其中解析和机器学习依赖的行为不构成正式应用契约。

### 已批准的申论 V1 架构

#### 前端

已选技术栈：

- React
- TypeScript
- Ant Design 或类似企业级 UI 系统
- Playwright 用于关键流程截图验证

理由：

- 工作台是高密度表单和中后台页面。
- Ant Design 风格适合任务型中台。
- React 生态便于后续组件化。

#### 后端

已选技术栈：

- Python FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic 1.x

重要后端能力：

- 文件上传和存储元数据
- 解析器适配器接口
- 带版本化的题目 CRUD
- 审核工作流
- 检索 API
- 基于角色的访问控制

#### 数据库

已选：

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

该布局已作为申论 V1 的工程基线。`SHV1-004` 先创建 API、迁移和后端测试部分；正式 Web 应用在 `G-04` 通过后开始。

### 第一段实现切片

1. 搭建已批准的 FastAPI、Alembic 和后端测试结构。
2. 实现 `M-001` 至 `M-005`，包括可复用共享材料和准确题目版本关联。
3. 实现材料/题目草稿创建、更新、提交和新建修订版本的事务服务。
4. 实现已批准的 API 契约和错误语义。
5. 通过迁移和 API 契约测试，完成 `G-04`。
6. 只有在 `G-04` 通过后才开始 React 持久化接线。

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

### 申论 V1 持久化执行门禁

可执行工程契约拆分为：

- [`data-model.md`](./data-model.md)：实体归属、版本化和专项来源顺序语义；
- [`api-contract.md`](./api-contract.md)：与框架无关的请求、响应、校验、并发和事务行为；
- [`migration-plan.md`](./migration-plan.md)：PostgreSQL 映射、迁移顺序、恢复和验证。
- [`g02-g03-review.md`](./g02-g03-review.md)：已批准门禁决策、已解决问题和实现入口条件。

后续模型不得跳过以下门禁：

- `G-01 技术栈`：相关方明确选择前端、后端、数据库、ORM、迁移工具、包管理器和支持的运行时版本；当前候选列表不等于已决策。
- `G-02 契约`（`2026-08-28 已批准`）：申论四字段、可复用版本化共享材料、五个受控知识点、专项来源顺序、API 端点、版本不可变、幂等和乐观锁规则已固定。
- `G-03 迁移`（`2026-08-28 已批准`）：SQL 命名、非级联外键、延迟当前版本归属外键、索引、确定性种子、一次性 PostgreSQL 测试库、备份与回滚策略已固定。
- `G-04 后端验收`（`2026-08-31 已批准`）：迁移和后端契约测试通过后，才能开始前端持久化接线。
- `G-05 端到端验收`：正式前端使用脱敏草稿完成保存、重载、切题、提交和并发冲突验证，且不能绕过人工审核。

Terra 必须按 `tasks.md` 中 `SHV1-001` 至 `SHV1-012` 的依赖顺序执行。任一门禁未批准时应停止，不得猜测；必须保留工作区无关修改，并在对应 GitHub issue 记录每个实现检查点，且不得包含私有试卷内容。
