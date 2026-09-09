# WDV1 STEP 4.4B — Direct OOXML Text-first Parser Implementation Plan

**STATUS = PLAN ONLY**

This document is a bounded implementation plan for STEP 4.4B — Direct OOXML Text-first Parser. It translates the frozen B1–B9 decisions into an implementation-ready design grounded in the actual API repository.

**IMPLEMENTATION NOT AUTHORIZED.**

No production code is created or modified by this document.

---

## A. Authority and Scope

### Governance authority

```text
Repository: Judecoodingspace/gongkao-platform-prototype
main@2750027276b9696d632970a14239a27319fc656c
```

Frozen decision authority:

```text
docs/specs/001-question-annotation-workbench/WDV1_STEP4_4B_PARSER_FROZEN_DECISIONS.md
```

### API authority

```text
Repository: Judecoodingspace/gongkao-question-bank-api
main@f7f49399f05ebf16110d8a1a940f2681f000a32e
```

STEP 4.4A reader boundary authority:

```text
src/gongkao_api/modules/papers/storage.py
→ PrivateSourceReader Protocol
→ LocalPrivateSourceStorage.read(storage_uri) -> SourceReadResult
```

### Scope statement

```text
PLAN ONLY
IMPLEMENTATION NOT AUTHORIZED
```

This plan covers only the parser slice. It does not authorize Processing Service implementation, schema migration, API/OpenAPI changes, React/frontend work, or WDV1-004.

---

## B. Repository Inspection Findings

The following findings are based on the actual API repository at `main@f7f49399f05ebf16110d8a1a940f2681f000a32e`.

### B.1 Existing papers/storage modules

| Path | Responsibility |
| --- | --- |
| `src/gongkao_api/modules/papers/models.py` | `Paper` and `PaperVersion` ORM. `PaperVersion` holds immutable source evidence (`file_hash`, `storage_uri`, `upload_status`) and legacy `parser_*` fields. |
| `src/gongkao_api/modules/papers/storage.py` | STEP 4.4A read-only boundary. `PrivateSourceReader` protocol exposes `read(storage_uri) -> SourceReadResult`. `LocalPrivateSourceStorage` implements it and returns `content`, `size`, `sha256`. |
| `src/gongkao_api/modules/papers/service.py` | Upload/finalization service. It stages, promotes, and persists `PaperVersion`. It does not parse DOCX content. |
| `src/gongkao_api/modules/papers/validation.py` | DOCX upload validation. Uses `zipfile` and `xml.etree.ElementTree` from the standard library. |

### B.2 Existing processing-result models

| Path | Responsibility |
| --- | --- |
| `src/gongkao_api/modules/source_processing/models.py` | Contains `SourceProcessingResult`, `DocumentBlock`, `SourceProcessingGap`, and `PaperVersionActiveProcessing`. These ORM models already match the approved STEP 4.3 schema. |
| `src/gongkao_api/modules/source_processing/__init__.py` | Package marker. |

`DocumentBlock` constraints:

```text
source_order > 0
block_type = 'text'
UNIQUE (processing_result_id, source_order)
```

`SourceProcessingGap` fields:

```text
gap_type
source_order
source_region_kind
diagnostic_code
before_block_source_order
after_block_source_order
```

`SourceProcessingResult` carries:

```text
execution_state
result_status
parser_name / parser_version / parser_config
verified_source_hash
runtime_fingerprint
diagnostic_code / diagnostic_metadata
```

### B.3 Existing tests

| Path | Responsibility |
| --- | --- |
| `tests/api/test_paper_docx_upload_contract.py` | Upload contract, DOCX validation, idempotency, storage privacy. Uses synthetic in-memory ZIP fixtures. |
| `tests/api/test_paper_storage.py` | STEP 4.4A reader behavior: byte-for-byte read, SHA-256, safe failure, no path/URI leakage. |
| `tests/services/test_shenlun_services.py` | Source material and question services. Not directly related to parser. |
| `tests/services/conftest.py` | PostgreSQL 16 service-test engine and `service_session` fixture. |

### B.4 Existing XML/DOCX-related dependencies

`pyproject.toml` production dependencies do not include `python-docx`, `lxml`, `LibreOffice`, `PyMuPDF`, or any OCR/image library. DOCX handling currently uses Python standard library `zipfile` and `xml.etree.ElementTree`. The frozen technical choice T1 (Direct OOXML traversal) is therefore implementable without adding production dependencies.

