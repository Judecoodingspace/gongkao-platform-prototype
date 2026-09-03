# Review and Change Log / 评审与修改记录

## Purpose / 用途

This file records feedback from prototype reviews and business discussions before the feedback becomes a formal requirement.

本文档用于记录每次原型评审和业务讨论中的原始意见，并在意见成为正式需求前完成分析、决策与追踪。

The workflow is:

1. Record the original feedback without silently rewriting its meaning.
2. Separate the underlying problem from a proposed solution.
3. Analyze product, workflow, data, permission, and engineering impact.
4. Mark the decision as `Accepted`, `Rejected`, or `Deferred`.
5. Synchronize accepted decisions to the relevant PRD, spec, plan, task, data model, acceptance checklist, or prototype.

处理流程：

1. 忠实记录原始意见，不在记录时擅自改变其含义。
2. 区分“需要解决的问题”和“讨论者提出的解决方案”。
3. 分析其对产品、业务流程、数据、权限和工程实现的影响。
4. 将结论标记为 `已接受`、`已拒绝` 或 `暂缓`。
5. 把已接受的结论同步到相应的 PRD、spec、plan、tasks、data-model、acceptance-checklist 或原型中。

## Status Definitions / 状态定义

| Status                  | 中文   | Meaning                                                               |
| ----------------------- | ------ | --------------------------------------------------------------------- |
| `Proposed`            | 待分析 | Feedback has been recorded but not fully analyzed.                    |
| `Needs Clarification` | 待澄清 | Key user, scenario, rule, or boundary is still unclear.               |
| `Accepted`            | 已接受 | The team agrees to make the change.                                   |
| `Rejected`            | 已拒绝 | The team decides not to make the change; the reason must be recorded. |
| `Deferred`            | 暂缓   | The feedback is valid but is outside the current milestone.           |
| `Implemented`         | 已实现 | The accepted change has been implemented.                             |
| `Verified`            | 已验证 | The change has passed the agreed acceptance check.                    |

## Review Entry Template / 单次评审记录模板

Copy this section for every discussion. Use an ID such as `REV-20260707-01`.

每次讨论后复制本节，并使用类似 `REV-20260707-01` 的编号。

### REV-YYYYMMDD-01: Discussion title / 讨论主题

**Meeting information / 会议信息**

- Date / 日期：
- Participants and roles / 参与人及角色：
- Recorder / 记录人：
- Material reviewed / 评审材料：
- Review goal / 本次目标：

**Original feedback / 原始意见**

| ID   | Area                                             | Original feedback                                                   | Raised by | Initial priority  | Status       |
| ---- | ------------------------------------------------ | ------------------------------------------------------------------- | --------- | ----------------- | ------------ |
| F-01 | Prototype / Business / Data / Permission / Other | Record the feedback as closely as possible to the original wording. |           | P0 / P1 / P2 / P3 | `Proposed` |

**Analysis / 分析**

#### F-01

- Underlying problem / 实际问题：
- User and scenario / 用户与场景：
- Current behavior / 当前行为：
- Expected outcome / 期望结果：
- Is the proposed solution the only option? / 原建议是否为唯一方案：
- Affected workflow / 受影响流程：
- Data and versioning impact / 数据与版本影响：
- Permission and audit impact / 权限与审计影响：
- Prototype impact / 原型影响：
- Engineering impact / 工程影响：
- Risks and edge cases / 风险与边界情况：
- Open questions and evidence needed / 待澄清问题与所需依据：

**Decision / 决策**

| Feedback ID | Decision                                   | Reason | Milestone   | Owner |
| ----------- | ------------------------------------------ | ------ | ----------- | ----- |
| F-01        | `Accepted` / `Rejected` / `Deferred` |        | MVP / Later |       |

**Document and implementation synchronization / 文档与实现同步**

| Target                      | Required change | Owner | Status     | Link or commit |
| --------------------------- | --------------- | ----- | ---------- | -------------- |
| `docs/PRD.md`             |                 |       | Todo       |                |
| Relevant`spec.md`         |                 |       | Todo       |                |
| `plan.md` or `tasks.md` |                 |       | Todo       |                |
| `data-model.md`           |                 |       | Not needed |                |
| `acceptance-checklist.md` |                 |       | Todo       |                |
| HTML/Figma prototype        |                 |       | Todo       |                |

**Verification / 验证**

- Acceptance scenario / 验收场景：
- Reviewer / 验证人：
- Verification result / 验证结果：
- Remaining issues / 遗留问题：

---

### REV-20260902-01: G-05 end-to-end acceptance / G-05 端到端验收

**Decision and verification / 决策与验证**

- `G-05` 通过：React 工作台在一次性 PostgreSQL 16 `gongkao_api_test` 与真实 FastAPI 上完成脱敏草稿创建、保存、重载、切题前保存、真实 `STALE_DRAFT` 冲突提示与重新加载；没有路由拦截或审核绕过。
- Playwright 在 1440×900、1366×768 和 1280×720 生成并复跑截图基线；正常复跑在空 schema 迁移、最小脱敏试卷版本夹具恢复后通过。
- 临时 `X-Actor-Id` 仍仅用于开发/测试；未实现正式认证、审核、图文内容或发布能力。验收使用后应停止 FastAPI 与 `postgres-test`，不保留测试服务或数据库数据。

**Traceability / 追溯**

- Web issue #3 记录开始、前端工作流修正、真实服务检查和完成结论；SHV1-011 修正提交为 `b0a7069`，G-05 测试与配置在独立 Web 提交中记录。

---

## Review Records / 评审记录

### REV-20260803-01: Switch DocumentBlock POC source from Docling to LibreOffice PDF / DocumentBlock POC 数据源从 Docling 切换到 LibreOffice PDF

**Meeting information / 会议信息**

- Date / 日期：2026-08-03
- Participants and roles / 参与人及角色：项目负责人、Codex
- Recorder / 记录人：Codex
- Material reviewed / 评审材料：`scripts/docling_poc/convert_with_docling.py`，`scripts/document_block_poc/build_document_blocks.py`，`docs/docling-poc-results/2026年3月29日..._答案解析.docling.json`，`docs/libreoffice-poc-results/01-.../...pdf`，`docs/docling-poc.md`，`docs/libreoffice-poc.md`
- Review goal / 本次目标：解决 Docling 路线下 Word 公式图片被替换为 24×11 占位图的问题，确定 DocumentBlock POC 的下一阶段数据源

**Validation boundary / 可验证性边界**

- 当前可以验证：LibreOffice 能把 DOCX 转成 PDF 且 PDF 中方法二公式完整保留（已人工对照）；`build_document_blocks.py` 改用 PDF 输入源后能产出与 Docling 路线同构的 `document-blocks.json`；原型 HTML 无需改动即可加载新 JSON。
- 当前不能验证：后端 DocumentParser 服务、数据库持久化、真实图片文件上传到对象存储、PDF parser 对所有题型的覆盖率、跨样本稳定性、生产环境 LibreOffice worker 的安全隔离。
- 本轮只改 POC 脚本和 POC 文档，不进入正式前后端应用开发，不提交真实试卷正文或生成的解析结果。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | ---- | ----------------- | ---------------- | ------ |
| PDF-01 | Parser POC | Docling 解析 Word 公式图片时输出 24×11 占位图，方法二那段公式在原型左侧看不到；需要换数据源让公式图能正确进入 DocumentBlock。 | P0 | `Proposed` |

**Analysis / 分析**

#### PDF-01：Docling 对 DrawingML 图片的栅格化依赖 LibreOffice，且 torch 在 Python 3.13 上不稳定

- 实际问题：在原型左侧加载 `document-blocks.json` 后，第 46 题方法二的公式图位置只显示占位图，标注员看不到真实公式，无法完成"从当前原文块填入"。
- 根因链（已逐项验证）：
  1. Word 中方法二的公式是图片形式（从外部粘贴或截图嵌入），被 Word 用 DrawingML/VML 包装。
  2. Docling 的 `MsWordDocumentBackend` 处理 DrawingML 时调用 `_convert_elements_via_docx()`，通过 LibreOffice 把 DrawingML 栅格化为 PNG 写入 `image.uri`。
  3. 当 LibreOffice 不可用时，`pil_image=None`，`_add_picture_to_doc` 创建无 image 内容的占位 PictureItem，最终在 JSON 里输出统一 24×11 占位图（`iVBORw0KGgoAAAANSUhEUgAAABgAAAALCAYAAABlNU3N...`）。
  4. 当前环境 `convert_with_docling.py` 未配置 LibreOffice 路径，`DOCLING_LIBREOFFICE_CMD` 未设置，soffice 不在 PATH，Docling 走"无 LibreOffice"路径，全部 DrawingML 公式图变成占位图。
  5. 即使配置 LibreOffice，Docling 在本机 Python 3.13 上的 `torch` 依赖已损坏（`c10.dll` 加载失败，`WinError 1114`），`import docling` 阶段就报错，无法启动解析。
- 对比验证：LibreOffice headless 单独把同一份 DOCX 转 PDF，PDF 中方法二公式完整保留（已人工对照 PDF 与 Word 原图）。
- 路线选择：放弃"修 torch + 配置 Docling LibreOffice 后端"路线，改为直接用 LibreOffice 生成的 PDF 作为 `build_document_blocks.py` 的输入源。理由：
  - PDF parser（pdfplumber/PyMuPDF）依赖轻量，不依赖 torch，在 Python 3.13 Windows 上稳定。
  - PDF 中图片是原生嵌入对象，可直接抽取为 PNG 字节流转 data URI，不依赖 DrawingML 栅格化。
  - PDF parser 自带 `page_no` 和 `bbox`，比 Docling 当前 `prov: []` 全空的来源信息更完整。
  - LibreOffice → PDF 路线已在本机验证可用，且 `docs/libreoffice-poc.md` 已有完整记录。
- 不采用"整段截图入库"方案：合作者曾提出把含公式的解析整段截图存入数据库。该方案违反 `constitution.md` 第 4 原则（保留原始文本）和 `acceptance-checklist.md` 数据验收项（文本投影可搜索、图片通过资源 ID 引用）。整段截图会牺牲文字搜索、版本 diff、来源追溯能力，且后期组卷导出版式不可控。`region_screenshot` 只作为无法安全拆分时的兜底内容块，不是主路径。
- 范围边界：
  - 本轮只改 `build_document_blocks.py` 的输入源，不改原型 HTML、不改数据模型、不改 Docling 脚本。
  - PDF 路线只负责提供原文块（文本块 + 图片块），不自动识别题目边界、不自动归类公式图到题干/选项/解析。图片归属仍由标注员在工作台人工确认。
  - `document-blocks.json` schema 保持向后兼容，新增 `source_format` 字段区分 `docling` 和 `libreoffice-pdf`。
  - 不把 Docling 路线删除，保留 `build_from_docling()` 函数作为备选；torch 修复后可重新启用。

**Decision / 决策**

