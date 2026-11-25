from fastapi.testclient import TestClient

from app.ai_suggester import _parse_json_array, _validate_original
from app.main import SAMPLE_RESUME, app
from app.models import CalibrationConfig
from app.scorer import extract_metrics, get_dynamic_weights

client = TestClient(app)

STRONG_RESUME = """Jordan Lee
jordan.lee@email.com | +1 (555) 987-6543 | linkedin.com/in/jordanlee | github.com/jordanlee

## SUMMARY
Final-year Computer Science student and backend developer with 2 years of internship experience building Python and FastAPI services. Delivered 3 production-ready projects with automated tests, including an API that reduced response time by 35% across 20k daily requests. Seeking a Backend Software Engineer role focused on scalable systems.

## EXPERIENCE
Software Engineering Intern - BrightApps (2024 - 2025)
- Engineered REST APIs with FastAPI and PostgreSQL, reducing average latency by 35% across 20k daily requests.
- Automated CI/CD tests with pytest and GitHub Actions, cutting deployment regressions by 40%.
- Collaborated with 4 engineers to ship a React dashboard used by 500+ customers.

## SKILLS
Languages: Python, JavaScript, TypeScript, SQL
Frameworks: FastAPI, React, Node.js
Tools: PostgreSQL, Docker, Git, AWS

## PROJECTS
Resume Analyser | Python, FastAPI, React, PostgreSQL
- Built a full-stack resume analyser with FastAPI and React, serving 500+ test users.
- Implemented 40 automated tests with pytest, achieving 95% coverage.
- Deployed the API on AWS with Docker and monitored 20k requests per day.

## EDUCATION
B.Tech in Computer Science, State University (2022 - 2026)
CGPA: 8.6/10
Relevant Coursework: Data Structures, Algorithms, DBMS, Machine Learning
"""


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_calibration_weights_differ_by_level():
    fresher_weights = get_dynamic_weights(CalibrationConfig(experience_level="fresher"))
    experienced_weights = get_dynamic_weights(
        CalibrationConfig(experience_level="experienced")
    )
    assert fresher_weights["Projects"] > experienced_weights["Projects"]
    assert experienced_weights["Experience"] > fresher_weights["Experience"]
    assert abs(sum(fresher_weights.values()) - 1.0) < 0.01
    assert abs(sum(experienced_weights.values()) - 1.0) < 0.01


def test_every_section_has_100_points():
    res = client.post("/api/analyze", json={"resume_text": SAMPLE_RESUME})
    assert res.status_code == 200
    data = res.json()
    assert len(data["sections"]) == 6

    for section in data["sections"]:
        assert sum(item["max_points"] for item in section["criteria"]) == 100
        assert section["score"] == sum(item["earned"] for item in section["criteria"])
        assert 0 <= section["score"] <= 100


def test_strong_resume_scores_high():
    res = client.post(
        "/api/analyze",
        json={
            "resume_text": STRONG_RESUME,
            "calibration": {"experience_level": "fresher", "target_domain": "software"},
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["overall_score"] >= 90
    for section in data["sections"]:
        assert section["score"] >= 90, section["name"]


def test_analyze_and_recheck_delta():
    res1 = client.post(
        "/api/analyze",
        json={
            "resume_text": SAMPLE_RESUME,
            "calibration": {"experience_level": "fresher", "target_domain": "software"},
        },
    )
    assert res1.status_code == 200
    data1 = res1.json()
    prev_map = {s["name"]: s["score"] for s in data1["sections"]}
    prev_overall = data1["overall_score"]

    improved_resume = SAMPLE_RESUME.replace(
        "alex.rivera@email.com | +1 (555) 234-5678",
        "alex.rivera@email.com | +1 (555) 234-5678 | linkedin.com/in/alexrivera | github.com/alexrivera",
    ).replace(
        "- Worked on backend tasks and helped the team with APIs.",
        "- Engineered RESTful APIs using FastAPI and PostgreSQL, reducing latency by 35% across 20k requests.",
    )

    res2 = client.post(
        "/api/analyze",
        json={
            "resume_text": improved_resume,
            "calibration": {"experience_level": "fresher", "target_domain": "software"},
            "previous_scores": prev_map,
            "previous_overall": prev_overall,
        },
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["overall_score"] > prev_overall
    assert data2["overall_delta"] > 0


def test_metrics_ignore_years():
    assert extract_metrics("Worked on a project in 2025.") == []
    assert extract_metrics("Reduced latency by 35% across 20k requests.")


def test_gemini_json_parser_and_safe_snippet_validation():
    items = _parse_json_array(
        '```json\n[{"section":"Summary","original_text":"old text"}]\n```'
    )
    assert items == [{"section": "Summary", "original_text": "old text"}]

    original, replaceable = _validate_original("Built a small app.", "I Built a small app. today")
    assert replaceable is True
    assert original == "Built a small app."

    _, missing = _validate_original("This snippet is gone.", "A different resume.")
    assert missing is False


def test_rule_based_suggestions_without_api_key():
    analyze_res = client.post("/api/analyze", json={"resume_text": SAMPLE_RESUME})
    sections = analyze_res.json()["sections"]

    res = client.post(
        "/api/suggest",
        json={
            "resume_text": SAMPLE_RESUME,
            "sections": sections,
            "gemini_api_key": "",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["source"] == "rule_based"
    assert len(data["suggestions"]) > 0
    assert all(item["replaceable"] is False for item in data["suggestions"])


def test_rejects_empty_resume():
    res = client.post("/api/analyze", json={"resume_text": "   "})
    assert res.status_code == 400


def test_parse_pdf_rejects_non_pdf():
    res = client.post(
        "/api/parse-pdf",
        files={"file": ("resume.txt", b"not a pdf", "text/plain")},
    )
    assert res.status_code == 400
