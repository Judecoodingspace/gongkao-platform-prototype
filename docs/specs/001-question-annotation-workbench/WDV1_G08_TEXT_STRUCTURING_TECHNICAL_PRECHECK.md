# WDV1-003 / G-08 Text-Structuring Technical Precheck

**Status: TECHNICAL PRECHECK = PASS.** This is a disposable, synthetic-only comparison performed before any WDV1-003 implementation. It does not approve implementation; [`WDV1_G08_IMPLEMENTATION_CONTRACT.md`](./WDV1_G08_IMPLEMENTATION_CONTRACT.md) remains `PENDING PRODUCT APPROVAL`.

## 1. Baseline verification

- Platform repository: `main` and `origin/main` both resolved to `0edf99e4a8f8b0e68ebfd19c8a76986e44b2881f`; the working tree was clean before this report was added.
- API repository: `main` and `origin/main` both resolved to `8fbe0a6fa9a2ed96993a220ed6d65526cd703b66`; the sole pre-existing change was untracked `compose.local.yaml`, which was not read, changed, staged, or committed.
- The comparison ran outside both repositories in a disposable system temporary directory, using Python 3.12.13 and an isolated virtual environment with `python-docx 1.1.2`. No production dependency, code, schema, API, parser, fixture, or DOCX binary was added to either repository.
- All eight DOCX fixtures were generated from short synthetic labels only. Neither route opened a document viewer, contacted the network, followed a hyperlink, or used LibreOffice, PDF, Docling, PyMuPDF, OCR, page/bbox extraction, preview, or semantic inference.

## 2. Fixture matrix A–H

| ID | Purpose | Observed by both routes | Unexpected result |
| --- | --- | --- | --- |
| A | Title followed by three ordinary paragraphs | Four paragraphs in main-body order | None |
| B | One paragraph with a manual visual line break | One paragraph; break retained within it | None |
| C | Empty paragraph between ordinary paragraphs | Empty paragraph retained in order | None |
| D | Tab plus manual line break | Both inline controls retained within one paragraph | None |
| E | Visible-text hyperlink | Visible text retained; no network access | None |
| F | Paragraph, table, paragraph | Main-body order was paragraph, table, paragraph | None |
| G | Paragraph, inline image/drawing, paragraph | Direct OOXML marked the drawing at its real body position | `python-docx` presented the drawing paragraph as an empty paragraph unless inspected through its underlying XML |
| H | Word Heading style followed by body text | Both paragraphs retained in order; no semantic label inferred | None |

The fixture suite is intentionally structural: it asserts element order, paragraph emptiness, tabs, manual breaks, and detected non-text containers. It does not store or publish fixture binaries, complete text output, real paper content, visual layout, or business labels.

## 3. `python-docx` findings

`python-docx 1.1.2` reliably exposed the main-document paragraphs for A–E and H, including empty paragraphs, visible hyperlink text, tabs, and manual breaks. Its public `iter_inner_content()` sequence also preserved the paragraph/table/paragraph ordering in F.

The decisive limitation is G: the high-level paragraph view yielded an empty paragraph at the drawing position. The precheck could only identify the drawing by looking through the paragraph's underlying XML. Therefore `python-docx` alone cannot honestly distinguish a genuinely empty paragraph from an unsupported drawing-only paragraph without adding a second, lower-level inspection path. It is useful as a convenience layer, but not sufficient as the authoritative WDV1-003 traversal.

## 4. Direct OOXML findings

Direct traversal of the DOCX ZIP's `word/document.xml` iterated the main body in document order. It reconstructed paragraph text from Word text, tab, and break elements; retained empty paragraphs; retained visible hyperlink text; and identified table body elements and the drawing inside G's otherwise empty paragraph.

This route met the narrow precheck objective: preserve the natural main-body paragraph order and text while producing an explicit non-text/unsupported signal at a reliable source-order position. It did not infer whether text was a title, question, answer, material, or any other business concept. Page and bounding-box information were not requested and remain unavailable.

## 5. Comparison

| Criterion | `python-docx` | Direct OOXML |
| --- | --- | --- |
| Paragraph text/order for text-first fixtures | Pass | Pass |
| Empty paragraph retention | Pass | Pass |
| Tab and manual-break retention | Pass | Pass |
| Visible hyperlink text without network access | Pass | Pass |
| Table position in main body | Pass through `iter_inner_content()` | Pass through body-child traversal |
| Detect drawing at its source-order position without private XML fallback | Insufficient | Pass |
| Minimal production dependency | Requires external package | Python standard-library ZIP/XML handling |

## 6. Recommendation

**Recommendation: `DIRECT_OOXML` as the WDV1-003 authoritative text-first route.**

It provides one source of truth for main-body natural order and for known non-text structures that must not be silently swallowed. `python-docx` may be used later only as a non-authoritative convenience, if a future approved implementation demonstrates that it neither changes ordering nor hides gaps. This precheck does not require a hybrid route and does not freeze a library choice beyond the recommendation.

## 7. Proposed implementation boundary (prose only)

For a finalized DOCX obtained through the approved read-only private-storage boundary, the future processor should first re-check its byte hash, then inspect only the OOXML main document body. It should emit text blocks at natural paragraph granularity in body order, retaining original text and inline tab/manual-break behavior. It should record tables, drawings, embedded/other unsupported main-body structures as explicit gap evidence at the most reliable source-order vicinity available. It must mark the result `partial` or `failed` when the frozen status rules require it; it must never silently turn an unrecognized structure into a complete text-only result.

This boundary excludes page/bbox recovery, PDF/LibreOffice conversion, visual preview, table semantics, image extraction, OCR, text-box semantics, business classification, question drafting, SourceSpan, field fill, React, RBAC, and all production implementation decisions not already frozen.

## 8. Remaining technical risks

- The fixture suite covers representative main-body structures only. Future approved implementation tests must include additional synthetic OOXML cases such as nested tables, text boxes, equations, `altChunk`, headers/footers, footnotes/endnotes, and malformed but accepted G-07 inputs, while preserving the same no-silent-loss rule.
- OOXML text reconstruction requires a carefully versioned policy for less common inline elements and whitespace behavior. Any normalization must preserve an authoritative raw representation and requires the contract's approval path.
- This precheck demonstrates source order, not visual page layout, rendered line wrapping, page numbers, or bounding boxes; those remain WDV1-004 work.

`BLOCKERS = NONE` for the limited technical-route decision. The implementation authorization blocker remains: the WDV1-003 implementation contract is still pending explicit product-owner approval.

## 9. Gate

`TECHNICAL PRECHECK = PASS`

`WDV1-003 IMPLEMENTATION = NOT STARTED`

The gate passes because the direct OOXML route preserved synthetic main-body paragraph text/order, detected a known non-text gap without PDF/LibreOffice/Docling or semantic inference, used reproducible synthetic fixtures only, and did not conflict with frozen G-08 D1–D6 or contract P1–P3.

## 10. Git status

This report is documentation-only. Its commit metadata is recorded after the final diff and working-tree checks; no production API or platform implementation is authorized by that commit.