| Feedback ID | Decision | Reason | Milestone | Owner |
| ----------- | -------- | ------ | --------- | ----- |
| PDF-01 | `Accepted` | 改用 LibreOffice PDF 作为 DocumentBlock POC 的主数据源，绕开 Docling + torch 的不稳定性。 | Prototype POC | Codex |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| ------ | --------------- | ----- | ------ | -------------- |
| `scripts/document_block_poc/build_document_blocks.py` | 新增 `build_from_pdf()` 函数和 `--from-pdf` 命令行参数；schema 加 `source_format` 字段；保留现有 `build_from_docling()` 不删除 | Codex | Todo | |
| `scripts/document_block_poc/requirements.txt` 或等价依赖声明 | 新增 pdfplumber 或 PyMuPDF 依赖 | Codex | Todo | |
| `docs/libreoffice-poc.md` | 补充 PDF 作为 DocumentBlock 数据源的说明和运行命令 | Codex | Todo | |
| `prototypes/question-bank-prototype/README.md` | 更新本地 DocumentBlock 测试流程，说明可加载 PDF 路线生成的 JSON | Codex | Todo | |
| `docs/docling-poc.md` | 记录 Docling 在本机的 torch 依赖问题，标注为当前不可用路径 | Codex | Todo | |
| GitHub issue（如有对应 issue） | 记录本轮开始和完成结论 | Codex | Todo | |

**Verification / 验证**

- Acceptance scenario / 验收场景：用 LibreOffice 把第 46 题所在 DOCX 转 PDF，跑新的 `build_document_blocks.py --from-pdf` 生成 `document-blocks.json`，在原型 HTML 加载该 JSON，翻到方法二那段，左侧 DocumentBlock 列表应出现真实公式图片（非 24×11 占位图），点击"从当前原文块填入"后右侧解析区应出现带 `source_span_id` 的图片 ContentBlock。
- Reviewer / 验证人：项目负责人
- Verification result / 验证结果：待实现后验证
- Remaining issues / 遗留问题：PDF parser 对表格、复杂版式的文本抽取顺序可能与 Word 原文有差异，需要在真实样本上人工对照；公式图的归属（题干/选项/解析）仍需人工确认；后续若 torch 修复，Docling 路线可重新评估。

---

### REV-20260801-03: Local DocumentBlock source-list integration / 本地 DocumentBlock 来源块接入

**Meeting information / 会议信息**

- Date / 日期：2026-08-01
- Participants and roles / 参与人及角色：项目负责人、Codex
- Recorder / 记录人：Codex
- Material reviewed / 评审材料：`prototypes/question-bank-prototype/index.html`，`scripts/document_block_poc/build_document_blocks.py`，`prototypes/question-bank-prototype/README.md`
- Review goal / 本次目标：把本地 LibreOffice/Docling POC 后续可归一化出的 `DocumentBlock` 样例接入左侧来源块列表，让“一键填入”使用真实解析块数据而不是 HTML 中写死的模拟块

**Validation boundary / 可验证性边界**

- 当前可以验证：本地 Docling JSON 可转换为 `DocumentBlock` JSON；静态原型可选择本地 JSON 并渲染左侧来源块；右侧“从当前原文块填入”使用当前块文本和 `source_span_id`。
- 当前不能验证：后端 DocumentParser 服务、数据库持久化、真实图片文件上传、图片裁剪、多人协作、审核复查链路。
- 本轮不把真实解析正文写入受版本控制文件；生成的 `docs/document-block-poc-results/` 已加入 git ignore。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | ---- | ----------------- | ---------------- | ------ |
| DB-01 | Prototype / Parser POC | 把 LibreOffice/Docling 解析出的真实 `DocumentBlock` 样例接进左侧块列表，让“一键填入”用真实块数据，而不是写死的模拟文本。 | P0 | `Implemented` |

**Analysis / 分析**

#### DB-01：真实样例通过本地文件加载，不固化到 HTML

- 实际问题：上一轮 `content_blocks` POC 只验证了交互外形，左侧来源块仍是写死模拟文本，无法验证真实解析块的一键填入体验。
- 安全边界：真实试卷正文不能进入 `index.html`、README、GitHub issue 或其他受版本控制文档。
- 实现决策：新增本地转换脚本，把 ignored 的 Docling JSON 转成 ignored 的 `DocumentBlock` JSON；静态 HTML 通过文件选择器加载该 JSON。加载控件放在题本区顶部、DOCX/HTML 选择行下方、预览框上方，避免被大面积预览区压到折叠以下。转换脚本输出“文本样本 + 图片样本”，并把 Docling 图片的 `image.uri`、宽高和 MIME 写入 asset，避免截断后完全没有图片块，也让原型能渲染真实图片而不是仅显示占位。
- 交互决策：加载后左侧来源块列表由 `DocumentBlock` 生成；点击来源块后，题干、选项、解析的“从当前原文块填入”生成带 `source_span_id` 的 ContentBlock；问题字段仍保持纯文本。
- 图片边界：若来源块是图片节点，题干会生成图形块，选项/解析生成图片块；公式识别仍只是基于标签/文本的原型级判断，不能作为生产规则。

**Decision / 决策**

| Feedback ID | Decision | Reason | Milestone | Owner |
| ----------- | -------- | ------ | --------- | ----- |
| DB-01 | `Implemented` | 已完成本地 DocumentBlock JSON 加载和来源块填入联动，适合下一轮用真实样本做人工操作体验验证。 | Prototype POC | Codex |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| ------ | --------------- | ----- | ------ | -------------- |
| `.gitignore` | 忽略 `docs/document-block-poc-results/` | Codex | Done | 本地修改 |
| `scripts/document_block_poc/build_document_blocks.py` | 新增 Docling JSON 到本地 DocumentBlock JSON 的转换脚本 | Codex | Done | 本地修改 |
| `prototypes/question-bank-prototype/index.html` | 新增选择 DocumentBlock JSON、渲染来源块、来源块文本/图片筛选、按当前来源块生成 ContentBlock 的交互，并将加载入口上移到题本首屏 | Codex | Done | 本地修改 |
| `prototypes/question-bank-prototype/README.md` | 增加本地 DocumentBlock 测试流程和隐私边界 | Codex | Done | 本地修改 |
| GitHub issue #2 | 记录本轮开始和完成结论 | Codex | Done | https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/2#issuecomment-5151306495 / https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/2#issuecomment-5151321337 |

**Verification / 验证**

- Acceptance scenario / 验收场景：从本地 Docling JSON 生成 `DocumentBlock` JSON，打开静态原型，选择该 JSON 后左侧来源块替换为真实解析块，点击来源块并填入右侧字段。
- Reviewer / 验证人：Codex
- Verification result / 验证结果：`python -m py_compile scripts\document_block_poc\build_document_blocks.py` 通过；用本地 `docs/docling-poc-results/` 生成 3 个 ignored 的 `*.document-blocks.json`，使用 `--max-blocks 500 --image-limit 50`；题本样例生成 500 个文本块和 14 个图片块，解析样例生成 500 个文本块和 30 个图片块；题本样例 14 个图片块均带 data URI；静态扫描确认 DocumentBlock 文件选择、文本/图片筛选、归一化、图片预览渲染和 `source_span_id` 使用入口均存在；Chrome headless 截图确认 1920 x 900 首屏可见“选择 DocumentBlock JSON”和来源块列表，并用临时 HTML 验证图片 data URI 可渲染。
- Remaining issues / 遗留问题：仍需人工在浏览器中选择本地 JSON 文件验证真实操作手感；后续正式实现应由后端 DocumentParser 直接提供 `DocumentBlock` API，而不是依赖前端读取本地 JSON。

---

### REV-20260801-02: Content blocks interaction POC / 图文内容块交互原型

**Meeting information / 会议信息**

- Date / 日期：2026-08-01
- Participants and roles / 参与人及角色：项目负责人、Codex
- Recorder / 记录人：Codex
- Material reviewed / 评审材料：`prototypes/question-bank-prototype/index.html`，`prototypes/question-bank-prototype/README.md`
- Review goal / 本次目标：在现有静态 HTML 原型中验证操作员能否把文本块、图片块和公式/图形图片块组合为题干、选项和解析，并导出 `content_blocks` JSON

**Validation boundary / 可验证性边界**

- 当前可以验证：内容块新增、删除、上移、下移、模拟来源标记、从当前原文块一键填入、整题 JSON 预览和基础布局。
- 当前不能验证：真实图片上传、裁剪、对象存储、后端保存、数据库版本化、富文本编辑器、正式 React/Vue 组件实现。
- 本轮只修改静态 HTML 原型和原型 README，不写入真实题库，不提交真实试卷内容。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | ---- | ----------------- | ---------------- | ------ |
| CB-01 | Prototype / Content blocks | 先在现有静态 HTML 原型里做 `content_blocks` 交互 POC，验证文本块 + 图片块/公式图块组成题干、选项、解析，并能调整顺序和保存为 JSON。 | P0 | `Implemented` |

**Analysis / 分析**

#### CB-01：用静态原型验证内容块编辑成本

- 实际问题：题干、选项和解析可能出现文字夹杂图片、公式图、图形图，单一 textarea 或整段截图都不能同时满足可搜索、可编辑、可审核和来源追溯。
- 原型决策：题干、选项 A-D、解析升级为内容块编辑区；问题暂时保持普通文本字段。
- 图片策略：本轮只生成 mock asset 和占位预览，验证归属、顺序和类型表达，不处理真实上传。
- 来源策略：从当前原文块填入会生成 text 类型 ContentBlock，并带模拟 `source_span_id`；块级“标记来源”用于验证后续 `SourceSpan` 绑定入口。
- JSON 策略：原型弹窗输出 `stem_blocks`、`option_blocks`、`explanation_blocks`，用于检查 UI 操作是否能产出数据模型所需结构。

**Decision / 决策**

| Feedback ID | Decision | Reason | Milestone | Owner |
| ----------- | -------- | ------ | --------- | ----- |
| CB-01 | `Implemented` | 已在静态原型中完成最小内容块交互，能支持下一轮人工试用和数据模型回看。 | Prototype POC | Codex |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| ------ | --------------- | ----- | ------ | -------------- |
| `prototypes/question-bank-prototype/index.html` | 增加题干、选项 A-D、解析内容块编辑器，支持 mock 图片块、排序、删除、来源标记和 JSON 预览 | Codex | Done | 本地修改 |
| `prototypes/question-bank-prototype/README.md` | 记录 `content_blocks` POC 能力、边界和下一步试用建议 | Codex | Done | 本地修改 |
| GitHub issue #2 | 记录本轮开始和完成结论 | Codex | Done | https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/2#issuecomment-5150999162 / https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/2#issuecomment-5151030498 |

**Verification / 验证**

- Acceptance scenario / 验收场景：打开静态原型，确认题干、选项 A-D、解析均有内容块编辑区；可新增文本块和 mock 图片/公式/图形块；块可上移、下移、删除和标记模拟来源；可从当前原文块填入；JSON 弹窗结构符合 `content_blocks` 思路。
- Reviewer / 验证人：Codex
- Verification result / 验证结果：静态扫描确认 6 个内容块编辑器、13 个新增块按钮、6 个从当前原文块填入按钮、7 个 JSON 预览入口；Chrome headless 可渲染本地 HTML；已在 1440 x 900 普通界面和 1280 x 720 JSON 弹窗截图检查，未见明显重叠或弹窗截断。
- Remaining issues / 遗留问题：需要人工标注员试用后决定是否保留当前操作密度；真实图片上传、图片来源裁剪、对象存储、后端保存、审核复查和正式组件化仍属于后续阶段。

---