### B.5 Typing/style conventions

- Python `>=3.12,<3.13`
- `ruff` line-length 100, selects `E,F,I,UP,B,SIM`
- `mypy` `strict = true`, `files = ["src"]`
- SQLAlchemy 2.0 style with `Mapped` / `mapped_column`
- Standard-library `dataclasses` with `frozen=True, slots=True` are already used for internal types (e.g., `StagedSource`, `SourceReadResult`).

### B.6 Why the parser belongs in `source_processing`

The parser transforms verified DOCX bytes into a `SourceProcessingResult`-shaped candidate (blocks + gaps + status + diagnostics). It does not belong in:

- `papers/` — that module owns source identity, storage, and upload/finalization.
- `source_materials/` — that module owns business-facing material drafts.
- `api/` — HTTP boundary must remain thin and must not contain parsing logic.

The existing `source_processing` module already owns the result schema, so the parser is a natural resident.

---

## C. Proposed File-Level Change Scope

| Path | Status | Responsibility | B1–B9 decisions implemented |
| --- | --- | --- | --- |
| `src/gongkao_api/modules/source_processing/parser_types.py` | add | Persistence-agnostic internal types: `ParsedBlockCandidate`, `GapCandidate`, `ParserDiagnostic`, `ParseResult`, `ParserConfig`. | B1, B7, B8, B9 |
| `src/gongkao_api/modules/source_processing/parser_constants.py` | add | Controlled constants: parser name/version, gap types, region kinds, diagnostic codes, canonical config keys. | B5, B6, B8, B9 |
| `src/gongkao_api/modules/source_processing/parser.py` | add | Direct OOXML traversal and text reconstruction. Consumes `bytes`, returns `ParseResult`. No DB, no ORM, no storage. | B1, B2, B3, B4, B5, B6, B7, B8, B9 |
| `src/gongkao_api/modules/source_processing/__init__.py` | modify | Export public parser API (`parse_docx`, `ParseResult`, etc.). Minimal surface only. | B1 |
| `tests/services/test_source_processing_parser.py` | add | Unit tests for parser against synthetic DOCX bytes. No real private documents. | B3, B4, B5, B6, B7, B8, B9 |
| `tests/services/fixtures/source_processing.py` | add (optional) | Synthetic OOXML/DOCX fixture builders used only by tests. | B3, B4, B5, B6, B9 |

Files that MUST NOT be changed:

```text
src/gongkao_api/modules/papers/models.py
src/gongkao_api/modules/papers/storage.py
src/gongkao_api/modules/papers/service.py
src/gongkao_api/modules/papers/validation.py
src/gongkao_api/modules/source_processing/models.py
src/gongkao_api/modules/source_materials/*
src/gongkao_api/modules/questions/*
src/gongkao_api/api/*
src/gongkao_api/main.py
migrations/*
pyproject.toml (no new dependencies)
```

No schema migration is required. If implementation discovers that the existing `DocumentBlock` / `SourceProcessingGap` / `SourceProcessingResult` schema cannot satisfy B1–B9, the implementation MUST STOP and report `SCHEMA_REDESIGN_REQUIRED`.

---

## D. Parser Internal Contract

The parser must remain independent from `PaperVersion` ORM, `ProcessingResult` ORM, DB session, `storage_uri`, absolute path, HTTP request, and actor/user context.

Proposed internal types (names are candidates, not mandatory):

### D.1 `ParserConfig`

```text
parser_name: str          # e.g. "wdv1-direct-ooxml"
parser_version: str       # e.g. "4.4b.0"
canonical_config: dict    # normalized JSONB-safe config
```

Ownership: parser-only. Persisted later by Processing Service into `SourceProcessingResult.parser_*`.

### D.2 `ParsedBlockCandidate`

```text
source_order: int         # > 0, authoritative w:body traversal position
block_type: str           # always "text" for WDV1-003
text_original: str        # exact reconstructed paragraph text; may be ""
```

Ownership: parser-only. Derived from `DocumentBlock` schema but not an ORM instance. Persisted later by Processing Service.

### D.3 `GapCandidate`

```text
gap_type: str             # table | drawing | omml | textbox | embedded_object | unknown
source_order: int         # body-level order or containing paragraph order
source_region_kind: str   # body_child | within_paragraph
diagnostic_code: str      # stable parser diagnostic
before_block_source_order: int | None
after_block_source_order: int | None
```

Ownership: parser-only. Derived from `SourceProcessingGap` schema. Persisted later by Processing Service.

