from typing import List, Literal, Optional

from pydantic import BaseModel, Field


ExperienceLevel = Literal["fresher", "experienced"]
TargetDomain = Literal["software", "data", "product", "general"]


class CalibrationConfig(BaseModel):
    """User's calibration settings that adjust section weights and ATS checks."""

    experience_level: ExperienceLevel = "fresher"
    target_domain: TargetDomain = "software"
    target_role: str = ""


class CriterionResult(BaseModel):
    """One explainable ATS check inside a resume section."""

    id: str
    label: str
    earned: int = Field(ge=0)
    max_points: int = Field(ge=0)
    passed: bool
    advice: str = ""
    example: str = ""


class SectionScore(BaseModel):
    """ATS score and point-by-point breakdown for a single resume section."""

    name: str
    score: int = Field(ge=0, le=100)
    weight: float
    weighted_contribution: float
    previous_score: Optional[int] = None
    delta: Optional[int] = None
    start: Optional[int] = None
    end: Optional[int] = None
    criteria: List[CriterionResult] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    resume_text: str
    calibration: CalibrationConfig = Field(default_factory=CalibrationConfig)
    previous_scores: Optional[dict[str, int]] = None
    previous_overall: Optional[int] = None


class AnalyzeResponse(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    previous_overall: Optional[int] = None
    overall_delta: Optional[int] = None
    sections: List[SectionScore]
    word_count: int


class Suggestion(BaseModel):
    """A rewrite that can be copied, or safely applied when original_text matches."""

    id: str
    section: str
    title: str
    reason: str
    original_text: str
    replacement_text: str
    replaceable: bool = False
    match_start: Optional[int] = None
    match_end: Optional[int] = None


class SuggestRequest(BaseModel):
    resume_text: str
    calibration: CalibrationConfig = Field(default_factory=CalibrationConfig)
    sections: List[SectionScore] = Field(default_factory=list)
    gemini_api_key: Optional[str] = None


class SuggestResponse(BaseModel):
    source: Literal["gemini", "rule_based"]
    suggestions: List[Suggestion] = Field(default_factory=list)
