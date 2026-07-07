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

| Status | 中文 | Meaning |
| --- | --- | --- |
| `Proposed` | 待分析 | Feedback has been recorded but not fully analyzed. |
| `Needs Clarification` | 待澄清 | Key user, scenario, rule, or boundary is still unclear. |
| `Accepted` | 已接受 | The team agrees to make the change. |
| `Rejected` | 已拒绝 | The team decides not to make the change; the reason must be recorded. |
| `Deferred` | 暂缓 | The feedback is valid but is outside the current milestone. |
| `Implemented` | 已实现 | The accepted change has been implemented. |
| `Verified` | 已验证 | The change has passed the agreed acceptance check. |

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

| ID | Area | Original feedback | Raised by | Initial priority | Status |
| --- | --- | --- | --- | --- | --- |
| F-01 | Prototype / Business / Data / Permission / Other | Record the feedback as closely as possible to the original wording. |  | P0 / P1 / P2 / P3 | `Proposed` |

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

| Feedback ID | Decision | Reason | Milestone | Owner |
| --- | --- | --- | --- | --- |
| F-01 | `Accepted` / `Rejected` / `Deferred` |  | MVP / Later |  |

**Document and implementation synchronization / 文档与实现同步**

| Target | Required change | Owner | Status | Link or commit |
| --- | --- | --- | --- | --- |
| `docs/PRD.md` |  |  | Todo |  |
| Relevant `spec.md` |  |  | Todo |  |
| `plan.md` or `tasks.md` |  |  | Todo |  |
| `data-model.md` |  |  | Not needed |  |
| `acceptance-checklist.md` |  |  | Todo |  |
| HTML/Figma prototype |  |  | Todo |  |

**Verification / 验证**

- Acceptance scenario / 验收场景：
- Reviewer / 验证人：
- Verification result / 验证结果：
- Remaining issues / 遗留问题：

---

## Review Records / 评审记录

### REV-20260704-01: First prototype and workflow review / 第一次原型与业务流程评审

**Meeting information / 会议信息**

- Date / 日期：2026-07-04（根据文档名称推定，待确认）
- Participants and roles / 参与人及角色：项目组师兄等，具体名单与角色待补充
- Recorder / 记录人：待补充
- Material reviewed / 评审材料：静态录题工作台原型，以及判断推理、资料分析题目图片样例
- Source note / 原始记录：`关键问题确认0704.docx`
- Review goal / 本次目标：确认录题界面调整方向，并提前识别尚未实现的录题业务规则

**Validation boundary / 可验证性边界**

- 当前可以验证：页面区域、字段、控件类型、预览滚动与复制、图片插入入口、图片排版模式和真题/模拟题入口表达。
- 当前无法完成端到端验证：知识点后台校验、上一题默认值持久化、图片上传与存储、查重算法、题库权限隔离和富文本公式保存。
- 因此，本轮对前一类意见进行原型评审；后一类只形成需求假设与工程建议，待功能实现后再做验收。

**Original feedback / 原始意见**

| ID | Area | Original feedback | Initial priority | Status |
| --- | --- | --- | --- | --- |
| F-01 | 原文预览 | 题本和解析均需支持预览、复制和滚动。 | P1 | `Proposed` |
| F-02 | 知识点 | 知识点改为输入；提交时与后台配置校验，不相符则不通过并提示。 | P1 | `Needs Clarification` |
| F-03 | 连续录题效率 | 科目、类型、知识点、年份、省份和难度默认沿用上一题的输入。 | P1 | `Proposed` |
| F-04 | 选项与评分 | 删除分值/评分项；选项均为单选。 | P1 | `Needs Clarification` |
| F-05 | 题干图片 | 题干编辑区域新增插图功能。 | P0 | `Proposed` |
| F-06 | 图片排版 | 题干与选项图片分开处理；支持单图一行、双图并列、四图两行两列等分类排版。 | P0 | `Needs Clarification` |
| F-07 | 查重 | 在同一知识点范围内查重；部分含图题仅看题干难以判断，可参考解析。 | P1 | `Needs Clarification` |
| F-08 | 题库与权限 | 谁上传的题归谁的题库；合作老师有独立上传权限和独立组卷范围，避免与其他老师题目混用。 | P0 | `Needs Clarification` |
| F-09 | 真题/模拟题入口 | 上传前先确认是真题还是模拟题，再进入传题界面。 | P1 | `Proposed` |
| F-10 | 图片公式 | 解析中不可编辑的公式图片需要与文字共同录入；需确认行内图片、整段截图或富文本方案。 | P0 | `Needs Clarification` |

**Analysis / 分析**