### D.4 `ParserDiagnostic`

```text
code: str                 # stable controlled code
stage: str                # e.g. "archive", "document_xml", "body_traversal"
source_order: int | None
structure_kind: str | None
bounded_metadata: dict    # counts, indexes, safe flags only
```

Ownership: parser-only. May be persisted later as `diagnostic_metadata` by Processing Service. Must be source-content-free.

### D.5 `ParseResult`

```text
blocks: tuple[ParsedBlockCandidate, ...]
gaps: tuple[GapCandidate, ...]
status_candidate: str     # success | partial | failed
reliability_flags: dict   # internal reliability booleans
diagnostics: tuple[ParserDiagnostic, ...]
```

Ownership: parser-only. No database IDs, no ORM entities, no storage_uri, no absolute path.

---

## E. Direct OOXML Traversal Strategy

Authoritative route:

```text
DOCX ZIP
→ word/document.xml
→ w:body
→ body children in document order
```

Algorithm-level description:

1. Open `word/document.xml` from the in-memory DOCX bytes using `zipfile.ZipFile`.
2. Parse the XML with `xml.etree.ElementTree.fromstring`.
3. Locate `w:body`. If missing or unparseable, emit `failed` with safe diagnostic.
4. Iterate body children in document order. Assign `source_order` as the 1-based index of each body child.
5. For each body child:
   - `w:p` → paragraph handling (see F).
   - `w:tbl` → body-level table Gap (see G).
   - `w:sectPr` → ignore (section properties carry no text content for this slice).
   - any other body child → `unknown` body-level Gap; if its presence makes block/order reliability unprovable, mark `failed`.
6. Within a paragraph, inspect runs and inline structures:
   - supported: `w:r` containing `w:t`, `w:tab`, `w:br`, `w:cr`; `w:hyperlink` containing supported runs.
   - unsupported but known: `w:drawing`, `w:pict`, `m:oMath`, `m:oMathPara`, `w:txbxContent`, `w:object`, `w:altChunk`.
   - unknown: any other element that is reliably located and may carry or alter source content / reading structure (e.g., `w:ins`, `w:del`, `w:moveFrom`, `w:moveTo`, `w:altChunk`) is treated as a bounded unknown inline Gap. Pure bookkeeping/property/range markers (e.g., `w:pPr`, `w:rPr`, `w:proofErr`, `w:bookmarkStart`, `w:bookmarkEnd`, `w:lastRenderedPageBreak`) do not create gaps on their own.
7. `source_order` for body-level objects is their body-child index. `source_order` for inline objects is the containing paragraph's body-child index, with `source_region_kind = within_paragraph`.

The parser does not use `python-docx`. It does not follow external relationships. It does not extract images, resolve drawing embeds, or reconstruct visual layout.

---

## F. Text Reconstruction Policy

This policy is explicit, reviewable, and deterministic. It does not use semantic splitting or normalization. It does not use `strip()` to decide source emptiness.

### F.1 Supported inline elements

| OOXML element | Reconstruction rule |
| --- | --- |
| `w:t` | Append its exact text content (`element.text or ""`). Preserve all whitespace characters exactly as they appear between tags. Do not strip, trim, or normalize. |
| `w:tab` | Append `"\t"`. |
| `w:br` | Append `"\n"`. |
| `w:cr` | Append `"\r"`. |
| `w:hyperlink` | Recursively process its supported children (`w:r`) in document order. Do not follow the relationship target. Do not add any marker for the hyperlink itself. |
| `w:r` | Process its children in document order. Ignore run properties (`w:rPr`). |

### F.2 Paragraph handling

- One `w:p` produces at most one `ParsedBlockCandidate`.
- A paragraph is never split by sentence punctuation, manual line break, tab, or hyperlink.
- Adjacent paragraphs are never merged.
- Heading paragraphs are treated as ordinary paragraphs; no business type is inferred.

### F.3 Empty paragraph

A paragraph is a genuine empty paragraph only when:

```text
reconstructed text = ""
AND
no unsupported/content-bearing structure is detected inside it
```

It must be preserved with `text_original = ""`.

Whitespace-only, tab-only, or manual-break-only paragraphs are not genuine empty paragraphs because they contain supported inline elements. They are preserved with their reconstructed text (e.g., `"\t"`, `"\n"`).

### F.4 Mixed paragraph

If a paragraph contains both supported text and unsupported content:

