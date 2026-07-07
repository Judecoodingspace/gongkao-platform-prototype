# Handoff

## One-Sentence Context

This project is a maintainable, production-oriented platform for manually extracting, annotating, reviewing, and versioning civil-service exam questions from historical source papers.

## Current State

- The project has no production app code yet.
- A temporary clickable HTML prototype exists at `prototypes/question-bank-prototype/index.html`.
- The initial documentation scaffold has been created under `docs/`.
- The first scoped feature is `001-question-annotation-workbench`.

## Why This Project Exists

The team needs to process historical civil-service exam papers, mostly Word files at the beginning, into a structured question bank. Human annotators will split raw papers into question stems, questions, options, answers, explanations, images, and metadata. Reviewers will approve the results before they become available for teachers to search and assemble papers.

## Product Roles

- Annotator: splits and labels questions from source papers.
- Reviewer: checks annotated questions and approves or rejects them.
- Teacher: searches approved questions and assembles papers.
- Admin: manages papers, users, taxonomies, and releases.

## Durable Engineering Principles

- Use specification-driven development.
- Treat uploaded documents as untrusted input.
- Keep provenance and version history for every question.
- Do not let AI-generated extraction bypass human review.
- Prefer small, verifiable tasks for Codex or Claude Code.
- Keep docs and implementation synchronized.

## Important Documents

- `AGENTS.md`: durable coding-agent instructions and harness boundary.
- `docs/constitution.md`: project principles.
- `docs/PRD.md`: product requirements.
- `docs/specs/001-question-annotation-workbench/spec.md`: first feature spec.
- `docs/specs/001-question-annotation-workbench/plan.md`: initial technical plan.
- `docs/specs/001-question-annotation-workbench/data-model.md`: domain data model draft.
- `docs/specs/001-question-annotation-workbench/tasks.md`: task breakdown.
- `docs/specs/001-question-annotation-workbench/acceptance-checklist.md`: acceptance criteria.

## Current Prototype Notes

The prototype follows a hand-drawn layout:

- Left top: source paper upload and source blocks.
- Left bottom: answer/explanation upload and matching area.
- Right main: structured question editing form.
- Far right: vertical workflow steps.

The prototype is intentionally static and dependency-free. It is for discussion, not the final application architecture.

## Suggested Next Steps

1. Review `docs/PRD.md` with the project stakeholders.
2. Review the clickable prototype with senior students, annotators, and teachers.
3. Convert agreed UI into a Figma high-fidelity prototype.
4. Decide the first real technical stack and repository layout.
5. Implement the smallest backend and frontend slice only after the first spec is accepted.

## Recommended First Implementation Slice

Build a minimal local workflow:

1. Upload one DOCX paper.
2. Store it as a `paper_version`.
3. Convert it into source blocks through a parser adapter.
4. Display source blocks in the annotation workbench.
5. Allow manual creation of one draft question linked to a source block.
6. Submit that draft question for review.

## Open Questions

- Which backend stack will be used: FastAPI, NestJS, Django, or another framework?
- Which frontend stack will be used: React plus Ant Design, Vue plus TDesign, or another stack?
- Will Docling be adopted as the first parser POC?
- What are the exact province/year/subject/type taxonomies?
- What data privacy constraints apply to historical papers and answer keys?
- Who is the final reviewer for accepted question-bank releases?
