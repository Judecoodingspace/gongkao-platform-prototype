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
