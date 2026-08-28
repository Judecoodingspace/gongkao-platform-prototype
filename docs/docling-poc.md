# Docling Visual Preview POC / Docling 可视化预览 POC

## Purpose

Use Docling as the second-stage POC tool after the basic DOCX structure check.

This POC evaluates whether Docling output can support:

- left-side source preview for human annotators;
- structured assistance for splitting stem, question, options, explanation, and images;
- image ownership decisions for stem images, A-D option images, explanation images, and option image groups.

It must not write parsed questions to the database.

## Tool

Docling is an open-source document-conversion project. Its official usage uses `DocumentConverter` as the main Python entry point and `export_to_markdown()` / `export_to_dict()` for export.

## Install

```powershell
python -m pip install docling
```

If the local environment has disabled package indexes or proxies, check:

```powershell
Get-ChildItem Env: | Where-Object { $_.Name -match 'PIP|PROXY' }
```

In an earlier Codex sandbox attempt, Docling started downloading from PyPI but installation was blocked by local temporary-file permissions. If that happens again, run the install in a normal PowerShell session where pip can write temporary files.

## Run

```powershell
python scripts\docling_poc\convert_with_docling.py docs\raw_doc --out-dir docs\docling-poc-results --write-markdown --write-json
```

The output directory is ignored by git because it may contain private exam text.

## 2026-07-22 Run Result

Command run:

```powershell
python .\scripts\docling_poc\convert_with_docling.py .\docs\raw_doc --out-dir .\docs\docling-poc-results --write-markdown --write-json
```

Local result:

| Sample | Markdown chars | Text nodes | Picture nodes | HTML exported | Markdown image links | HTML image tags |
| ------ | -------------- | ---------- | ------------- | ------------- | -------------------- | --------------- |
| Sample 1 | 39,956 | 673 | 124 | Yes | 0 | 0 |
| Sample 2 | 398,546 | 8,767 | 14 | Yes | 0 | 0 |
| Sample 3 | 1,041,686 | 22,006 | 30 | Yes | 0 | 0 |

Observed facts:

- All three local DOCX samples converted successfully.
- Docling JSON exposes `picture` nodes, and the picture nodes have `prov` provenance information.
- Markdown and HTML exports are text-readable, but neither export includes direct image links or `<img>` tags by default.
- In Sample 3, 30 picture nodes were detected; 29 include an `image` payload and one does not.
- Docling emitted image-related warnings for DrawingML export without LibreOffice and one missing VML image.
- Automated checks found A-D characters in extracted text, but not as reliable line-start option nodes. Question numbers also were not exposed as reliable line-start nodes.

Interim decision:

- Continue evaluating Docling as a structured extraction aid.
- Do not use Docling Markdown/HTML alone as the left-side visual preview for image-heavy DOCX files.
- Pair Docling with a visual preview strategy, likely LibreOffice-to-PDF/HTML or another document rendering path, before selecting the workbench preview approach.
- Treat image ownership as a parser suggestion plus mandatory human confirmation.

## Manual Inspection

For each representative sample, inspect the generated Markdown, optional HTML, and summary JSON:

- Does the reading order match the Word source?
- Are question numbers and A-D options preserved?
- Are images emitted as separate picture/image nodes?
- Can each image be assigned to stem, options, explanation, or option image group?
- Is Markdown good enough for the left-side preview, or only for structured assistance?
- Does Docling preserve enough context to support provenance fields later?

## Decision Rules

- If Docling preview is readable and image nodes are distinguishable, continue using Docling as the main parser POC path.
- If Docling structure is useful but preview fidelity is weak, pair Docling with PDF/HTML preview.
- If image ownership is ambiguous, require human confirmation in the annotation UI and store only parser suggestions.

## 2026-08-03 Environment Blocker: torch Dependency Failure

When rerunning Docling on the local machine (Python 3.13, Windows) to verify the DrawingML image rasterization path with LibreOffice configured, the Docling import chain failed before any parsing could start:

```text
OSError: [WinError 1114] 动态链接库(DLL)初始化例程失败。
Error loading "D:\python3.13\Lib\site-packages\torch\lib\c10.dll" or one of its dependencies.
```

Root cause:

- Docling 1.10.0 imports `torch` via the `pipeline_options_vlm_model` → `transformers` → `torch` chain.
- The installed `torch` 2.13.0 fails to load `c10.dll` on Python 3.13 / Windows in this environment.
- This blocks `import docling` entirely; the DrawingML rasterization path cannot be exercised until torch is repaired.

Decision:

- Do not attempt to downgrade or repair torch in this POC session. The stability of torch on Python 3.13 / Windows is out of scope for the current POC.
- The Docling POC script (`scripts/docling_poc/convert_with_docling.py`) and its existing JSON outputs under `docs/docling-poc-results/` remain as historical artifacts.
- The DocumentBlock POC has switched its input source to LibreOffice PDF. See `docs/libreoffice-poc.md` section "2026-08-03 PDF as DocumentBlock Source" and `REVIEW_LOG.md` entry `REV-20260803-01` for the full decision and scope.
- If torch is repaired in a future environment, Docling can be re-evaluated as an alternative input source. The `build_from_docling()` function in `scripts/document_block_poc/build_document_blocks.py` is preserved for that case.

---

# Docling 可视化预览 POC

## 目的

在第一阶段 DOCX 基础结构统计之后，用 Docling 作为第二阶段 POC 工具。

