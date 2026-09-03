# WDV1-003 / G-08 Text-First Source-Structuring Implementation Contract

**状态：PENDING PRODUCT APPROVAL。** 本合同将 G-06、G-07 与已冻结的 G-08 决策收敛为 WDV1-003 的候选实施边界。P1–P3 已写回；本合同仍需产品负责人批准才构成 implementation 授权。此前不得创建 migration、models、parser、依赖、API、OpenAPI、React 或 worker。

**权威输入：** [`WDV1_G06_FROZEN_DECISIONS.md`](./WDV1_G06_FROZEN_DECISIONS.md)、[`WDV1_G07_ACCEPTANCE_REPORT.md`](./WDV1_G07_ACCEPTANCE_REPORT.md)、[`WDV1_G08_FROZEN_DECISIONS.md`](./WDV1_G08_FROZEN_DECISIONS.md)。发生冲突时停止并补充评审；不得在代码中自行裁决。

## 1. 目标与非目标

WDV1-003 的唯一目标是：对已经 G-07 `finalized` 的、以纯文字为主的申论 DOCX，由人工明确触发一次独立处理，形成稳定、有序、自然段级的文字来源结构，并诚实记录成功、部分或失败。

本切片完成时只能声明：`WDV1-003 = COMPLETE`、`G-08 = IN PROGRESS`。G-08 仍须等待 WDV1-004 的视觉预览、视觉/来源联动、图片/其他可靠证据与可见 partial 体验。

本合同外：视觉预览、LibreOffice production integration、PDF/PDF upload、PyMuPDF、image asset workflow、OCR、表格语义重建、图文正式题目、SourceSpan 到题目字段、多块填入、React、自动建题/提交、AI 语义推断、RBAC、审核与发布。

## 2. 输入与不变性

- 只接受已存在且 `finalized` 的 G-07 DOCX `PaperVersion`；不得重新上传、替换、删除或改写原始 bytes、hash、storage reference 或上传状态。
- parser/service 必须通过 provider-neutral 的**只读私有来源存储抽象**取得原始 bytes、stream 或 file-like object。不得解析 `storage_uri`、推导本地绝对路径、直接依赖 `LocalPrivateSourceStorage`，或假设生产环境永久使用本地 filesystem。普通 API 响应、日志和错误不得泄露私有 URI 或路径。
- parser 开始结构化前，必须对本次实际读取的完整 bytes 重新计算 SHA-256，并确认等于 `PaperVersion.file_hash`。不一致时返回安全 integrity failure：不得产生 `success`/`partial`、不得改写 `PaperVersion`、不得改变 active selection，也不得影响已有历史结果。
- 每次处理由受控操作者明确请求。相同原件可以产生多个独立结果；这不是重新上传，也不是对 `PaperVersion` 的新版本。
- 输入的 source hash、处理器名称/版本、规范化后的处理配置及受支持运行环境必须被记录为该次结果的可追溯元数据。
- `X-Actor-Id` 若仍存在，只是开发/测试 actor audit identity，绝非正式认证/RBAC。

## 3. 处理结果、历史与 active 语义

一次人工处理请求形成一个 immutable processing result，拥有自己的状态、时间、处理器元数据和 `DocumentBlock` 集合。G-08 的 parser name、parser version、parser config、source hash 与 trigger actor 属于该 specific processing result；不得因重新解析修改 `PaperVersion.parser_*`，也不得把该组历史字段当成当前 processing metadata 的权威存储。重新处理绝不覆盖、删除或重写旧结果及其块。

- active selection 是独立的可变选择状态；processing result 本体不可因 active 切换而更新。任一 `PaperVersion` 同时最多一个 active result，切换必须原子完成，且不得修改 processing result 的 blocks、status、parser metadata 或 gap evidence。
- 当且仅当该 `PaperVersion` 当前没有 active result 且新的 terminal result 为 `success` 时，该 success 自动成为 initial active result；该 initial-active selection 必须与 terminal success commit 原子完成。
- 后续 `success` 结果先保持 inactive，只有明确、受控的人工作用才能成为 active。
- `partial` 默认 inactive，但可由受控操作者明确、可审计且原子地 activation；active partial 读取时必须同时暴露 `status = partial` 与 gap/unsupported evidence，active 不等于 complete。
- `failed` 永远不得通过普通 activation 成为 active。
- 已有任意 active（包括人工激活的 partial）时，新的 success 或 partial 都默认 inactive；不得静默替换。
- 历史结果只读保留；不提供物理删除。
- 未来任何字段来源关系必须指向具体 processing result 与具体 block，不能依赖 PaperVersion + order number。

