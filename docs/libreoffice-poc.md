# LibreOffice Visual Rendering POC / LibreOffice 可视化渲染 POC

## Purpose

Use LibreOffice headless conversion to evaluate whether DOCX files can be rendered into a visual preview that is close enough to the original Word document for human annotation.

This POC focuses on visual rendering, not question parsing.

It must not:

- split questions automatically;
- infer answers, explanations, difficulty, province, year, type, or knowledge points;
- write parsed content into the question bank;
- commit private generated outputs to GitHub.

## Tool Role

LibreOffice and FastAPI solve different problems:

- LibreOffice renders DOC/DOCX files into PDF, HTML, or other visual formats.
- FastAPI would later expose upload, parsing, preview, and annotation APIs.
- A future FastAPI service may call LibreOffice in a sandboxed background worker, but FastAPI itself is not a document renderer.

## Install

Install LibreOffice locally, then make sure `soffice` is available on `PATH`, or pass its path explicitly:

```powershell
python scripts\libreoffice_poc\convert_with_libreoffice.py docs\raw_doc --soffice "C:\Program Files\LibreOffice\program\soffice.exe"
```

## Run

PDF-only check:

```powershell
python scripts\libreoffice_poc\convert_with_libreoffice.py docs\raw_doc --out-dir docs\libreoffice-poc-results --format pdf
```

PDF plus HTML check:

```powershell
python scripts\libreoffice_poc\convert_with_libreoffice.py docs\raw_doc --out-dir docs\libreoffice-poc-results --format pdf --format html
```

The output directory is ignored by git because it may contain private exam content.

## 2026-07-22 Local Check Result

Checks run:

```powershell
python -m py_compile .\scripts\libreoffice_poc\convert_with_libreoffice.py
python .\scripts\libreoffice_poc\convert_with_libreoffice.py --help
python .\scripts\libreoffice_poc\convert_with_libreoffice.py .\docs\raw_doc --out-dir .\docs\libreoffice-poc-results --format pdf --format html
```

Observed result:

- The POC script compiles successfully.
- The command-line help works.
- Three local DOCX samples are present under `docs/raw_doc/`.
- Actual conversion is blocked because LibreOffice is not currently available as `soffice` / `libreoffice` and was not found at the common Windows install path.

Current blocker:

```text
LibreOffice was not found.
Install LibreOffice, or rerun with --soffice pointing to soffice.exe.
Common Windows path: C:\Program Files\LibreOffice\program\soffice.exe
```

Next action:

- Install LibreOffice locally, or provide the exact `soffice.exe` path.
- Rerun the PDF plus HTML command.
- Inspect generated PDF/HTML before deciding whether LibreOffice can serve as the left-side visual preview path.

## 2026-07-22 Manual Conversion Result

After LibreOffice was installed locally, the conversion command completed successfully with the explicit `soffice.exe` path:

```powershell
python .\scripts\libreoffice_poc\convert_with_libreoffice.py .\docs\raw_doc --out-dir .\docs\libreoffice-poc-results --format pdf --format html --soffice "C:\Program Files\LibreOffice\program\soffice.exe"
```

Local artifact summary:

| Sample | PDF files | PDF size | PDF pages | HTML files | HTML size | Top-level image assets | HTML `<img>` tags |
| ------ | --------- | -------- | --------- | ---------- | --------- | ---------------------- | ----------------- |
| Sample 1 | 1 | 1.27 MB | 43 | 1 | 755 KB | 103 | 0 |
| Sample 2 | 1 | 8.11 MB | 956 | 1 | 2.26 MB | 14 | 0 |
| Sample 3 | 1 | 31.77 MB | 2,609 | 1 | 6.81 MB | 21 | 0 |

Observed facts:

- All three representative DOCX samples produced both PDF and HTML outputs.
- PDF output is available for page-based visual preview inspection.
- HTML output exists and generated image asset files, but automated checks did not find direct `<img>` tags in the HTML files.
- The generated artifacts remain under `docs/libreoffice-poc-results/`, which is ignored by git.

Interim decision:

- LibreOffice is viable enough to continue as the visual-rendering POC path.
- PDF should be inspected first as the likely left-side visual preview candidate.
- HTML needs manual browser inspection before treating it as a selectable-text preview candidate.
- Final preview strategy is still not decided until visual fidelity is checked against the original Word files.