#### F-01：题本与解析预览

- 当前原型已有独立题本、解析区域和滚动容器，但复制能力没有明确操作反馈。
- 下一版原型应允许正常文本选择，并在题本块、解析块提供复制图标按钮；复制操作需要有成功提示。
- 长文档应保持题本区和解析区各自独立滚动，不让右侧表单位置随左侧滚动丢失。
- 功能实现后需验证复制结果保留文本顺序，并且不执行源 DOCX 中的宏或活动内容。

#### F-02：知识点输入与校验

- 不建议使用完全自由输入并等到提交时才报错，这会增加返工，也容易产生同义词、错别字和重复分类。
- 建议改成“可搜索的组合框”：允许键入关键词，但只能从当前科目和题型对应的后台知识点中确认一个有效值。
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
- 待确认：申论、面试题和未来扩展题型是否复用同一题目模型。

#### F-05 与 F-06：图片内容和排版

- 这不是只在题干输入框旁增加一个上传按钮的问题。当前数据模型仅有题目级 `has_image` 和选项级 `image_uri`，无法表达题干、问题、选项、解析中多张图片的顺序与布局。
- 建议把题干、问题、选项和解析表示为有序内容块，最小支持 `text`、`image` 和后续可选的 `formula` 类型。
- 每个图片块至少记录资源 ID、顺序、所属字段、布局组、布局方式、宽高、文件哈希和来源片段。
- 原型应提供插图按钮和有限的布局选择：单图通栏、双图并列、选项四图 2x2；不要让录题员自由拖出不可控版式。
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

| Group | Scope | Suggested contents | Verification timing |
| --- | --- | --- | --- |
| A | 下一版静态原型 | 预览复制、知识点可搜索输入、上一题默认值提示、移除分值、答案单选、题干/选项插图入口、有限图片布局、真题/模拟题标识 | 现在可评审 |
| B | 正式规格与数据模型 | 有序内容块、媒体资源、图片布局、题库/工作空间归属、来源类型、查重候选记录 | 原型方向确认后更新 |
| C | 后端业务功能 | 后台知识点校验、默认值作用域、对象存储、查重计算、权限控制、审计日志 | 实现后验收 |
| D | 后续增强 | 公式 OCR/LaTeX、自动裁图、图片感知查重、跨题库受控共享 | MVP 后评估 |

**Preliminary decision / 初步决策**

| Feedback ID | Preliminary decision | Reason | Next step |
| --- | --- | --- | --- |
| F-01, F-03 | 建议接受 | 明确改善连续录题效率，风险较低 | 纳入下一版原型 |
| F-02 | 调整方案后接受 | 使用可搜索组合框和即时校验优于提交时才校验 | 确认新增知识点流程 |
| F-04 | 仅接受 MVP 界面调整 | 避免过早删除未来扩展能力 | 确认题库长期题型范围 |
| F-05, F-06 | 原则接受 | 需要先补内容块和图片布局模型 | 先画图片编辑交互原型 |
| F-07 | 暂不按原方案实现 | 仅看解析或硬拦截会产生误判 | 定义候选信号和人工确认流程 |
| F-08 | 暂缓到权限专题确认 | 属于系统级数据边界 | 单独召开权限/题库归属评审 |
| F-09 | 建议接受 | 单一工作台加来源类型即可实现 | 确认类别枚举 |
| F-10 | 原则接受 MVP 行内图片 | 受控内容块比任意 HTML 更可维护 | 确认导出展示要求 |

**Documents to synchronize after decisions / 决策确认后需同步的文档**

| Target | Required change | Status |
| --- | --- | --- |
| `docs/PRD.md` | 增加连续录题效率、来源类型、私有/共享题库边界和查重流程 | Waiting for decision |
| `spec.md` | 补充图片内容块、预览复制、默认值继承和知识点校验场景 | Waiting for decision |
| `data-model.md` | 评估内容块、媒体资源、题库归属、成员关系和查重候选实体 | Waiting for decision |
| `tasks.md` | 增加权限专题、图片编辑器和查重 POC 任务 | Waiting for decision |
| `acceptance-checklist.md` | 增加复制、默认值边界、图片布局、单选和权限隔离验收项 | Waiting for decision |
| HTML/Figma prototype | 实现 Group A 的可点击交互 | Todo |

**Verification / 验证**

- 当前结果：已提取 DOCX 正文和 4 张嵌入截图，并完成截图与文字的对应核对。
- 尚未验证：所有依赖真实后端、数据库、对象存储和用户权限的功能。
- 下一次评审建议：先确认 F-04、F-06、F-08、F-09 和 F-10 的待确认问题，再修改静态原型。