同一次明确人工 processing intent 的网络超时、HTTP retry 或客户端重发必须幂等，返回同一 processing result；只有新的明确人工请求才创建新的 processing result。合同不冻结 header、URL、request 字段、processing result/run/status 表名或 schema。

## 4. text-first `DocumentBlock` 最小语义

WDV1-003 的最低覆盖仅为 DOCX main document body（主正文）中可可靠识别的 paragraph、paragraph order 与自然文字结构。每个可用 text block 表示这类 DOCX 自身结构，保留原始文字、全局 source order、block type，及可靠时的 page/position。

- 视觉换行不是边界；不得以句号、分号、冒号或业务含义拆分/合并/重排。
- 标题可作为其原始文字结构保存，但不是业务标签。
- header、footer、footnote、endnote 与其他 Word story 不在 WDV1-003 覆盖范围；不得由 parser 随机纳入或排除。它们不是 main-body `success` 的隐含承诺，后续若要处理须独立评审。
- `normalized text` 不是本切片默认必需字段；若实现需要它，必须说明它的非权威用途、保留原始文字，并经合同修订批准。
- 不能可靠取得的 page/bbox 必须为 unavailable，不得制造。
- `DocumentBlock` 不得含 stem、requirement、question、answer、material、knowledge point、question type 或任何机器业务结论。

## 5. 非文字与缺口证据

本切片不结构化图片、drawing、复杂 table、text box、embedded object、公式对象或其他非文字内容，但不能静默忽略。若这些结构在 main document body 中被可靠检测，结构化过程应通过 DOCX/OOXML 自然结构或等价的可靠容器证据将其作为不支持/未结构化缺口记录到该 processing result。

缺口记录只保存类型与可靠位置（例如 source-order region、`between block A and B` 或可用 page）；不得把无法可靠定位的内容假装有 bbox。failed result 若保留诊断 fragment，不得把它作为 usable `DocumentBlock` 对外暴露。图片/表格 block、视觉资产和 preview 都留给 WDV1-004。

## 6. 状态的可测试最低条件

一次处理结果在进入 terminal state 时，下列内容必须形成单个一致提交结果：

```text
processing-result metadata
+ terminal status
+ DocumentBlock collection
+ gap / unsupported evidence
```

不得存在 `success`/`partial` 但仅持久化部分 blocks，也不得留下 blocks 却没有所属 processing result。数据库提交失败时，不得留下可见半成品 `success`/`partial`，不得改变 existing active selection、`PaperVersion` 或历史 processing results；若触发 automatic initial activation，terminal success commit 与 initial active selection 必须同一一致原子结果。具体事务机制不在本合同冻结。

| 状态 | WDV1-003 最低含义 |
| --- | --- |
| `success` | 自然段级文字块与阅读顺序可靠，且在本切片可检测范围内没有未说明缺口。 |
| `partial` | 已产生的文字块与顺序可靠，但检测到可识别的未结构化/不可靠缺口；结果保留并带类型与可靠范围内的位置。默认 inactive，但可经明确人工 activation 成为 active。 |
| `failed` | 无法产生足够可靠的文字块，无法确认阅读顺序，存在未知丢失，或无法区分可信与缺失内容；不得成为普通 active result。 |

不得用“处理器未报错”、块数量百分比、confidence score 或 AI risk score 代替上述判断。source-structuring status 与未来 visual-preview status 必须是独立概念。

## 7. 技术 precheck（实施前，仍非 implementation）

在开始代码前，必须以不提交真实内容的方式，对获准的脱敏 text-first DOCX fixture 做一个有限 precheck：比较 `python-docx` 与 direct OOXML traversal 是否能稳定保留自然段及 document order，并识别是否有当前代表样本必须直接读取 OOXML XML 的结构。该 precheck 也可解决 hyperlink visible text 的保留但绝不访问网络、soft line break、tab、empty paragraph、table/body element traversal、parser-config canonicalization、bytes vs stream 读取、runtime fingerprint、fixture generation 与 parser adapter 最小边界。

产物只能记录汇总结论、工具版本、fixture 类别、顺序/段落结构是否一致及已知限制；不得提交文件正文、完整解析输出、私有路径或真实上传件。不得引入 Docling 大型依赖、LibreOffice、PyMuPDF、PDF 路线或 production parser 代码。若两种候选都无法证明目标结构稳定，应停止并回到设计评审。

## 8. 确定性与安全

在相同 source hash、parser version、parser config 和受支持运行环境下，处理必须产生稳定的 block text、source order、block type、缺口记录及可靠 provenance。数据库 UUID 不要求相同。