### REV-20260801-01: Mixed content blocks for question fields / 题目字段图文内容块

**Meeting information / 会议信息**

- Date / 日期：2026-08-01
- Participants and roles / 参与人及角色：项目负责人、Codex
- Recorder / 记录人：Codex
- Material reviewed / 评审材料：`docs/specs/001-question-annotation-workbench/spec.md`，`docs/specs/001-question-annotation-workbench/data-model.md`，`docs/specs/001-question-annotation-workbench/acceptance-checklist.md`
- Review goal / 本次目标：明确题干、问题、选项和解析支持 `content_blocks`，用于处理文字中夹杂公式图片、图形图片和区域截图的情况

**Validation boundary / 可验证性边界**

- 当前可以验证：规格和数据模型是否表达图文混排内容、图片资产引用、文本投影、内容块级来源追溯。
- 当前不能验证：实际富文本编辑器、图片上传接口、对象存储、后端数据库迁移、组卷导出版式。
- 本轮只更新文档，不进入 React/Vue 或后端实现。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | ---- | ----------------- | ---------------- | ------ |
| C-01 | 图文混排模型 | 在转向正式前后端前，先更新 spec / data-model，明确题干、选项、解析支持 `content_blocks`。 | P0 | `Proposed` |

**Analysis / 分析**

#### C-01：平台自有内容块，而不是整段截图或编辑器 HTML

- 实际问题：解析和选项中会出现公式图片、图形图片和文字混排，纯文本字段不足以表达。
- 不采用整段截图作为主路径：整段截图会牺牲文字搜索、编辑、审核和导出版式控制，只能作为无法安全拆分内容的兜底块。
- 不采用某个 RichText 插件格式作为数据库模型：富文本编辑器可以作为前端编辑/渲染工具，但持久化结构应由平台控制。
- 决策：增加 `DocumentAsset` 和 `ContentBlock`，题干、问题、选项和解析用有序内容块表达；纯文本字段保留为搜索和展示兜底投影。
- 来源追溯：`SourceSpan` 可以绑定到整个字段，也可以绑定到具体 `ContentBlock`。

**Decision / 决策**

| Feedback ID | Decision | Reason | Milestone | Owner |
| ----------- | -------- | ------ | --------- | ----- |
| C-01 | `Implemented` | 已在规格、数据模型和验收清单中明确 `content_blocks`、资产引用和来源追溯规则。 | Spec / Data model | Codex |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| ------ | --------------- | ----- | ------ | -------------- |
| `docs/specs/001-question-annotation-workbench/spec.md` | 增加题干、选项、解析图文内容块能力和富文本边界 | Codex | Done | 本地修改 |
| `docs/specs/001-question-annotation-workbench/data-model.md` | 增加 `DocumentAsset`、`ContentBlock`，调整 `QuestionVersion` / `QuestionOption` 字段说明和 `SourceSpan` 关系 | Codex | Done | 本地修改 |
| `docs/specs/001-question-annotation-workbench/acceptance-checklist.md` | 增加图文内容块、资产引用、文本投影和内容块来源追溯验收项 | Codex | Done | 本地修改 |
| GitHub issue #2 | 记录本轮开始和完成结论 | Codex | Done | https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/2#issuecomment-5150787131 / https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/2#issuecomment-5150800507 |

**Verification / 验证**

- Acceptance scenario / 验收场景：阅读规格和模型，确认题干、选项、解析可由有序内容块表达，图片通过资源引用，常规文字保留文本投影，来源可绑定到内容块。
- Reviewer / 验证人：Codex
- Verification result / 验证结果：文档关键项扫描确认 `ContentBlock`、`DocumentAsset`、`source_span_id`、`content_block_id`、文本投影和区域截图兜底规则均已出现；残留扫描确认旧的选项 `image_uri` 主路径和旧全文索引描述已从 `data-model.md` 移除。
- Remaining issues / 遗留问题：后续需要设计内容块编辑器 POC、图片上传/裁剪接口、对象存储策略、组卷导出渲染规则和公式 OCR/LaTeX 的后续扩展边界。

---

### REV-20260723-03: DOCX HTML preview replaces PDF positioning / DOCX HTML 预览替代 PDF 定位

**Meeting information / 会议信息**

- Date / 日期：2026-07-23
- Participants and roles / 参与人及角色：项目负责人、Codex
- Recorder / 记录人：Codex
- Material reviewed / 评审材料：`prototypes/question-bank-prototype/index.html`，`docs/libreoffice-poc.md`
- Review goal / 本次目标：将题本预览主路径从 PDF 预览改为 DOCX 衍生 HTML 预览，并为解析栏增加对应 DOCX 预览入口

**Validation boundary / 可验证性边界**

- 当前可以验证：静态原型中是否移除 PDF 页码/缩放定位、是否支持题本 DOCX + HTML 预览、解析 DOCX + HTML 预览、是否保留可复制文本块作为填入辅助。
- 当前不能验证：浏览器原生 DOCX 渲染、生产后端转换服务、真实 `DocumentBlock` / `SourceSpan` 字段级精确定位。
- 本轮仍不引入 FastAPI，不创建正式前端工程，不提交真实转换输出。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | ---- | ----------------- | ---------------- | ------ |
| H-01 | 题本预览 | 在 HTML 原型里把 PDF 预览改成 DOCX 预览。 | P0 | `Proposed` |
| H-02 | 解析预览 | 解析文件栏也需要添加 DOCX 预览相关按钮。 | P0 | `Proposed` |
| H-03 | PDF 定位 | 题本的原文块按钮没有实际用途；当前 PDF 预览定位功能不能准确定位。 | P0 | `Proposed` |

**Analysis / 分析**

#### H-01 / H-02 / H-03：DOCX 衍生预览与受控文本块分层

- 实际问题：PDF 可以视觉浏览，但页码/缩放定位无法承担字段级来源定位；“原文块 / PDF”模式切换也让原文块像一个无效按钮。
- 关键边界：浏览器中的静态 HTML 不能可靠直接渲染 `.docx` 原文件。原型中的“DOCX 预览”应表达为“原始 DOCX 文件 + LibreOffice 生成的 HTML 预览文件”。
- 交互决策：题本区移除 PDF 页码/缩放定位和“原文块”模式按钮，改为 DOCX 文件、HTML 预览、来源绑定、可复制文本块同屏展示。
- 交互决策：解析区新增解析 DOCX 和解析 HTML 预览按钮，并提供内嵌预览。
- 工程影响：正式系统中应由后端转换服务生成只读 HTML 预览地址；可复制文本块和字段来源仍应由 `DocumentBlock` / `SourceSpan` 支撑。

**Decision / 决策**

| Feedback ID | Decision | Reason | Milestone | Owner |
| ----------- | -------- | ------ | --------- | ----- |
| H-01 | `Implemented` | 已将题本 PDF 预览替换为 DOCX 衍生 HTML 预览候选。 | Prototype | Codex |
| H-02 | `Implemented` | 已为解析栏增加解析 DOCX 和解析 HTML 预览入口。 | Prototype | Codex |
| H-03 | `Implemented` | 已移除 PDF 页码/缩放定位和“原文块”模式按钮；原文块改为可复制文本块区域。 | Prototype | Codex |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| ------ | --------------- | ----- | ------ | -------------- |
| `prototypes/question-bank-prototype/index.html` | 替换 PDF 预览为 DOCX/HTML 预览，新增解析 DOCX/HTML 预览，移除 PDF 定位和原文块模式按钮 | Codex | Done | 本地修改 |
| `prototypes/question-bank-prototype/README.md` | 记录 DOCX 原文件和 HTML 预览文件分离、解析预览入口、可复制文本块定位 | Codex | Done | 本地修改 |
| `docs/libreoffice-poc.md` | 记录 DOCX HTML 预览集成和范围边界 | Codex | Done | 本地修改 |
| GitHub issue #1 | 记录本轮开始、反馈背景和完成结论 | Codex | Done | https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/1#issuecomment-5058613230 / https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/1#issuecomment-5058680030 |

**Verification / 验证**

- Acceptance scenario / 验收场景：打开静态原型，确认题本区显示 DOCX/HTML 预览控件和可复制文本块，解析区显示 DOCX/HTML 预览控件，页面中不再出现 PDF 页码/缩放定位路径。
- Reviewer / 验证人：Codex
- Verification result / 验证结果：静态 HTML 解析通过；原型 HTML 中旧 PDF 预览引用扫描通过；文档关键项检查通过；Chrome headless DOM 检查确认 DOCX/HTML 预览控件、解析预览控件和可复制文本块均能渲染；已在 1440 x 900 和 1280 x 720 下截图检查，并修复左侧题本内容增多后挤出解析面板的问题。
- Remaining issues / 遗留问题：后续需要验证 LibreOffice HTML 在浏览器内的字体、图片资源相对路径和复制行为；正式系统仍需服务端转换、来源块映射和权限隔离。

---

### REV-20260723-02: Question slot navigation logic / 题位导航逻辑

**Meeting information / 会议信息**

- Date / 日期：2026-07-23
- Participants and roles / 参与人及角色：项目负责人、Codex
- Recorder / 记录人：Codex
- Material reviewed / 评审材料：`prototypes/question-bank-prototype/index.html`，`docs/specs/001-question-annotation-workbench/spec.md`，`docs/specs/001-question-annotation-workbench/data-model.md`
- Review goal / 本次目标：将右侧题目切换从最近草稿快捷入口改为按试卷题位顺序导航，并支持任意题位跳转

**Validation boundary / 可验证性边界**

- 当前可以验证：静态原型中题位与草稿分离、上一题/下一题按题位顺序移动、完整题目列表支持搜索和任意跳转、未开始题位不自动生成草稿 ID。
- 当前不能验证：后端草稿持久化、多人并发锁定、正式审计日志、真实 `SourceSpan` 同步定位。
- 本轮仍不进入正式前端工程和数据库迁移。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | ---- | ----------------- | ---------------- | ------ |
| S-01 | 题目切换 | 当前题目切换似乎只能切换到最近录入的题目，不能自由切换任意题目；需要讨论并完成这部分业务逻辑。 | P0 | `Proposed` |

**Analysis / 分析**

#### S-01：题位导航与草稿历史分离

- 实际问题：上一版原型把可切换对象建模为草稿数组，容易退化成“最近录入题目快捷切换”，无法代表整份试卷的题号顺序。
- 期望结果：工作台应以 `QuestionSlot` 作为导航单位，以 `QuestionDraft` / `Question` 作为挂在题位上的编辑内容。未开始题位可以被查看，但不应因为查看而自动生成草稿 ID。
- 交互决策：右侧上下文条只显示当前题位和附近题位；完整跳转通过“题目列表”弹层完成，支持搜索题号、草稿 ID、来源页码和按状态筛选。
- 工程影响：正式实现需要后端持久化题位、草稿状态、自动保存、并发锁定和来源同步。本轮只在静态原型验证业务逻辑。

**Decision / 决策**

