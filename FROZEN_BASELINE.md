# Frozen Baseline: Shenlun V1 Specification And High-Fidelity Prototype

## Baseline

- Freeze date: 2026-08-28
- Annotated Git tag: `shenlun-v1-hifi-spec-baseline-2026-08-28`
- Governing GitHub repository: `Judecoodingspace/gongkao-platform-prototype`
- Split decision: three independent Git repositories

This baseline preserves the reviewed Shenlun V1 product rules, data model, API contract, migration plan, review history, document-processing POCs, and the static HTML high-fidelity reference.

## Repository Responsibilities

| Repository | Local path | Responsibility |
| --- | --- | --- |
| Specification/reference | `D:\gongkao-question-bank-platform` | Product specifications, review records, parser/LibreOffice POCs, and frozen prototype reference |
| Production API | `D:\gongkao-question-bank-api` | FastAPI, SQLAlchemy, Alembic, PostgreSQL schema, backend tests, and generated OpenAPI |
| Production Web | `D:\gongkao-question-bank-web` | React/TypeScript application; documentation-only until `G-04` passes |

## Freeze Rules

- No production frontend or backend code is added to this repository.
- `prototypes/question-bank-prototype/index.html` is the frozen Shenlun V1 interaction/layout reference. It is not production React source code.
- A new prototype change requires an explicit new prototype revision and a new review record; do not silently alter this tagged baseline.
- Governing specifications under `docs/` may continue to evolve after the tag. The tag remains the immutable reference for what was approved at freeze time.
- Production repositories implement the contracts; they do not copy prototype JavaScript business logic.

## Excluded Local Data

The baseline does not include raw papers, answer documents, parser output directories, LibreOffice/Docling generated results, review DOCX files, credentials, local databases, or local prototype PDF exports. These remain ignored and require separate privacy review before any publication.

## Approved Implementation Entry

- `G-01`, `G-02`, and `G-03` are complete.
- API implementation begins with `SHV1-004` in the production API repository.
- React implementation and API wiring begin only after backend gate `G-04` passes.
