# 传题系统临时可点击原型

## 当前 V1 试行范围

当前入口实现的是纯文本题录入 POC，而不是完整图文录题工作台：

- 左侧题本和解析使用本地选择的 LibreOffice 衍生 HTML，只读展示且可复制文字。
- 右侧题干、问题、选项 A-D 和解析使用受限 wangEditor；只开放基础文字和段落格式，不提供图片、视频、表格、外链或任意 HTML 插入。
- 网络无法加载 wangEditor CDN 时，页面自动保留可编辑的纯文本框，操作员仍可完成验证。
- 含公式图、图形、统计图、表格截图、图片选项和图文混排的题目不进入 V1；相关 `DocumentBlock` / `ContentBlock` POC 代码和数据模型保留给 V2。
- 原型只在浏览器内保存模拟状态，不上传文件、不写数据库、不代表审核通过。
- 点击“申论”后，页面进入主观题模式：隐藏行测类型、A-D 选项和正确答案；题干、要求、问题、参考答案分别使用独立编辑器；使用归纳概括、提出对策、综合分析、应用文写作、大作文五个专项作为受控知识点，并按专项内题序导航。

入口文件：`index.html`

## 对应草图结构

- 顶部：系统标题、当前题号、预览、提交审核。
- 左侧上半区：题本 DOCX 上传、DOCX 衍生 HTML 预览、来源绑定、可复制文本块。
- 左侧下半区：解析 DOCX 上传、解析 HTML 预览、同版匹配、当前解析摘录。
- 右侧主区：当前题号预览、题目切换、题目结构化录入，包括科目、类型、知识点、年份、省份、难度、题干、问题、选项、附图、答案、解析。
- 最右侧：纵向流程提示，包括上传题本、拆解题干、补全选项、审核入库。

## 已实现的临时交互

- 点击"上传文件"会模拟填入题本/解析文件名。
- 点击左侧原文块会切换当前来源定位。
- 左侧题本区使用 DOCX 衍生 HTML 预览候选，不再保留 PDF 页码/缩放定位控件。
- 题本 DOCX 与预览 HTML 分开选择：DOCX 用于标记源文件，HTML 预览用于浏览器内只读对照。
- 题本区使用连续页面来源预览，文字、公式图片和普通图片按页面坐标共同显示；该预览仍是原型模拟，不等同于生产解析结果。
- 题本区顶部支持选择本地 `DocumentBlock` JSON，控件位于 DOCX/HTML 选择行下方、预览框上方；加载后会用真实解析块替换左侧模拟来源块。真实解析输出应保存在 `docs/document-block-poc-results/` 等 git ignored 目录。
- 解析区支持选择解析 DOCX 和解析预览 HTML，并在左下区域进行对照。
- 右侧录入区标题下方支持查看当前题位、字段完整度、来源摘要，并按题位顺序上一题/下一题切换。
- 右侧支持打开完整"题目列表"，按题号、草稿 ID、来源页码搜索并自由跳转任意题位；未开始题位不会无故生成草稿 ID。
- "追加题"表示追加到题本末尾，"保存并录下一题"表示保存当前题位并进入下一顺序题位。
- 科目、类型、选项模式可以切换。
- 难度星级可以切换。
- 正确答案为 A-D 单选。
- 题干、选项 A-D、解析已增加 `content_blocks` 交互 POC：支持文本块、模拟图片块、模拟公式图块/图形块，支持新增、删除、上移、下移和标记模拟来源。
- 左侧连续页面预览支持点击、Shift 多选或拖动框选文字和图片区域；选择目标后可一次性填入题干、问题、选项 A-D 或解析，并按阅读顺序生成带 `source_span_id` 的混合 ContentBlock。
- 每个内容块字段可查看当前 JSON，整题 JSON 预览会输出 `stem_blocks`、`option_blocks` 和 `explanation_blocks`。
- 图片块仅使用 mock asset 和占位预览，不上传真实图片，不接后端，不写数据库。
- 保存草稿、提交审核会更新顶部状态、当前题状态并显示提示。

## 后续 DocumentBlock 测试流程（V2 图文题，不是 V1 主路径）

支持两条数据源路线：LibreOffice PDF（推荐）和 Docling JSON。

### 路线 A：LibreOffice PDF（推荐，公式图片保真）

1. 先把 DOCX 转成 PDF（需要本机已安装 LibreOffice）：

   ```powershell
   python scripts\libreoffice_poc\convert_with_libreoffice.py docs\raw_doc --out-dir docs\libreoffice-poc-results --format pdf --soffice "C:\Program Files\LibreOffice\program\soffice.exe"
   ```

2. 安装 PyMuPDF（首次使用时）：

   ```powershell
   python -m pip install pymupdf
   ```

3. 从 PDF 生成原型用 JSON：

   ```powershell
   python scripts\document_block_poc\build_document_blocks.py --from-pdf "docs\libreoffice-poc-results\01-...\sample.pdf" --out-dir docs\document-block-poc-results --image-limit 50
   ```

   `--image-limit` 控制图片块数量。PDF 路线下图片块是真实嵌入图片（带 data URI），不是占位图，能正确呈现 Word 中的公式图。

### 路线 B：Docling JSON（备用，当前在本机不可用）

1. 从本地 Docling POC 结果生成原型用 JSON：

   ```powershell
   python scripts\document_block_poc\build_document_blocks.py docs\docling-poc-results --out-dir docs\document-block-poc-results --max-blocks 500 --image-limit 50
   ```

   注意：Docling 1.10.0 在本机 Python 3.13 上的 `torch` 依赖已损坏（`c10.dll` 加载失败），`import docling` 阶段就报错。在 torch 修复前，请使用路线 A。详见 `docs/docling-poc.md` 的 "2026-08-03 Environment Blocker" 段落。

### 加载到原型

1. 打开 `index.html`。
2. 在左侧题本区顶部点击"选择 DocumentBlock JSON"。
3. 选择 `docs\document-block-poc-results\*.document-blocks.json`。
4. 在连续页面预览中点击或拖动框选文字和图片区域。
5. 在选择工具栏指定填入目标，点击"填入所选区域"。

注意：生成的 `DocumentBlock` JSON 可能包含真实试卷正文，只能保留在本地 ignored 目录，不要上传 GitHub。

## V1 人工验收方式

1. 用 LibreOffice 生成一个纯文本题本或解析 DOCX 的 HTML 预览文件。
2. 打开 `index.html`，分别选择 DOCX 文件和对应 HTML 预览。
3. 在左侧 HTML 预览中复制文字，在右侧题干、问题、选项或解析中粘贴并修正。
4. 切换任意题位后再切回，确认草稿文本和基础格式仍在。
5. 保存草稿、保存并录下一题、提交审核，确认题位状态变化；这些都是浏览器内模拟，不写后端。

## 下一步建议

- 让标注员试用纯文本题流程，记录 DOCX HTML 复制后的换行、编号和选项整理成本。
- 根据 V1 结果确定是否在正式前端采用受限 wangEditor，以及文本格式允许范围。
- 在 V2 单独恢复并验证 `content_blocks`、图片资产、`DocumentBlock` 辅助定位和图文混排录入。
- 补充"审核员视角"和"题库检索页"两个页面。
- 将确认后的布局重建到 Figma，高保真化为可评审设计稿。
- 之后再迁移到正式 React 工程，并拆成组件。
