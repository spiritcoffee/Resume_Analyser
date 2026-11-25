import re
from typing import Dict, List

from .models import (
    AnalyzeRequest,
    AnalyzeResponse,
    CalibrationConfig,
    CriterionResult,
    SectionScore,
)


SECTION_ORDER = ["Contact", "Summary", "Experience", "Skills", "Projects", "Education"]

# Longest phrases first so "work experience" wins over a bare "experience".
SECTION_KEYWORDS: Dict[str, List[str]] = {
    "Summary": [
        "professional summary",
        "career summary",
        "career objective",
        "about me",
        "summary",
        "objective",
        "profile",
    ],
    "Experience": [
        "professional experience",
        "work experience",
        "employment history",
        "work history",
        "internships",
        "internship",
        "experience",
        "employment",
    ],
    "Skills": [
        "technical skills",
        "core competencies",
        "key skills",
        "competencies",
        "technologies",
        "skills",
    ],
    "Projects": [
        "academic projects",
        "personal projects",
        "projects",
        "project",
    ],
    "Education": [
        "academic background",
        "academic qualifications",
        "qualifications",
        "academics",
        "education",
    ],
}

# Words that may surround a section keyword without turning the line into prose.
HEADING_NOISE = {
    "and", "or", "plus", "with", "of", "to", "in", "for", "the", "a", "an",
    "my", "our", "key", "core", "technical", "professional", "work", "academic",
    "personal", "relevant", "selected", "major", "overview", "details",
    "information", "history", "achievement", "achievements", "highlight",
    "highlights", "section", "list", "record", "research", "teaching",
    "leadership", "volunteer", "community", "industry", "freelance", "consulting",
}

HEADING_MARKDOWN_RE = re.compile(r"^#{1,6}\s*")
BULLET_START_RE = re.compile(r"^[-*•]\s+")

ACTION_VERBS = {
    "achieved", "accelarated", "accelerated", "analyzed", "architected", "automated",
    "boosted", "built", "collaborated", "configured", "coordinated", "created",
    "cut", "debugged", "decreased", "delivered", "deployed", "designed", "developed",
    "documented", "drove", "engineered", "enhanced", "established", "evaluated",
    "fixed",
    "generated", "grew", "implemented", "improved", "increased", "integrated",
    "launched", "led", "maintained", "managed", "mentored", "migrated", "monitored",
    "optimized", "owned", "presented", "reduced", "redesigned", "researched",
    "revamped", "scaled", "secured", "spearheaded", "streamlined", "tested",
    "trained", "transformed", "won",
}

ROLE_STOPWORDS = {
    "and", "the", "with", "for", "role", "job", "developer", "engineer",
    "analyst", "manager", "specialist", "associate",
}

EMAIL_RE = re.compile(r"[\w.\-+]+@[\w\-]+\.[\w.\-]+")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s\-().]{7,}\d)")
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
DEGREE_RE = re.compile(
    r"\b(?:b\.?\s?tech|m\.?\s?tech|b\.?\s?e\.?|m\.?\s?e\.?|b\.?\s?sc|m\.?\s?sc|"
    r"b\.?\s?s\.?|m\.?\s?s\.?|bca|mca|bachelor|master|ph\.?\s?d|diploma)\b",
    re.IGNORECASE,
)
INSTITUTION_RE = re.compile(
    r"\b(?:university|college|institute|school|academy|polytechnic)\b",
    re.IGNORECASE,
)
GPA_RE = re.compile(
    r"\b(?:gpa|cgpa|percentage|percent|honors?|honours?|distinction|first\s+class)\b"
    r"|\b\d{1,2}(?:\.\d+)?\s*/\s*\d{1,2}(?:\.\d+)?\b",
    re.IGNORECASE,
)
COURSEWORK_RE = re.compile(
    r"\b(?:coursework|courses|subjects|specialization|electives|curriculum)\b",
    re.IGNORECASE,
)
SENIORITY_RE = re.compile(
    r"\b(?:\d+\+?\s*years?|graduate|student|intern|fresher|entry[\s-]level|"
    r"senior|lead|mid[\s-]level|experienced)\b",
    re.IGNORECASE,
)