```text
one ParsedBlockCandidate with the supported text
+
one or more GapCandidate records
```

Unsupported content never creates a fake text block.

### F.5 Unsupported-only paragraph

If a paragraph contains no supported text but contains unsupported/content-bearing structure:

```text
no ParsedBlockCandidate is created
GapCandidate records are emitted instead
```

### F.6 Final candidate mapping for `w:br` and `w:cr`

| OOXML element | Reconstructed character | Reason |
| --- | --- | --- |
| `w:br` | `"\n"` | WordprocessingML line break; maps to a single line-feed to preserve explicit author line break intent without inventing visual layout. |
| `w:cr` | `"\r"` | WordprocessingML carriage-return element; preserves its distinct identity from `w:br`. |

The mapping preserves the distinct OOXML element identity (`w:br` versus `w:cr`) in reconstructed text. Their ordinary line-ending behavior is equivalent in WordprocessingML; the different Python characters are a deliberate lexical/source-representation choice, not a claim of different visual line-breaking semantics. Downstream consumers (if any) may render them as they see fit in a later, separately reviewed slice.

`w:t` whitespace is always taken exactly as the element text value (`element.text or ""`). No `strip()`, trim, or normalization is applied regardless of the presence or absence of `xml:space="preserve"`.

```text
PLAN_DECISION_REQUIRES_REVIEW = NO
```

---

## G. Gap Generation Plan

Gap occurrence principle:

```text
one reliably distinguishable unsupported occurrence
→ one GapCandidate
```

Duplicate nested OOXML implementation nodes inside a single recognized container do not create additional gaps.

### G.1 Body-level occurrence

| Structure | Detection rule | gap_type | source_order | source_region_kind |
| --- | --- | --- | --- | --- |
| Table | body child is `w:tbl` | `table` | body-child index | `body_child` |
| Unknown body child | any other body child not `w:p`, `w:tbl`, `w:sectPr` | `unknown` | body-child index | `body_child` |

`before_block_source_order` = highest text-block `source_order` before the gap (if any).  
`after_block_source_order` = lowest text-block `source_order` after the gap (if any).

### G.2 Within-paragraph occurrence

The parser scans each paragraph for reliably distinguishable unsupported logical occurrences. Each occurrence produces one `GapCandidate`, regardless of whether the same `gap_type` appears multiple times in the same paragraph.

Duplicate nested OOXML implementation nodes inside a single recognized container do not create additional gaps.

| Anchor | gap_type | Notes |
| --- | --- | --- |
| `w:drawing` or `w:pict` | `drawing` | One drawing/picture occurrence. Two separate `w:drawing` elements in the same paragraph → two drawing gaps. Nested elements inside the drawing do not create extra gaps. |
| `m:oMath` or `m:oMathPara` | `omml` | One formula occurrence. Two separate formula elements in the same paragraph → two omml gaps. |
| `w:txbxContent` | `textbox` | Text box content. Text inside is not treated as main-body paragraph text. |
| `w:object` | `embedded_object` | Embedded object. |
| `w:altChunk` | `unknown` | External chunk inclusion; content cannot be trusted as normal main-body text. |
| `w:ins`, `w:del`, `w:moveFrom`, `w:moveTo`, comment ranges | `unknown` | Tracked changes / comments are not supported in WDV1-003. Only elements that may carry or alter source content produce gaps. |
| Any other content-bearing element not in the supported set | `unknown` | Bounded unknown gap. |

The following non-content bookkeeping/property/range markers do NOT create gaps on their own:

```text
w:pPr
w:rPr
w:proofErr
w:bookmarkStart
w:bookmarkEnd
w:lastRenderedPageBreak
```

All within-paragraph gaps share the containing paragraph's `source_order` and use `source_region_kind = within_paragraph`.

### G.3 Unsupported-only paragraph

If a paragraph contains only unsupported anchors (e.g., a drawing-only paragraph), it emits gaps but no text block. It is not treated as a genuine empty paragraph.

### G.4 Out-of-scope stories

`header`, `footer`, `footnote`, `endnote` parts are not traversed. They are out of scope for WDV1-003 and do not generate gaps.

### G.5 Forbidden behavior

The parser MUST NOT:

```text
extract image assets
perform OCR
reconstruct table semantics
convert OMML to LaTeX/MathML
recover visual layout or page/bbox
analyze image alt-text as main-body text
create ImageSource / TableSource / FormulaSource
```

---

## H. Status Derivation