## 2026-07-22 Manual Inspection Result

The generated PDF and HTML were manually compared with the original DOCX samples.

Manual finding:

- The LibreOffice-generated PDF and HTML can correspond to the original DOCX layout for the current representative samples.

Updated interim decision:

- Continue with PDF as the first left-side visual preview candidate.
- Keep HTML as a secondary candidate for selectable-text and browser-native preview experiments.
- Do not treat visual correspondence as automatic question splitting. Parsing and field assignment still need separate validation and human confirmation.

## 2026-07-22 PDF Preview Integration POC

The static annotation prototype now includes a PDF preview mode in the left source-paper panel:

- switch between simulated source blocks and PDF preview;
- load a local LibreOffice-generated PDF with a file picker;
- set page number and zoom through PDF viewer hash parameters;
- record manual source binding notes for stem, question, options, explanation, or option image group;
- update the footer source chip with the selected PDF page and field.

Scope boundary:

- This is a prototype-level integration POC.
- The browser-native PDF preview is used for visual inspection only.
- The prototype does not extract text from the PDF.
- The PDF source binding record is a UI placeholder for a future `SourceSpan`; it is not a production data model implementation.
- Generated PDF files remain local and git-ignored.

Next validation:

- Open `prototypes/question-bank-prototype/index.html`.
- Switch the source-paper panel to `PDF`.
- Select one generated PDF under `docs/libreoffice-poc-results/`.
- Check whether page navigation, zoom, and source binding notes are ergonomic enough for annotators.
- Decide whether the next POC should use browser-native PDF, PDF page images, or PDF.js for stronger page/selection control.

Prototype checks run:

- Static HTML parse completed.
- Required PDF preview elements and functions are present.
- Desktop screenshots were captured for PDF mode at 1440 x 900 and 1280 x 720.
- The first 1280 x 720 screenshot showed the PDF control row was too wide; the controls were adjusted to wrap into two columns below 1366 px.
- The follow-up 1280 x 720 screenshot showed no obvious control overlap in the unloaded PDF state.
- Manual testing found that selecting a PDF could update the file name while leaving the embedded preview blank in some local browser contexts.
- The prototype now uses `object` / `embed` for browser-native PDF rendering, loads the embedded preview with the plain local blob URL, and exposes a visible `Open PDF` fallback button using the page/zoom URL fragment.

## 2026-07-23 Preview and Copy Separation

Manual prototype review confirmed that the PDF preview can be browsed normally, but using browser PDF text selection as the primary copy source can introduce line breaks and paragraph cleanup work for annotators.

Current decision:

- Keep LibreOffice PDF as a high-fidelity visual reference candidate.
- Do not rely on PDF copy/paste as the main annotation input path.
- Use a controlled source-text layer, such as `DocumentBlock` candidates from DOCX/Docling/other parsers, for selectable text insertion and future `SourceSpan` mapping.
- Treat DOCX-derived visual rendering, source text extraction, and structured field assignment as separate layers.

The prototype now adds a right-side current-question switcher above the structured entry form. It shows the current question ID, draft status, field completeness, source summary, previous/next controls, existing draft tabs, and a new-question action.

## 2026-07-23 DOCX HTML Preview Integration

The static prototype replaced the browser-native PDF preview path with a DOCX-derived HTML preview candidate:

- the source-paper panel now records the original DOCX file separately from the LibreOffice-generated HTML preview file;
- the embedded preview uses the selected local HTML file in an iframe;
- the old PDF page, zoom, and positioning controls were removed because manual testing showed they could not provide reliable field-level positioning;
- the source-block mode button was removed; source blocks are now shown as an always-visible "copyable text blocks" area under the visual preview;
- the explanation panel now has matching DOCX and HTML preview controls.

Scope boundary:

- This does not mean the browser can natively render DOCX.
- The current prototype expects a local HTML preview generated by LibreOffice or a future backend conversion service.
- The copyable text block area remains a prototype sidecar for controlled copy/fill workflows, not a production parser result.
- Field-level provenance still requires future `DocumentBlock` / `SourceSpan` mapping.

## Manual Inspection

For each representative sample, inspect the generated PDF or HTML locally:

- Does the preview visually match Word reading order?
- Are embedded images visible?
- Are images close to the original surrounding text?
- Are question numbers and A-D options readable?
- Is the output suitable as the left-side annotation preview?
- Can this visual output be paired with Docling source nodes for provenance?

