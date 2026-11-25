# ATS Resume Analyser (Group 1)

A split-screen resume analyser that scores a resume with an **explainable, 100% rule-based ATS rubric** and uses **Google Gemini only for rewrite suggestions**. No RAG, no vector search, and no LLM-computed score.

## Features

- **ATS Readiness Score** across six sections: Contact, Summary, Experience, Skills, Projects, Education.
- **Point-by-point ATS checks** — every section score is the sum of explicit criteria, with no free base points.
- **Calibration** — experience level changes section weights; target domain and optional target role tailor the checks.
- **PDF-to-Editable-Text** — upload a `.pdf` resume or load the sample, then edit it in the source editor or formatted preview.
- **Recheck with deltas** — edit the resume, click **Recheck Score**, and see updated section scores with `+delta` badges.
- **Gemini rewrite suggestions** — grounded in the failed ATS checks and the exact resume text. A rule-based fallback works without an API key.
- **Safe replacement** — a suggestion can replace its exact source snippet in the resume; if the snippet is gone, the app asks you to copy instead of appending text.
- **Export** — download the edited resume as `.txt`.

## Scoring

Each section has criteria that sum to 100 points:

- Contact: name, email, phone, LinkedIn, GitHub/portfolio
- Summary: length, role alignment, seniority signal, quantified achievement, relevant skills
- Experience: timeline, bullets, action verbs, metrics, domain keywords
- Skills: skill count, categories, domain relevance, tools
- Projects: tech stack, bullets, action verbs, metrics, tool keywords
- Education: degree, institution, graduation year, GPA/honors, coursework

Overall score = weighted average of section scores. Fresher weights emphasise Projects and Education; experienced weights emphasise Experience.

## How to Run

### 1. Backend (FastAPI)

```powershell
cd Group_1\Source_Code\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (React + Vite)

```powershell
cd Group_1\Source_Code\frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Tests

```powershell
cd Group_1\Source_Code\backend
pytest -v
```

### Frontend Build

```powershell
cd Group_1\Source_Code\frontend
npm run build
```

## API

- `GET /api/health`
- `GET /api/sample-resume`
- `POST /api/parse-pdf`
- `POST /api/analyze` — ATS scores and criterion breakdowns
- `POST /api/suggest` — Gemini rewrite suggestions, or rule-based fallback advice

## Documentation

- [Software Requirements Specification](../Documentation/SRS.md) — requirements, scoring model, interfaces, verification.
- Print-ready copy: `Documentation/SRS.html` (open in a browser, then Print → Save as PDF).

## Notes

- The ATS score is a transparent readiness rubric, not a simulation of a commercial ATS.
- Gemini is optional. Without a key, suggestions still work as copyable rule-based advice.
- A Gemini API key can be supplied per session in the toolbar or through `GEMINI_API_KEY` in the backend environment.