METRIC_PATTERNS = [
    r"\b\d+(?:\.\d+)?\s?%",
    r"[$€£]\s?\d[\d,.]*",
    r"\b\d+(?:\.\d+)?\s?x\b",
    r"\b\d+(?:\.\d+)?\s?[KkMmBb]\+?\b",
    r"\b\d[\d,]*\+?\s+(?:users?|customers?|clients?|requests?|records?|rows?|"
    r"transactions?|projects?|teams?|engineers?|students?|downloads?|installs?|"
    r"tickets?|leads?|hours?|days?|weeks?|months?)\b",
    r"\b(?:reduced|increased|improved|cut|saved|grew|boosted|accelerated|decreased)\b"
    r"[^.\n]{0,40}\b(?:by|to)\s+\$?\d[\d,.]*\s?"
    r"(?:%|x|hours?|days?|weeks?|months?|ms|seconds?)\b",
    r"\b\d+(?:\.\d+)?\s?(?:ms|seconds?|secs?|minutes?)\b",
]

DOMAIN_KEYWORDS = {
    "software": {
        "python", "java", "javascript", "typescript", "react", "node", "node.js",
        "fastapi", "django", "flask", "sql", "postgresql", "mysql", "mongodb",
        "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux", "html",
        "css", "rest", "api", "apis", "backend", "frontend", "full-stack",
        "web", "graphql", "microservices", "c++", "c#", ".net", "spring",
        "flutter", "swift", "kotlin", "redis", "ci/cd", "testing", "pytest",
        "jest", "data structures", "algorithms",
    },
    "data": {
        "python", "sql", "pandas", "numpy", "scikit-learn", "sklearn",
        "tensorflow", "pytorch", "keras", "machine learning", "deep learning",
        "nlp", "computer vision", "tableau", "power bi", "excel", "statistics",
        "regression", "classification", "clustering", "bigquery", "spark",
        "airflow", "etl", "data visualization", "a/b testing", "matlab",
    },
    "product": {
        "product management", "roadmap", "stakeholder", "user research",
        "analytics", "a/b testing", "jira", "confluence", "figma", "kpi",
        "okr", "agile", "scrum", "wireframe", "prototyping", "go-to-market",
        "requirement", "prd", "sql", "excel", "tableau", "mixpanel", "amplitude",
    },
    "general": {
        "communication", "leadership", "project management", "excel", "sql",
        "analytics", "stakeholder", "problem solving", "teamwork",
        "documentation", "reporting", "budgeting", "operations",
        "customer service", "sales", "marketing",
    },
}

TOOL_KEYWORDS = {
    "python", "java", "javascript", "typescript", "react", "node", "node.js",
    "fastapi", "django", "flask", "sql", "postgresql", "mysql", "mongodb",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux", "html",
    "css", "rest", "graphql", "c++", "c#", ".net", "spring", "flutter", "swift",
    "kotlin", "redis", "pytest", "jest", "pandas", "numpy", "scikit-learn",
    "sklearn", "tensorflow", "pytorch", "keras", "tableau", "power bi", "excel",
    "spark", "airflow", "bigquery", "jira", "confluence", "figma", "mixpanel",
    "amplitude", "matlab",
}


def get_dynamic_weights(config: CalibrationConfig) -> Dict[str, float]:
    """Return section weights (summing to 1.0) for the experience level."""
    if config.experience_level == "experienced":
        weights = {
            "Contact": 0.10,
            "Summary": 0.15,
            "Experience": 0.35,
            "Skills": 0.20,
            "Projects": 0.10,
            "Education": 0.10,
        }
    else:
        weights = {
            "Contact": 0.10,
            "Summary": 0.15,
            "Experience": 0.20,
            "Skills": 0.20,
            "Projects": 0.20,
            "Education": 0.15,
        }

    total = sum(weights.values())
    return {key: round(value / total, 4) for key, value in weights.items()}


def _phrase_index(words: List[str], phrase: List[str]) -> int | None:
    span = len(phrase)
    if not span:
        return None
    for index in range(len(words) - span + 1):
        if words[index : index + span] == phrase:
            return index
    return None