## Decision Rules

- If PDF rendering is visually faithful, use PDF or page images as the primary left-side visual preview candidate.
- If HTML rendering preserves images and text order well enough, evaluate HTML preview for selectable text and browser integration.
- If selectable text from PDF/HTML introduces formatting cleanup cost, prefer parser-produced source blocks as the copy/input layer.
- If LibreOffice visual output is good but source-node mapping is weak, pair LibreOffice preview with Docling JSON for structured `DocumentBlock` candidates.
- If visual output is poor on representative samples, evaluate alternative rendering paths before implementing production upload APIs.

## 2026-08-03 PDF as DocumentBlock Source

Starting from 2026-08-03, the DocumentBlock POC can build `document-blocks.json` directly from a LibreOffice-generated PDF, in addition to the original Docling JSON path. This route was introduced after Docling's `torch` dependency failed on the local Python 3.13 environment and after manual verification confirmed that LibreOffice-rendered PDFs preserve formula images that Docling turned into 24x11 placeholder images.

Background:

- Word documents in this corpus embed some formula content as images wrapped in DrawingML/VML elements.
- Docling's `MsWordDocumentBackend` rasterizes DrawingML via LibreOffice. Without `DOCLING_LIBREOFFICE_CMD` or soffice on PATH, it emits a uniform 24x11 placeholder image instead of the real picture.
- Even after configuring LibreOffice for Docling, `import docling` fails on this machine due to `torch` / `c10.dll` load failure (`WinError 1114`). See `docs/docling-poc.md` section "2026-08-03 Environment Blocker".
- LibreOffice headless conversion of the same DOCX to PDF preserves all formula images (manually verified for Sample 1, question 46 method 2).

Run:

```powershell
# 1. Convert DOCX to PDF with LibreOffice (if not already done).
python scripts\libreoffice_poc\convert_with_libreoffice.py docs\raw_doc --out-dir docs\libreoffice-poc-results --format pdf --soffice "C:\Program Files\LibreOffice\program\soffice.exe"

# 2. Build document-blocks.json from the PDF.
python scripts\document_block_poc\build_document_blocks.py --from-pdf "docs\libreoffice-poc-results\01-...\sample.pdf" --out-dir docs\document-block-poc-results --image-limit 50
```

Install PyMuPDF first (it is not bundled with the project):

```powershell
python -m pip install pymupdf
```

Schema:

- Output JSON uses `schema: "document_blocks_poc.v2"` and adds a `source_format` field (`docling` or `libreoffice-pdf`) so downstream tooling can distinguish the input route.
- Text blocks carry `page_no` and `bbox` (top-left origin) provenance, which is more complete than the empty `prov: []` produced by the current Docling run.
- Image blocks are extracted via `page.get_images()` + `doc.extract_image(xref)` and deduplicated by xref across the whole document. Each image block stores a real `data:image/...;base64,...` URI instead of a placeholder.

Scope boundary:

- This is a POC-level input source. It does not auto-split questions, infer answers, or assign images to stem/option/explanation. Image ownership is still confirmed by the annotator in the workbench.
- The Docling route (`build_from_docling`) is preserved in the same script for future re-evaluation once torch is repaired.
- Full decision, root-cause analysis, and verification plan are recorded in `REVIEW_LOG.md` entry `REV-20260803-01`.

## Security Notes

Uploaded exam documents are untrusted input. A production worker must run LibreOffice with:

- headless mode;
- isolated temporary user profile;
- timeout limits;
- no macro execution or active-content trust;
- private output directories;
- logs that avoid full paper text, answer keys, and generated private content.

---

# LibreOffice 可视化渲染 POC

## 目的

用 LibreOffice headless 转换验证 DOCX 是否能渲染成接近 Word 原貌的视觉预览，供后续人工拆题工作台左侧预览参考。

这个 POC 只验证视觉渲染，不做正式拆题解析。

它不能：

- 自动拆题；
- 推断答案、解析、难度、省份、年份、题型或知识点；
- 把解析内容写入题库；
- 把包含私有真题内容的生成结果提交到 GitHub。

## 工具定位

LibreOffice 和 FastAPI 不是同一类工具：

