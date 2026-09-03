# Data Model Draft

## English Version

This is a domain model draft for the question annotation platform. It is not yet a database migration.

### Core Entities

#### Paper

Represents a logical exam paper.

Fields:

- `id`
- `title`
- `province`
- `year`
- `subject`
- `exam_type`
- `created_at`
- `created_by`

#### PaperVersion

Represents a specific uploaded source file version.

Fields:

- `id`
- `paper_id`
- `version_number`
- `file_name`
- `file_type`
- `file_hash`
- `storage_uri`
- `upload_status`
- `parser_name`
- `parser_version`
- `parser_config`
- `created_at`
- `created_by`

#### DocumentBlock

Represents a parsed or manually defined source block. For Word V1, a parsed block belongs to one specific processing result of one immutable `PaperVersion`; it must not be identified only by `PaperVersion` plus an order number, because later reprocessing creates a separate block set.

Fields:

- `id`
- `paper_version_id`
- `block_type`
- `page_number`
- `order_index`
- `text_original`
- `text_normalized`
- `bbox`
- `image_uri`
- `parser_confidence`
- `created_at`

Possible `block_type`:

- `text`
- `table`
- `image`
- `unknown`

Word V1 `DocumentBlock` values describe reliable source structure only. They must not encode inferred business roles such as question, answer, requirement, material, option, knowledge point, or question type. Original printed labels may be retained as source text, not parser conclusions. Text-first WDV1-003 targets natural-paragraph blocks; the model is not permanently text-only, and later G-08 work may add image, table, or other reliable source evidence. A later migration must retain original reading order and any reliable page/bounding-box information without manufacturing unavailable coordinates. Processing-result history, active-result selection, and `success`/`partial`/`failed` semantics require an approved implementation contract before schema design.

#### SourceMaterial

Represents the stable identity of a reusable source-material group, such as a Shenlun "Material 1" passage shared by multiple questions.

Fields:

- `id`
- `paper_version_id`
- `source_order_index`
- `current_version_id`
- `status`
- `created_at`
- `created_by`

`SourceMaterial` is not a parsed `DocumentBlock`. It is a human-confirmed reusable business entity. Its current version may change, but historical question versions keep links to the exact material version they used.

Constraints:

- `UNIQUE (paper_version_id, source_order_index)`.
- `source_order_index > 0`.
- The current material version retains the same paper-version and source-order snapshot; historical versions keep their original snapshot.

#### SourceMaterialVersion

Represents one immutable-after-submission version of reusable source material.

Fields:

- `id`
- `source_material_id`
- `version_number`
- `paper_version_id`
- `status`
- `source_order_index`
- `source_label`
- `content_text`
- `row_version`
- `created_at`
- `updated_at`
- `created_by`
- `change_reason`

Rules:

- Draft material text may be edited with optimistic locking.
- Submitted, approved, and rejected material versions are immutable; corrections create a new version.
- `content_text` preserves meaningful paragraph breaks and is not duplicated into every linked question's `stem_text`.
- One material version may be linked to many question versions.

#### QuestionVersionMaterial

Links a question version to an exact source-material version.

Fields:

- `question_version_id`
- `source_material_version_id`
- `order_index`

Constraints:

- `PRIMARY KEY (question_version_id, source_material_version_id)`.
- `UNIQUE (question_version_id, order_index)`.
- `order_index > 0`.

#### DocumentAsset

Represents a file asset extracted from a source paper or uploaded by a human annotator. Assets include formula images, diagrams, option images, table snapshots, and fallback region screenshots.

Fields:

- `id`
- `paper_version_id`
- `document_block_id`
- `asset_type`
- `storage_uri`
- `original_file_name`
- `mime_type`
- `file_hash`
- `width`
- `height`
- `source`
- `created_at`
- `created_by`

Possible `asset_type`:

- `image`
- `formula_image`
- `diagram_image`
- `table_image`
- `region_screenshot`

Possible `source`:

- `parser_extracted`
- `human_uploaded`
- `human_cropped`
- `clipboard_paste`

#### QuestionSlot

Represents an ordered position in one paper, such as "question 1" or "question 2". A slot may be unstarted, or it may point to a draft/submitted question. This separates paper navigation from recent draft history.

Fields:

