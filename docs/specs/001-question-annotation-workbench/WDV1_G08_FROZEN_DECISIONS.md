# WDV1 G-08 Frozen Decisions

**状态：APPROVED 产品决策基线。** 本文是 STEP 3 的权威输入。它冻结 G-08 的产品语义，不冻结数据库 schema、表名、API、worker、Python library、LibreOffice、PDF、HTML、PyMuPDF 或 React 实现，也不授权 production implementation。

## 1. 双层派生表示

Word V1 对同一个不可变 `PaperVersion` 采用互补的视觉阅读层和来源结构层；原始 DOCX 始终是唯一权威来源。视觉层尽可能忠实供人工阅读、核对和定位分页、文字、图片、公式、表格及相对布局。来源结构层提供可排序、可选择、可追溯的 text/image/other reliable source blocks，以及可靠时的页码/位置。两层不是两份独立来源，也不相互替代。

可靠位置关系存在时，来源块可联动到视觉层的页或附近区域；不存在可靠 page/bbox 时不得制造。未来前端应把它们呈现为同一来源工作区的互补视图，而非两个独立工具。

## 2. 自然结构块

`DocumentBlock` 的边界来自文档自身自然结构，不来自题干、问题、答案、材料、知识点或题型等业务理解。Word V1 的 text block 以自然段级粒度为主要目标；标题、图片、表格及其他可靠独立结构可各自形成来源块。

视觉换行不是 block boundary。超长自然段优先保持原始自然段，不得按句号、分号、冒号或中文语义默认再次切碎。若未来试点证明粒度过粗，必须以独立产品决策评审 block 内选择或人工拆块能力。

## 3. 独立处理历史与 active result

同一 `PaperVersion` 可被多次人工触发处理。每次 processing result 独立、只读保留自己的来源块集合、parser version、parser config、状态与创建时间；不提供物理删除，不静默覆盖。

首次成功处理可成为 initial active result。之后的成功结果必须先独立保留，只有明确、受控的人工作用才能切换 active result。新的 partial 或 failed 结果不得自动替换已有完整 success active result。未来字段来源必须追溯到 `PaperVersion → specific processing result → specific DocumentBlock`，不能只依赖 PaperVersion 加 block 编号。

## 4. WDV1-003 text-first 分片

当前业务主路径为以纯文字为主的申论 DOCX。WDV1-003 优先证明：已 finalized DOCX 经独立处理后，能稳定得到按自然段结构排列的 ordered text blocks、source order 及可靠时的 page/position。

WDV1-003 不实现 image asset workflow、图片识别、公式结构化、OCR、表格语义重建、混合内容正式题目或图文题能力。若检测到图片、复杂表格、unsupported object 或其他非文字内容，必须留下明确 unsupported/unstructured signal，或将结果标为 partial；不得静默吞掉后仍声称完整 success。

`WDV1-003 = COMPLETE` 仅表示文字来源结构基础完成。视觉预览、visual/source linking、image/other reliable evidence 与完整的 partial 体验属于 WDV1-004；G-08 在两者均验收前为 `IN PROGRESS`。

## 5. 文字结构化主路线

WDV1-003 的主路线直接读取 DOCX/OOXML 的自然文档结构，忠实取得 paragraph、document order 与其他可靠结构元素，再形成 ordered text blocks。不得为了获得 page/bbox 而先将已有自然段变成页面行、再反推自然段。

直接 DOCX/OOXML 路线无法可靠取得 page 或 bbox 时，记录 unavailable，不得制造。LibreOffice → PDF 仍是 WDV1-004 视觉预览的主要 production candidate；PyMuPDF 仍可作为 PDF page/bbox/image/visual-linking 候选。Docling 不作为 Word V1 第一版 production 主路线，保留未来重评估可能性。实现保留轻量 parser adapter 边界，但不得为未知未来过度抽象。具体 Python library 尚未冻结；STEP 3 可安排有限 technical precheck 比较 `python-docx` 和直接 OOXML traversal。

## 6. 结构化状态语义

来源结构化使用 `success`、`partial`、`failed` 三态；判断的是结果的可靠可用性和缺口能否识别，不是程序是否抛出 exception。

- `success`：在当前承诺范围内，来源块及阅读顺序可靠，且没有已知未说明的结构缺口。
- `partial`：可靠块仍可使用，但存在可识别的结构缺口；必须至少说明非完整、缺口类型和可靠范围内的位置（页、source-order region、相邻块或其他可靠 vicinity）。
- `failed`：无法产生足够可靠的 text blocks、无法确认阅读顺序、存在未知内容丢失，或无法确认哪些内容可信。不得作为普通 active source structure 给标注员使用。

未知丢失或未知顺序完整性不得标为 success。不采用简单百分比阈值、confidence score 或 AI risk score。structuring status 与 visual preview status 必须分开；不得用一个 `document_status` 混合 upload、structuring 与 preview。

## Gate 状态

`G-08 DESIGN DECISIONS = APPROVED`

`G-08 = NOT PASSED`

现在仅允许 STEP 3：拟定 `WDV1-003 Implementation Contract`，其状态必须为 `PENDING PRODUCT APPROVAL`。未获得该合同明确批准前，禁止创建 migration、models、parser、依赖、API、OpenAPI、React、预览、字段填入、SourceSpan、G-09、OCR、PDF upload、AI 语义推断或 RBAC 实现。