- LibreOffice 负责把 DOC/DOCX 渲染成 PDF、HTML 或其他视觉格式。
- FastAPI 后续负责上传、解析任务、预览地址和人工标注 API。
- 未来 FastAPI 服务可以在隔离后台任务中调用 LibreOffice，但 FastAPI 本身不是文档渲染器。

## 安装

本机安装 LibreOffice 后，确认 `soffice` 在 `PATH` 中，或显式传入路径：

```powershell
python scripts\libreoffice_poc\convert_with_libreoffice.py docs\raw_doc --soffice "C:\Program Files\LibreOffice\program\soffice.exe"
```

## 运行

只检查 PDF：

```powershell
python scripts\libreoffice_poc\convert_with_libreoffice.py docs\raw_doc --out-dir docs\libreoffice-poc-results --format pdf
```

同时检查 PDF 和 HTML：

```powershell
python scripts\libreoffice_poc\convert_with_libreoffice.py docs\raw_doc --out-dir docs\libreoffice-poc-results --format pdf --format html
```

输出目录已被 git 忽略，因为其中可能包含私有真题内容。

## 2026-07-22 本地检查结果

已运行检查：

```powershell
python -m py_compile .\scripts\libreoffice_poc\convert_with_libreoffice.py
python .\scripts\libreoffice_poc\convert_with_libreoffice.py --help
python .\scripts\libreoffice_poc\convert_with_libreoffice.py .\docs\raw_doc --out-dir .\docs\libreoffice-poc-results --format pdf --format html
```

观察结果：

- POC 脚本语法检查通过。
- 命令行帮助可正常输出。
- `docs/raw_doc/` 下有 3 个本地 DOCX 样本。
- 实际转换被环境阻塞：当前找不到 `soffice` / `libreoffice` 命令，也没有找到常见 Windows 安装路径。

当前阻塞：

```text
LibreOffice was not found.
Install LibreOffice, or rerun with --soffice pointing to soffice.exe.
Common Windows path: C:\Program Files\LibreOffice\program\soffice.exe
```

下一步：

- 本机安装 LibreOffice，或提供准确的 `soffice.exe` 路径。
- 重新运行 PDF + HTML 转换命令。
- 人工检查生成的 PDF/HTML 后，再判断 LibreOffice 是否适合作为左侧视觉预览路径。

## 2026-07-22 手动转换结果

本机安装 LibreOffice 后，使用显式 `soffice.exe` 路径运行转换命令成功：

```powershell
python .\scripts\libreoffice_poc\convert_with_libreoffice.py .\docs\raw_doc --out-dir .\docs\libreoffice-poc-results --format pdf --format html --soffice "C:\Program Files\LibreOffice\program\soffice.exe"
```

本地产物摘要：

| 样本 | PDF 文件 | PDF 大小 | PDF 页数 | HTML 文件 | HTML 大小 | 顶层图片资源 | HTML `<img>` 标签 |
| ---- | -------- | -------- | -------- | --------- | --------- | ------------ | ----------------- |
| 样本 1 | 1 | 1.27 MB | 43 | 1 | 755 KB | 103 | 0 |
| 样本 2 | 1 | 8.11 MB | 956 | 1 | 2.26 MB | 14 | 0 |
| 样本 3 | 1 | 31.77 MB | 2,609 | 1 | 6.81 MB | 21 | 0 |

观察结论：

- 三份代表性 DOCX 样本均生成了 PDF 和 HTML。
- PDF 已可用于页面级视觉预览检查。
- HTML 已生成并带有图片资源文件，但自动检查没有在 HTML 文件中发现直接 `<img>` 标签。
- 生成结果仍保存在被 git 忽略的 `docs/libreoffice-poc-results/` 中。

阶段性判断：

- LibreOffice 可以继续作为视觉渲染 POC 路线。
- 应优先人工检查 PDF，判断其是否适合作为左侧原文视觉预览候选。
- HTML 还需要用浏览器人工检查，再判断是否适合作为可选择文本预览候选。
- 最终预览方案仍需等视觉保真度与原 Word 对照检查后再决定。

## 2026-07-22 人工检查结果

已将生成的 PDF 和 HTML 与原始 DOCX 样本进行人工对照。

人工结论：

- 当前代表性样本中，LibreOffice 生成的 PDF 和 HTML 能够与原 DOCX 版式对应。

