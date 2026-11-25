export type ExperienceLevel = "fresher" | "experienced";
export type TargetDomain = "software" | "data" | "product" | "general";

export interface CalibrationConfig {
  experience_level: ExperienceLevel;
  target_domain: TargetDomain;
  target_role: string;
}

export interface CriterionResult {
  id: string;
  label: string;
  earned: number;
  max_points: number;
  passed: boolean;
  advice: string;
  example: string;
}

export interface SectionScore {
  name: string;
  score: number;
  weight: number;
  weighted_contribution: number;
  previous_score?: number | null;
  delta?: number | null;
  criteria: CriterionResult[];
}

export interface AnalyzeResponse {
  overall_score: number;
  previous_overall?: number | null;
  overall_delta?: number | null;
  sections: SectionScore[];
  word_count: number;
}

export interface Suggestion {
  id: string;
  section: string;
  title: string;
  reason: string;
  original_text: string;
  replacement_text: string;
  replaceable: boolean;
}

export interface SuggestResponse {
  source: "gemini" | "rule_based";
  suggestions: Suggestion[];
}
