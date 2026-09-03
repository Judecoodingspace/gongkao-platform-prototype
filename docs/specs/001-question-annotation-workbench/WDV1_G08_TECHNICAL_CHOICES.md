# WDV1 G-08 Technical Choices

**状态：APPROVED 技术路线冻结。** 本文记录已通过技术预检查、并由产品负责人冻结的实施技术选择。它不改变 G-06/G-07/G-08 的产品语义，也不表示 WDV1-003 implementation 已完成或 G-08 已通过。

## T1 — Direct OOXML traversal

`T1 = APPROVED`

`WDV1-003 authoritative structural parser route = DIRECT OOXML TRAVERSAL`

### 权威结构来源

WDV1-003 对 DOCX main document body 的 text-first 结构读取，直接遍历 DOCX 内部 OOXML：

```text
word/document.xml
→ w:body
→ document child / paragraph structure
```

该路线是 natural paragraph structure、document/source order 与 unsupported/non-text structural evidence 的唯一权威来源。

### `python-docx` 的受限角色

`python-docx` 不得作为 source order、completeness、unsupported-gap detection 或 authoritative structural truth 的来源。若未来获批实施确有便利需求，它只能作为 non-authoritative helper；Direct OOXML traversal 的顺序和结构身份始终优先，且不得形成两套 block 后再猜测对齐。

### Fail-visible 规则

```text
KNOWN + SUPPORTED
→ normal text block

KNOWN + UNSUPPORTED
→ explicit gap / unsupported evidence

UNKNOWN MAIN-BODY STRUCTURE
→ must not silently become success
```

当前 supported path 仅为 main document body 中的 natural paragraphs、visible text 与 stable order。表格、drawing/image、OMML formula、textbox、embedded object 及其他不支持的非文字 main-body 结构，不得静默消失；应按冻结的 D6 状态语义形成 identifiable gap、`partial`，或必要时 safe `failed`。

header、footer、footnote、endnote、visual page reconstruction、PDF、LibreOffice、bbox 与 preview 仍不在 WDV1-003 范围内。后续实现测试只需保护 main-body silent-loss 风险，不需要在 implementation 前研究完整 Word 功能或复杂 nested-table 语义。

## 关联状态

```text
TECHNICAL PRECHECK = PASS
T1 = DIRECT_OOXML APPROVED
WDV1-003 IMPLEMENTATION = NOT STARTED
G-08 = IN PROGRESS
```

技术预检查的可复核证据见 [`WDV1_G08_TEXT_STRUCTURING_TECHNICAL_PRECHECK.md`](./WDV1_G08_TEXT_STRUCTURING_TECHNICAL_PRECHECK.md)。