- `id`
- `paper_id`
- `paper_version_id`
- `slot_number`
- `question_id`
- `source_hint`
- `status`
- `created_at`
- `updated_at`

Constraints:

- `UNIQUE (paper_version_id, slot_number)`.
- `slot_number > 0`.
- One `question_id` can be associated with at most one slot in the same paper version.
- For the current question version, `slot_number` equals `source_order_index`; specialty-local ordering never replaces this stable global slot.

Possible `status`:

- `not_started`
- `drafting`
- `submitted`
- `approved`
- `skipped`

#### Question

Represents the stable identity of a question.

Fields:

- `id`
- `current_version_id`
- `status`
- `created_at`
- `created_by`

Possible `status`:

- `draft`
- `submitted`
- `approved`
- `rejected`
- `archived`

#### QuestionVersion

Represents a versioned snapshot of question content.

Fields:

- `id`
- `question_id`
- `version_number`
- `paper_version_id`
- `status`
- `subject`
- `question_type`
- `knowledge_point_id`
- `province`
- `year`
- `difficulty`
- `stem_text`
- `requirement_text`
- `question_text`
- `reference_answer_text`
- `answer`
- `explanation_text`
- `source_order_index`
- `source_topic_order`
- `source_question_order`
- `source_topic_label`
- `row_version`
- `score`
- `is_multiple_choice`
- `has_image`
- `created_at`
- `updated_at`
- `created_by`
- `change_reason`

`paper_version_id` is required and identifies the immutable uploaded source version used for annotation. `row_version` is an integer optimistic-lock counter; it starts at `1` and increments on each permitted draft update.

For Shenlun V1, `stem_text`, `requirement_text`, `question_text`, and `reference_answer_text` are distinct plain-text fields that preserve paragraph breaks. `stem_text` contains only question-specific stem text; reusable source material is linked through `QuestionVersionMaterial`. `explanation_text` remains optional teacher analysis and must not be used as a substitute for the reference answer. Shenlun versions do not create `QuestionOption` rows and do not set the A-D `answer` field.

The source-order fields are provenance snapshots, not question-bank identities:

- `source_order_index`: stable global order in one `PaperVersion`, starting at `1`;
- `source_topic_order`: order of the specialty section in the source document, starting at `1`;
- `source_question_order`: question order inside that specialty section, starting at `1`;
- `source_topic_label`: exact source table-of-contents or section-label snapshot.

For Shenlun V1 these four source-order fields are required. `knowledge_point_id` stores the controlled taxonomy value used for search; `source_topic_label` preserves how the source named that section and never creates or replaces a knowledge point automatically. All versions of the same `Question` normally copy the same ordering snapshot. A provenance correction requires a new `QuestionVersion` and a recorded `change_reason`.

Text fields such as `stem_text`, `requirement_text`, `question_text`, `reference_answer_text`, and `explanation_text` are the authoritative editable values for the V1 pure-text profile. When the V2 mixed-content profile is enabled, they become normalized projections and the authoritative representation is stored in `ContentBlock`.

Constraints:

- `UNIQUE (question_id, version_number)`.
- `paper_version_id` must reference an existing immutable `PaperVersion`.
- `row_version >= 1`.
- `status` is one of `draft`, `submitted`, `approved`, or `rejected`; only `draft` is mutable.
- For `subject = shenlun`, `question_type` is the controlled subjective type, `knowledge_point_id` must belong to the Shenlun taxonomy, and the four source-order fields must be present and positive.
- `QuestionSlot` owns navigation identity. Its `slot_number` should equal the current version's `source_order_index`, with `UNIQUE (paper_version_id, slot_number)`; specialty-local order is display/provenance metadata and is not a primary key.

#### QuestionOption

Represents one option in one question version.

Fields:

- `id`
- `question_version_id`
- `label`
- `text`
- `order_index`

`QuestionOption.text` is a normalized plain-text projection. The authoritative mixed-content representation is stored in `ContentBlock` with `field_name = option` and `option_label` set to `A`, `B`, `C`, or `D`.

#### ContentBlock

Represents one ordered piece of question content. This allows stems, question text, options, and explanations to mix editable text with formula images, diagrams, table snapshots, or fallback region screenshots without storing editor-specific HTML.

Fields:

