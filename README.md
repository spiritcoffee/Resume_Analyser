# ATS Resume Analyser — Group 1

A split-screen resume analyser that scores a resume against an **explicit, 100% rule-based
ATS rubric**, shows the points earned for every check, and offers **Gemini-assisted rewrites**
that can be applied to the resume and immediately re-scored.

No RAG, no vector search, no chat, and no LLM-computed score.

## Repository Contents

| Path | What it is |
| --- | --- |
| [`Source_Code/`](Source_Code) | FastAPI backend, React + Vite frontend, tests |
| [`Documentation/SRS.md`](Documentation/SRS.md) | Software Requirements Specification (Markdown) |
| [`Documentation/SRS.html`](Documentation/SRS.html) | Print-ready SRS — open and use Print → Save as PDF |
| [`implementation_plan.md`](implementation_plan.md) | Current design and scope decisions |

## What It Does

1. **Ingest** — upload a PDF (text is normalised into editable sections) or load the sample.
2. **Calibrate** — fresher or experienced, target domain, optional target role.
3. **Score** — six sections (Contact, Summary, Experience, Skills, Projects, Education), each
   0–100 from explicit criteria, combined into a weighted overall score.
4. **Explain** — every criterion shows points earned, points available, and what to write.
5. **Suggest** — Gemini rewrites the weakest checks using the candidate's own text; without a
   key, deterministic rule-based advice is returned instead.
6. **Apply safely** — a rewrite replaces its exact source snippet, or is copy-only when that
   snippet no longer exists. Text is never appended.
7. **Recheck** — re-score after editing and see per-section and overall deltas.

## Quick Start

```powershell
# Backend
cd Source_Code\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```powershell
# Frontend (new terminal)
cd Source_Code\frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Gemini is optional: paste a key in the toolbar or set
`GEMINI_API_KEY` in `Source_Code/backend/.env` (see `.env.example`).

## Verification

```powershell
cd Source_Code\backend
pytest -q            # 10 passed

cd ..\frontend
npm run build        # tsc + vite, clean
```

## Documentation Build

`Documentation/SRS.html` is generated from `SRS.md`:

```powershell
pip install markdown
python Documentation\build_docs.py
```

## Team

Group 1.