更新后的阶段性判断：

- 下一步可以把 PDF 作为左侧视觉预览第一候选继续验证。
- HTML 可作为可选择文本和浏览器原生预览的第二候选继续实验。
- 视觉对应不等于可以自动拆题；拆题和字段归属仍需要单独验证，并且必须人工确认。

## 2026-07-22 PDF 预览集成 POC

静态拆题原型的左侧题本面板已新增 PDF 预览模式：

- 支持在模拟原文块和 PDF 预览之间切换；
- 支持选择本地 LibreOffice 生成的 PDF；
- 支持通过页码和缩放参数定位 PDF 视图；
- 支持为题干、问题、选项、解析或选项图片组记录人工来源绑定备注；
- 支持把底部来源 chip 更新为当前 PDF 页码和字段。

范围边界：

- 这是原型级集成 POC。
- 浏览器原生 PDF 预览只用于视觉检查。
- 原型不会从 PDF 中抽取文本。
- PDF 来源绑定记录只是未来 `SourceSpan` 的 UI 占位，不是生产数据模型实现。
- 生成的 PDF 文件仍只保存在本地忽略目录中。

下一步验证：

- 打开 `prototypes/question-bank-prototype/index.html`。
- 将题本面板切换到 `PDF`。
- 选择 `docs/libreoffice-poc-results/` 下的一个生成 PDF。
- 检查页码、缩放和来源绑定备注对标注员是否顺手。
- 决定下一轮 POC 使用浏览器原生 PDF、PDF 页面图片，还是 PDF.js 以获得更强的页码/选择控制。

已运行的原型检查：

- 静态 HTML 解析通过。
- PDF 预览相关元素和函数均存在。
- 已在 1440 x 900 和 1280 x 720 下截取 PDF 模式桌面截图。
- 第一张 1280 x 720 截图显示 PDF 控制栏过宽，因此已将 1366 px 以下的控件调整为两列换行。
- 修正后的 1280 x 720 截图中，未加载 PDF 状态下未见明显控件重叠。
- 人工测试发现，部分本地浏览器环境中选择 PDF 后文件名会更新，但内嵌预览区域可能为空白。
- 原型已改为使用 `object` / `embed` 调用浏览器原生 PDF 渲染，内嵌预览使用纯本地 blob URL，并新增可见的“打开 PDF”兜底按钮，页码/缩放参数用于新标签打开链接和来源记录。

## 2026-07-23 预览与复制分层

人工评审确认 PDF 预览已经可以正常浏览，但如果把浏览器 PDF 文本选择作为主要复制来源，复制结果可能带入换行和分段整理成本。

当前决策：

- 保留 LibreOffice PDF 作为高保真视觉参照候选。
- 不依赖 PDF 复制粘贴作为主要录入路径。
- 可复制文本和未来 `SourceSpan` 映射优先来自可控的来源文本层，例如 DOCX/Docling/其他解析器生成的 `DocumentBlock` 候选。
- DOCX 衍生视觉渲染、来源文本抽取、结构化字段归属必须分层处理。

静态原型已在右侧结构化录入表单上方增加当前题切换条，展示当前题 ID、草稿状态、字段完整度、来源摘要，并支持上一题、下一题、已录草稿切换和新建题目。

## 2026-07-23 DOCX HTML 预览集成

静态原型已将浏览器原生 PDF 预览路径替换为 DOCX 衍生 HTML 预览候选：

- 题本面板现在分别记录原始 DOCX 文件和 LibreOffice 生成的 HTML 预览文件；
- 内嵌预览通过 iframe 加载本地 HTML 预览文件；
- 已移除旧的 PDF 页码、缩放和定位控件，因为人工测试表明它们无法提供可靠的字段级定位；
- 已移除“原文块”模式按钮，原文块改为视觉预览下方始终可见的“可复制文本块”区域；
- 解析面板也新增了对应的 DOCX 和 HTML 预览控件。

范围边界：

- 这不代表浏览器可以原生渲染 DOCX。
- 当前原型需要选择由 LibreOffice 或后续后端转换服务生成的 HTML 预览文件。
- 可复制文本块仍是受控复制/填入流程的原型辅助层，不是生产解析结果。
- 字段级来源追溯仍需要后续 `DocumentBlock` / `SourceSpan` 映射。

## 人工检查

