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

Represents a parsed or manually defined source block.

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

- `paragraph`
- `question_candidate`
- `option_candidate`
- `answer_candidate`
- `table`
- `image`
- `unknown`

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
- `subject`
- `question_type`
- `knowledge_point_id`
- `province`
- `year`
- `difficulty`
- `stem`
- `question_text`
- `answer`
- `explanation`
- `score`
- `is_multiple_choice`
- `has_image`
- `created_at`
- `created_by`
- `change_reason`

#### QuestionOption

Represents one option in one question version.

Fields:

- `id`
- `question_version_id`
- `label`
- `text`
- `image_uri`
- `order_index`

#### SourceSpan

Connects a question version or field to source document blocks.

Fields:

- `id`
- `question_version_id`
- `field_name`
- `paper_version_id`
- `document_block_id`
- `page_number`
- `char_start`
- `char_end`
- `note`

#### KnowledgePoint

Represents the taxonomy for knowledge points.

Fields:

- `id`
- `parent_id`
- `name`
- `subject`
- `question_type`
- `status`
- `created_at`

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

### Provenance Rules

- Every `QuestionVersion` should have at least one `SourceSpan`.
- Each source span should refer to a `DocumentBlock` when available.
- Manual source references are allowed when parser coordinates are unavailable.

### Indexing Draft

Likely search indexes:

- `Question.status`
- `QuestionVersion.year`
- `QuestionVersion.province`
- `QuestionVersion.subject`
- `QuestionVersion.question_type`
- `QuestionVersion.knowledge_point_id`
- `QuestionVersion.difficulty`
- Full-text index on `stem`, `question_text`, option text, and `explanation`

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

表示解析得到或人工定义的来源块。

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

- `paragraph`，段落
- `question_candidate`，疑似题目
- `option_candidate`，疑似选项
- `answer_candidate`，疑似答案
- `table`，表格
- `image`，图片
- `unknown`，未知

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
- `subject`
- `question_type`
- `knowledge_point_id`
- `province`
- `year`
- `difficulty`
- `stem`
- `question_text`
- `answer`
- `explanation`
- `score`
- `is_multiple_choice`
- `has_image`
- `created_at`
- `created_by`
- `change_reason`

#### QuestionOption，题目选项

表示某个题目版本中的一个选项。

字段：

- `id`
- `question_version_id`
- `label`
- `text`
- `image_uri`
- `order_index`

#### SourceSpan，来源片段

将题目版本或题目字段连接到来源文档块。

字段：

- `id`
- `question_version_id`
- `field_name`
- `paper_version_id`
- `document_block_id`
- `page_number`
- `char_start`
- `char_end`
- `note`

#### KnowledgePoint，知识点

表示知识点分类体系。

字段：

- `id`
- `parent_id`
- `name`
- `subject`
- `question_type`
- `status`
- `created_at`

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

### 来源追溯规则

- 每个 `QuestionVersion` 至少应有一个 `SourceSpan`。
- 在条件允许时，每个来源片段都应引用一个 `DocumentBlock`。
- 当解析器坐标不可用时，允许人工来源引用。

### 索引草案

可能需要的检索索引：

- `Question.status`
- `QuestionVersion.year`
- `QuestionVersion.province`
- `QuestionVersion.subject`
- `QuestionVersion.question_type`
- `QuestionVersion.knowledge_point_id`
- `QuestionVersion.difficulty`
- `stem`、`question_text`、选项文本和 `explanation` 的全文索引
