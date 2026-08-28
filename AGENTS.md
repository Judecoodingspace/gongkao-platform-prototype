# AGENTS.md

## Project

This repository is for a production-oriented platform that turns Chinese civil-service exam papers into a reviewed, searchable, versioned question bank.

Core workflow:

1. Import source papers, initially DOCX and later PDF or scanned files.
2. Preserve source document provenance.
3. Let human annotators split stems, questions, options, answers, explanations, images, and metadata.
4. Let reviewers approve or reject annotated questions.
5. Publish stable question-bank releases for teachers to search and assemble papers.

## Current Stage

The project is currently in the Infra and specification stage.

Do not start implementing production application code until the relevant spec, plan, tasks, data model, and acceptance checklist are reviewed.

The existing HTML page under `prototypes/question-bank-prototype/` is a temporary clickable prototype, not the final application architecture.

## Repository Boundary

The project is split into three independent Git repositories:

- `D:\gongkao-question-bank-platform`: specifications, review history, document-parsing POCs, and frozen high-fidelity prototype references.
- `D:\gongkao-question-bank-api`: the production FastAPI, SQLAlchemy, Alembic, PostgreSQL, backend-test, and OpenAPI repository.
- `D:\gongkao-question-bank-web`: the production React and TypeScript repository. It remains documentation-only until backend gate `G-04` passes.

Do not add production frontend or backend application code to this repository. Do not copy prototype JavaScript into either production repository as business logic. After the tagged Shenlun V1 baseline, modify the frozen HTML prototype only when the user explicitly starts a new prototype revision; cross-repository product and architecture decisions continue to be recorded under `docs/` here.

Run GitHub CLI progress management in the repository that owns the scoped work. Link implementation issues back to the governing specification or review record when useful.

## Non-Negotiable Domain Rules

- Never insert AI-parsed questions directly into the final question bank without human review.
- Every question must keep source provenance: `paper_id`, `paper_version_id`, and source block/page/span when available.
- Preserve original Chinese source text exactly unless a human edit is explicitly recorded.
- Approved question content must not be overwritten in place. Create a new version instead.
- Do not invent answer keys, explanations, difficulty, province, year, subject, question type, or knowledge points.
- Uploaded exam documents are untrusted input. Do not execute macros or embedded active content.
- Do not log full private papers, answer keys, credentials, tokens, or institution-private data.

## Harness Boundary

Before finishing any future implementation task, run the smallest relevant checks.

Backend:

- Unit tests for the changed module.
- Type check or static analysis.
- Migration check against a local test database when schema changes.

Frontend:

- Lint and type check.
- Component or interaction tests for changed workflows.
- Screenshot checks for major layout changes, especially the annotation workbench.
- Verify that text, controls, and scroll areas do not overlap at common desktop widths.

Document parsing:

- Use fixtures under future `tests/fixtures/papers/`.
- Parser changes must include snapshot-like assertions for extracted blocks.
- Parsed output must include provenance metadata.
- Parser behavior must be deterministic for the same input and parser version.

If a command is unavailable or blocked by the local environment, report that clearly in the final answer.

## Scope Control

- Keep changes limited to the requested feature or document.
- Do not refactor unrelated areas.
- Do not change database schema without updating `data-model.md` and writing a migration plan.
- Do not add dependencies unless they remove clear complexity or match the agreed technical plan.
- Prefer explicit domain terms over vague names such as `item`, `data`, or `content`.

## Collaboration Stance

- Do not simply follow the user's latest suggestion when it may weaken the product, architecture, data quality, or maintainability.
- Challenge assumptions clearly and respectfully. When disagreeing, explain the product or engineering risk and propose a better alternative.
- Treat prototype decisions, document-parsing decisions, data-model decisions, and workflow decisions as separate layers. Do not let a quick prototype shortcut silently become a production rule.
- When a feature sounds plausible but belongs to a later stage, say so and preserve only the minimum information needed by the current stage.
- Use GitHub CLI to manage development progress for each scoped development or POC step when the repository has a relevant GitHub issue. Record start, important blockers, and completion notes on the issue. If GitHub CLI is unavailable or blocked, report the attempted command and blocker clearly.
- GitHub progress comments must not include full private paper text, answer keys, generated private parsing outputs, credentials, tokens, or institution-private data.

中文补充：

- 不要为了迎合用户的表述而直接沿着某个方案实现；如果方案会损害产品、架构、数据质量或长期维护性，需要明确指出。
- 反驳时要给出理由，并给出更合适的替代方案。
- 区分原型、文档解析、数据模型和业务流程，不要让原型阶段的临时做法变成默认的生产规则。
- 如果某个能力更适合后续阶段实现，应说明原因，并在当前阶段只保留必要的信息结构。
- 对每一个有对应 GitHub issue 的开发或 POC 步骤，使用 GitHub CLI 管理进度，在 issue 中记录开始、关键阻塞和完成结论；如果 GitHub CLI 不可用或被网络/代理阻塞，必须说明尝试过的命令和阻塞原因。
- GitHub 进度记录不得包含完整私有试卷正文、答案、生成的私有解析结果、凭证、token 或机构内部数据。

## Documentation Rules

When changing behavior or architecture, update the closest relevant document:

- Product behavior: `docs/PRD.md` or the relevant `spec.md`.
- Engineering plan: `plan.md`.
- Tasks: `tasks.md`.
- Data structure: `data-model.md`.
- Verification: `acceptance-checklist.md`.
- Durable agent guidance: this file.

## Expected PR Summary

Every future PR should include:

- What changed
- Why it changed
- Screenshots for UI changes
- Data model or migration notes, if any
- Tests or checks run
- Known limitations

## First Files To Read In A New Codex Session

1. `HANDOFF.md`
2. `AGENTS.md`
3. `docs/constitution.md`
4. `docs/PRD.md`
5. The relevant file under `docs/specs/`