The parser derives a `status_candidate` using only deterministic reliability checks.

### H.1 Reliability flags

```text
archive_reliable          # DOCX ZIP and document.xml readable
body_traversal_reliable   # w:body found and children enumerable
text_reconstruction_reliable
order_reliable
unknown_loss_risk         # any unbounded or unlocatable unknown structure
```

### H.2 Decision procedure

```text
positive_reliability_flags:
- archive_reliable
- body_traversal_reliable
- text_reconstruction_reliable
- order_reliable

if not all(positive_reliability_flags):
    status_candidate = failed
elif unknown_loss_risk:
    status_candidate = failed
elif gap_count > 0:
    status_candidate = partial
else:
    status_candidate = success
```

Hard rules preserved:

```text
Gap > 0 → status MUST NOT be success
Gap = 0 → does NOT automatically mean success
```

Reader failure or source-integrity mismatch are handled by Processing Service, not by this parser.

### H.3 Internal representation of reliability failure

When reliability fails, the parser emits a `ParseResult` with:

```text
status_candidate = failed
blocks = ()   # no usable blocks
gaps = bounded gaps that could be reliably located, or () if none
diagnostics = safe parser diagnostics explaining the failure stage
```

No confidence score, percentage, or AI risk score is used.

---

## I. Diagnostics Design

Parser diagnostics are structured, bounded, stable, and source-content-free.

### I.1 Proposed bounded diagnostic codes

| Code | Stage | Meaning |
| --- | --- | --- |
| `DOCX_ARCHIVE_INVALID` | archive | DOCX ZIP cannot be read or `word/document.xml` missing. |
| `DOCUMENT_XML_PARSE_ERROR` | document_xml | `word/document.xml` is not well-formed XML. |
| `BODY_MISSING` | body_traversal | `w:body` not found. |
| `UNKNOWN_BODY_CHILD` | body_traversal | Unrecognized body child that prevents reliable success. |
| `UNKNOWN_INLINE_STRUCTURE` | paragraph | Bounded unknown inline structure. |
| `TABLE_DETECTED` | paragraph/body | Known table gap. |
| `DRAWING_DETECTED` | paragraph | Known drawing/image gap. |
| `OMML_DETECTED` | paragraph | Known OMML gap. |
| `TEXTBOX_DETECTED` | paragraph | Known textbox gap. |
| `EMBEDDED_OBJECT_DETECTED` | paragraph | Known embedded object gap. |
| `PARSER_INTERNAL_ERROR` | parser | Unexpected parser failure; sanitized. |

### I.2 Diagnostic metadata

Allowed metadata fields:

```text
stage
source_order
structure_kind
body_child_index
gap_count
block_count
```

Forbidden metadata:

```text
source text
raw XML
DOCX bytes
image/asset bytes
storage_uri
absolute path
credentials
arbitrary exception messages
unsanitized traceback
```

Normal `success` results should have an empty diagnostics tuple or only harmless informational entries; they must not contain noise.

---

## J. Determinism Strategy

The parser must be deterministic under the same:

```text
source SHA-256
parser name/version
canonical parser config
supported runtime fingerprint
```

### J.1 Deterministic inputs

- Input is `bytes` only.
- No random values, network access, current time/date, local absolute paths, database insertion order, or uncontrolled locale/environment state.
- `ParserConfig` is canonicalized (e.g., sorted keys, explicit versions) before use.

### J.2 Library/runtime threats

- `zipfile` and `xml.etree.ElementTree` are standard-library and deterministic for the same bytes.
- ElementTree preserves document order; it does not reorder children.
- The parser must not rely on dictionary iteration order for semantic output; use explicit ordering.

### J.3 Semantic stability

Repeated parsing must produce identical:

```text
block count
block text_original
block source_order
block_type
gap count
gap type
gap source_order / source_region_kind
status_candidate
diagnostic classification
```

Run-instance metadata (UUIDs, timestamps) is excluded from parser output and left to Processing Service.

---

## K. Synthetic Fixture and Test Matrix

Fixtures must be synthetic, generated in test code as in-memory DOCX ZIPs or minimal XML strings. No real private question-bank documents may be committed.

### K.1 Fixture builders

Tests may include a small helper that builds a DOCX byte stream from:

```text
[Content_Types].xml
word/document.xml
optional word/_rels/document.xml.rels
```

This mirrors the existing upload-test pattern and keeps fixtures inspectable.

### K.2 Test matrix