对每份代表性样本，在本地打开生成的 PDF 或 HTML：

- 预览阅读顺序是否接近 Word 原文？
- 嵌入图片是否可见？
- 图片是否接近原文中的上下文位置？
- 题号和 A-D 选项是否可读？
- 是否适合作为拆题工作台左侧预览？
- 能否与 Docling 来源节点配合支持来源追溯？

## 决策规则

- 如果 PDF 渲染足够保真，则把 PDF 或页面图片作为左侧原文视觉预览候选。
- 如果 HTML 渲染能较好保留图片和文本顺序，则继续评估 HTML 预览的文本选择和浏览器集成。
- 如果从 PDF/HTML 选择文本会带来较高格式整理成本，则优先使用解析器生成的原文块作为复制/填入层。
- 如果 LibreOffice 视觉输出好但来源节点映射弱，则采用 LibreOffice 预览 + Docling JSON 结构候选的混合方案。
- 如果代表性样本视觉输出较差，先评估其他渲染路径，不进入正式上传 API 开发。

## 2026-08-03 PDF 作为 DocumentBlock 数据源

从 2026-08-03 起，DocumentBlock POC 可以直接从 LibreOffice 生成的 PDF 构建 `document-blocks.json`，作为原有 Docling JSON 路线的替代。引入这条路线的原因是：Docling 的 `torch` 依赖在本机 Python 3.13 环境下损坏，且人工验证确认 LibreOffice 渲染的 PDF 保留了 Docling 被替换为 24×11 占位图的公式图片。

背景：

- 本题库中的 Word 文档，部分公式内容以图片形式嵌入，被 Word 用 DrawingML/VML 元素包装。
- Docling 的 `MsWordDocumentBackend` 通过 LibreOffice 栅格化 DrawingML。未设置 `DOCLING_LIBREOFFICE_CMD` 或 PATH 中没有 soffice 时，会输出统一的 24×11 占位图代替真实图片。
- 即使为 Docling 配置 LibreOffice，本机 `import docling` 仍因 `torch` / `c10.dll` 加载失败（`WinError 1114`）而无法启动。详见 `docs/docling-poc.md` "2026-08-03 环境阻塞" 段落。
- 用 LibreOffice headless 把同一份 DOCX 转 PDF，公式图片完整保留（已对样本 1 第 46 题方法二人工对照验证）。

运行：

```powershell
# 1. 用 LibreOffice 把 DOCX 转 PDF（如尚未生成）。
python scripts\libreoffice_poc\convert_with_libreoffice.py docs\raw_doc --out-dir docs\libreoffice-poc-results --format pdf --soffice "C:\Program Files\LibreOffice\program\soffice.exe"

# 2. 从 PDF 构建 document-blocks.json。
python scripts\document_block_poc\build_document_blocks.py --from-pdf "docs\libreoffice-poc-results\01-...\sample.pdf" --out-dir docs\document-block-poc-results --image-limit 50
```

首次使用前需安装 PyMuPDF（项目未内置）：

```powershell
python -m pip install pymupdf
```

Schema：

- 输出 JSON 使用 `schema: "document_blocks_poc.v2"`，新增 `source_format` 字段（`docling` 或 `libreoffice-pdf`）以便下游区分输入路线。
- 文本块带 `page_no` 和 `bbox`（左上角原点）来源信息，比当前 Docling 运行产出的空 `prov: []` 更完整。
- 图片块通过 `page.get_images()` + `doc.extract_image(xref)` 抽取，按 xref 在整篇文档内去重。每个图片块保存真实的 `data:image/...;base64,...` URI，不再是占位图。

范围边界：

- 这是 POC 级输入源。它不会自动拆题、推断答案，也不会把图片归属到题干/选项/解析。图片归属仍由标注员在工作台人工确认。
- Docling 路线（`build_from_docling`）在同一脚本中保留，未来 torch 修复后可重新评估。
- 完整决策、根因分析和验证计划记录在 `REVIEW_LOG.md` 条目 `REV-20260803-01`。

## 安全说明

上传考试文档属于不可信输入。生产环境中的 LibreOffice worker 必须满足：

- headless 模式；
- 独立临时用户配置目录；
- 超时限制；
- 不信任宏或主动内容；
- 私有输出目录；
- 日志中避免完整试卷正文、答案和生成的私有内容。
