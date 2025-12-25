 <!-- SYNC IMPACT REPORT
Version change: N/A -> 1.0.0
Modified principles: N/A (new constitution)
Added sections: All sections added for AI-Native Book Creation project
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md ⚠ pending
  - .specify/templates/spec-template.md ⚠ pending
  - .specify/templates/tasks-template.md ⚠ pending
  - .specify/templates/commands/*.md ⚠ pending
Runtime docs: README.md ⚠ pending
Follow-up TODOs: None
-->

# AI-Native Book Creation with Integrated RAG Chatbot Constitution

## Core Principles

### Specification-First Development
All work must be driven by clear, versioned specifications before implementation.

### Source-Grounded Intelligence
The chatbot and book content must rely only on verified, indexed book material—no hallucinations.

### Clarity for Technical Learners
Content must be understandable by developers with basic to intermediate AI/software background.

### Reproducibility & Automation
Any setup, deployment, or generation step must be repeatable via documented commands.

### Separation of Concerns
Book content, chatbot backend, embeddings, database, and UI must be cleanly modularized.

### AI Behavior Constraints
No hallucinated answers, no external knowledge unless explicitly indexed, prefer "I don't know based on the provided content" over guessing.

## Book Authoring Standards
Framework: Docusaurus
Writing method: Claude Code + Spec-Kit Plus
Structure: Clear chapters with headings and sub-headings, progressive learning flow, tone: instructional, precise, non-marketing
Content must be: Original, technically accurate, free from filler or vague explanations

## RAG Chatbot Architecture
Architecture: FastAPI backend, OpenAI Agents / ChatKit SDK, Neon Serverless Postgres (metadata + auth), Qdrant Cloud Free Tier (vector storage)
Capabilities: Answer questions using entire book content, answer questions using only user-selected text, reject questions when context is insufficient
Behavior: Cite chapter/section source internally, never invent facts beyond indexed content

## Technical Constraints
Deployment: Book hosted on GitHub Pages, backend deployed separately (cloud-ready)
Code quality: Clear, maintainable, well-documented code with proper testing

## Development Workflow
All development must follow Spec-Driven Development (SDD) methodology using Spec-Kit Plus tools. Every feature must have clear specifications before implementation, with testable acceptance criteria and proper documentation.

## Quality Standards
All code must include comprehensive tests, proper error handling, and follow security best practices. Content must be technically accurate and verified against authoritative sources.

## Governance
This constitution governs all development activities for the AI-Native Book Creation project. All team members must adhere to these principles and standards. Any deviations require explicit approval and documentation of the rationale.

**Version**: 1.0.0 | **Ratified**: 2025-12-23 | **Last Amended**: 2025-12-23