| Feedback ID | Decision | Reason | Milestone | Owner |
| ----------- | -------- | ------ | --------- | ----- |
| S-01 | `Implemented` | 已将原型切换逻辑改为顺序题位导航，并增加完整题目列表自由跳转。 | Prototype | Codex |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| ------ | --------------- | ----- | ------ | -------------- |
| `prototypes/question-bank-prototype/index.html` | 引入 `questionSlots` 原型模型、附近题位快捷入口、完整题目列表、搜索/筛选/任意跳转和追加题逻辑 | Codex | Done | 本地修改 |
| `prototypes/question-bank-prototype/README.md` | 记录题位导航、题目列表、追加题和保存并录下一题语义 | Codex | Done | 本地修改 |
| `docs/specs/001-question-annotation-workbench/spec.md` | 补充顺序题位导航、完整题目列表和切换前保留草稿 | Codex | Done | 本地修改 |
| `docs/specs/001-question-annotation-workbench/data-model.md` | 增加候选 `QuestionSlot` 实体说明 | Codex | Done | 本地修改 |
| `docs/specs/001-question-annotation-workbench/acceptance-checklist.md` | 增加题位顺序导航、任意跳转、未开始题位不自动生成草稿 ID 等验收项 | Codex | Done | 本地修改 |
| GitHub issue #3 | 创建并跟踪本轮题位导航 POC | Codex | Done | https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/3 / https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/3#issuecomment-5058467774 |

**Verification / 验证**

- Acceptance scenario / 验收场景：打开静态原型，查看附近题位快捷入口，打开题目列表，搜索/筛选题位，点击任意题位跳转，并确认未开始题位不会自动生成草稿 ID。
- Reviewer / 验证人：Codex
- Verification result / 验证结果：静态 HTML 解析通过；旧草稿导航引用清理通过；文档关键项检查通过；Chrome headless DOM 检查确认普通状态和题目列表状态均能渲染；已在 1440 x 900 和 1280 x 720 下截图检查普通题位导航与题目列表弹层，未见明显重叠或截断。
- Remaining issues / 遗留问题：后续正式应用需明确插入题位、跳过题位、题号重排、并发编辑锁定和左侧来源同步定位策略。

---

### REV-20260723-01: Preview copy strategy and question switching / 预览复制策略与题目切换

**Meeting information / 会议信息**

- Date / 日期：2026-07-23
- Participants and roles / 参与人及角色：项目负责人、Codex
- Recorder / 记录人：Codex
- Material reviewed / 评审材料：`prototypes/question-bank-prototype/index.html`，`docs/libreoffice-poc.md`
- Review goal / 本次目标：处理 PDF 复制换行成本，并补充右侧当前题号预览与题目切换能力

**Validation boundary / 可验证性边界**

- 当前可以验证：PDF 预览和可复制文本应分层；右侧录入区能否显示当前题、来源摘要、字段完整度，并在临时草稿之间切换。
- 当前不能验证：正式 DOCX 在线预览服务、生产级 `DocumentBlock` / `SourceSpan` 写库、跨文档题目状态持久化、多人协同锁定。
- 本轮仍只修改静态原型和 POC 文档，不进入正式前后端应用开发。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | ---- | ----------------- | ---------------- | ------ |
| Q-01 | 左侧预览 / 复制 | PDF 能正常浏览，但从 PDF 复制文字可能带入换行或分段，增加重新排版成本；考虑使用 DOCX 预览。 | P0 | `Proposed` |
| Q-02 | 右侧录入 | 右侧缺少题号预览，不知道当前插入的是哪一道题，也不能切换到之前插入的题。 | P0 | `Proposed` |

**Analysis / 分析**

#### Q-01：预览与复制分层

- 实际问题：PDF 的视觉保真与复制体验不是同一个问题；PDF 适合看版式，但浏览器 PDF 文本选择可能带来换行清理成本。
- 期望结果：操作员左侧能对照原貌，同时复制/填入文本来自更可控的来源文本层。
- 原建议是否为唯一方案：不是。浏览器不能直接稳定“原生预览 DOCX”；所谓 DOCX 预览仍需要 LibreOffice/Office/解析器渲染。更稳妥的方案是 PDF 或页面图做视觉参照，`DocumentBlock` 候选做可复制文本。
- 工程影响：后续应把 visual preview、source text blocks、field assignment 分层设计，不把 PDF copy/paste 当作生产录入主路径。

#### Q-02：题目切换位置

- 实际问题：录题员缺少当前题上下文和回看入口，容易把内容填到错误题目或无法回退检查。
- 期望结果：右侧录入界面始终显示当前题号、状态、来源摘要和字段完整度，并提供上一题、下一题、已录草稿列表和新建题入口。
- 原型影响：题目切换放在右侧表单标题下方、基础信息上方；这里属于编辑上下文，不适合放在顶部全局栏或最右侧流程条。
- 工程影响：正式应用中该能力需要后端草稿状态、来源绑定、并发锁定和审计日志；本轮只做静态原型 POC。

**Decision / 决策**

| Feedback ID | Decision | Reason | Milestone | Owner |
| ----------- | -------- | ------ | --------- | ----- |
| Q-01 | `Accepted with constraints` | 接受 PDF 不作为主要复制来源的结论；保留 PDF 视觉参照，复制/填入优先来自可控原文块。 | Infra POC | 项目负责人 |
| Q-02 | `Implemented` | 已在右侧表单标题下方加入当前题预览与临时草稿切换。 | Prototype | Codex |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| ------ | --------------- | ----- | ------ | -------------- |
| `prototypes/question-bank-prototype/index.html` | 增加当前题号条、已录草稿 tabs、上一题/下一题/新建题交互，并同步保存/提交/来源状态 | Codex | Done | 本地修改 |
| `prototypes/question-bank-prototype/README.md` | 记录题号切换和 PDF 只作视觉参照 | Codex | Done | 本地修改 |
| `docs/libreoffice-poc.md` | 记录 PDF 预览与复制文本分层结论 | Codex | Done | 本地修改 |
| GitHub issue #1 | 记录人工反馈、策略结论、原型改动方向和完成结果 | Codex | Done | https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/1#issuecomment-5058218438 / https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/1#issuecomment-5058291134 |

**Verification / 验证**

- Acceptance scenario / 验收场景：打开静态原型，查看右侧当前题号，切换已录草稿，新建下一题，并确认布局在常见桌面宽度下不重叠。
- Reviewer / 验证人：Codex
- Verification result / 验证结果：静态 HTML 解析通过；关键题号切换元素和函数存在；Chrome headless 执行后的 DOM 包含第 5/6/7 题 tabs 和当前题号；已在 1440 x 900、1280 x 720 下截图检查，未见明显重叠。
- Remaining issues / 遗留问题：需要真实录题员试用后确认题号条密度和切换位置；正式系统仍需设计草稿持久化、题目锁定、SourceSpan 绑定和审核追溯。

---

### REV-20260722-03: PDF left preview integration POC / PDF 左侧预览集成 POC

**Meeting information / 会议信息**

- Date / 日期：2026-07-22
- Participants and roles / 参与人及角色：项目负责人、Codex
- Recorder / 记录人：Codex
- Material reviewed / 评审材料：`prototypes/question-bank-prototype/index.html`，`docs/libreoffice-poc.md`
- Review goal / 本次目标：把 LibreOffice 生成的 PDF 作为拆题工作台左侧视觉预览候选接入静态原型

**Validation boundary / 可验证性边界**

- 当前可以验证：左侧题本区能否切换到 PDF 模式、能否加载本地 PDF、能否记录页码/字段/区域备注形式的来源绑定。
- 当前不能验证：生产级 PDF 服务、真实 `SourceSpan` 写库、PDF 文本精确选择、PDF 区域坐标和 Docling block 的自动映射。
- 本轮不引入 FastAPI，不引入正式前端工程，不提交生成的 PDF 文件。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | ---- | ----------------- | ---------------- | ------ |
| P-01 | PDF 左侧预览 | 实现把 PDF 作为左侧预览候选的集成 POC，并继续使用 GitHub CLI 管理进度。 | P0 | `Proposed` |

**Analysis / 分析**

#### P-01：PDF 作为左侧视觉预览候选

- 现有静态原型已有左侧题本、解析和右侧结构化录题表单，适合做最小集成 POC。
- 已在题本面板增加“原文块 / PDF”切换，保留原有模拟原文块能力。
- PDF 模式支持选择本地 LibreOffice 生成的 PDF，不把 PDF 文件写入仓库。
- PDF 模式支持页码、缩放、绑定字段、区域备注和来源确认状态，底部来源 chip 会同步显示 PDF 页码和字段。
- 初版采用浏览器原生 PDF iframe，人工测试发现部分本地浏览器环境中选择 PDF 后可能只更新文件名但预览区空白。
- 已改为 `object` / `embed` 加载纯 blob URL，并新增可见的“打开 PDF”兜底按钮；该方案适合验证视觉预览和人工来源绑定，但不适合承诺精确文本选择、区域坐标或跨浏览器一致行为。
- 自动拆题应作为单独 POC，不应混入本次 PDF 视觉预览 POC。

**Decision / 决策**

| Feedback ID | Decision | Reason | Milestone | Owner |
| ----------- | -------- | ------ | --------- | ----- |
| P-01 | `Accepted with constraints` | PDF 左侧预览已接入静态原型；该方案验证视觉预览和人工来源绑定，不代表生产 PDF 服务或自动拆题能力。 | Infra POC | 项目负责人 |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| ------ | --------------- | ----- | ------ | -------------- |
| `prototypes/question-bank-prototype/index.html` | 增加 PDF 预览模式、页码/缩放控制和来源绑定记录 | Codex | Done | 本地修改 |
| `prototypes/question-bank-prototype/README.md` | 记录 PDF 预览 POC 交互 | Codex | Done | 本地修改 |
| `docs/libreoffice-poc.md` | 记录 PDF 预览集成 POC、范围边界和下一步验证 | Codex | Done | 本地修改 |
| GitHub issue #1 | 记录 PDF 左侧预览 POC 开始与结果 | Codex | Done | https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/1#issuecomment-5045744761 |

**Verification / 验证**

- Acceptance scenario / 验收场景：打开静态原型，切换到 PDF 模式，选择本地 PDF，调整页码/缩放并记录一个来源绑定。
- Verification result / 验证结果：静态 HTML 解析通过；PDF 预览元素和函数存在；已用 Chrome headless 截取 1440 x 900 和 1280 x 720 的 PDF 模式截图；发现并修复 1280 宽度下控制栏截断问题；发现并修复选择 PDF 后内嵌预览可能空白的问题，增加 `object` / `embed` 和“打开 PDF”兜底；修正后未见明显控件重叠。
- Remaining issues / 遗留问题：需要由标注员实际选择本地 PDF 操作，确认浏览器原生 PDF 的页码、缩放和人工绑定流程是否顺手；若需要更强页码、坐标或文本选择控制，后续评估 PDF.js 或页面图片方案。

### REV-20260722-02: LibreOffice visual rendering POC / LibreOffice 可视化渲染 POC

**Meeting information / 会议信息**

- Date / 日期：2026-07-22
- Participants and roles / 参与人及角色：项目负责人、Codex
- Recorder / 记录人：Codex
- Material reviewed / 评审材料：`scripts/libreoffice_poc/convert_with_libreoffice.py`，`docs/libreoffice-poc.md`，`docs/raw_doc/` 本地样本
- Review goal / 本次目标：验证 LibreOffice headless 是否可作为 DOCX 左侧视觉预览渲染路径

**Validation boundary / 可验证性边界**

