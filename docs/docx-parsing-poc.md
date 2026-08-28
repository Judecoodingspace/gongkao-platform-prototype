# DOCX Parsing POC / DOCX 解析 POC

## Purpose

This POC checks whether representative civil-service exam DOCX files can support the annotation workbench preview before a backend parser is designed.

It is not a production parser and does not write parsed questions into the database.

## What It Verifies

- Whether the DOCX can be opened as a valid Office Open XML package.
- Whether text blocks can be read in document order.
- Whether tables are present and need visual fidelity checks.
- Whether embedded images and media files can be detected.
- Whether each sample should be handled by simple DOCX-to-HTML parsing or a stronger document pipeline.

## What It Does Not Do

- It does not split questions automatically.
- It does not infer answers, explanations, difficulty, province, year, type, or knowledge points.
- It does not upload images, store files, or write to PostgreSQL.
- It does not output full private exam text by default.

## Command

```powershell
python scripts\docx_poc\extract_docx_summary.py docs\raw_doc --out-dir docs\docx-poc-results
```

Use `--include-snippets` only for non-private fixtures because it writes short text snippets to JSON.

## Acceptance Checklist

- At least three representative DOCX files can be summarized without parser failure.
- The summary reports paragraph, table, image, and media counts.
- Files with tables are flagged for visual preview checks.
- Files with images are flagged for image ownership checks.
- Generated JSON summaries stay under `docs/docx-poc-results/`, which is ignored by git.
- The POC result is used to decide the next parser path: Mammoth-style HTML conversion, Docling-style structured extraction, LibreOffice/PDF preview, or a hybrid.

---

# DOCX 解析 POC

## 目的

这个 POC 用来在正式设计后端解析器之前，验证真实公务员/事业单位考试 DOCX 文件是否能够支撑录题工作台的左侧预览。

它不是生产解析器，也不会把解析后的题目写入数据库。

## 验证内容

- DOCX 是否能作为合法的 Office Open XML 包打开。
- 文本块是否能按文档顺序读取。
- 是否存在表格，以及是否需要额外做视觉保真检查。
- 是否能检测到嵌入图片和媒体文件。
- 判断样本更适合简单 DOCX 转 HTML、Docling 结构化解析、LibreOffice/PDF 预览，还是混合方案。

## 不做的事情

- 不自动拆题。
- 不推断答案、解析、难度、省份、年份、题型或知识点。
- 不上传图片、不存储文件、不写入 PostgreSQL。
- 默认不输出完整私有真题文本。

## 运行命令

```powershell
python scripts\docx_poc\extract_docx_summary.py docs\raw_doc --out-dir docs\docx-poc-results
```

只有在使用非私有测试样本时，才建议加 `--include-snippets`，因为它会把短文本片段写入 JSON。

## 验收清单

- 至少三份代表性 DOCX 文件可以完成摘要解析，不报错。
- 摘要结果包含段落、表格、图片和媒体文件数量。
- 含表格文件会被标记为需要视觉保真检查。
- 含图片文件会被标记为需要图片归属检查。
- 生成的 JSON 摘要保存在 `docs/docx-poc-results/`，并被 git 忽略。
- POC 结果用于决定下一步解析路线：Mammoth 风格 HTML 转换、Docling 风格结构化抽取、LibreOffice/PDF 预览，或混合方案。
