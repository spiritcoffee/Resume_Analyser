# Software Requirements Specification

## ATS Resume Analyser

| Field | Value |
| --- | --- |
| Project | ATS Resume Analyser (Resume Analysis and Improvement Tool) |
| Group | Group 1 |
| Document | Software Requirements Specification (SRS) |
| Version | 1.0 |
| Date | 25 November 2026 |
| Status | Baseline — matches the implemented system |
| Repository | `Source_Code/` (FastAPI backend + React/Vite frontend) |

## Revision History

| Revision | Date | Description |
| --- | --- | --- |
| 0.1 | 25 Nov 2026 | Initial draft from the earlier RAG-based design |
| 1.0 | 25 Nov 2026 | Rewritten for the final 100% rule-based ATS design; RAG, hybrid scoring, and chat removed |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features](#3-system-features)
4. [Scoring Model](#4-scoring-model)
5. [External Interface Requirements](#5-external-interface-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [System Architecture](#7-system-architecture)
8. [Data Requirements](#8-data-requirements)
9. [Verification and Acceptance](#9-verification-and-acceptance)
10. [Constraints, Assumptions, and Risks](#10-constraints-assumptions-and-risks)
11. [Out of Scope and Future Work](#11-out-of-scope-and-future-work)
12. [Appendices](#12-appendices)

---

# 1. Introduction

## 1.1 Purpose

This SRS defines the requirements for the **ATS Resume Analyser**, a web application that
scores a resume against an explicit, rule-based Applicant Tracking System (ATS) rubric,
explains every deduction point by point, and offers AI-assisted rewrites that the user can
apply safely and re-score.

The document is written for the project team, the course evaluator, and any future
maintainer. It specifies *what* the system does and *how it is verified*, at a level of
detail that matches the code shipped in `Source_Code/`.

## 1.2 Problem Statement

Students and early-career applicants routinely receive rejections without any explanation.
Commercial ATS platforms hide their scoring, and generic advice ("add more keywords",
"use action verbs") cannot tell a candidate *which* line of *their* resume is failing or
*what to write instead*. The result is guesswork: candidates rewrite blindly, resubmit, and
still cannot tell whether the resume improved.

The system targets one core problem:

> **Candidates cannot see which specific parts of their resume an ATS rejects, or how to
> fix those parts in their own document.**

The product answers that with a transparent score, a point-by-point breakdown, and a
rewrite that can be applied to the candidate's own text and immediately re-scored.

## 1.3 Scope

### In scope

- Uploading a resume as a PDF and converting it into editable plain text.
- Loading a built-in sample resume for demonstration.
- Calibration by experience level (fresher / experienced), target domain, and optional
  target role.
- Deterministic ATS scoring across six standard resume sections.
- A per-criterion breakdown showing points earned, points available, and advice.
- AI-generated rewrite suggestions (Google Gemini), grounded in the failed criteria and the
  candidate's exact text, with a rule-based fallback when no key is configured.
- Safe application of a rewrite to the resume, followed by re-scoring with deltas.
- Exporting the edited resume as `.txt`.

### Deliberately out of scope

- Retrieval-Augmented Generation, vector databases, and embedding similarity.
- TF-IDF or any learned/hybrid scoring. The score is 100% rule-based.
- Chat with the resume. There is no conversational endpoint or chat pane.
- Job-description matching. The product has one core problem and does not attempt to score
  fit against a specific posting.
- Accounts, authentication, persistence, and multi-user storage.
- DOCX ingestion, OCR of scanned PDFs, and non-English resumes.
- Recruiter-side or bulk/enterprise features.

## 1.4 Definitions and Abbreviations

| Term | Meaning |
| --- | --- |
| **ATS** | Applicant Tracking System; software that parses and filters resumes before a human reads them. |
| **ATS Readiness Score** | The system's 0–100 weighted score. A transparent readiness rubric, not a reproduction of any commercial ATS. |
| **Section score** | A 0–100 score for one of Contact, Summary, Experience, Skills, Projects, Education. |
| **Criterion** | One explicit check inside a section, with an id, label, earned points, maximum points, advice, and an example. |
| **Calibration** | The user's experience level, target domain, and optional target role. Changes weights and some checks. |
| **Suggestion** | A structured rewrite: section, title, reason, optional original snippet, replacement text, and a replaceable flag. |
| **Replaceable** | True only when the suggestion's `original_text` was found verbatim in the current resume, so the UI may replace it. |
| **Bullet** | A resume line beginning with `-`, `*`, or `•`; if fewer than two such lines exist, any line of five or more words is treated as a bullet. |
| **Metric** | A quantified impact value (percentage, currency, multiplier, count with a unit, or a reduction/increase figure). Bare years are excluded. |
| **Gemini** | Google's generative model, used only to draft wording. It never computes or alters the score. |

## 1.5 References

1. IEEE 830-1998, *Recommended Practice for Software Requirements Specifications* — structural reference.
2. FastAPI documentation, https://fastapi.tiangolo.com
3. React documentation, https://react.dev
4. Vite documentation, https://vite.dev
5. `pypdf` documentation, https://pypdf.readthedocs.io
6. Google Gen AI SDK (Python), https://googleapis.github.io/python-genai
7. Project `README.md` and `implementation_plan.md` in the repository root.

## 1.6 Document Overview

Section 2 describes the product and its users. Section 3 specifies each feature with
inputs, behaviour, and acceptance criteria. Section 4 is the normative scoring model, which
is the heart of the system. Sections 5–6 cover interfaces and quality attributes. Section 7
maps requirements to the implemented architecture, and Sections 8–11 cover data,
verification, risks, and future work.

---

# 2. Overall Description

## 2.1 Product Perspective

The product is a self-contained, locally run web application with two processes:

- A **FastAPI** backend that parses PDFs, computes scores, and calls Gemini for suggestions.
- A **React + Vite** single-page frontend that provides a split-screen editor and results panel.

The frontend dev server proxies `/api` to the backend, so the browser sees a single origin.
There is no database and no server-side session state: every score is a pure function of the
submitted text and calibration. This makes results reproducible and the deployment trivial.

The previous iteration of this project combined a hand-written ATS heuristic (60%) with a
TF-IDF similarity score against a small knowledge base (40%), and exposed a chat pane. Both
were removed: the hybrid score could not explain itself, and the chat duplicated the
suggestion feature while adding an unbounded API surface. The current system keeps only what
serves the core problem.

## 2.2 Product Functions (summary)

| ID | Function |
| --- | --- |
| F1 | Ingest resume text from PDF upload or sample |
| F2 | Calibrate the analysis |
| F3 | Compute the rule-based ATS score |
| F4 | Explain each section with criteria |
| F5 | Generate rewrite suggestions |
| F6 | Apply a rewrite safely and edit the resume |
| F7 | Re-score after edits and show deltas |
| F8 | Export the edited resume |

## 2.3 User Classes and Characteristics

| User | Description | Needs |
| --- | --- | --- |
| **Student / fresher** | Final-year or recent graduate with projects and internships | Know why a project section scores zero; get a first professional rewrite |
| **Early-career professional** | 1–5 years of experience | Emphasise work history; quantify impact |
| **Evaluator / demonstrator** | Course instructor or reviewer | Reproducible demo without API keys; visible rule logic |
| **Maintainer** | Future developer | Clear rubric, isolated modules, tests |

The primary user is technically comfortable but not a resume expert. The interface therefore
uses plain language, never raw regex, and always shows *points earned out of points available*.

## 2.4 Operating Environment

| Layer | Requirement |
| --- | --- |
| Backend runtime | Python 3.10+ (3.11/3.12 recommended) |
| Frontend runtime | Node.js 18+ (20 LTS recommended) |
| Browser | Current Chrome, Edge, Firefox, or Safari |
| Operating system | Windows, macOS, or Linux (developed and verified on Windows) |
| Deployment | Local processes; backend `uvicorn` on port 8000, frontend dev server on port 5173 |
| Network | None required except an optional outbound HTTPS call to Gemini when a key is supplied |

## 2.5 Design Constraints

- **C1 — Explainability.** The score must be reconstructible from displayed criteria; no
  hidden component, no learned weights.
- **C2 — Determinism.** Identical text and calibration must always produce an identical score.
- **C3 — Graceful degradation.** Every feature except AI wording must work with no API key and
  no network.
- **C4 — No invented facts.** Rewrites must not fabricate employers, titles, dates, degrees,
  or metrics; missing numbers are represented as placeholders such as `[X%]`.
- **C5 — Safe editing.** The system must never silently append text to a resume.
- **C6 — Statelessness.** No resume content is stored on the server after a response.

## 2.6 Assumptions and Dependencies

- The resume is machine-readable text (a text-based PDF, not a scan).
- Section headings can be normalised to `## SECTION` form; the PDF parser does this for known
  synonyms, and users can type or edit headings directly.
- Resumes are in English.
- Gemini availability, quota, and latency are outside the system's control; failures fall back
  to rule-based advice.
- `pypdf` extraction quality depends on the source PDF's text layer.

---

# 3. System Features

Each feature below states its description, triggering inputs, behaviour, and acceptance
criteria. Requirement identifiers are used in the traceability matrix in Section 12.3.

## 3.1 F1 — Resume Ingestion

### 3.1.1 Description and priority

Users bring their own resume into the editor. Priority: **High** (prerequisite for every
other feature).

### 3.1.2 Functional requirements

| ID | Requirement |
| --- | --- |
| FR-1.1 | The system shall expose `GET /api/sample-resume` returning a demonstration resume as `{ "resume_text": string }`. |
| FR-1.2 | The frontend shall load the sample resume automatically on first mount and analyse it without tracking deltas. |
| FR-1.3 | The system shall expose `POST /api/parse-pdf` accepting one multipart file field named `file`. |
| FR-1.4 | The parser shall reject a file whose name does not end in `.pdf` with HTTP 400 and a human-readable detail. |
| FR-1.5 | The parser shall reject an empty upload and a PDF with no extractable text, each with HTTP 400. |
| FR-1.6 | The parser shall extract text from every page, collapse runs of whitespace to single spaces, drop blank-line runs, and normalise bullet glyphs (`•`, `●`, `▪`, `◦`, `‣`) to `- `. |
| FR-1.7 | The parser shall map recognised section headings to canonical `## SUMMARY`, `## EXPERIENCE`, `## SKILLS`, `## PROJECTS`, and `## EDUCATION` lines, accepting synonyms such as "Professional Summary", "Career Objective", "Core Competencies", and "Academic Background". |
| FR-1.8 | A successful parse shall return `{ "filename": string, "resume_text": string }`. |
| FR-1.9 | The editor shall let the user edit the extracted text freely, in a source view with line numbers and a formatted preview. |

### 3.1.3 Acceptance criteria

- AC-1.1: Uploading a text-based PDF yields editable text whose headings appear as `## SECTION`.
- AC-1.2: Uploading a `.txt` file returns 400 and the message "Please upload a valid .pdf file."
- AC-1.3: A `.pdf` containing no text returns 400 with "No readable text found in PDF."
- AC-1.4: The sample resume loads and is scored without any server-side storage.

## 3.2 F2 — Calibration

### 3.2.1 Description and priority

The same resume is judged differently for a fresher and a senior engineer. Calibration makes
that explicit. Priority: **High**.

### 3.2.2 Functional requirements

| ID | Requirement |
| --- | --- |
| FR-2.1 | The system shall accept `experience_level` ∈ {`fresher`, `experienced`}, defaulting to `fresher`. |
| FR-2.2 | The system shall accept `target_domain` ∈ {`software`, `data`, `product`, `general`}, defaulting to `software`. |
| FR-2.3 | The system shall accept an optional free-text `target_role`, defaulting to an empty string. |
| FR-2.4 | Section weights shall be derived from `experience_level` per Section 4.5. |
| FR-2.5 | Domain keyword sets, the portfolio advice, and role alignment shall use `target_domain` and `target_role`. |
| FR-2.6 | A calibration modal shall be shown before the first analysis and be re-openable from the toolbar. |
| FR-2.7 | Saving calibration shall re-run the analysis on the current text. |
| FR-2.8 | The active calibration shall be visible in the toolbar at all times. |

### 3.2.3 Acceptance criteria

- AC-2.1: Fresher weights give Projects 20% and Education 15%; experienced weights give
  Experience 35% and Projects 10%.
- AC-2.2: Weights sum to 1.0 within 0.01 for both levels.
- AC-2.3: Changing domain changes which skills count as domain-relevant.
- AC-2.4: Re-calibrating re-scores the resume and updates the weighted overall score.

## 3.3 F3/F4 — ATS Scoring and Explanation

### 3.3.1 Description and priority

The system computes a 0–100 score per section and a weighted overall score, then exposes every
criterion so the user can see exactly where points were lost. Priority: **Critical** — this is
the product's reason to exist.

### 3.3.2 Functional requirements

| ID | Requirement |
| --- | --- |
| FR-3.1 | The system shall expose `POST /api/analyze` accepting `resume_text`, an optional `calibration`, optional `previous_scores` (map of section name to score), and an optional `previous_overall`. |
| FR-3.2 | Analysis shall reject whitespace-only `resume_text` with HTTP 400 and "Resume text cannot be empty." |
| FR-3.3 | The system shall partition the resume into the six canonical sections using heading detection; text before the first heading is Contact. |
| FR-3.4 | Each section shall be scored 0–100 as the sum of its criteria, exactly per Section 4. |
| FR-3.5 | Each criterion shall report `id`, `label`, `earned`, `max_points`, `passed`, `advice`, and `example`. |
| FR-3.6 | `passed` shall be true only when `earned == max_points`; partial credit is therefore shown as not passed but still contributes points. |
| FR-3.7 | A missing or empty section shall score 0. No base, participation, or formatting points shall exist. |
| FR-3.8 | The overall score shall be `round(Σ section_score × weight)`, clamped to 0–100. |
| FR-3.9 | When previous values are supplied, each section shall report `previous_score` and `delta`, and the response shall report `previous_overall` and `overall_delta`. |
| FR-3.10 | The response shall include `word_count` computed as the number of word tokens in the submitted text. |
| FR-3.11 | The UI shall show the overall score, each section score with weight, a progress bar, and an expandable criterion list. |
| FR-3.12 | Colour coding shall be consistent: green ≥ 80, amber ≥ 60, red < 60. |

### 3.3.3 Acceptance criteria

- AC-3.1: For every section, the criteria maxima sum to exactly 100 (enforced by test).
- AC-3.2: For every section, `score == Σ earned` (enforced by test).
- AC-3.3: A resume with all six sections absent scores 0 overall.
- AC-3.4: The bundled strong-resume fixture scores ≥ 90 overall and ≥ 90 in every section.
- AC-3.5: Re-analysing an improved resume with previous values yields a positive delta.
- AC-3.6: Running the same input twice yields identical scores.

## 3.4 F5 — Rewrite Suggestions

### 3.4.1 Description and priority

Suggestions turn a deduction into an actionable rewrite in the candidate's own voice.
Priority: **High**.

### 3.4.2 Functional requirements

| ID | Requirement |
| --- | --- |
| FR-4.1 | The system shall expose `POST /api/suggest` accepting `resume_text`, `calibration`, the current `sections`, and an optional `gemini_api_key`. |
| FR-4.2 | If `sections` is empty, the backend shall compute them before generating suggestions. |
| FR-4.3 | The suggestion API key shall be taken from the request when present, otherwise from the `GEMINI_API_KEY` environment variable. |
| FR-4.4 | When a key is available, the backend shall consider the four lowest-scoring sections, include only those with failed criteria, and send their failed checks with earned/max points and advice, plus up to 1,400 characters of current section text. |
| FR-4.5 | The prompt shall instruct the model to return only a JSON array of at most four objects with keys `section`, `title`, `reason`, `original_text`, `replacement_text`; to quote `original_text` verbatim or leave it empty; to output section content without the header; and to invent no facts. |
| FR-4.6 | The backend shall strip Markdown code fences, parse the array, discard malformed items, and discard items whose `section` is not one of the six canonical names or whose `replacement_text` is empty. |
| FR-4.7 | Each suggestion's `original_text` shall be marked `replaceable` only if the exact snippet (after trimming and CRLF normalisation) still occurs in the resume. |
| FR-4.8 | On any Gemini failure — missing key, invalid key, network error, quota, or unparsable output — the system shall return rule-based suggestions instead, with `source = "rule_based"`. |
| FR-4.9 | Rule-based suggestions shall be generated from the largest point gap among failed criteria of the lowest-scoring sections, capped at four, and shall always have `replaceable = false`. |
| FR-4.10 | The response shall declare `source` as `gemini` or `rule_based`. |
| FR-4.11 | The UI shall label the source ("Gemini rewrite" / "Rule-based advice") and provide a per-suggestion editable textarea and a Copy action. |

### 3.4.3 Acceptance criteria

- AC-4.1: With no key, `source` is `rule_based`, at least one suggestion is returned for the
  sample resume, and every suggestion has `replaceable = false`.
- AC-4.2: A fenced JSON array is parsed into its object list.
- AC-4.3: A quoted snippet present in the resume yields `replaceable = true`; an absent snippet
  yields `false`.
- AC-4.4: An invalid key does not raise an error to the client; the response is rule-based.

## 3.5 F6 — Safe Rewrite Application

### 3.5.1 Description and priority

The original prototype appended rewrites to the end of the resume when the source text was not
found, corrupting the document. The requirement is therefore strict. Priority: **Critical**
(correctness).

### 3.5.2 Functional requirements

| ID | Requirement |
| --- | --- |
| FR-5.1 | The Replace action shall be offered only when the suggestion is `replaceable`. |
| FR-5.2 | The replace handler shall verify that `original_text` is a substring of the current resume text before mutating state. |
| FR-5.3 | On success, only the exact matched snippet shall be replaced — once, literally, with no regular-expression interpretation of the replacement. |
| FR-5.4 | The operation shall mark the document dirty and instruct the user to recheck. |
| FR-5.5 | On failure, the system shall not modify the resume, shall not append text, and shall display: "That original text is no longer in the resume. Copy the suggestion instead." |
| FR-5.6 | Every suggestion, replaceable or not, shall offer a Copy action that copies the edited replacement text. |
| FR-5.7 | Each suggestion card shall show the snippet it would replace, so the user can judge it before applying. |
| FR-5.8 | Per-suggestion edit state shall reset when a new suggestion set arrives. |

### 3.5.3 Acceptance criteria

- AC-5.1: A replaceable suggestion replaces its snippet in place and leaves the rest of the
  document byte-identical.
- AC-5.2: A stale snippet produces the copy-instead message and no document change.
- AC-5.3: No code path appends suggestion text to the resume.

## 3.6 F7 — Re-score with Deltas

### 3.6.1 Functional requirements

| ID | Requirement |
| --- | --- |
| FR-6.1 | The toolbar shall expose a Recheck action that re-analyses the current editor text. |
| FR-6.2 | When the document is dirty, the action label shall indicate that unsaved edits will be scored. |
| FR-6.3 | Re-analysis shall send the previous section scores and previous overall score so deltas can be computed. |
| FR-6.4 | The UI shall display deltas as `+n` (green), `-n` (red), or `0` (neutral) for each section and for the overall score. |
| FR-6.5 | Starting any analysis shall clear stale suggestions so the panel cannot show rewrites derived from an older document. |

### 3.6.2 Acceptance criteria

- AC-6.1: Editing a resume to fix a metric raises the Experience score and shows a positive delta.
- AC-6.2: The overall delta equals the new overall minus the previous overall.

## 3.7 F8 — Export

| ID | Requirement |
| --- | --- |
| FR-7.1 | The toolbar shall offer a `.txt` download of the current editor contents. |
| FR-7.2 | The download shall be generated client-side from a UTF-8 text blob. |

Acceptance: the downloaded file's text equals the editor contents exactly.

---

# 4. Scoring Model

This section is normative. The implementation in `backend/app/scorer.py` must match it, and
the test suite enforces the structural invariants.

## 4.1 Section Partitioning

The resume is split on canonical headings:

| Section | Accepted headings (case-insensitive, optional `#`/`##`/`###` prefix) |
| --- | --- |
| Summary | summary, professional summary, objective, profile, about me |
| Experience | experience, work experience, professional experience, employment, internships |
| Skills | skills, technical skills, core competencies, technologies |
| Projects | project, projects, academic projects, personal projects |
| Education | education, academic background, qualifications |

All lines before the first detected heading belong to **Contact**. A heading line is consumed
and does not contribute content. Sections without content are empty and score 0.

The PDF parser additionally normalises capitalised headings to `## SECTION`, so a parsed PDF
is already in canonical form.

## 4.2 Contact — 100 points

| ID | Criterion | Points | Rule |
| --- | --- | --- | --- |
| `contact-name` | Full name in header | 10 | First non-empty line is 2–4 words containing only letters, `.`, `'`, or `-`. |
| `contact-email` | Professional email | 30 | Matches `name@host.tld`. |
| `contact-phone` | Phone number | 20 | 8 or more digits, allowing `+`, spaces, dashes, dots, and parentheses. |
| `contact-linkedin` | LinkedIn profile | 20 | Contact text contains `linkedin.com`. |
| `contact-portfolio` | GitHub / portfolio | 20 | Contains `github.com`, `gitlab.com`, or the word "portfolio", or any non-LinkedIn URL. |

## 4.3 Summary — 100 points

| ID | Criterion | Points | Rule |
| --- | --- | --- | --- |
| `summary-length` | 25–80 word summary | 25 | 25 points for 25–80 words; 15 points for 15–100 words outside that band; otherwise 0. |
| `summary-role` | Target-role alignment | 20 | A significant token of `target_role` appears, or at least 2 domain keywords appear. |
| `summary-seniority` | Seniority / experience signal | 15 | Matches a pattern such as `N years`, graduate, student, intern, fresher, entry-level, senior, lead, mid-level, experienced. |
| `summary-metric` | Quantified achievement | 20 | At least one metric per Section 4.8. |
| `summary-skills` | Relevant skills or tools | 20 | At least 2 domain keyword hits or at least 2 tool hits. |

## 4.4 Experience — 100 points

| ID | Criterion | Points | Rule |
| --- | --- | --- | --- |
| `experience-timeline` | Role and timeline with year | 20 | Contains a 19xx or 20xx year. |
| `experience-bullets` | 3+ experience bullets | 20 | At least 3 bullets. |
| `experience-verbs` | Action-verb bullets | 20 | At least 2 bullets begin with a listed action verb. |
| `experience-metrics` | 2+ quantified metrics | 25 | At least 2 distinct metrics. |
| `experience-relevance` | Domain or tool keywords | 15 | At least 1 domain keyword or at least 1 tool keyword. |

## 4.5 Skills — 100 points

| ID | Criterion | Points | Rule |
| --- | --- | --- | --- |
| `skills-count` | 8+ listed skills | 30 | At least 8 unique items after splitting on `,`, `|`, `;`, `•`, newlines, and stripping `Category:` prefixes. |
| `skills-categories` | 2+ skill categories | 25 | At least 2 distinct `Category:` prefixes on separate lines or `;` segments. |
| `skills-domain` | Domain-relevant skills | 25 | At least 3 domain keyword hits. |
| `skills-tools` | Tools, languages, or frameworks | 20 | At least 2 tool keyword hits. |

## 4.6 Projects — 100 points

| ID | Criterion | Points | Rule |
| --- | --- | --- | --- |
| `projects-tech` | Project name and tech stack | 20 | At least 1 tool keyword or a `|` separator. |
| `projects-bullets` | 2+ project bullets | 20 | At least 2 bullets. |
| `projects-verbs` | Action-verb bullets | 20 | At least 2 bullets begin with an action verb. |
| `projects-metric` | Quantified project result | 20 | At least 1 metric. |
| `projects-tools` | 2+ tech or tool keywords | 20 | At least 2 tool keyword hits. |

## 4.7 Education — 100 points

| ID | Criterion | Points | Rule |
| --- | --- | --- | --- |
| `education-degree` | Degree title | 30 | Matches a degree pattern: B.Tech, M.Tech, B.E., M.E., B.Sc, M.Sc, B.S., M.S., BCA, MCA, bachelor, master, PhD, diploma. |
| `education-institution` | Institution name | 20 | Contains university, college, institute, school, academy, or polytechnic. |
| `education-year` | Graduation year | 20 | Contains a 19xx or 20xx year. |
| `education-gpa` | GPA, percentage, or honors | 15 | Contains GPA/CGPA/percentage/percent/honors/honours/distinction/first class, or an `x/y` ratio with 1–2 digit operands. |
| `education-coursework` | Relevant coursework | 15 | Contains coursework, courses, subjects, specialization, electives, or curriculum. |

## 4.8 Metric Detection

A metric is one of:

- a percentage, e.g. `35%`;
- a currency amount, e.g. `$12,000`;
- a multiplier, e.g. `3x`;
- an abbreviated magnitude, e.g. `20k`, `1.5M`;
- a count followed by a unit such as users, customers, clients, requests, records, rows,
  transactions, projects, teams, engineers, students, downloads, installs, tickets, leads,
  hours, days, weeks, or months — e.g. `500+ customers`;
- a reduction/increase verb followed by `by`/`to` and a number with a unit, e.g.
  `reduced latency by 35%`;
- a duration, e.g. `120 ms`, `3 seconds`.

**Bare years are explicitly excluded.** `Worked on a project in 2025` yields no metric.
Duplicates are removed case-insensitively.

## 4.9 Action Verbs

Action verbs are checked **only at the start of a bullet**. The checked list includes:
achieved, accelerated, analysed/analyzed, architected, automated, boosted, built, collaborated,
configured, coordinated, created, cut, debugged, decreased, delivered, deployed, designed,
developed, documented, drove, engineered, enhanced, established, evaluated, fixed, generated,
grew, implemented, improved, increased, integrated, launched, led, maintained, managed,
mentored, migrated, monitored, optimized, owned, presented, reduced, redesigned, researched,
revamped, scaled, secured, spearheaded, streamlined, tested, trained, transformed, won.

A verb appearing mid-sentence does not satisfy the check.

## 4.10 Section Weights and Overall Score

| Section | Fresher | Experienced |
| --- | --- | --- |
| Contact | 10% | 10% |
| Summary | 15% | 15% |
| Experience | 20% | 35% |
| Skills | 20% | 20% |
| Projects | 20% | 10% |
| Education | 15% | 10% |

```
overall = clamp(round(Σ (section_score × weight)), 0, 100)
```

Weights are normalised by their sum before use, so they always total 1.0. The weighted
contribution of each section is reported for transparency.

## 4.11 Reference Scores

| Fixture | Overall | Section scores |
| --- | --- | --- |
| Bundled sample resume (weak, fresher/software) | 35 | Contact 60, Summary 15, Experience 35, Skills 45, Projects 0, Education 70 |
| Strong-resume test fixture (fresher/software) | 100 | 100 in all six sections |

These values are asserted by the automated tests and serve as regression anchors.

---

# 5. External Interface Requirements

## 5.1 User Interface

Single page, dark theme, three regions:

1. **Toolbar** — brand, active calibration pill, Upload PDF, Load Sample, Recalibrate,
   Gemini Key (toggles an optional key field), `.txt` export, and Recheck (highlighted when
   the document has unsaved edits).
2. **Left pane — Resume Editor** — source view with synchronised line numbers, or a formatted
   preview where `## ` lines become headings, `- ` lines become bullets, and the first line is
   rendered as the candidate name. Shows word count and a dirty indicator.
3. **Right pane — Analysis Panel** — two tabs. *ATS Score* shows the overall score, the
   "100% rule-based" label, delta badges, and expandable section cards. *Suggestions* shows
   the source badge and rewrite cards with snippet, editable replacement, Copy, and Replace.

The calibration modal presents two button groups (experience level, target domain) and one
optional text field (target role), with Save & Analyze and Cancel.

Accessibility: buttons are real `<button>` elements with type attributes, the line-number
gutter is `aria-hidden`, and no interaction depends on colour alone (points and deltas are
always printed as text).

## 5.2 Application Programming Interface

Base path `/api`. JSON unless noted. Errors use FastAPI's `{ "detail": string }` shape.

### 5.2.1 `GET /api/health`

```json
{ "status": "ok" }
```

### 5.2.2 `GET /api/sample-resume`

```json
{ "resume_text": "Alex Rivera\n..." }
```

### 5.2.3 `POST /api/parse-pdf`

`multipart/form-data` with field `file`. Success `200`:

```json
{ "filename": "resume.pdf", "resume_text": "Alex Rivera\n## SUMMARY\n..." }
```

Failures: `400` for non-PDF, empty file, unparsable PDF, or no extractable text.

### 5.2.4 `POST /api/analyze`

Request:

```json
{
  "resume_text": "string",
  "calibration": {
    "experience_level": "fresher",
    "target_domain": "software",
    "target_role": "Backend Engineer"
  },
  "previous_scores": { "Contact": 60, "Summary": 15 },
  "previous_overall": 35
}
```

`calibration`, `previous_scores`, and `previous_overall` are optional. Response:

```json
{
  "overall_score": 35,
  "previous_overall": 30,
  "overall_delta": 2,
  "word_count": 118,
  "sections": [
    {
      "name": "Contact",
      "score": 60,
      "weight": 0.1,
      "weighted_contribution": 6.0,
      "previous_score": 60,
      "delta": 0,
      "criteria": [
        {
          "id": "contact-email",
          "label": "Professional email address",
          "earned": 30,
          "max_points": 30,
          "passed": true,
          "advice": "Add a professional email address.",
          "example": "alex.rivera@email.com"
        }
      ]
    }
  ]
}
```

Validation: `resume_text` is required; whitespace-only input returns `400`.

### 5.2.5 `POST /api/suggest`

Request:

```json
{
  "resume_text": "string",
  "calibration": { "experience_level": "fresher", "target_domain": "software", "target_role": "" },
  "sections": [ /* SectionScore objects, optional */ ],
  "gemini_api_key": "optional-string"
}
```

Response:

```json
{
  "source": "gemini",
  "suggestions": [
    {
      "id": "ai-1",
      "section": "Experience",
      "title": "Quantify the API result",
      "reason": "No quantified metric was found in this section.",
      "original_text": "- Worked on backend tasks and helped the team with APIs.",
      "replacement_text": "- Engineered RESTful APIs with FastAPI, cutting latency by [X%] for [N] daily requests.",
      "replaceable": true
    }
  ]
}
```

`source` is exactly `gemini` or `rule_based`. `suggestions` may be empty.

### 5.2.6 Removed endpoints

`POST /api/chat` and every RAG/similarity endpoint are removed. Requests to them return 404.

## 5.3 Software Interfaces

| Dependency | Version | Purpose |
| --- | --- | --- |
| fastapi | 0.115.6 | HTTP API |
| uvicorn[standard] | 0.34.0 | ASGI server |
| pydantic | 2.10.4 | Request/response models and validation |
| python-multipart | 0.0.20 | Multipart upload parsing |
| pypdf | 5.1.0 | PDF text extraction |
| google-genai | 1.2.0 | Gemini client |
| python-dotenv | 1.0.1 | `.env` loading |
| pytest / httpx | 8.3.4 / 0.28.1 | Tests and test transport |
| react, react-dom | ^18.3.1 | UI |
| lucide-react | ^0.469.0 | Icons |
| typescript | ^5.7.2 | Type checking |
| vite, @vitejs/plugin-react | ^6.0.5 / ^4.3.4 | Dev server and build |

Gemini model: `gemini-2.5-flash`, called through `google.genai.Client.models.generate_content`.

## 5.4 Communication Protocols

- Browser ↔ frontend dev server: HTTP on port 5173.
- Frontend ↔ backend: HTTP JSON under `/api`, proxied by Vite to `http://127.0.0.1:8000`.
- Backend ↔ Gemini: HTTPS to Google's API, only when a key is supplied.
- CORS: permissive (`*`) because the application is single-user and local; this must be
  tightened before any public deployment (see Risk R5).

---

# 6. Non-Functional Requirements

| ID | Category | Requirement | Verification |
| --- | --- | --- | --- |
| NFR-1 | Performance | A single analysis of a two-page resume completes in well under 200 ms; measured on the bundled sample: median **1.37 ms**, p95 **2.41 ms**, max **5.72 ms** over 200 runs. Scoring is linear in text length with compiled regexes. | Measured locally (200-run loop) |
| NFR-2 | Determinism | Identical `resume_text` and `calibration` always produce identical scores. No randomness, clock, or network input affects scoring. | Design + repeat-run check |
| NFR-3 | Availability | All features except AI wording work offline with no key. | Rule-based suggestion test |
| NFR-4 | Fault tolerance | Any Gemini error is caught and converted into a rule-based response; the client never sees a 500 from the suggestion path. | Key-failure test |
| NFR-5 | Privacy | Resume text is held only in browser and request memory. It leaves the machine only when the user supplies a Gemini key. No logs persist resume content and no database stores it. | Code review |
| NFR-6 | Usability | A first-time user can load the sample, read the score breakdown, apply a rewrite, and see a delta without documentation. Labels are plain language; every criterion states points earned and available. | Demo walkthrough |
| NFR-7 | Explainability | 100% of the score is attributable to displayed criteria; no component is hidden from the UI. | Design + UI review |
| NFR-8 | Maintainability | Rubric criteria are declared in one module, one function per section, each criterion carrying its own advice and example. A new check is one list entry plus its points. | Code review |
| NFR-9 | Type safety | The backend runs with Pydantic-validated models; the frontend compiles with TypeScript `strict` settings and no build errors. | `tsc` in build |
| NFR-10 | Portability | Runs on Windows, macOS, and Linux with Python 3.10+ and Node 18+; no OS-specific paths or native builds beyond wheels. | Setup on a clean machine |
| NFR-11 | Testability | Every API endpoint and the core scoring invariants are covered by automated tests; the suite runs in under two seconds. | `pytest -q` |
| NFR-12 | Response clarity | Error responses use a single `detail` string that names the problem and the fix. | API tests |

---

# 7. System Architecture

## 7.1 Component View

```text
┌──────────────────────────────────────────────────────────────┐
│ Browser — React 18 + Vite (port 5173)                        │
│                                                              │
│  App.tsx            state: text, calibration, analysis,      │
│                     suggestions, dirty, loading, error       │
│    ├─ ResumeEditor      source / preview, word count         │
│    ├─ AnalysisPanel     tabs: ATS Score | Suggestions        │
│    └─ CalibrationModal  2 choices + optional role            │
│                                                              │
│  api.ts  ── fetch ──►  /api/*  (Vite proxy)                  │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP JSON
┌───────────────────────────▼──────────────────────────────────┐
│ FastAPI (port 8000)                                          │
│                                                              │
│  main.py          routes, CORS, sample resume                │
│    ├─ pdf_parser.py      pypdf → normalised text             │
│    ├─ scorer.py          section split + ATS rubric          │
│    └─ ai_suggester.py    prompt → Gemini → validate           │
│                          └─ fallback: rule-based advice      │
│  models.py        Pydantic schemas                           │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTPS (optional)
                     ┌──────▼──────┐
                     │ Gemini 2.5  │
                     │   Flash     │
                     └─────────────┘
```

## 7.2 Module Responsibilities

| Module | Responsibility | Must not |
| --- | --- | --- |
| `app/main.py` | Route definitions, upload validation, CORS, sample fixture | Contain scoring logic |
| `app/pdf_parser.py` | PDF bytes → normalised editable text | Store uploads |
| `app/scorer.py` | Section partitioning, rubric evaluation, weighted overall, deltas | Call any network service |
| `app/ai_suggester.py` | Suggestion prompt, Gemini call, response parsing, snippet validation, deterministic fallback | Compute or alter scores |
| `app/models.py` | Request/response schemas and enums | Contain business rules |
| `frontend/src/api.ts` | Typed fetch wrappers and error extraction | Contain presentation logic |
| `frontend/src/App.tsx` | State ownership, orchestration, safe replace | Render detailed result markup |
| `AnalysisPanel.tsx` | Score and suggestion rendering, replace/copy actions | Mutate resume text directly |
| `ResumeEditor.tsx` | Editing and preview rendering | Call the API |
| `CalibrationModal.tsx` | Collect calibration | Persist settings |

## 7.3 Key Sequences

### 7.3.1 Analyze

1. User clicks Recheck (or a load/upload completes).
2. `App` clears prior suggestions and marks loading.
3. `POST /api/analyze` with text, calibration, and previous scores when tracking deltas.
4. `scorer.analyze_resume` splits sections, evaluates criteria, applies weights, computes deltas.
5. `App` stores the response, clears the dirty flag, then requests suggestions with the new
   sections.
6. `AnalysisPanel` renders the overall score and section cards.

### 7.3.2 Suggest and apply

1. `POST /api/suggest` with text, calibration, sections, and an optional key.
2. With a key: build a prompt from the four weakest sections' failed criteria; call Gemini;
   parse; validate snippets; return `source = "gemini"`.
3. Without a key or on any failure: derive one suggestion per weak section from the largest
   point gap; return `source = "rule_based"`.
4. User edits the replacement in the card.
5. Replace is offered only when `replaceable`; the handler re-checks `includes(original)`,
   replaces once with a literal replacement, marks dirty.
6. A missing snippet yields the copy-instead message and no change.
7. Recheck re-scores and shows deltas.

## 7.4 Design Rationale

- **Rules over retrieval.** The requirement is to explain a deduction. A rule either passes or
  fails and can print its own reason; a cosine similarity cannot. Removing TF-IDF also removed
  scikit-learn, a knowledge base, and any claim that the score reflects real ATS behaviour it
  could not substantiate.
- **Gemini scoped to wording.** Generative models are good at rewriting a bullet and bad at
  producing a stable, auditable number. The score stays local and deterministic; the model is
  given the failed checks as constraints and never sees a score it could inflate.
- **Suggestions carry their own source text.** `original_text` makes a suggestion verifiable.
  The backend only marks it replaceable if the snippet exists, so the UI can never apply a
  rewrite to the wrong place.
- **Copy-first fallback.** Rule-based suggestions are advisory by design. They are useful
  without a key and cannot corrupt a document, because they are never auto-applied.
- **Stateless API.** No database keeps the tool demo-ready, privacy-preserving, and trivial to
  run; every result is reproducible from the request.

---

# 8. Data Requirements

## 8.1 Entities

| Entity | Fields | Notes |
| --- | --- | --- |
| Calibration | `experience_level`, `target_domain`, `target_role` | Enumerations validated by Pydantic |
| SectionScore | `name`, `score`, `weight`, `weighted_contribution`, `previous_score?`, `delta?`, `criteria[]` | `score` constrained 0–100 |
| CriterionResult | `id`, `label`, `earned`, `max_points`, `passed`, `advice`, `example` | `earned`/`max_points` non-negative |
| Suggestion | `id`, `section`, `title`, `reason`, `original_text`, `replacement_text`, `replaceable` | `replaceable` computed server-side |

## 8.2 Persistence

There is none. Resume text exists in React state and in request bodies; it is never written to
disk, a database, or a log by the application. The only on-disk artefacts are source files,
the optional `.env` holding `GEMINI_API_KEY`, and the frontend build output.

## 8.3 Retention and Privacy

- Server memory is released when the response completes.
- Gemini receives resume excerpts only on an explicit user action (Recheck with a key set) and
  is subject to Google's terms; the README discloses this.
- The optional key entered in the toolbar is held in component state only, not in
  `localStorage`, and is cleared on reload.

## 8.4 Configuration

| Variable | Required | Effect |
| --- | --- | --- |
| `GEMINI_API_KEY` | No | Enables Gemini suggestions when the request carries no key. Absent → rule-based advice. |

A `.env.example` documents the variable. `.env` is git-ignored.

---

# 9. Verification and Acceptance

## 9.1 Automated Tests

`backend/tests/test_api.py`, run with `pytest -q` (10 tests, all passing).

| # | Test | Verifies |
| --- | --- | --- |
| 1 | `test_health` | Health endpoint contract |
| 2 | `test_calibration_weights_differ_by_level` | Weights differ by level and each set sums to 1.0 |
| 3 | `test_every_section_has_100_points` | Six sections; criteria maxima sum to 100; score equals sum of earned; score in 0–100 |
| 4 | `test_strong_resume_scores_high` | Strong fixture ≥ 90 overall and per section |
| 5 | `test_analyze_and_recheck_delta` | Improvement produces positive overall delta |
| 6 | `test_metrics_ignore_years` | Bare years excluded; real metrics detected |
| 7 | `test_gemini_json_parser_and_safe_snippet_validation` | Fenced JSON parsed; present snippet replaceable; absent snippet not |
| 8 | `test_rule_based_suggestions_without_api_key` | Fallback source, non-empty suggestions, none replaceable |
| 9 | `test_rejects_empty_resume` | Whitespace-only input returns 400 |
| 10 | `test_parse_pdf_rejects_non_pdf` | Non-PDF upload returns 400 |

## 9.2 Build Gates

| Gate | Command | Expected |
| --- | --- | --- |
| Backend syntax | `python -m compileall -q app` | Exit 0 |
| Backend behaviour | `pytest -q` | 10 passed |
| Frontend types + bundle | `npm run build` | `tsc` clean, Vite build succeeds |

## 9.3 Manual Acceptance Scenario

1. Start backend and frontend; open `http://localhost:5173`.
2. Calibration modal appears; choose Fresher / Software, save.
3. Sample loads and scores **35** overall with Contact 60, Summary 15, Experience 35,
   Skills 45, Projects 0, Education 70.
4. Expand Projects: every criterion shows `0/…` with advice.
5. Open Suggestions: four rule-based cards, each with Copy and no Replace.
6. Paste a Gemini key: suggestions carry the "Gemini rewrite" badge; at least one is replaceable.
7. Click Replace: the snippet changes in place; the editor shows "Edited".
8. Click Recheck: section and overall scores rise with `+` badges.
9. Upload a PDF: text normalises to `## SECTION` headings and is editable.
10. Export `.txt`: contents match the editor.

## 9.4 Requirements Traceability

| Requirement group | Implementation | Verification |
| --- | --- | --- |
| FR-1.x ingestion | `main.py` routes, `pdf_parser.py`, `ResumeEditor.tsx` | Tests 9, 10; manual 9 |
| FR-2.x calibration | `models.CalibrationConfig`, `scorer.get_dynamic_weights`, `CalibrationModal.tsx` | Test 2 |
| FR-3.x scoring | `scorer.analyze_resume`, `models`, `AnalysisPanel.tsx` | Tests 3, 4, 6 |
| FR-4.x suggestions | `ai_suggester.py`, `SuggestionCard` | Tests 7, 8 |
| FR-5.x safe replace | `App.handleReplaceText`, `SuggestionCard.handleReplace` | Test 7 (validation); manual 7 |
| FR-6.x deltas | `scorer` previous fields, `DeltaBadge` | Test 5 |
| FR-7.x export | `App.handleDownloadTxt` | Manual 10 |
| NFR-1…12 | See Section 6 | Build gates and code review |

---

# 10. Constraints, Assumptions, and Risks

| ID | Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| R1 | A PDF has no text layer (scan), so extraction returns nothing | Medium | Medium | Explicit 400 message; user can paste or edit text manually |
| R2 | Section headings differ from the recognised synonyms | Medium | Medium | Broad synonym list, parser normalisation, and free editing in the source view |
| R3 | Rubric over- or under-rewards an unusual resume | Medium | Medium | Criteria are explicit and disclosed; users see the exact reason and can judge it |
| R4 | Gemini hallucinated facts in a rewrite | Medium | High | Prompt forbids invention and asks for placeholders; replacement is user-editable; replace requires an existing snippet; advice says to verify facts |
| R5 | Permissive CORS if deployed publicly | Low (local use) | High | Documented; tighten `allow_origins` before any public deployment |
| R6 | Gemini quota or outage | Medium | Low | Deterministic fallback keeps the feature usable; UI labels the source |
| R7 | API key entered by a user is exposed to that browser | Low | Medium | Key is per-session, never persisted, and sent only to the local backend |
| R8 | Score perceived as an official ATS verdict | Medium | Medium | UI states "100% rule-based"; README calls it a readiness rubric |

---

# 11. Out of Scope and Future Work

Potential extensions, deliberately excluded from v1.0:

- Job-description targeting and keyword gap analysis.
- DOCX ingestion and layout-aware PDF parsing (columns, tables).
- Local, downloadable resume templates and PDF export with formatting preserved.
- Persistence of history, so a user can track scores across sessions.
- Authentication and multi-user accounts.
- Multilingual resumes and locale-specific conventions (e.g. non-US phone formats).
- Weight learning from recruiter feedback — this would break the explainability constraint
  unless criteria remain visible.

---

# 12. Appendices

## 12.1 Sample Resume Fixture

```text
Alex Rivera
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
```

## 12.2 Domain Keyword Sets (abridged)

- **Software:** python, java, javascript, typescript, react, node, fastapi, django, flask, sql,
  postgresql, mongodb, docker, kubernetes, aws, azure, gcp, git, linux, html, css, rest, api,
  apis, backend, frontend, full-stack, web, graphql, microservices, c++, c#, .net, spring,
  flutter, swift, kotlin, redis, ci/cd, testing, pytest, jest, data structures, algorithms.
- **Data:** python, sql, pandas, numpy, scikit-learn, tensorflow, pytorch, keras, machine
  learning, deep learning, nlp, computer vision, tableau, power bi, excel, statistics,
  regression, classification, clustering, bigquery, spark, airflow, etl, data visualization,
  a/b testing, matlab.
- **Product:** product management, roadmap, stakeholder, user research, analytics, a/b testing,
  jira, confluence, figma, kpi, okr, agile, scrum, wireframe, prototyping, go-to-market,
  requirement, prd, sql, excel, tableau, mixpanel, amplitude.
- **General:** communication, leadership, project management, excel, sql, analytics,
  stakeholder, problem solving, teamwork, documentation, reporting, budgeting, operations,
  customer service, sales, marketing.

## 12.3 Repository Layout

```text
Group_1/
├── Source_Code/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   ├── scorer.py
│   │   │   ├── ai_suggester.py
│   │   │   └── pdf_parser.py
│   │   ├── tests/test_api.py
│   │   ├── requirements.txt
│   │   └── .env.example
│   ├── frontend/
│   │   └── src/
│   │       ├── App.tsx
│   │       ├── api.ts
│   │       ├── types.ts
│   │       ├── index.css
│   │       └── components/
│   │           ├── ResumeEditor.tsx
│   │           ├── AnalysisPanel.tsx
│   │           └── CalibrationModal.tsx
│   ├── README.md
│   └── .gitignore
├── Documentation/
│   ├── SRS.md
│   ├── SRS.html
│   └── build_docs.py
└── implementation_plan.md
```

## 12.4 Glossary of Rubric Advice

Every criterion carries a fixed `advice` and `example`. Examples:

| Criterion | Advice | Example |
| --- | --- | --- |
| `summary-length` | Keep the summary to 2–3 sentences (about 25–80 words). | "Computer Science graduate with hands-on experience building FastAPI and React applications." |
| `experience-verbs` | Start each bullet with a strong action verb. | "Engineered a REST API using FastAPI and PostgreSQL." |
| `experience-metrics` | Add at least two numbers such as %, $, users, latency, or time saved. | "Reduced API latency by 35% across 20k daily requests." |
| `projects-tech` | List each project with its name and tech stack. | "Resume Analyser \| Python, FastAPI, React, PostgreSQL" |
| `education-coursework` | List relevant coursework. | "Relevant Coursework: Data Structures, Algorithms, DBMS, Machine Learning" |

---

*End of document.*