- `id`
- `question_version_id`
- `field_name`
- `option_label`
- `block_type`
- `order_index`
- `text`
- `asset_id`
- `display_mode`
- `alt_text`
- `source_span_id`
- `created_at`
- `created_by`

Possible `field_name`:

- `stem`
- `requirement`
- `question_text`
- `option`
- `reference_answer`
- `explanation`

Possible `block_type`:

- `text`
- `image`
- `formula_image`
- `diagram_image`
- `table_image`
- `region_screenshot`

Possible `display_mode`:

- `inline`
- `block`
- `option_image`
- `option_image_group`

Rules:

- Text content should be stored as `block_type = text` whenever it is reasonably editable.
- Formula or diagram images should reference `DocumentAsset.id` through `asset_id`.
- Full-region screenshots should be used only when safe text/image separation is not practical.
- `source_span_id` should be set when the block can be traced to a source document span.

#### SourceSpan

Connects a question version field to one or more source document blocks as a human-confirmed provenance relationship. It does not assert character-level equality between final edited text and source text.

Fields:

- `id`
- `question_version_id`
- `field_name`
- `content_block_id`
- `paper_version_id`
- `document_block_id`
- `page_number`
- `char_start`
- `char_end`
- `note`

Word V1 must allow multiple `SourceSpan` records for the same `question_version_id` and `field_name`, retain their source order, and allow a human correction to the provenance relationship. A source span may reference an image block as evidence even though the current pure-text field cannot embed that image.

#### KnowledgePoint

Represents the taxonomy for knowledge points.

Fields:

- `id`
- `parent_id`
- `code`
- `name`
- `subject`
- `question_type`
- `default_order`
- `status`
- `created_at`

`code` is a stable machine identifier and must be unique. Display-name edits do not change the code. For Shenlun V1 the controlled codes are `shenlun.summary`, `shenlun.countermeasure`, `shenlun.analysis`, `shenlun.applied_writing`, and `shenlun.essay`; `default_order` controls taxonomy display only and does not replace source-document ordering.

#### AnnotationTask

Represents assigned annotation work.

Fields:

- `id`
- `paper_id`
- `paper_version_id`
- `assignee_id`
- `status`
- `due_at`
- `created_at`
- `created_by`

#### ReviewRecord

Represents a review action.

Fields:

- `id`
- `question_id`
- `question_version_id`
- `reviewer_id`
- `decision`
- `comment`
- `created_at`

Possible `decision`:

- `approved`
- `rejected`
- `needs_changes`

#### DatasetRelease

Represents a stable release of approved question-bank content.

Fields:

- `id`
- `name`
- `description`
- `release_version`
- `status`
- `created_at`
- `created_by`
- `published_at`

#### DatasetReleaseItem

Represents one question version included in a release.

Fields:

- `id`
- `dataset_release_id`
- `question_id`
- `question_version_id`
- `included_at`

### Versioning Rules

- `Question.id` is stable across edits.
- `QuestionVersion.id` changes whenever approved or submitted content is revised.
- `DatasetReleaseItem` must point to a specific `question_version_id`, not only `question_id`.
- `PaperVersion` must be immutable after upload metadata is finalized.
- Mixed content blocks belong to a specific `QuestionVersion`; revising approved mixed content creates a new question version and a new set of content blocks.

### Provenance Rules

- Every `QuestionVersion` must reference a `PaperVersion` and retain source ordering. A `SourceSpan` is additionally required whenever page/block coordinates are available; Shenlun V1 must not manufacture a fake span when the LibreOffice HTML preview exposes no stable coordinates.
- Each source span should refer to a `DocumentBlock` when available.
- Manual source references are allowed when parser coordinates are unavailable.
- A `SourceSpan` may point to an entire field or to a specific `ContentBlock`.
- Image content blocks should keep source provenance through `source_span_id` when the image can be traced to the source document.

### Indexing Draft

Likely search indexes:

- `Question.status`
- `QuestionVersion.year`
- `QuestionVersion.province`
- `QuestionVersion.subject`
- `QuestionVersion.question_type`
- `QuestionVersion.knowledge_point_id`
- `QuestionVersion.difficulty`
- Full-text index on `stem_text`, `requirement_text`, `question_text`, `reference_answer_text`, option text projections, `explanation_text`, and text-type `ContentBlock.text`
- Hash index on `DocumentAsset.file_hash`

## 中文版本