- 当前可以验证：POC 脚本是否可运行、是否能检测 LibreOffice 命令、是否能在没有 LibreOffice 时给出明确阻塞。
- 当前不能验证：PDF/HTML 是否接近 Word 原貌、图片是否显示、题号和 A-D 是否可读、输出是否适合左侧预览。
- 本轮不启动 FastAPI，不创建正式应用结构，不输出或提交真实题目正文。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | ---- | ----------------- | ---------------- | ------ |
| L-01 | DOCX 视觉预览 | 开始做 LibreOffice 视觉渲染路径，并用 GitHub CLI 管理每个开发步骤进度。 | P0 | `Proposed` |

**Analysis / 分析**

#### L-01：LibreOffice 作为视觉渲染路径

- LibreOffice 与 FastAPI 分工不同：LibreOffice 负责文档渲染，FastAPI 后续负责上传、任务、预览和标注 API。
- 当前阶段应先验证 LibreOffice headless 能否把真实 DOCX 样本渲染为可检查的 PDF/HTML，而不是进入正式后端开发。
- 已新增本地 POC 脚本，支持检测 `soffice`、按样本生成独立输出目录、使用独立 LibreOffice 用户配置目录、设置单文件超时，并写出本地 summary。
- 已新增 `docs/libreoffice-poc.md`，说明运行命令、检查清单、安全边界和当前阻塞。
- 初始检查时本机未找到 `soffice` / `libreoffice`，真实 PDF/HTML 转换曾被阻塞。
- 安装 LibreOffice 后，使用显式 `C:\Program Files\LibreOffice\program\soffice.exe` 路径完成转换，三份代表性 DOCX 样本均生成 PDF 和 HTML。
- PDF 已可进入人工视觉保真检查；HTML 虽生成了图片资源文件，但自动检查未发现直接 `<img>` 标签，需要浏览器人工确认实际展示效果。
- 人工检查后确认：当前代表性样本中，LibreOffice 生成的 PDF 和 HTML 能够与原 DOCX 版式对应。
- 该结论只支持“视觉预览路径可继续推进”，不代表可以自动拆题或绕过人工确认。

**Decision / 决策**

| Feedback ID | Decision | Reason | Milestone | Owner |
| ----------- | -------- | ------ | --------- | ----- |
| L-01 | `Accepted with constraints` | 当前样本的 PDF/HTML 视觉对应关系通过人工检查；下一步可验证 PDF 左侧预览集成，但自动拆题和字段归属仍需单独 POC 且必须人工确认。 | Infra POC | 项目负责人 |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| ------ | --------------- | ----- | ------ | -------------- |
| `AGENTS.md` | 增加 GitHub CLI 进度管理长期规则 | Codex | Done | 本地修改 |
| `docs/libreoffice-poc.md` | 记录脚本、运行命令、安全边界、初始阻塞和安装后的转换结果 | Codex | Done | 本地修改 |
| `.gitignore` | 忽略 `docs/libreoffice-poc-results/` | Codex | Done | 本地修改 |
| GitHub issue #1 | 记录 LibreOffice POC 开始、初始阻塞和安装后的转换结果 | Codex | Done | https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/1#issuecomment-5045096400 |

**Verification / 验证**

- Acceptance scenario / 验收场景：运行脚本语法检查、帮助输出和 PDF/HTML 转换命令。
- Verification result / 验证结果：`py_compile` 通过，`--help` 通过；安装 LibreOffice 后，3 个样本均成功生成 PDF 和 HTML；人工检查确认当前样本中 PDF/HTML 与原 DOCX 能够对应；输出目录为 git ignored。
- Remaining issues / 遗留问题：需要做 PDF 左侧预览集成 POC；若探索自动拆题，必须另起结构化拆题 POC，并保留人工确认和审核边界。

### REV-20260722-01: Docling DOCX preview POC / Docling DOCX 预览 POC

**Meeting information / 会议信息**

- Date / 日期：2026-07-22
- Participants and roles / 参与人及角色：项目负责人、Codex
- Recorder / 记录人：Codex
- Material reviewed / 评审材料：`scripts/docling_poc/convert_with_docling.py`，`docs/raw_doc/` 本地样本，`docs/docling-poc-results/` 本地生成结果
- Review goal / 本次目标：验证 Docling 是否适合作为 DOCX 左侧原文预览或结构化拆题辅助

**Validation boundary / 可验证性边界**

- 当前可以验证：Docling 是否能读取三份本地 DOCX、是否能生成 Markdown/HTML/JSON、本地 JSON 是否包含文本节点、图片节点和来源信息。
- 当前不能完全验证：Markdown/HTML 与 Word 原文的视觉一致性、图片真实位置是否足够还原、每张图片是否能自动归属到题干/选项/解析。
- 本轮不输出、提交或版本化真实题目正文；生成结果保存在已忽略的本地目录。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | ---- | ----------------- | ---------------- | ------ |
| D-01 | DOCX 预览 | 先用 Docling 做第二阶段 POC，验证 Markdown/HTML 可读性、阅读顺序、题号和 A-D、图片节点与图片归属。 | P0 | `Proposed` |

**Analysis / 分析**

#### D-01：Docling 作为 DOCX 预览与结构化辅助

- 三份本地 DOCX 样本均转换成功，说明 Docling 可以作为后续解析 POC 的候选工具继续评估。
- JSON 中存在 `picture` 节点，并且图片节点带 `prov` 来源信息，可作为后续 `DocumentBlock` 与 `SourceSpan` 设计的参考输入。
- Docling 默认 Markdown/HTML 导出没有直接图片链接或 `<img>` 标签，因此不能单独承担含图 DOCX 的左侧视觉预览。
- 自动结构检查能在文本中找到 A-D 字符，但不能稳定识别为行首选项节点；题号也没有稳定暴露为行首题号节点。
- 其中一个样本出现图片相关警告：未配置 LibreOffice 时部分 DrawingML 内容无法导出，并有 VML 图片找不到。这会影响图片保真和图片归属判断。
- 因此，Docling 更适合作为结构化辅助拆题与来源节点候选，而不是当前阶段的唯一可视化预览方案。

**Decision / 决策**

| Feedback ID | Decision | Reason | Milestone | Owner |
| ----------- | -------- | ------ | --------- | ----- |
| D-01 | `Accepted with constraints` | 继续使用 Docling 做结构化 POC；左侧视觉预览需另行验证 LibreOffice/PDF/HTML 渲染路径；图片归属必须人工确认。 | Infra POC | 项目负责人 |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| ------ | --------------- | ----- | ------ | -------------- |
| `docs/docling-poc.md` | 记录运行命令、结构计数、图片导出限制和阶段性判断 | Codex | Done | 本地修改 |
| `docs/specs/001-question-annotation-workbench/plan.md` | 若后续确认混合预览方案，再更新解析器策略 | 项目负责人 | Deferred |  |
| `docs/specs/001-question-annotation-workbench/data-model.md` | 若采用 Docling 节点作为来源块输入，再补充图片资源与内容块细节 | 项目负责人 | Deferred |  |
| GitHub issue #1 | 补充 Docling 预览 POC 结果 | Codex | Done | https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/1#issuecomment-5043141137 |
| GitHub issue #2 | 补充图片归属仍需人工确认的依据 | Codex | Done | https://github.com/Judecoodingspace/gongkao-platform-prototype/issues/2#issuecomment-5043143295 |

**Verification / 验证**

- Acceptance scenario / 验收场景：运行 `python .\scripts\docling_poc\convert_with_docling.py .\docs\raw_doc --out-dir .\docs\docling-poc-results --write-markdown --write-json`
- Verification result / 验证结果：3 个样本转换成功；生成 Markdown、HTML、JSON 和 summary JSON；输出目录为 git ignored。
- Remaining issues / 遗留问题：需要人工打开 Word 与导出结果对照阅读顺序；需要安装或配置 LibreOffice 后验证图片导出；不能把 Docling 输出直接写入题库。

### REV-20260704-01: First prototype and workflow review / 第一次原型与业务流程评审

**Meeting information / 会议信息**

- Date / 日期：2026-07-04（根据文档名称推定，待确认）
- Participants and roles / 参与人及角色：项目组师兄等，具体名单与角色待补充
- Recorder / 记录人：杨祖敏
- Material reviewed / 评审材料：静态录题工作台原型，以及判断推理、资料分析题目图片样例
- Source note / 原始记录：`关键问题确认0704.docx`
- Review goal / 本次目标：确认录题界面调整方向，并提前识别尚未实现的录题业务规则

**Validation boundary / 可验证性边界**

- 当前可以验证：页面区域、字段、控件类型、预览滚动与复制、图片插入入口、图片排版模式和真题/模拟题入口表达。
- 当前无法完成端到端验证：知识点后台校验、上一题默认值持久化、图片上传与存储、查重算法、题库权限隔离和富文本公式保存。
- 因此，本轮对前一类意见进行原型评审；后一类只形成需求假设与工程建议，待功能实现后再做验收。

**Original feedback / 原始意见**

| ID   | Area            | Original feedback                                                                                                                                                   | Initial priority | Status                  |
| ---- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------------------- |
| F-01 | 原文预览        | 题本和解析均需支持预览、复制和滚动。                                                                                                                                | P1               | `Proposed`            |
| F-02 | 知识点          | 知识点改为输入；提交时与后台配置校验，不相符则不通过并提示（这需要在后端开发过程中确认）。                                                                          | P1               | `Needs Clarification` |
| F-03 | 连续录题效率    | 科目、类型、知识点、年份、省份和难度默认沿用上一题的输入**（可以在原型阶段中确认）**。                                                                             | P1               | `Proposed`            |
| F-04 | 选项与评分      | 删除分值/评分项；选项均为单选（可以在原型中确认，但是要明确是否影响后续的可扩展性）。                                                                               | P1               | `Needs Clarification` |
| F-05 | 题干图片        | 题干编辑区域新增插图功能（**这个插图功能在原型验证阶段应该怎么处理，在后续操作员操作中应用以什么样的方式插入，截图吗？如果是截图的话如何保证按这样的格式处理）**。 | P0               | `Proposed`            |
| F-06 | 图片排版        | 题干与选项图片分开处理；支持单图一行、双图并列、四图两行两列等分类排版（**还是回到刚才的问题如果是截图的话这如何实现）**。                                         | P0               | `Needs Clarification` |
| F-07 | 查重            | 在同一知识点范围内查重；部分含图题仅看题干难以判断，可参考解析。                                                                                                    | P1               | `Needs Clarification` |
| F-08 | 题库与权限      | 谁上传的题归谁的题库；合作老师有独立上传权限和独立组卷范围，避免与其他老师题目混用。                                                                                | P0               | `Needs Clarification` |
| F-09 | 真题/模拟题入口 | 上传前先确认是真题还是模拟题，再进入传题界面。                                                                                                                      | P1               | `Proposed`            |
| F-10 | 图片公式        | 解析中不可编辑的公式图片需要与文字共同录入；需确认行内图片、整段截图或富文本方案。                                                                                  | P0               | `Needs Clarification` |

**Analysis / 分析**

#### F-01：题本与解析预览

- 当前原型已有独立题本、解析区域和滚动容器，但复制能力没有明确操作反馈。
- 下一版原型应允许正常文本选择，并在题本块、解析块提供复制图标按钮；复制操作需要有成功提示。
- 长文档应保持题本区和解析区各自独立滚动，不让右侧表单位置随左侧滚动丢失。
- 功能实现后需验证复制结果保留文本顺序，并且不执行源 DOCX 中的宏或活动内容。