| Fixture | Expected blocks | Expected gaps | Expected status | Diagnostic focus |
| --- | --- | --- | --- | --- |
| Pure paragraphs (title + 3 body) | 4 blocks, orders 1–4, exact text | 0 | success | none |
| Empty paragraph between text | 3 blocks; middle `text_original = ""` | 0 | success | none |
| Whitespace-only paragraph | 1 block with exact whitespace text | 0 | success | none |
| Tab-only paragraph | 1 block with `"\t"` | 0 | success | none |
| Manual-break-only paragraph | 1 block with `"\n"` | 0 | success | none |
| Mixed tab/break within text | 1 block with exact combined text | 0 | success | none |
| Hyperlink visible text | 1 block with visible text only | 0 | success | none |
| Heading paragraph | 1 block with heading text | 0 | success | none |
| Body-level table between paragraphs | 2 blocks, orders 1 and 3 | 1 `table` gap at order 2 | partial | `TABLE_DETECTED` |
| Drawing-only paragraph | 0 blocks | 1 `drawing` gap, within_paragraph | partial | `DRAWING_DETECTED` |
| Text + drawing + text | 1 block with surrounding text | 1 `drawing` gap | partial | `DRAWING_DETECTED` |
| OMML in paragraph | 1 block with surrounding text | 1 `omml` gap | partial | `OMML_DETECTED` |
| Two OMML occurrences in one paragraph | 1 block with surrounding text | 2 `omml` gaps, same `source_order` | partial | `OMML_DETECTED` |
| Textbox in paragraph | 1 block with surrounding text | 1 `textbox` gap | partial | `TEXTBOX_DETECTED` |
| Two drawings in one paragraph with text | 1 block with surrounding text | 2 `drawing` gaps, same paragraph `source_order` | partial | `DRAWING_DETECTED` |
| Unknown bounded body child | blocks before/after preserved | 1 `unknown` gap | partial | `UNKNOWN_BODY_CHILD` |
| Unknown inline structure | block with supported text | 1 `unknown` gap | partial | `UNKNOWN_INLINE_STRUCTURE` |
| Paragraph with only property/bookkeeping markers | 1 block with text | 0 | success | none |
| Malformed document.xml | 0 blocks | 0 | failed | `DOCUMENT_XML_PARSE_ERROR` |
| Missing `w:body` | 0 blocks | 0 | failed | `BODY_MISSING` |
| Repeat-parse determinism | identical semantic output on second run | identical | identical | identical |

### K.3 Assertions

For each fixture, tests assert:

```text
len(blocks)
[block.source_order]
[block.text_original]
[block.block_type]
len(gaps)
[gap.gap_type]
[gap.source_order]
[gap.source_region_kind]
[gap.before_block_source_order]
[gap.after_block_source_order]
status_candidate
diagnostic codes
```

For determinism, the same bytes are parsed twice and compared field-by-field.

---

## L. Verification Plan

After future implementation, the following commands are expected to pass in the API repository:

```powershell
# targeted parser tests
python -m pytest tests/services/test_source_processing_parser.py -q

# full test suite
python -m pytest -q

# lint
ruff check src tests

# type check
mypy src
```

The existing regression suite (`tests/api/test_paper_storage.py`, `tests/api/test_paper_docx_upload_contract.py`, etc.) must continue to pass without modification.

No verification is run now beyond read-only inspection.

---

## M. Stop Conditions

Implementation MUST STOP and return to design review if any of the following occurs:

```text
schema redesign required
Frozen Decisions conflict found
Direct OOXML route cannot satisfy B1–B9
unsupported content could be silently lost
real private source content would need to be committed or logged
Processing Service logic becomes necessary to complete the parser slice
API/React changes become necessary
OCR/image/table/formula support becomes necessary
```

---

## N. Explicit Non-Goals

This plan does NOT authorize:

```text
Parser production implementation
Processing Service implementation
database/schema migration
API endpoint changes
OpenAPI changes
React/frontend changes
WDV1-004
OCR
image extraction
table reconstruction
formula conversion
visual preview
PDF/LibreOffice/PyMuPDF work
```

No runtime behavior is created.

---

## O. Plan Gate

```text
STEP 4.4B IMPLEMENTATION PLAN = COMPLETE
IMPLEMENTATION = NOT AUTHORIZED
MERGE TO MAIN = NOT AUTHORIZED
```

Next authorized stage: Team A review of this plan, followed by Product Owner approval before any implementation begins.