这是题目人工标注平台的领域数据模型草案，尚不是数据库迁移文件。

### 核心实体

#### Paper，试卷

表示一份逻辑上的考试试卷。

字段：

- `id`
- `title`
- `province`
- `year`
- `subject`
- `exam_type`
- `created_at`
- `created_by`

#### PaperVersion，试卷版本

表示某一次上传的源文件版本。

字段：

- `id`
- `paper_id`
- `version_number`
- `file_name`
- `file_type`
- `file_hash`
- `storage_uri`
- `upload_status`
- `parser_name`
- `parser_version`
- `parser_config`
- `created_at`
- `created_by`

#### DocumentBlock，文档块

表示解析得到或人工定义的来源块。Word V1 中，解析块属于某个不可变 `PaperVersion` 的某一次具体处理结果；不能只用 `PaperVersion` 加顺序号识别，因为重新处理会生成独立的块集合。

字段：

- `id`
- `paper_version_id`
- `block_type`
- `page_number`
- `order_index`
- `text_original`
- `text_normalized`
- `bbox`
- `image_uri`
- `parser_confidence`
- `created_at`

可能的 `block_type`：

- `text`，文字
- `table`，表格
- `image`，图片
- `unknown`，未知

Word V1 的 `DocumentBlock` 只表达可靠来源结构，不能编码题目、答案、作答要求、材料、选项、知识点或题型等推断出的业务角色。原始文件中印出的标题或标签可以作为来源文字保留，但不是解析器结论。text-first 的 WDV1-003 以自然段级文字块为目标；模型长期并非永久 text-only，后续 G-08 工作可增加图片、表格或其他可靠来源证据。后续迁移必须保存原始阅读顺序和可靠的页码/坐标，不能制造不存在的坐标。处理结果历史、active result 选择及 `success`/`partial`/`failed` 语义必须先由已批准的实施合同转化为 schema，不能在本说明中自行定表。

#### SourceMaterial，共享来源材料

表示可被多道题共同引用的一组来源材料的稳定身份，例如申论中的“材料 1”。

字段：

- `id`
- `paper_version_id`
- `source_order_index`
- `current_version_id`
- `status`
- `created_at`
- `created_by`

`SourceMaterial` 不是解析器产生的 `DocumentBlock`，而是经人工确认、可复用的业务实体。其当前版本可以变化，但历史题目版本始终指向当时使用的准确材料版本。

约束：

- `UNIQUE (paper_version_id, source_order_index)`。
- `source_order_index > 0`。
- 当前材料版本保留相同的试卷版本和来源顺序快照，历史版本保留各自原始快照。

#### SourceMaterialVersion，共享来源材料版本

表示共享来源材料的一次版本化快照，提交后不可原地修改。

字段：

- `id`
- `source_material_id`
- `version_number`
- `paper_version_id`
- `status`
- `source_order_index`
- `source_label`
- `content_text`
- `row_version`
- `created_at`
- `updated_at`
- `created_by`
- `change_reason`

规则：

- 草稿材料使用乐观锁编辑。
- 已提交、已通过和已驳回的材料版本不可修改；修订时创建新版本。
- `content_text` 保留段落换行，不得复制到每一道关联题目的 `stem_text` 中。
- 一个材料版本可以关联多个题目版本。

#### QuestionVersionMaterial，题目版本与共享材料关联

把题目版本连接到准确的共享材料版本。

字段：

- `question_version_id`
- `source_material_version_id`
- `order_index`

约束：

- `PRIMARY KEY (question_version_id, source_material_version_id)`。
- `UNIQUE (question_version_id, order_index)`。
- `order_index > 0`。

#### DocumentAsset，文档资源

表示从源试卷中抽取或由人工上传的文件资源。资源包括公式图片、图形、选项图片、表格截图和兜底区域截图。

字段：

- `id`
- `paper_version_id`
- `document_block_id`
- `asset_type`
- `storage_uri`
- `original_file_name`
- `mime_type`
- `file_hash`
- `width`
- `height`
- `source`
- `created_at`
- `created_by`

可能的 `asset_type`：

- `image`，普通图片
- `formula_image`，公式图片
- `diagram_image`，图形图片
- `table_image`，表格图片
- `region_screenshot`，区域截图

可能的 `source`：