#### F-02：知识点输入与校验

- 不建议使用完全自由输入并等到提交时才报错，这会增加返工，也容易产生同义词、错别字和重复分类。
- **建议改成“可搜索的组合框”：允许键入关键词，但只能从当前科目和题型对应的后台知识点中确认一个有效值。**
- 在失焦或选择时即时校验，提交时再做后端权威校验；前端校验不能替代后端校验。
- 待确认：是否允许标注员提交“新增知识点申请”，以及由谁审核和维护知识点体系。

#### F-03：沿用上一题元数据

- 该建议能显著减少同一套试卷连续录题的重复操作，应进入下一版交互原型。
- 默认值应限定在当前录题任务或当前试卷会话中，不能跨用户、跨试卷静默继承。
- 年份、省份和科目优先从当前试卷元数据带入；类型、知识点和难度可沿用上一题。
- 页面应提供清除或恢复任务默认值的能力，避免错误值连续污染多道题。
- 功能验收需检查刷新、切换试卷、切换用户和新建任务时的边界行为。

#### F-04：删除分值并限定单选

- 下一版原型可以先移除“分值/评分备注”，正确答案控件改为单选。
- 不建议此时从数据模型永久删除 `score` 或多选能力。PRD 当前把分值、多选列为可扩展字段，申论或未来其他题库可能仍会使用。
- 建议把“本项目当前行测客观题只录单选”定义为业务规则，而不是数据库不可逆约束。
- **待确认：申论、面试题和未来扩展题型是否复用同一题目模型**。

#### F-05 与 F-06：图片内容和排版

- 这不是只在题干输入框旁增加一个上传按钮的问题。当前数据模型仅有题目级 `has_image` 和选项级 `image_uri`，无法表达题干、问题、选项、解析中多张图片的顺序与布局。
- 建议把题干、问题、选项和解析表示为有序内容块，最小支持 `text`、`image` 和后续可选的 `formula` 类型。
- 每个图片块至少记录资源 ID、顺序、所属字段、布局组、布局方式、宽高、文件哈希和来源片段。
-
- 判断推理中“题干文字 + 一张包含 A-D 的选项总图”应允许把该图标记为“选项图组”，而不是错误归到题干图片。
- 资料分析多图按来源顺序逐行排列；不自动并列。
- 待确认：图片是否需要裁剪、旋转、压缩、替换和图片说明，以及双图的先后阅读顺序。

#### F-07：查重

- 查重应产生“疑似重复候选”，不应自动阻止入库；最终由人工确认，且决定需要记录。
- 不建议仅用知识点限制范围并只比较解析。相同题目可能有不同解析，不同题目也可能使用模板化解析。
- 建议先按题库/工作空间、科目、题型、知识点缩小候选范围，再综合标准化题干、问题、选项、解析和图片感知哈希计算相似度。
- 对含图判断推理题，应把图片相似度纳入信号；OCR 文本只能作为辅助。
- 待确认：查重范围是老师私有题库、机构共享题库，还是全平台；跨题库是否允许提示但禁止展示正文。

#### F-08：题库所有权与权限隔离

- “谁上传谁拥有”不能只依赖 `created_by` 字段实现。它实际引入了工作空间/机构、题库、成员关系、角色和数据可见范围。
- 建议增加 `Workspace` 或 `Organization`、`QuestionBank`、`Membership`，并让试卷、任务和题目明确归属 `question_bank_id`。
- 需要区分至少两类题库：机构共享的正式真题库，以及合作老师私有或受限共享的模拟题库。
- 管理员是否能查看所有私有题库、老师之间能否共享、人员退出后的题目归属、跨题库组卷和查重均需形成权限矩阵。
- 这是正式开发前必须确认的架构边界，优先级高于页面微调。

#### F-09：真题与模拟题入口

- 建议在创建上传任务时增加 `paper_kind` 或 `source_kind`，首版至少包含 `official_exam` 和 `mock_exam`。
- 用户可先选择类型再进入同一个录题工作台；不建议复制两套工作台代码。
- 工作台标题区应持续显示醒目的类型标识，避免录题过程中混淆。
- 待确认：面试热点预测题属于模拟题的子类，还是需要独立类别。

#### F-10：图片公式与富文本

- 对现有不可编辑公式图片，MVP 应支持“文字中插入行内图片”，并保留图片原件；整段截图只作为复杂版式的兜底方案。
- 不建议直接存储任意 HTML。建议存受控的富文本 JSON 或有序内容块，并对允许的节点和属性做白名单校验。
- 图片文件存对象存储，数据库保存资源元数据、顺序、尺寸、哈希、来源和版本关系。
- LaTeX/MathML 识别与可编辑公式可作为后续能力，AI/OCR 转换结果仍需人工核对。
- 待确认：MVP 是否要求公式与正文同行显示，以及导出组卷时必须支持哪些格式。

**Recommended change groups / 建议修改分组**

| Group | Scope              | Suggested contents                                                                                                 | Verification timing |
| ----- | ------------------ | ------------------------------------------------------------------------------------------------------------------ | ------------------- |
| A     | 下一版静态原型     | 预览复制、知识点可搜索输入、上一题默认值提示、移除分值、答案单选、题干/选项插图入口、有限图片布局、真题/模拟题标识 | 现在可评审          |
| B     | 正式规格与数据模型 | 有序内容块、媒体资源、图片布局、题库/工作空间归属、来源类型、查重候选记录                                          | 原型方向确认后更新  |
| C     | 后端业务功能       | 后台知识点校验、默认值作用域、对象存储、查重计算、权限控制、审计日志                                               | 实现后验收          |
| D     | 后续增强           | 公式 OCR/LaTeX、自动裁图、图片感知查重、跨题库受控共享                                                             | MVP 后评估          |

**Preliminary decision / 初步决策**

| Feedback ID | Preliminary decision  | Reason                                     | Next step                  |
| ----------- | --------------------- | ------------------------------------------ | -------------------------- |
| F-01, F-03  | 建议接受              | 明确改善连续录题效率，风险较低             | 纳入下一版原型             |
| F-02        | 调整方案后接受        | 使用可搜索组合框和即时校验优于提交时才校验 | 确认新增知识点流程         |
| F-04        | 仅接受 MVP 界面调整   | 避免过早删除未来扩展能力                   | 确认题库长期题型范围       |
| F-05, F-06  | 原则接受              | 需要先补内容块和图片布局模型               | 先画图片编辑交互原型       |
| F-07        | 暂不按原方案实现      | 仅看解析或硬拦截会产生误判                 | 定义候选信号和人工确认流程 |
| F-08        | 暂缓到权限专题确认    | 属于系统级数据边界                         | 单独召开权限/题库归属评审  |
| F-09        | 建议接受              | 单一工作台加来源类型即可实现               | 确认类别枚举               |
| F-10        | 原则接受 MVP 行内图片 | 受控内容块比任意 HTML 更可维护             | 确认导出展示要求           |

**Documents to synchronize after decisions / 决策确认后需同步的文档**

| Target                      | Required change                                         | Status               |
| --------------------------- | ------------------------------------------------------- | -------------------- |
| `docs/PRD.md`             | 增加连续录题效率、来源类型、私有/共享题库边界和查重流程 | Waiting for decision |
| `spec.md`                 | 补充图片内容块、预览复制、默认值继承和知识点校验场景    | Waiting for decision |
| `data-model.md`           | 评估内容块、媒体资源、题库归属、成员关系和查重候选实体  | Waiting for decision |
| `tasks.md`                | 增加权限专题、图片编辑器和查重 POC 任务                 | Waiting for decision |
| `acceptance-checklist.md` | 增加复制、默认值边界、图片布局、单选和权限隔离验收项    | Waiting for decision |
| HTML/Figma prototype        | 实现 Group A 的可点击交互                               | Todo                 |

**Verification / 验证**

- 当前结果：已提取 DOCX 正文和 4 张嵌入截图，并完成截图与文字的对应核对。
- 尚未验证：所有依赖真实后端、数据库、对象存储和用户权限的功能。
- 下一次评审建议：先确认 F-04、F-06、F-08、F-09 和 F-10 的待确认问题，再修改静态原型。
### REV-20260811-01: Continuous source preview and region-fill POC / 连续来源预览与区域填入 POC

**Review goal / 本次目标**

解决公式图片只能在单独图片块筛选中查看、操作员需要在文本块和图片块之间往返切换，以及右侧普通输入框和 `content_blocks` 编辑区重复的问题。

**Decision / 决策**

- 接受“连续页面预览 + 区域选择 + 混合内容一次性填入”作为下一版静态原型 POC 交互。
- `DocumentBlock` 保留为原子来源与解析输出单位；界面不再把逐块列表作为主要阅读和录题方式。
- 页面预览根据 `page_no` 和来源 `bbox` 将文本、图片和公式图片共同呈现。操作员可点击、Shift 多选或拖动框选来源区域。
- 选中区域按页面阅读顺序填入题干、问题、选项或解析；每个生成的 `ContentBlock` 保留自己的 `source_span_id`。
- 右侧 `content_blocks` 编辑区是人工修正的权威入口；题干、选项和解析的普通输入框仅保留为纯文本投影，不作为第二套独立内容存储。

**Scope boundary / 范围边界**

- 本轮只修改静态 HTML 原型及规格、数据模型、验收文档和本评审记录。
- 本轮不实现自动题目边界识别、不实现后端 DocumentParser、不改变正式数据库 schema。
- 区域选择是操作员确认后的来源绑定，不代表系统自动完成拆题。

**Verification / 验证**

- 静态检查应确认原型不再依赖来源块筛选器和逐块“从当前原文块填入”按钮。
- 浏览器人工验收待完成：加载 PDF 路线生成的 `document-blocks.json`，确认第 18 页公式图片可与相邻文本同时显示，并能框选混合区域填入右侧。

---
### REV-20260811-02: Natural-flow rendering correction / 自然流渲染修复

**Operator feedback / 操作员反馈**

- PDF DocumentBlock 页面预览出现明显截断，长文本只显示部分内容。
- 选中一题解析后，右侧每个来源块以独立纵向卡片显示，阅读成本高。
- 含公式图片的解析与 DOCX 中的文字、图片相对布局差距明显。

**Decision / 决策**

- 来源页面改为按页、按 `page_no`/`bbox` 阅读顺序的自然流渲染，不再把每个文本块限制在 PDF 单行 bbox 高度内。
- 图片和公式图片作为来源阅读流中的内嵌元素显示；`DocumentBlock` 仍保留原子来源 ID 和坐标。
- 右侧填入结果改为紧凑混合内容流，文本块和图片块不再默认纵向堆叠为大卡片；仍保留逐块编辑、排序、删除和来源操作。

**Scope boundary / 范围边界**

- 本轮只修复静态 POC 的显示与编辑交互，不声称已经实现 DOCX 像素级还原。
- PDF 文本块与图片块仍来自解析器的独立输出；行内公式的精确基线、字号和换行仍需后续用真实样本人工验收。

**Verification / 验证**

- 本地 JSON 结构统计：1274 个块、43 页、50 个图片块；未修改真实解析产物。
- HTML 结构解析通过。
- 浏览器实际截图和拖拽验收仍待有可用浏览器实例时完成。

