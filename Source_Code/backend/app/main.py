from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .ai_suggester import generate_suggestions
from .models import (
    AnalyzeRequest,
    AnalyzeResponse,
    SuggestRequest,
    SuggestResponse,
)
from .pdf_parser import extract_text_from_pdf
from .scorer import analyze_resume

app = FastAPI(title="ATS Resume Analyser", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLE_RESUME = """Alex Rivera
alex.rivera@email.com | +1 (555) 234-5678

## SUMMARY
Motivated Computer Science student looking for a software internship to learn new technologies.

## EXPERIENCE
Software Intern - BrightApps (Summer 2025)
- Worked on backend tasks and helped the team with APIs.
- Fixed bugs in the frontend dashboard.

## SKILLS
Python, JavaScript, HTML, CSS, Git

## PROJECTS
Task Tracker App
- Built a to-do list web app for managing daily tasks.

## EDUCATION
B.Tech in Computer Science, State University (2022 - 2026)
"""


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/sample-resume")
def get_sample_resume():
    return {"resume_text": SAMPLE_RESUME}


@app.post("/api/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid .pdf file.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded PDF file is empty.")

    try:
        extracted = extract_text_from_pdf(file_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {exc}") from exc

    if not extracted:
        raise HTTPException(status_code=400, detail="No readable text found in PDF.")

    return {"filename": file.filename, "resume_text": extracted}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    if not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")
    return analyze_resume(request)


@app.post("/api/suggest", response_model=SuggestResponse)
def suggest(request: SuggestRequest):
    if not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")
    return generate_suggestions(request)