def _detect_heading(line: str) -> tuple[str, str] | None:
    """Return (section, inline_content) when a line is a section heading."""
    stripped = line.strip()
    if not stripped or BULLET_START_RE.match(stripped):
        return None

    marked = bool(HEADING_MARKDOWN_RE.match(stripped))
    candidate = HEADING_MARKDOWN_RE.sub("", stripped).strip()

    inline = ""
    colon = re.match(r"^([^:]{2,45}):\s*(\S.*)$", candidate)
    if colon:
        candidate, inline = colon.group(1), colon.group(2).strip()

    candidate = candidate.strip().strip("-–—:|").strip()
    words = re.findall(r"[A-Za-z]+", candidate.lower())
    if not words or len(words) > 8 or len(candidate) > 70:
        return None

    best: tuple[int, int, str, List[str]] | None = None
    for section, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            keyword_words = keyword.split()
            start = _phrase_index(words, keyword_words)
            if start is None:
                continue
            rank = (start, -len(keyword_words))
            if best is None or rank < (best[0], best[1]):
                best = (rank[0], rank[1], section, keyword_words)

    if best is None:
        return None

    start, _, section, keyword_words = best
    if not marked:
        covered = set(range(start, start + len(keyword_words)))
        extra = [word for index, word in enumerate(words) if index not in covered]
        if any(word not in HEADING_NOISE for word in extra):
            return None

    return section, inline


def _collect_section_lines(resume_text: str) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {name: [] for name in SECTION_ORDER}
    current_section = "Contact"

    for line in resume_text.splitlines():
        detected = _detect_heading(line)
        if detected:
            current_section, inline = detected
            if inline:
                sections[current_section].append(inline)
            continue
        sections[current_section].append(line)

    return sections


def split_into_sections(resume_text: str) -> Dict[str, str]:
    """Parse resume text into the six standard sections."""
    return {
        name: "\n".join(lines).strip()
        for name, lines in _collect_section_lines(resume_text).items()
    }


def split_into_sections_with_spans(
    resume_text: str,
) -> Dict[str, tuple[str, int, int]]:
    """Map each section to (text, start, end) offsets within the resume text."""
    parsed = split_into_sections(resume_text)
    spans: Dict[str, tuple[str, int, int]] = {
        name: (text, -1, -1) for name, text in parsed.items()
    }

    located: List[tuple[int, str, str]] = []
    for name, text in parsed.items():
        if not text:
            continue
        index = resume_text.find(text)
        if index >= 0:
            located.append((index, name, text))

    located.sort()
    cursor = 0
    for index, name, text in located:
        if index < cursor:
            continue  # over-lapping sections cannot be replaced safely
        spans[name] = (text, index, index + len(text))
        cursor = index + len(text)

    return spans


def _check(
    criterion_id: str,
    label: str,
    earned: int,
    max_points: int,
    advice: str,
    example: str = "",
) -> CriterionResult:
    earned = max(0, min(max_points, earned))
    return CriterionResult(
        id=criterion_id,
        label=label,
        earned=earned,
        max_points=max_points,
        passed=earned >= max_points,
        advice=advice,
        example=example,
    )


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w+#.-]+\b", text))


def _keyword_hit(text: str, keyword: str) -> bool:
    keyword = keyword.lower()
    if len(keyword) <= 1:
        return False
    if not keyword.isalnum():
        return keyword in text
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def _count_hits(text: str, keywords: set[str]) -> int:
    lower = text.lower()
    return sum(1 for keyword in keywords if _keyword_hit(lower, keyword))


def _count_domain_hits(text: str, domain: str) -> int:
    return _count_hits(text, DOMAIN_KEYWORDS.get(domain, DOMAIN_KEYWORDS["general"]))


def _count_tool_hits(text: str) -> int:
    return _count_hits(text, TOOL_KEYWORDS)


def extract_metrics(text: str) -> List[str]:
    """Return quantified impact strings while ignoring standalone years."""
    found: List[str] = []
    for pattern in METRIC_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group(0).strip()
            if not value:
                continue
            if re.fullmatch(r"(?:19|20)\d{2}", value):
                continue
            found.append(value)

    unique: List[str] = []
    seen = set()
    for value in found:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            unique.append(value)
    return unique