---

### REV-20260823-01: V1 pure-text annotation workbench pilot / V1 纯文本题录题工作台试行

**Decision / 决策**

- 第一版可运行工作台只处理题干、问题、A-D 选项和解析均为文字的题目。
- 左侧主路径改为 LibreOffice 衍生 HTML 原文预览，操作员从预览中选中、复制，再在右侧录入。
- 右侧接入受限 wangEditor，用于基础文字和段落格式；关闭图片、视频、表格、附件、外链和任意 HTML 插入。
- 图文题、公式图、统计图、截图和图片选项明确后置；`DocumentBlock`、`SourceSpan`、`DocumentAsset` 和 `ContentBlock` 仅保留为 V2 能力基础，不作为 V1 强制操作。
- wangEditor HTML 仅作为原型草稿表示；后端权威数据模型不得绑定编辑器 HTML。

**Reason / 原因**

- 当前优先验证人工录题、题位切换、草稿、审核状态和后续检索字段的完整闭环，避免图文解析与资产管理阻塞第一版。
- 直接把左侧 DOCX 转成不可复制的图片会增加重新录入成本，因此采用可复制 HTML 预览，而不是静态截图预览。

**Verification / 验证**

- 原型静态检查确认 V1 范围提示、LibreOffice HTML 预览入口、wangEditor CDN 引用和纯文本回退控件存在。
- 当前会话未获得可用浏览器实例，未完成截图和实际点击验收；需要由操作员按原型 README 的 V1 验收流程复核。

---

### REV-20260823-02: Shenlun V1 subjective-mode navigation / 申论 V1 主观题模式与专项导航

**Decision / 决策**

- 经确认，教师版 DOC 中的归纳概括、提出对策、综合分析、应用文写作和大作文属于可用的知识点分类；原文按这些知识点展开题目。
- 科目切换为申论后，隐藏行测类型、A-D 选项和正确答案单选；字段改为题干正文、作答要求和参考答案。
- 五个专项以受控按钮展示，专项顺序和专项内题序用于录题导航；题目仍保留全局稳定题位与 ID。
- 题干正文在当前样本文档中每题独有，不把共享材料关系作为 V1 默认模型。

**Verification / 验证**

- 静态原型已增加申论字段显隐、专项按钮、专项内题位标签和跨专项导航逻辑。
- 需要在可用浏览器中完成申论切换、专项跳转、保存草稿后回切的人工验收。

---

### REV-20260823-03: Shenlun four-field content model / 申论四字段内容模型

**Decision / 决策**

- 根据教师版 DOC 的实际结构，申论题必须区分题干、要求、问题、参考答案四段内容；不得将要求与问题合并为一个字段。
- 申论模式为四段内容分别提供独立受限 wangEditor，并将字段纳入草稿保存、题位切换和完整度计算。
- 数据模型使用 `stem_text`、`requirement_text`、`question_text`、`reference_answer_text`；`explanation_text` 留给后续可选教师解析或批注，不混作参考答案。

**Verification / 验证**

- 静态原型已增加 `requirement` 编辑器及对应草稿字段。
- 浏览器切换与回填验收仍待可用浏览器实例完成。

---

### REV-20260823-04: Shenlun V1 persistence contract / 申论 V1 持久化契约

**Decision / 决策**

- 将 `requirement_text`、`reference_answer_text`、`paper_version_id`、专项来源顺序和 `row_version` 纳入正式 `QuestionVersion` 实体定义，不再只放在文末补充说明。
- 专项来源顺序属于题目版本的来源追溯快照；稳定导航身份仍由 `QuestionSlot` 管理，专项内题序不能作为题库主键。
- 新增框架无关的申论 V1 API 契约，明确四字段、幂等、乐观锁、提交后不可变和新建修订版本规则。
- 新增 PostgreSQL 迁移计划；FastAPI、SQLAlchemy 和 Alembic 只是待 `G-01` 明确批准的候选实现基线，不因静态 HTML 原型自动生效。
- 后续 Terra 按 `SHV1-001` 至 `SHV1-012` 执行，并受 `G-01` 至 `G-05` 门禁约束；未批准门禁时必须停止而不是自行猜测。

**Scope boundary / 范围边界**

- 本轮只更新数据模型、API 契约、迁移计划、任务和验收基线。
- 本轮不创建正式前后端、不运行数据库迁移、不导入原型草稿或私有试卷内容。

**Verification / 验证**

- 需要检查正式实体字段、API payload、SQL 列映射和任务字段名完全一致。
- 实际迁移和 API 测试必须在技术栈与三个实施前置门禁批准后执行。

---

### REV-20260823-05: G-01 approved technology baseline / G-01 已批准技术基线

**Decision / 决策**

- 正式前端采用 React 19、TypeScript 5.7、Ant Design 5，运行于 Node.js 22 LTS 和 npm 10。
- 正式 API 采用 CPython 3.12、FastAPI、Pydantic、SQLAlchemy 2.x 和 Alembic 1.x。
- 正式数据库采用 PostgreSQL 16；后端契约与迁移使用 Pytest，正式 Web 交互与截图使用 Playwright。
- DOCX POC 的 Python 3.13 环境与生产 API 隔离，不能因为本机已安装 Docling 就成为正式运行时。

**Consequence / 后续影响**

- `SHV1-001` 已完成；下一步进入 `G-02` 契约评审，再进入 `G-03` 迁移评审。
- 在 `G-02` 与 `G-03` 未通过前，不创建后端工程、不安装生产依赖、不执行数据库迁移。

---

### REV-20260828-01: G-02 and G-03 persistence review / G-02 契约与 G-03 迁移评审

**Decision / 决策**

- `G-02` 已批准：申论四字段保持独立；共享长材料通过 `SourceMaterial`、`SourceMaterialVersion` 和 `QuestionVersionMaterial` 只保存一次并按准确版本复用。
- 提交要求为“要求、问题、参考答案非空”，并要求“题目独有题干非空”或“至少关联一个有效共享材料版本”；草稿阶段允许正文不完整。
- `QuestionVersion.status` 保存历史状态；只有当前草稿可修改。已提交、已通过、已驳回版本均不可原地修改，修订必须新建版本。
- `G-03` 已批准：PostgreSQL 使用复数 `snake_case`、应用生成 UUIDv4、`varchar + CHECK` 状态、非级联外键、复合延迟当前版本归属外键和确定性知识点种子。
- 测试数据库固定为一次性 PostgreSQL 16，要求 `APP_ENV=test` 且数据库名以 `_test` 结尾；SQLite 不作为迁移或契约测试替代。
- 已创建 GitHub issue #4 独立管理本阶段，不再混入图片归属 issue #2。

**Resolved risks / 已解决风险**

- 修正 API 有版本状态而 schema 无状态字段的问题。
- 修正共享材料重复复制进每道题导致的冗余和修订不一致问题。
- 明确题目来源顺序变更与 `QuestionSlot` 必须同事务更新。
- 明确循环外键、删除策略、操作者身份边界、幂等键范围、备份和回滚策略。
- 修正 V1 无稳定坐标时强制伪造 `SourceSpan` 的冲突；有坐标时必须保存，无坐标时不得伪造。

**Scope boundary / 范围边界**

- 本轮只完成契约与迁移评审和文档同步，没有创建 React/FastAPI 工程、安装依赖或运行数据库迁移。
- 难度字段责任、文件对象存储、身份提供方、审核 API 和图文 V2 仍为独立后续决策。

**Next step / 下一步**

- `SHV1-002`、`SHV1-003` 完成；Terra 可以从 `SHV1-004` 开始搭建已批准的后端、迁移和测试结构。

---

### REV-20260828-02: Frozen baseline and three-repository split / 冻结基线与三仓库拆分

**Decision / 决策**

- 当前 `gongkao-question-bank-platform` 仓库保留为规格、评审、文档解析 POC 和高保真参考仓库，不再承载生产前后端代码。
- 冻结提交为 `533e172`，注释标签为 `shenlun-v1-hifi-spec-baseline-2026-08-28`；标签与提交均已推送。
- 正式 API 独立为私有仓库 `Judecoodingspace/gongkao-question-bank-api`；正式 Web 独立为私有仓库 `Judecoodingspace/gongkao-question-bank-web`。
- API 使用 uv 管理 CPython 3.12、`pyproject.toml` 和 `uv.lock`。Web 在 `G-04` 前保持仅文档状态，不创建 React 工程。
- 本地高保真 PDF 未经隐私审查，不进入冻结提交；HTML 原型是可审计的冻结交互参考。

**Implementation / 实现**

- `SHV1-004` 已在 API 仓库提交 `a73f24a` 完成：FastAPI 应用、健康端点、配置与数据库边界、空 Alembic 框架、PostgreSQL 16 Compose、OpenAPI 导出和测试骨架。
- Web 仓库提交 `f5a172c` 只包含 README、架构边界、AGENTS 和忽略规则；不存在 `package.json` 或 `src/`。

**Verification / 验证**

- API：Ruff 通过；MyPy 严格模式检查 22 个源文件通过；Pytest 4 项通过且无警告；OpenAPI、Alembic heads 和 Compose 配置检查通过。
- API 临时启动成功，`GET /api/v1/health` 返回 HTTP 200 和 `{ "status": "ok" }`，验证后已停止服务。
- 参考仓库原始试卷、评审 DOCX、所有 POC 结果目录和本地 PDF 保持 Git 忽略。

**Next step / 下一步**

- 在 API 仓库开始 `SHV1-005`，实现 `M-001` 至 `M-005`；在 `G-04` 前不开始 React 持久化。

---

### REV-20260830-01: SHV1-005 and SHV1-006 migration completion / SHV1-005 与 SHV1-006 迁移完成

**Implementation / 实现**

- API 仓库 `SHV1-005` 已以独立提交 `dcbc2df` 完成并推送；对应 GitHub issue #2 已关闭。
- 五个批准的 Alembic revision 保持独立且按依赖排序：`0001_m001`、`0002_m002`、`0003_m003`、`0004_m004`、`0005_m005`。
- API 仓库 `SHV1-006` 已以独立提交 `f2e2f55` 完成并推送；对应 GitHub issue #3 已关闭。
- 未实现 `SHV1-007` 的 Repository、Service、业务 API，也未创建 React、审核、发布、DocumentBlock、ContentBlock 或 DocumentAsset 生产代码。

**Verification / 验证**

- 使用 `compose.yaml` 的 PostgreSQL 16 `postgres-test`，并要求 `GONGKAO_APP_ENV=test` 与数据库名以 `_test` 结尾；SQLite 目标会被拒绝。
- 空数据库按五个 revision 升级到 `0005_m005 (head)` 通过；重复 upgrade 不重复插入五个固定 UUID/code 的申论知识点种子。
- schema 检查覆盖所有业务表、字段、主键、具名 CHECK、UNIQUE、索引和 18 个外键；所有外键均无级联删除，两个复合 current-version 外键为 `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`。
- 约束实验确认：同一题目的两个版本可保留相同来源顺序；同一 `paper_version` 重复题位被拒绝；一个材料版本可关联两个题目版本；重复材料关联和同题重复关联顺序被拒绝。
- downgrade 只在双重保护的一次性测试数据库执行，随后重新 upgrade 到 head 并再次核对 schema 与种子。
- 最终检查：Ruff 通过；MyPy 严格模式检查 22 个源文件通过；Pytest 10 项通过；Alembic current 与 heads 均为 `0005_m005 (head)`。

