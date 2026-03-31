# Contributing to Universal Video Downloader

## For new contributors (freshers)

Start with the **README** → then the **Project structure** and **Key concepts** sections → then this CONTRIBUTING file. Run the app locally (see [Quick start](README.md#quick-start)) and explore the API at **http://localhost:8000/docs**. Good first tasks: improving README or translations, adding tests, small UI tweaks, or fixing issues labeled "good first issue."

## How to set up locally

Same as [Quick start](README.md#quick-start) in the README:

1. Backend: `cd backend`, create and activate venv, `pip install -r requirements.txt`, copy `.env.example` to `.env`, run `uvicorn main:app --reload --host 0.0.0.0 --port 8000`.
2. Frontend: `cd frontend`, `npm install`, `npm run dev`.
3. Open http://localhost:5173 and API docs at http://localhost:8000/docs.

## Lint and tests before pushing

- **Backend:** Run Ruff (if configured): `ruff check backend/`. Run tests: `pytest backend/tests -v` from repo root with backend venv activated.
- **Frontend:** Run ESLint: `npm run lint`. Run tests: `npm run test` (if configured).

## Branch and PR workflow

- Branch from `main` (or the default branch).
- Open a pull request with a short description of the change.
- Ensure lint and tests pass. If CI is set up, wait for it to pass.

Full build and design details: see the implementation plan in `docs/` (if present).