def _get_bullets(text: str) -> List[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    explicit = [
        re.sub(r"^[-*•]\s*", "", line)
        for line in lines
        if re.match(r"^[-*•]\s+", line)
    ]
    if len(explicit) >= 2:
        return explicit
    return [line for line in lines if len(line.split()) >= 5]


def _starts_with_action_verb(line: str) -> bool:
    match = re.match(r"^([A-Za-z][A-Za-z-]*)", line)
    return bool(match and match.group(1).lower() in ACTION_VERBS)


def _action_verb_count(bullets: List[str]) -> int:
    return sum(1 for bullet in bullets if _starts_with_action_verb(bullet))


def _skill_items(text: str) -> List[str]:
    parts = re.split(r"[,|;•\n]", text)
    items: List[str] = []
    for raw in parts:
        item = raw.strip(" \t-*")
        if ":" in item:
            item = item.split(":", 1)[1].strip()
        if len(item) > 1:
            items.append(item)

    unique: List[str] = []
    seen = set()
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def _category_count(text: str) -> int:
    categories = set()
    for line in re.split(r"[\n;]", text):
        if ":" not in line:
            continue
        category = line.split(":", 1)[0].strip().lower()
        if category:
            categories.add(category)
    return len(categories)


def _has_name(text: str) -> bool:
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return bool(
        re.match(
            r"^[A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){1,3}$",
            first_line,
        )
    )


def _has_portfolio_link(text: str) -> bool:
    lower = text.lower()
    if "github.com" in lower or "gitlab.com" in lower or "portfolio" in lower:
        return True
    urls = re.findall(r"https?://[^\s|,;]+", text, flags=re.IGNORECASE)
    return any("linkedin.com" not in url.lower() for url in urls)


def _summary_role_aligned(text: str, config: CalibrationConfig) -> bool:
    lower = text.lower()
    role_tokens = [
        token
        for token in re.findall(r"[a-z]{3,}", config.target_role.lower())
        if token not in ROLE_STOPWORDS
    ]
    if role_tokens and any(token in lower for token in role_tokens):
        return True
    return _count_domain_hits(text, config.target_domain) >= 2


def _score_contact(text: str, config: CalibrationConfig) -> List[CriterionResult]:
    lower = text.lower()
    has_email = bool(EMAIL_RE.search(text))
    has_phone = bool(PHONE_RE.search(text))
    has_linkedin = "linkedin.com" in lower
    has_portfolio = _has_portfolio_link(text)
    has_name = _has_name(text)

    return [
        _check(
            "contact-name",
            "Full name in header",
            10 if has_name else 0,
            10,
            "Start the resume with your full name on its own line.",
            "Alex Rivera",
        ),
        _check(
            "contact-email",
            "Professional email address",
            30 if has_email else 0,
            30,
            "Add a professional email address.",
            "alex.rivera@email.com",
        ),
        _check(
            "contact-phone",
            "Phone number",
            20 if has_phone else 0,
            20,
            "Add a contact phone number.",
            "+1 (555) 234-5678",
        ),
        _check(
            "contact-linkedin",
            "LinkedIn profile",
            20 if has_linkedin else 0,
            20,
            "Add your LinkedIn profile URL.",
            "linkedin.com/in/alexrivera",
        ),
        _check(
            "contact-portfolio",
            "GitHub / portfolio link",
            20 if has_portfolio else 0,
            20,
            (
                "Add a GitHub link for technical roles, or a portfolio/website link."
                if config.target_domain in ("software", "data")
                else "Add a portfolio or personal website link."
            ),
            "github.com/alexrivera",
        ),
    ]


def _score_summary(text: str, config: CalibrationConfig) -> List[CriterionResult]:
    word_count = _word_count(text)
    if 25 <= word_count <= 80:
        length_earned = 25
    elif 15 <= word_count <= 100:
        length_earned = 15
    else:
        length_earned = 0

    has_metric = bool(extract_metrics(text))
    has_role = _summary_role_aligned(text, config)
    has_seniority = bool(SENIORITY_RE.search(text))
    has_skills = (
        _count_domain_hits(text, config.target_domain) >= 2
        or _count_tool_hits(text) >= 2
    )

    return [
        _check(
            "summary-length",
            "25-80 word summary",
            length_earned,
            25,
            "Keep the summary to 2-3 sentences (about 25-80 words).",
            "Computer Science graduate with hands-on experience building FastAPI and React applications.",
        ),
        _check(
            "summary-role",
            "Target-role alignment",
            20 if has_role else 0,
            20,
            "Mention the target role or at least two keywords from the target domain.",
            "Seeking a Backend Software Engineer role focused on Python and distributed systems.",
        ),
        _check(
            "summary-seniority",
            "Seniority / experience signal",
            15 if has_seniority else 0,
            15,
            "State your level, e.g. final-year student, recent graduate, or 4+ years of experience.",
            "Final-year Computer Science student with 2 internship experiences.",
        ),
        _check(
            "summary-metric",
            "Quantified achievement",
            20 if has_metric else 0,
            20,
            "Add one measurable result to the summary.",
            "Delivered 3 production-ready projects with automated tests.",
        ),
        _check(
            "summary-skills",
            "Relevant skills or tools",
            20 if has_skills else 0,
            20,
            "Name at least two tools or skills that matter for the target domain.",
            "Python, FastAPI, React, PostgreSQL",
        ),
    ]


def _score_experience(text: str, config: CalibrationConfig) -> List[CriterionResult]:
    bullets = _get_bullets(text)
    metrics = extract_metrics(text)
    has_timeline = bool(YEAR_RE.search(text))
    has_relevance = (
        _count_domain_hits(text, config.target_domain) >= 1
        or _count_tool_hits(text) >= 1
    )

    return [
        _check(
            "experience-timeline",
            "Role and timeline with year",
            20 if has_timeline else 0,
            20,
            "Include at least one role with a company and a year or date range.",
            "Software Engineer - BrightApps (2024 - 2025)",
        ),
        _check(
            "experience-bullets",
            "3+ experience bullets",
            20 if len(bullets) >= 3 else 0,
            20,
            "Use at least three bullet points per role.",
            "- Engineered REST APIs with FastAPI.\n- Automated tests with pytest.\n- Reduced response time by 35%.",
        ),
        _check(
            "experience-verbs",
            "Action-verb bullets",
            20 if _action_verb_count(bullets) >= 2 else 0,
            20,
            "Start each bullet with a strong action verb such as Built, Engineered, Reduced, or Led.",
            "Engineered a REST API using FastAPI and PostgreSQL.",
        ),
        _check(
            "experience-metrics",
            "2+ quantified metrics",
            25 if len(metrics) >= 2 else 0,
            25,
            "Add at least two numbers such as %, $, users, latency, or time saved.",
            "Reduced API latency by 35% across 20k daily requests.",
        ),
        _check(
            "experience-relevance",
            "Domain or tool keywords",
            15 if has_relevance else 0,
            15,
            "Mention relevant tools or domain terms in the experience section.",
            "FastAPI, PostgreSQL, Docker, AWS",
        ),
    ]


def _score_skills(text: str, config: CalibrationConfig) -> List[CriterionResult]:
    items = _skill_items(text)
    categories = _category_count(text)
    domain_hits = _count_domain_hits(text, config.target_domain)
    tool_hits = _count_tool_hits(text)

    return [
        _check(
            "skills-count",
            "8+ listed skills",
            30 if len(items) >= 8 else 0,
            30,
            "List at least eight relevant skills.",
            "Python, JavaScript, TypeScript, React, FastAPI, PostgreSQL, Docker, Git",
        ),
        _check(
            "skills-categories",
            "2+ skill categories",
            25 if categories >= 2 else 0,
            25,
            "Group skills into categories such as Languages, Frameworks, and Tools.",
            "Languages: Python, JavaScript\nFrameworks: FastAPI, React\nTools: Docker, Git",
        ),
        _check(
            "skills-domain",
            "Domain-relevant skills",
            25 if domain_hits >= 3 else 0,
            25,
            "Add at least three skills that are relevant to the target domain.",
            "FastAPI, PostgreSQL, Docker",
        ),
        _check(
            "skills-tools",
            "Tools, languages, or frameworks",
            20 if tool_hits >= 2 else 0,
            20,
            "Include at least two concrete tools, languages, or frameworks.",
            "Python, React",
        ),
    ]


def _score_projects(text: str, config: CalibrationConfig) -> List[CriterionResult]:
    bullets = _get_bullets(text)
    metrics = extract_metrics(text)
    tool_hits = _count_tool_hits(text)
    has_tech = tool_hits >= 1 or "|" in text

    return [
        _check(
            "projects-tech",
            "Project name and tech stack",
            20 if has_tech else 0,
            20,
            "List each project with its name and tech stack, e.g. 'Resume Analyser | Python, FastAPI, React'.",
            "Resume Analyser | Python, FastAPI, React, PostgreSQL",
        ),
        _check(
            "projects-bullets",
            "2+ project bullets",
            20 if len(bullets) >= 2 else 0,
            20,
            "Describe each project with at least two bullet points.",
            "- Built a full-stack resume analyser with FastAPI and React.\n- Added 40 automated tests with pytest.",
        ),
        _check(
            "projects-verbs",
            "Action-verb bullets",
            20 if _action_verb_count(bullets) >= 2 else 0,
            20,
            "Start project bullets with action verbs such as Built, Designed, Implemented, or Deployed.",
            "Built a full-stack resume analyser using FastAPI and React.",
        ),
        _check(
            "projects-metric",
            "Quantified project result",
            20 if metrics else 0,
            20,
            "Add at least one measurable result, such as users, accuracy, latency, or test coverage.",
            "Achieved 95% test coverage across 40 automated tests.",
        ),
        _check(
            "projects-tools",
            "2+ tech or tool keywords",
            20 if tool_hits >= 2 else 0,
            20,
            "Mention at least two technologies used in the project.",
            "FastAPI, React, PostgreSQL",
        ),
    ]


def _score_education(text: str, config: CalibrationConfig) -> List[CriterionResult]:
    has_degree = bool(DEGREE_RE.search(text))
    has_institution = bool(INSTITUTION_RE.search(text))
    has_year = bool(YEAR_RE.search(text))
    has_gpa = bool(GPA_RE.search(text))
    has_coursework = bool(COURSEWORK_RE.search(text))

    return [
        _check(
            "education-degree",
            "Degree title",
            30 if has_degree else 0,
            30,
            "State your degree clearly, e.g. B.Tech in Computer Science.",
            "B.Tech in Computer Science and Engineering",
        ),
        _check(
            "education-institution",
            "Institution name",
            20 if has_institution else 0,
            20,
            "Include the university, college, or institute name.",
            "State University",
        ),
        _check(
            "education-year",
            "Graduation year",
            20 if has_year else 0,
            20,
            "Add your graduation year or expected completion year.",
            "2022 - 2026",
        ),
        _check(
            "education-gpa",
            "GPA, percentage, or honors",
            15 if has_gpa else 0,
            15,
            "Add your CGPA if it is strong, or list honors and distinctions.",
            "CGPA: 8.6/10",
        ),
        _check(
            "education-coursework",
            "Relevant coursework",
            15 if has_coursework else 0,
            15,
            "List relevant coursework such as Data Structures, DBMS, or Machine Learning.",
            "Relevant Coursework: Data Structures, Algorithms, DBMS, Machine Learning",
        ),
    ]


def _score_section(
    name: str, text: str, config: CalibrationConfig
) -> List[CriterionResult]:
    if name == "Contact":
        return _score_contact(text, config)
    if name == "Summary":
        return _score_summary(text, config)
    if name == "Experience":
        return _score_experience(text, config)
    if name == "Skills":
        return _score_skills(text, config)
    if name == "Projects":
        return _score_projects(text, config)
    return _score_education(text, config)


def analyze_resume(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the explainable, rule-based ATS rubric across all sections."""
    parsed_sections = split_into_sections(request.resume_text)
    weights = get_dynamic_weights(request.calibration)
    previous_scores = request.previous_scores or {}

    section_results: List[SectionScore] = []
    total_weighted = 0.0

    for section_name in SECTION_ORDER:
        section_text = parsed_sections.get(section_name, "")
        criteria = _score_section(section_name, section_text, request.calibration)
        score = min(100, sum(criterion.earned for criterion in criteria))
        weight = weights[section_name]
        weighted_contribution = round(score * weight, 2)
        total_weighted += weighted_contribution

        previous = previous_scores.get(section_name)
        delta = (score - previous) if previous is not None else None

        section_results.append(
            SectionScore(
                name=section_name,
                score=score,
                weight=weight,
                weighted_contribution=weighted_contribution,
                previous_score=previous,
                delta=delta,
                criteria=criteria,
            )
        )

    overall = int(min(100, max(0, round(total_weighted))))
    overall_delta = (
        (overall - request.previous_overall)
        if request.previous_overall is not None
        else None
    )
    word_count = len(re.findall(r"\b\w+\b", request.resume_text))

    return AnalyzeResponse(
        overall_score=overall,
        previous_overall=request.previous_overall,
        overall_delta=overall_delta,
        sections=section_results,
        word_count=word_count,
    )