**Known limitations and next step / 已知限制与下一步**

- 迁移测试要求本地或 CI 可连接 PostgreSQL 16；服务级跨表事务规则尚未实现或验证。
- 下一项依赖任务为 `SHV1-007`：实现材料/题目草稿创建、乐观锁更新、提交和修订版本创建的领域服务事务；不得在该任务开始前扩展业务 API。

---

### REV-20260830-02: SHV1-007 domain-service completion / SHV1-007 领域服务完成

**Implementation / 实现**

- API 仓库以独立提交 `91fd09f` 完成并推送 `SHV1-007`；GitHub issue #4 已关闭。
- 已实现可复用来源材料的草稿创建、乐观锁更新和从当前已通过/已驳回版本创建修订草稿；历史版本不原地覆盖。
- 已实现申论题目的草稿创建、乐观锁更新、提交和修订版本创建事务；题位移动与题目版本来源顺序在同一事务中处理。
- 服务在事务中校验 finalized `paper_version`、有效申论知识点、同试卷当前材料版本、草稿可变性、提交完整度和来源顺序冲突；提交时把关联的当前 draft 材料版本同步转为 submitted。
- 审计只保存动作、实体 ID、字段名、状态转换及其他安全元数据；幂等只保存 SHA-256 请求摘要和结果资源元数据，不保存题目或材料正文。

**Verification / 验证**

- 使用一次性 PostgreSQL 16 `postgres-test` 执行服务事务测试，输入仅包含合成标签、UUID 和脱敏文本。
- 覆盖材料幂等重放、不同载荷复用请求 ID、过期草稿写入、修订版本；题目草稿创建、原子题位移动与冲突回滚、提交后的材料状态转换、已提交版本不可 PATCH 和保留历史内容的修订版本。
- 最终检查：Ruff 通过；MyPy 严格模式检查 36 个源文件通过；Pytest 13 项通过；Alembic current 与 heads 均为 `0005_m005 (head)`。

**Scope boundary and next step / 范围边界与下一步**

- 本轮没有增加业务 HTTP 路由、FastAPI 请求/响应模型、审核/驳回端点、React、图文内容、解析器入口或物理删除接口。
- 下一任务为 `SHV1-008`：在不改变已批准服务语义的前提下，实现 `api-contract.md` 定义的 HTTP 路由和错误翻译；其后才是 `SHV1-009` 的完整契约测试。

---

### REV-20260831-01: SHV1-008 API contract endpoint completion / SHV1-008 API 契约端点完成

**Implementation / 实现**

- API 仓库以独立提交 `66d94cb` 完成 `SHV1-008`；GitHub issue #5 记录了开始、设计检查、明确决策和验证结论。
- 已实现申论 V1 的知识点读取、来源材料创建/草稿更新/修订版本、题目草稿创建/列表/当前版本读取/草稿更新/提交/修订版本端点，以及请求/响应模型、LF 行尾规范化、游标分页和 OpenAPI 输出。
- 已实现统一 JSON 错误响应、4 MiB 请求体限制、字段级长度限制，以及临时必需的 `X-Actor-Id` UUID 开发/测试身份上下文；缺失或非法身份返回 `401 UNAUTHENTICATED`。
- 已确保草稿修改/提交/修订只允许创建者操作；没有实现审核、驳回、发布、图文内容、解析器入口或物理删除接口。

**Verification / 验证**

- 在一次性 Compose PostgreSQL 16 `postgres-test` 数据库中执行最终检查：Ruff 通过；MyPy 严格模式检查 43 个源文件通过；Pytest 17 项通过；Alembic current 与 heads 均为 `0005_m005 (head)`。
- 新增 API 边界测试覆盖临时身份缺失、非法 JSON、4 MiB 请求体拒绝，以及已批准的字段长度和 LF 规范化；OpenAPI 已重新生成。

**Known limitations and next step / 已知限制与下一步**

- `X-Actor-Id` 仅是本切片经确认的开发/测试身份适配器，正式认证、角色映射和审核权限仍待后续设计替换。
- 下一项为 `SHV1-009`：补全契约级 PostgreSQL 端到端测试；不得在该任务前增加审核或混合内容能力。

---

### REV-20260831-02: SHV1-009 API contract-test completion / SHV1-009 API 契约测试完成

**Implementation / 实现**

- API 仓库以独立提交 `371316e` 完成 `SHV1-009`；GitHub issue #6 记录本轮开始、验证与完成结论。
- 新增只使用合成 UUID、标签和文本的 PostgreSQL 16 HTTP 契约测试夹具；每个测试均重建 disposable `public` schema 并从空库升级至 head。
- 覆盖四字段与来源顺序原样往返、知识点读取/拒绝、稳定游标及跨试卷游标拒绝、共享材料复用、幂等重放与冲突、来源顺序冲突、过期写入、题位冲突原子回滚、提交完整度、已提交不可修改、草稿材料随提交转换、修订历史不变，以及 V1 不接受编辑器 HTML 且不产生选项或审核表。

**Verification / 验证**

- 使用 Compose PostgreSQL 16 `postgres-test`、`GONGKAO_APP_ENV=test` 和 `_test` 数据库名完成验证；Ruff 通过，MyPy 严格模式检查 43 个源文件通过，Pytest 21 项通过，Alembic current 与 heads 均为 `0005_m005 (head)`。
- 验证后移除 `postgres-test` 容器；未使用 SQLite、真实试卷正文、答案或数据库转储。

**Known limitations and next step / 已知限制与下一步**

- 临时 `X-Actor-Id` 开发/测试身份适配器仍待正式认证与角色映射替换；审核端点、图文内容和发布能力仍不在本切片。
- 下一项为 `SHV1-010`：完成 G-04，并在 GitHub issue 汇总迁移命令、测试数量、回滚说明和已知限制；在该门禁完成前不得开始正式前端持久化。

---

### REV-20260831-03: G-04 backend acceptance / G-04 后端验收

**Decision / 决策**

- `G-04` 于 2026-08-31 通过。申论 V1 后端的五个 PostgreSQL migration、领域事务、HTTP 契约和契约测试已完成；正式前端持久化接线现在具备开始条件。
- 本门禁不批准审核、图文内容、解析器、发布、物理删除或其他新的后端能力；它们仍按各自后续切片和门禁执行。

**Verification / 验证**

- 使用 Compose PostgreSQL 16 `postgres-test`、`GONGKAO_APP_ENV=test` 和 `_test` 数据库名，执行 `alembic upgrade head`、`alembic current`、`alembic heads`、Ruff、MyPy 严格模式和完整 Pytest。
- 空库按 `0001_m001` 至 `0005_m005` 升级成功；current 与 heads 均为 `0005_m005 (head)`；MyPy 检查 43 个源文件通过，Pytest 21 项通过。
- 回滚只在一次性测试数据库执行：`alembic downgrade base` 成功，再次 `alembic upgrade head` 后 current 仍为 `0005_m005 (head)`；验证后移除 `postgres-test` 容器。

**Traceability and limitations / 追溯与限制**

- API 基线与切片提交：`a73f24a`（SHV1-004）、`dcbc2df`（SHV1-005）、`f2e2f55`（SHV1-006）、`91fd09f`（SHV1-007）、`66d94cb`（SHV1-008）、`371316e`（SHV1-009）。相应 GitHub issues #2 至 #7 记录范围与验证；#7 记录本门禁命令、数量、回滚和结论。
- 临时 `X-Actor-Id` 仅用于开发/测试身份上下文，仍需在后续正式认证设计中替换；审核权限、混合内容、解析器和发布尚未实现。

**Next step / 下一步**

- 可开始 `SHV1-011`：在独立的正式 Web 仓库中实现已批准的 React 持久化接线，并使用纯文本 payload 完成保存、重载与提交；不得绕过人工审核。

---

### REV-20260901-01: SHV1-011 production frontend wiring / SHV1-011 正式前端持久化接线

**Implementation / 实现**

- 独立 Web 仓库完成 React 19、TypeScript、Vite 和 Ant Design 5 的申论纯文本工作台；请求与响应类型由后端 OpenAPI 生成，保存、重载草稿与提交审核均使用已批准的纯文本契约。
- 使用官方 `@ant-design/v5-patch-for-react-19` 兼容补丁；已将弃用的 `Input` `addonAfter` 改为 `Space.Compact`。未引入编辑器 HTML/JSON、选项、审核记录或混合内容能力。
- Playwright 使用合成 UUID、标签和文本拦截 API，并维护截图基线；未提交真实试卷正文、答案、凭证或数据库数据。

**Verification / 验证**

- 在 Windows Node 22.23.2 与 npm 10.9.8 下执行 `npm run lint`、`npm run typecheck`、`npm run build` 和 `npm run test:e2e`，全部通过；截图已人工检查。
- 构建报告首个 JavaScript chunk 为约 650 kB、超过 Vite 默认 500 kB 提示阈值；这是非阻断的性能优化项，未改变功能验收结论。

**Traceability and next step / 追溯与下一步**

- Web GitHub issue #2 记录开始、Node 环境阻塞解除、兼容性检查和完成结论，并将在相应 Web 与文档提交推送后关闭。
- `SHV1-011` 已完成；下一项只能是 `SHV1-012 / G-05` 的脱敏端到端验收，不得在 G-05 通过前扩展新的产品能力。

---

### REV-20260903-01: Word-assisted annotation V1 planning / Word 辅助录题 V1 规划

- 产品规划确认下一阶段目标是降低人工在 Word 与工作台之间复制、定位和核对的成本，而不是自动拆题或自动入库。
- 纠正过期任务：`papers` 与 `paper_versions` 已在 M-001 实现；Word V1 后续只在 G-06 批准后新增上传、解析候选块和来源片段的已评审变更。
- 新增 `word-assisted-annotation-v1.md`，定义 G-06/G-07/G-08、WDV1-001 至 WDV1-006、范围边界与完成证据；GitHub issue #6 记录本次规划。

---

### REV-20260903-02: G-06 Word design approval / G-06 Word 设计批准

**Decision / 决策**

- 产品负责人已冻结 Word V1 的八项决策：原始 DOCX 长期私有保留、只接收安全 `.docx`、仅来源结构化、人工多块明确填入、字段到多来源块追溯、上传/预览/结构化失败分离、受控内部试点及以人工工作流为成功证据。
- `G-06` 于 2026-09-03 通过。唯一权威基线是 `WDV1_G06_FROZEN_DECISIONS.md`；它不选择云厂商或解析器库，也不批准任何生产实现。

**Consistency findings / 一致性结论**

- 既有 `papers` / `paper_versions` 和不可变版本规则继续有效；Word V1 不重建它们。
- 原 `DocumentBlock` 的业务语义候选类型与“无语义推断”决定冲突，已改为纯来源结构类型；`SourceSpan` 已明确为字段到多个有序块的人工确认来源关系，而非逐字映射。
- Gate 顺序修正为 G-07 原始 DOCX、G-08 来源结构化、G-09 人工辅助录题；PDF/OCR、图文正式题目、自动拆题、正式 RBAC、审核和发布仍未批准。

---