处理只能读取受控私有原件；不得访问网络、执行 DOCX 活动内容、输出真实正文到日志，或将真实 parser result、原始 DOCX、答案、私有路径、凭证或生成文件提交到 Git/GitHub。自动化测试允许提交人工构造的脱敏 synthetic fixture 及其受控 expected output（例如段落顺序与预期 block order），以验证确定性；它们不得含真实来源内容或私有解析输出。

## 9. PostgreSQL 与候选验收

若获批 implementation 需要 additive migration，必须使用 PostgreSQL 16 的一次性 `_test` 数据库验证 upgrade、current、heads，并按获批恢复策略验证 downgrade/re-upgrade；SQLite 不可替代。

候选验收至少包含：

1. finalized DOCX 才可人工触发处理，处理不改动 G-07 原始 bytes/hash/metadata；
2. 脱敏纯文字 fixture 产生自然段级、有序 text blocks，且重复处理的结构内容稳定；
3. 不可靠 page/position 不被伪造；
4. 非文字或复杂结构被检测时不会静默 success，而是产生明确 partial/缺口或 safe failed；
5. reprocessing 创建独立历史，后续结果不覆盖旧 block 集合；新的 partial/failed 不替换 success active result；
6. 无 active result + 首次 processing success 的 initial-active 行为符合 P2 的已批准选择；existing success active + new success 默认不静默替换；existing success active + new partial/failed 保持旧 active；显式 activation 后仍最多一个 active result；
7. 同一人工 processing intent 的技术重放不创建第二条 processing result；
8. 无任何业务语义标签、自动 question draft、字段填入或 SourceSpan；
9. 既有 G-04/G-07 后端测试继续通过，且 Git、日志、issue、fixture 不含真实私有正文或 parser output。

## 10. 停止条件

必须停止并回到设计审查，若：

- 需要改变 G-06/G-07/G-08 冻结语义或原始 DOCX 不变性；
- 需要用 PDF 反推自然段、接入 LibreOffice/PyMuPDF 或实现预览才能完成 text-first WDV1-003；
- 无法可靠检测已知非文字/复杂结构，可能把未知丢失标成 success；
- 需要新增业务语义、SourceSpan、填字段、React、RBAC、OCR、PDF upload 或 G-09 才能让本切片“可用”；
- precheck 无法在脱敏代表样本上证明自然段与顺序稳定。

## 11. 已批准的 P1–P3 与最小 backend contract

P1 已批准：partial 默认 inactive，但可由受控操作者明确、可审计、原子地设为 active；active partial 必须携带其 partial status 与 gap/unsupported evidence。failed 永远不可 active。后续 success 不自动替换 partial active。

P2 已批准：当且仅当没有 active result 时，新的 success 自动成为 initial active；该规则与 processing sequence 无关。已有 success 或人工激活的 partial 时，新 success 默认 inactive。

P3 已批准：WDV1-003 必须交付最小、正式、可集成测试且可供后续客户端消费的 backend contract。具体 URL、HTTP method、payload、pagination 与服务类名仍由后续最小 API contract 冻结；本合同只要求以下能力：

1. **Trigger processing**：受控地明确触发 finalized `PaperVersion` 的一次新处理，并遵循 source hash re-verification、processing-intent idempotency 与独立历史。
2. **Read processing result**：读取指定 result 的 identity、PaperVersion、status、parser metadata、timestamps/audit metadata、gap evidence 及相关 active 信息；不得泄露私有 storage URI、filesystem path、raw DOCX 或不必要真实来源正文。
3. **Read ordered text blocks**：按稳定 `source_order` 读取指定 result 的 text blocks；不得附加任何业务语义。
4. **Read active result**：读取一个 PaperVersion 的 current active result；若其为 partial，必须同时返回 partial status 与 gap/unsupported evidence。
5. **Activate result**：明确、受控地切换 active result；同一 PaperVersion 最多一个 active，切换原子，且不得修改 processing history、blocks、parser metadata 或 gap evidence。success 和 partial 可显式激活，failed 不可激活。

除创建新的 processing result 与独立 active selection 外，既有 processing result 本体只读。不得提供 PATCH block text、PATCH processing status、PATCH parser output 或 PATCH gap evidence；发现错误的正确动作是创建新的 processing result。

## 12. 拟议 issue 与批准后的实施顺序

获批后，在 API 仓库创建独立 `WDV1-003 / G-08 text-first source structuring` GitHub issue，只记录范围、开始、汇总 precheck、阻塞、验证、已知限制与完成结论，不含私有内容。顺序为：precheck → 经批准的最小 schema/API contract 补充（如确有需要）→ additive migration/处理边界 → PostgreSQL 16 tests → 验收记录。

在本合同获得产品负责人明确批准前，以上顺序不得开始。