- `parser_extracted`，解析器抽取
- `human_uploaded`，人工上传
- `human_cropped`，人工裁剪
- `clipboard_paste`，剪贴板粘贴

#### QuestionSlot，题位

表示某份试卷中的顺序题位，例如“第 1 题”或“第 2 题”。题位可以尚未开始，也可以指向一个草稿或已提交题目。该实体用于把试卷导航顺序与最近编辑草稿历史分开。

字段：

- `id`
- `paper_id`
- `paper_version_id`
- `slot_number`
- `question_id`
- `source_hint`
- `status`
- `created_at`
- `updated_at`

约束：

- `UNIQUE (paper_version_id, slot_number)`。
- `slot_number > 0`。
- 同一个 `question_id` 在同一试卷版本中最多关联一个题位。
- 对当前题目版本，`slot_number` 等于 `source_order_index`；专项内题序不能替代该全局稳定题位。

可能的 `status`：

- `not_started`，未开始
- `drafting`，录入中
- `submitted`，待审核
- `approved`，已通过
- `skipped`，跳过

#### Question，题目

表示一道题目的稳定身份。

字段：

- `id`
- `current_version_id`
- `status`
- `created_at`
- `created_by`

可能的 `status`：

- `draft`，草稿
- `submitted`，待审核
- `approved`，已通过
- `rejected`，已驳回
- `archived`，已归档

#### QuestionVersion，题目版本

表示题目内容的一次版本化快照。

字段：

- `id`
- `question_id`
- `version_number`
- `paper_version_id`
- `status`
- `subject`
- `question_type`
- `knowledge_point_id`
- `province`
- `year`
- `difficulty`
- `stem_text`
- `requirement_text`
- `question_text`
- `reference_answer_text`
- `answer`
- `explanation_text`
- `source_order_index`
- `source_topic_order`
- `source_question_order`
- `source_topic_label`
- `row_version`
- `score`
- `is_multiple_choice`
- `has_image`
- `created_at`
- `updated_at`
- `created_by`
- `change_reason`

`paper_version_id` 必填，指向录题所依据的不可变上传文件版本。`row_version` 是整数型乐观锁计数器，初始值为 `1`，每次允许的草稿更新后加一。

申论 V1 必须分别保存 `stem_text`、`requirement_text`、`question_text` 和 `reference_answer_text`，并保留段落换行。`stem_text` 只保存该题独有的题干文字；可被多题复用的材料通过 `QuestionVersionMaterial` 关联。`explanation_text` 仅用于后续可选的教师解析或批注，不得代替参考答案。申论题目版本不创建 `QuestionOption`，也不设置 A-D `answer`。

专项来源顺序是来源追溯快照，不是题库身份：

- `source_order_index`：同一 `PaperVersion` 内从 `1` 开始的全局稳定顺序；
- `source_topic_order`：专项在来源文档中从 `1` 开始的顺序；
- `source_question_order`：题目在专项内从 `1` 开始的顺序；
- `source_topic_label`：原文目录标题或分节标题的原样快照。

申论 V1 的上述四个来源顺序字段必填。检索分类使用受控的 `knowledge_point_id`；`source_topic_label` 只保留来源文档如何命名该专项，不能自动创建或替代知识点。同一 `Question` 的后续版本通常复制相同顺序快照；如果人工纠正来源归属或顺序，必须创建新 `QuestionVersion` 并记录 `change_reason`。

V1 纯文本配置中，`stem_text`、`requirement_text`、`question_text`、`reference_answer_text` 和 `explanation_text` 是权威可编辑值。V2 图文配置启用后，这些字段转为规范化纯文本投影，权威图文内容保存在 `ContentBlock` 中。

约束：

- `UNIQUE (question_id, version_number)`。
- `paper_version_id` 必须引用已存在且不可变的 `PaperVersion`。
- `row_version >= 1`。
- `status` 只能为 `draft`、`submitted`、`approved` 或 `rejected`，且只有 `draft` 可修改。
- 当 `subject = shenlun` 时，`question_type` 使用受控主观题类型，`knowledge_point_id` 必须属于申论知识点体系，四个来源顺序字段必须存在且为正数。
- `QuestionSlot` 负责导航身份；其 `slot_number` 应等于当前版本的 `source_order_index`，并满足 `UNIQUE (paper_version_id, slot_number)`。专项内题序只是展示和来源追溯信息，不能作为主键。

