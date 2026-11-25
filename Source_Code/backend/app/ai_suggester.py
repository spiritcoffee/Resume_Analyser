import json
import os
import re
from typing import List

from dotenv import load_dotenv

from .models import (
    AnalyzeRequest,
    SectionScore,
    SuggestRequest,
    SuggestResponse,
    Suggestion,
)
from .scorer import SECTION_ORDER, analyze_resume, split_into_sections

load_dotenv()


def generate_suggestions(request: SuggestRequest) -> SuggestResponse:
    """
    Generate resume rewrites from the deterministic ATS results.

    Gemini is used only for wording suggestions. The score itself is always
    calculated by the local ATS rubric, and Gemini never receives a score to
    invent or modify.
    """
    api_key = (request.gemini_api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    sections = request.sections
    if not sections:
        sections = analyze_resume(
            AnalyzeRequest(
                resume_text=request.resume_text,
                calibration=request.calibration,
            )
        ).sections

    if api_key:
        try:
            suggestions = _call_gemini(api_key, request, sections)
            if suggestions:
                return SuggestResponse(source="gemini", suggestions=suggestions)
        except Exception:
            # Invalid key, offline mode, quota limits, or malformed JSON all
            # fall back to the deterministic advice below.
            pass

    return SuggestResponse(
        source="rule_based",
        suggestions=_fallback_suggestions(sections),
    )


def _build_prompt(
    request: SuggestRequest,
    sections: List[SectionScore],
) -> str:
    parsed_sections = split_into_sections(request.resume_text)
    blocks: List[str] = []

    for section in sorted(sections, key=lambda item: item.score)[:4]:
        failed = [criterion for criterion in section.criteria if not criterion.passed]
        if not failed:
            continue

        failed_lines = "\n".join(
            f"- {criterion.label} ({criterion.earned}/{criterion.max_points}): "
            f"{criterion.advice}"
            for criterion in failed
        )
        current_text = parsed_sections.get(section.name, "")[:1400]
        blocks.append(
            f"Section: {section.name} (ATS score {section.score}/100)\n"
            f"Failed checks:\n{failed_lines}\n"
            f"Current text:\n{current_text}"
        )

    if not blocks:
        return ""

    calibration = request.calibration
    return (
        "You are an expert ATS resume editor embedded in a resume analysis tool. "
        "The ATS score is computed by deterministic rules; never invent or change a score.\n\n"
        f"Candidate level: {calibration.experience_level}\n"
        f"Target domain: {calibration.target_domain}\n"
        f"Target role: {calibration.target_role or 'not specified'}\n\n"
        "Rewrite the weakest resume content so it satisfies the failed checks. "
        "Return ONLY a JSON array of up to 4 objects with these keys:\n"
        '"section", "title", "reason", "original_text", "replacement_text".\n'
        "- section must be one of: " + ", ".join(SECTION_ORDER) + ".\n"
        "- original_text must be copied verbatim from the current section text "
        "and must be the exact text to replace. If you cannot quote it exactly, use an empty string.\n"
        "- replacement_text must be ready to paste and should preserve the candidate's facts.\n"
        "- replacement_text must contain only section content, not the section header, "
        "and should keep the original bullet or formatting style.\n"
        "- Do not invent employers, job titles, degrees, dates, or metrics. "
        "If a metric is missing, use a placeholder such as [X%] or [N users].\n"
        "- Do not wrap the JSON in markdown fences.\n\n"
        + "\n\n---\n\n".join(blocks)
    )


def _call_gemini(
    api_key: str,
    request: SuggestRequest,
    sections: List[SectionScore],
) -> List[Suggestion]:
    from google import genai

    prompt = _build_prompt(request, sections)
    if not prompt:
        return []

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    items = _parse_json_array((response.text or "").strip())

    suggestions: List[Suggestion] = []
    for index, item in enumerate(items[:4]):
        if not isinstance(item, dict):
            continue

        section = str(item.get("section", "")).strip()
        if section not in SECTION_ORDER:
            continue

        replacement_text = str(item.get("replacement_text", "")).strip()
        if not replacement_text:
            continue

        original_text, replaceable = _validate_original(
            str(item.get("original_text", "")),
            request.resume_text,
        )
        suggestions.append(
            Suggestion(
                id=f"ai-{index + 1}",
                section=section,
                title=str(item.get("title", f"Improve {section}")).strip(),
                reason=str(item.get("reason", "")).strip(),
                original_text=original_text,
                replacement_text=replacement_text,
                replaceable=replaceable,
            )
        )

    return suggestions


def _parse_json_array(raw: str) -> List[dict]:
    if not raw:
        return []

    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return []

    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return []

    return data if isinstance(data, list) else []


def _validate_original(original: str, resume_text: str) -> tuple[str, bool]:
    """Only allow replacement when the exact source text still exists."""
    if not original.strip():
        return "", False

    resume_normalized = resume_text.replace("\r\n", "\n")
    original_normalized = original.replace("\r\n", "\n").strip()
    if original_normalized and original_normalized in resume_normalized:
        return original_normalized, True

    return original.strip(), False


def _fallback_suggestions(sections: List[SectionScore]) -> List[Suggestion]:
    """Deterministic, copyable advice when Gemini is unavailable."""
    suggestions: List[Suggestion] = []

    for section in sorted(sections, key=lambda item: item.score):
        failed = [
            criterion
            for criterion in section.criteria
            if criterion.earned < criterion.max_points
        ]
        if not failed:
            continue

        criterion = max(
            failed,
            key=lambda item: item.max_points - item.earned,
        )
        replacement = criterion.example or criterion.advice or criterion.label
        suggestions.append(
            Suggestion(
                id=f"rule-{len(suggestions) + 1}",
                section=section.name,
                title=f"Improve {section.name}: {criterion.label}",
                reason=criterion.advice
                or f"Earn the remaining {criterion.max_points - criterion.earned} points.",
                original_text="",
                replacement_text=replacement,
                replaceable=False,
            )
        )

        if len(suggestions) >= 4:
            break

    return suggestions
