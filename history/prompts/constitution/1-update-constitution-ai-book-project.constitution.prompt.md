---
id: 1
title: Update Constitution AI Book Project
stage: constitution
date: 2025-12-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Mr. OBS
command: /sp.constitution
labels: [constitution,spec-driven-development,ai-book,rag-chatbot]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
---

## Prompt

```
/sp.constitution

Project:
AI-Native Book Creation with Integrated RAG Chatbot

Mission

Build a production-grade, AI/spec-driven technical book using Docusaurus, authored via Claude Code and Spec-Kit Plus, and publish it to GitHub Pages.
Embed a fully functional Retrieval-Augmented Generation (RAG) chatbot that can answer questions strictly from the book's content, including user-selected text.

Core Principles

Specification-First Development
All work must be driven by clear, versioned specifications before implementation.

Source-Grounded Intelligence
The chatbot and book content must rely only on verified, indexed book material—no hallucinations.

Clarity for Technical Learners
Content must be understandable by developers with basic to intermediate AI/software background.

Reproducibility & Automation
Any setup, deployment, or generation step must be repeatable via documented commands.

Separation of Concerns
Book content, chatbot backend, embeddings, database, and UI must be cleanly modularized.

Key Standards
Book Authoring

Framework: Docusaurus

Writing method: Claude Code + Spec-Kit Plus

Structure:

Clear chapters with headings and sub-headings

Progressive learning flow

Tone: instructional, precise, non-marketing

Content must be:

Original

Technically accurate

Free from filler or vague explanations

RAG Chatbot

Architecture:

FastAPI backend

OpenAI Agents / ChatKit SDK

Neon Serverless Postgres (metadata + auth)

Qdrant Cloud Free Tier (vector storage)

Capabilities:

Answer questions using entire book content

Answer questions using only user-selected text

Reject questions when context is insufficient

Behavior:

Cite chapter/section source internally

Never invent facts beyond indexed content

AI Behavior Constraints

No hallucinated answers

No external knowledge unless explicitly indexed

Prefer "I don't know based on the provided content" over guessing

Technical Constraints

Deployment:

Book hosted on GitHub Pages

Backend deployed separately (cloud-ready)

Code quality:

Clear
```

## Response snapshot

The constitution for the AI-Native Book Creation with Integrated RAG Chatbot project has been created, incorporating all specified principles and standards. The updated constitution file includes:

- Core Principles: Specification-First Development, Source-Grounded Intelligence, Clarity for Technical Learners, Reproducibility & Automation, Separation of Concerns, and AI Behavior Constraints
- Book Authoring Standards: Using Docusaurus framework with Claude Code + Spec-Kit Plus
- RAG Chatbot Architecture: FastAPI backend, OpenAI Agents/ChatKit SDK, Neon Serverless Postgres, Qdrant Cloud
- Technical Constraints: GitHub Pages deployment with code quality standards
- Development Workflow and Quality Standards sections
- Governance section with versioning information

Version 1.0.0 was established with ratification date of 2025-12-23.

## Outcome

- ✅ Impact: Project constitution established with all required principles and standards
- 🧪 Tests: N/A (documentation update)
- 📁 Files: Updated .specify/memory/constitution.md with comprehensive project governance
- 🔁 Next prompts: Proceed with spec creation using /sp.specify
- 🧠 Reflection: Constitution provides clear framework for AI book creation project with RAG chatbot

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create project specification based on constitution