#### QuestionOption，题目选项

表示某个题目版本中的一个选项。

字段：

- `id`
- `question_version_id`
- `label`
- `text`
- `order_index`

`QuestionOption.text` 是规范化纯文本投影。权威的图文混排选项内容应保存在 `ContentBlock` 中，其中 `field_name = option`，`option_label` 为 `A`、`B`、`C` 或 `D`。

#### ContentBlock，内容块

表示题目内容中的一个有序片段。该结构允许题干、问题、选项和解析混合保存可编辑文本、公式图片、图形、表格截图或兜底区域截图，同时避免把某个富文本编辑器的 HTML 作为数据库模型。

字段：

- `id`
- `question_version_id`
- `field_name`
- `option_label`
- `block_type`
- `order_index`
- `text`
- `asset_id`
- `display_mode`
- `alt_text`
- `source_span_id`
- `created_at`
- `created_by`

可能的 `field_name`：

- `stem`，题干
- `requirement`，作答要求
- `question_text`，问题
- `option`，选项
- `reference_answer`，参考答案
- `explanation`，解析

可能的 `block_type`：

- `text`，文本
- `image`，普通图片
- `formula_image`，公式图片
- `diagram_image`，图形图片
- `table_image`，表格图片
- `region_screenshot`，区域截图

可能的 `display_mode`：

- `inline`，行内
- `block`，独立块
- `option_image`，单个选项图片
- `option_image_group`，选项图片组

规则：

- 只要文字能够合理编辑，就应保存为 `block_type = text`。
- 公式或图形图片应通过 `asset_id` 引用 `DocumentAsset.id`。
- 只有在无法安全拆分文字和图片时，才使用整段区域截图作为兜底。
- 当内容块能追溯到源文档位置时，应设置 `source_span_id`。

#### SourceSpan，来源片段

把题目版本字段与一个或多个来源文档块连接为人工确认的来源关系；它不表示最终人工编辑文本与来源文字逐字一致。

字段：

- `id`
- `question_version_id`
- `field_name`
- `content_block_id`
- `paper_version_id`
- `document_block_id`
- `page_number`
- `char_start`
- `char_end`
- `note`

Word V1 必须允许同一个 `question_version_id` 和 `field_name` 对应多条 `SourceSpan`，保存它们的来源顺序，并允许人工更正来源关系。来源片段可以引用图片块作为证据，即使当前纯文本字段不能嵌入该图片。

#### KnowledgePoint，知识点

表示知识点分类体系。

字段：

- `id`
- `parent_id`
- `code`
- `name`
- `subject`
- `question_type`
- `default_order`
- `status`
- `created_at`

`code` 是唯一且稳定的机器标识，修改展示名称不改变 `code`。申论 V1 的受控代码为 `shenlun.summary`、`shenlun.countermeasure`、`shenlun.analysis`、`shenlun.applied_writing` 和 `shenlun.essay`；`default_order` 只控制知识点体系的展示顺序，不能替代来源文档顺序。

#### AnnotationTask，标注任务

表示分配出去的标注工作。

字段：

- `id`
- `paper_id`
- `paper_version_id`
- `assignee_id`
- `status`
- `due_at`
- `created_at`
- `created_by`

#### ReviewRecord，审核记录

表示一次审核动作。

字段：

- `id`
- `question_id`
- `question_version_id`
- `reviewer_id`
- `decision`
- `comment`
- `created_at`

可能的 `decision`：

- `approved`，通过
- `rejected`，驳回
- `needs_changes`，需要修改

#### DatasetRelease，数据集发布版本

表示一次稳定发布的已审核题库内容。

字段：

- `id`
- `name`
- `description`
- `release_version`
- `status`
- `created_at`
- `created_by`
- `published_at`

#### DatasetReleaseItem，发布版本条目

表示某个发布版本中包含的一道题目版本。

字段：

- `id`
- `dataset_release_id`
- `question_id`
- `question_version_id`
- `included_at`

### 版本规则

- `Question.id` 在多次编辑中保持稳定。
- 当已审核或已提交内容被修订时，`QuestionVersion.id` 会变化。
- `DatasetReleaseItem` 必须指向具体的 `question_version_id`，不能只指向 `question_id`。
- `PaperVersion` 在上传元数据确认后应保持不可变。
- 图文内容块属于具体的 `QuestionVersion`；已审核图文内容被修订时，应创建新的题目版本和新的内容块集合。

