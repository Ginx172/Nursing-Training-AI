# Copilot Instructions for Nursing Training AI

## Project Overview

This is a **Nursing Training AI** application designed to simulate NHS job interviews and support clinical skill development. The app lives in `Nursing_Training_AI_App/` and consists of:

- `backend/` — Python/FastAPI REST API
- `frontend/` — TypeScript/Next.js web application

---

## Project Structure

```
Nursing_Training_AI_App/
├── backend/
│   ├── main.py                   # FastAPI app entry point; registers all routers via _EXTRA_ROUTES
│   ├── api/
│   │   └── routes/               # FastAPI routers (one file per feature)
│   ├── core/                     # Business logic
│   │   └── ai_evaluation.py      # Google Gemini API integration for AI evaluation
│   ├── data/
│   │   └── question_banks/       # JSON files containing interview/clinical questions
│   ├── models/                   # Data models and self-learning weights
│   │   └── self_learning/
│   │       └── weights.json      # Adaptive scoring weights
│   └── tests/                    # pytest test suite
└── frontend/
    ├── pages/                    # Next.js pages (file-based routing)
    └── components/               # Reusable React components
```

---

## Key Conventions

### Backend (Python/FastAPI)
- All routes are **FastAPI routers** defined in `backend/api/routes/`
- New routers **must** be registered in `backend/main.py` via the `_EXTRA_ROUTES` list
- Use **Pydantic models** for request/response validation
- Question banks are loaded from **JSON files** in `backend/data/question_banks/`
- AI evaluation (scoring, feedback) goes through `backend/core/ai_evaluation.py` using the **Google Gemini API**
- Tests are written with **pytest** in `backend/tests/`

### Frontend (TypeScript/Next.js)
- Pages are in `frontend/pages/` following Next.js file-based routing conventions
- Reusable UI elements go in `frontend/components/`
- Use TypeScript interfaces that mirror the backend Pydantic models

---

## Rules for the Coding Agent

> **These rules exist to prevent empty "ghost" PRs that contain no real code changes.**

1. **Always create actual files with real code.** Never open a PR with zero file additions or modifications. If you cannot complete the implementation, do not open the PR.

2. **Verify before opening a PR.** Confirm that all files you intended to create or modify are actually present in the diff (visible in "Files changed"). A PR with 0 files changed must not be opened.

3. **One feature or fix per PR.** Keep PRs small and focused. Do not combine multiple unrelated features in one PR.

4. **Do not use [WIP] in PR titles.** Only open PRs when the work is complete and tested. A PR with [WIP] in the title should never be merged.

5. **Run tests before pushing.** Execute `pytest` in the `backend/` directory and verify the frontend builds (`npm run build`) before pushing if possible.

6. **Each PR must have visible additions in the diff.** If "Files changed" shows 0, the PR is empty and must not be merged.

7. **Do not modify `weights.json` automatically.** The file `backend/models/self_learning/weights.json` is managed by the self-learning system and should not be modified as part of feature PRs unless explicitly instructed.
