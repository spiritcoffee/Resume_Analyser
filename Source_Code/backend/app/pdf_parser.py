import io
import re
from pypdf import PdfReader


SECTION_HEADER_MAP = {
    "summary": "SUMMARY",
    "professional summary": "SUMMARY",
    "objective": "SUMMARY",
    "career objective": "SUMMARY",
    "about me": "SUMMARY",
    "profile": "SUMMARY",
    "experience": "EXPERIENCE",
    "work experience": "EXPERIENCE",
    "professional experience": "EXPERIENCE",
    "employment": "EXPERIENCE",
    "internships": "EXPERIENCE",
    "skills": "SKILLS",
    "technical skills": "SKILLS",
    "core competencies": "SKILLS",
    "projects": "PROJECTS",
    "academic projects": "PROJECTS",
    "personal projects": "PROJECTS",
    "education": "EDUCATION",
    "academic background": "EDUCATION",
    "qualifications": "EDUCATION",
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes and normalize common resume section headers."""
    reader = PdfReader(io.BytesIO(file_bytes))
    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages_text.append(text)

    raw_text = "\n".join(pages_text)
    return normalize_resume_text(raw_text)


def normalize_resume_text(raw_text: str) -> str:
    """Clean whitespace and standardize section headings for live editing."""
    lines = raw_text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = re.sub(r"\s+", " ", line).strip()
        if not stripped:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        # Normalize bullet characters to clean '- '
        stripped = re.sub(r"^[•●▪◦‣]\s*", "- ", stripped)

        # Check if line is a known section header
        header_key = re.sub(r"[:\-_]+$", "", stripped).strip().lower()
        if header_key in SECTION_HEADER_MAP:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            cleaned_lines.append(f"## {SECTION_HEADER_MAP[header_key]}")
        else:
            cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines).strip()