### 来源追溯规则

- 每个 `QuestionVersion` 必须引用 `PaperVersion` 并保留来源顺序。在具备页码或原文块坐标时还必须保存 `SourceSpan`；如果 LibreOffice HTML 预览没有稳定坐标，申论 V1 不得制造虚假来源片段。
- 在条件允许时，每个来源片段都应引用一个 `DocumentBlock`。
- 当解析器坐标不可用时，允许人工来源引用。
- `SourceSpan` 可以指向整个字段，也可以指向具体的 `ContentBlock`。
- 图片内容块如果能追溯到源文档位置，应通过 `source_span_id` 保留来源。

#### Source region selection，来源区域选择

来源区域选择是工作台交互层的临时组合，不替代 `DocumentBlock` 或 `SourceSpan` 实体。它由一个或多个来源块组成，用于把连续页面预览中的混合文字和图片一次性绑定到题目字段。

最小行为约束：

- 选择项必须引用现有 `DocumentBlock.block_id`，不能复制或改写来源块本身。
- 选择结果按 `page_no`、`bbox.t`、`bbox.l` 和稳定的解析顺序排序。
- 填入题干、问题、选项或解析后，每个生成的 `ContentBlock` 分别保留对应的 `source_span_id`。
- 一个来源区域可以包含文本块和图片块；图片块不应因被单独渲染而与相邻文本失去阅读顺序。
- 选择区域只表示人工确认的来源绑定，不表示系统已经自动识别出题目边界。

来源区域可以是前端 POC 的派生视图模型，正式持久化时可由题目字段与内容块来源引用重建；只有当后续需要保存操作员的选择轨迹时，才另行设计审计事件或绑定记录。

内容块编辑界面应以 `ContentBlock` 集合作为唯一可编辑真相。题干、选项和解析的纯文本投影可以为搜索、完整度计算和兼容导出保留，但不得与内容块形成两个可独立修改且可能冲突的权威字段。

来源预览层可以把多个带坐标的 `DocumentBlock` 组合为连续页面视图。该组合只改变展示和选择方式，不改变底层来源块的粒度、来源坐标或资源引用。

#### V1 纯文本题配置

第一版可运行配置只接收纯文本题。行测等客观题配置使用 `stem_text`、`question_text`、`QuestionOption.text` 和 `explanation_text`；申论配置使用 `stem_text`、`requirement_text`、`question_text` 和 `reference_answer_text`。受限富文本编辑器可以保留客户端草稿表示，用于段落和基础文字格式，但编辑器特有 HTML 或 JSON 不是权威数据库模型。

`ContentBlock`、`DocumentAsset` 和块级 `SourceSpan` 继续保留给后续图文题配置。V1 不应为了匹配未来 schema 而制造虚假的图片资源、来源片段或不完整图片块。

#### 申论 V1 专项规则

申论 V1 的题干、要求、问题、教师参考答案和专项来源顺序已经纳入上方正式 `QuestionVersion` 定义，本节只补充受控分类规则。

“归纳概括、提出对策、综合分析、应用文写作、大作文”映射为受控的 `knowledge_point_id`。为保持教师版 DOC 的展开顺序，题目版本额外保留：

- `source_order_index`：整份来源文档中的稳定顺序，从 `1` 开始；
- `source_topic_order`：知识点专项在来源文档中的顺序，从 `1` 开始；
- `source_question_order`：专项内题序，从 `1` 开始；
- `source_topic_label`：原文目录标题快照。

题库检索使用 `knowledge_point_id`；原文目录标题和顺序属于来源追溯信息，不替代标准知识点体系。

### 索引草案

可能需要的检索索引：

- `Question.status`
- `QuestionVersion.year`
- `QuestionVersion.province`
- `QuestionVersion.subject`
- `QuestionVersion.question_type`
- `QuestionVersion.knowledge_point_id`
- `QuestionVersion.difficulty`
- `stem_text`、`requirement_text`、`question_text`、`reference_answer_text`、选项文本投影、`explanation_text` 和文本型 `ContentBlock.text` 的全文索引
- `DocumentAsset.file_hash` 的哈希索引