这个 POC 验证 Docling 输出是否能支持：

- 给录题员看的左侧原文预览；
- 辅助拆解题干、问题、选项、解析和图片；
- 判断图片属于题干、A-D 选项、解析，还是选项图片组。

它不能把解析后的题目写入数据库。

## 工具

Docling 是开源文档转换项目。官方用法中，`DocumentConverter` 是主要 Python 入口，可通过 `export_to_markdown()` 和 `export_to_dict()` 导出结果。

## 安装

```powershell
python -m pip install docling
```

如果本地环境禁用了包索引或配置了代理，先检查：

```powershell
Get-ChildItem Env: | Where-Object { $_.Name -match 'PIP|PROXY' }
```

之前在 Codex 沙箱中，Docling 已能从 PyPI 开始下载，但安装被本地临时文件权限拦住。如果再次遇到这个问题，建议在普通 PowerShell 环境中运行安装命令。

## 运行

```powershell
python scripts\docling_poc\convert_with_docling.py docs\raw_doc --out-dir docs\docling-poc-results --write-markdown --write-json
```

输出目录已被 git 忽略，因为其中可能包含私有真题正文。

## 2026-07-22 运行结果

已运行命令：

```powershell
python .\scripts\docling_poc\convert_with_docling.py .\docs\raw_doc --out-dir .\docs\docling-poc-results --write-markdown --write-json
```

本地结果：

| 样本 | Markdown 字符数 | 文本节点 | 图片节点 | 已导出 HTML | Markdown 图片链接 | HTML 图片标签 |
| ---- | --------------- | -------- | -------- | ----------- | ----------------- | ------------- |
| 样本 1 | 39,956 | 673 | 124 | 是 | 0 | 0 |
| 样本 2 | 398,546 | 8,767 | 14 | 是 | 0 | 0 |
| 样本 3 | 1,041,686 | 22,006 | 30 | 是 | 0 | 0 |

观察结论：

- 三份本地 DOCX 样本均转换成功。
- Docling JSON 能输出 `picture` 节点，且图片节点带有 `prov` 来源信息。
- Markdown 和 HTML 导出具备文本可读性，但默认导出中没有直接图片链接或 `<img>` 标签。
- 样本 3 检测到 30 个图片节点，其中 29 个带 `image` 载荷，1 个不带。
- Docling 对图片输出了相关警告：未配置 LibreOffice 时无法导出部分 DrawingML 内容，并提示有 VML 图片找不到。
- 自动检查能在文本中找到 A-D 字符，但不能稳定识别为行首选项节点；题号也没有稳定暴露为行首题号节点。

阶段性判断：

- Docling 可以继续作为结构化抽取辅助。
- 对含图较多的 DOCX，不能只用 Docling Markdown/HTML 作为左侧视觉预览。
- 在确定工作台预览方案前，应继续验证 Docling + LibreOffice 转 PDF/HTML 或其他文档渲染路径。
- 图片归属只能作为解析器建议，最终必须由人工确认。

## 人工检查

对每份代表性样本，检查生成的 Markdown、可选 HTML 和 summary JSON：

- 阅读顺序是否与 Word 原文一致？
- 题号和 A-D 选项是否保留？
- 图片是否作为独立 picture/image 节点出现？
- 每张图片能否归属到题干、选项、解析或选项图片组？
- Markdown 是否足够作为左侧预览，还是只能作为结构化辅助？
- Docling 是否保留了后续来源追溯所需的上下文？

## 决策规则

- 如果 Docling 预览可读，且图片节点可区分，则继续把 Docling 作为主解析 POC 路线。
- 如果 Docling 结构有用但预览保真不足，则采用 Docling + PDF/HTML 预览的混合方案。
- 如果图片归属不明确，则 UI 中必须要求人工确认，数据库只保存解析器建议。

## 2026-08-03 环境阻塞：torch 依赖损坏

在本机（Python 3.13，Windows）重新运行 Docling 以验证配置 LibreOffice 后的 DrawingML 图片栅格化路径时，Docling 的 import 链在解析开始前就失败：

```text
OSError: [WinError 1114] 动态链接库(DLL)初始化例程失败。
Error loading "D:\python3.13\Lib\site-packages\torch\lib\c10.dll" or one of its dependencies.
```

根因：

- Docling 1.10.0 通过 `pipeline_options_vlm_model` → `transformers` → `torch` 链路导入 `torch`。
- 本机安装的 `torch` 2.13.0 在 Python 3.13 / Windows 环境下加载 `c10.dll` 失败。
- 这会阻塞 `import docling`，在 torch 修复前无法走 DrawingML 栅格化路径。

决策：

- 本次 POC 不尝试降级或修复 torch。torch 在 Python 3.13 / Windows 上的稳定性超出当前 POC 范围。
- Docling POC 脚本（`scripts/docling_poc/convert_with_docling.py`）和 `docs/docling-poc-results/` 下的现有 JSON 产物保留为历史存档。
- DocumentBlock POC 的输入源已切换到 LibreOffice PDF。完整决策和范围见 `docs/libreoffice-poc.md` "2026-08-03 PDF as DocumentBlock Source" 段落和 `REVIEW_LOG.md` 条目 `REV-20260803-01`。
- 未来环境修复 torch 后，可重新评估 Docling 作为备选输入源。`scripts/document_block_poc/build_document_blocks.py` 中的 `build_from_docling()` 函数已保留以支持该场景。
