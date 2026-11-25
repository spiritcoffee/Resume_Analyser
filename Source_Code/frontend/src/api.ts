import {
  AnalyzeResponse,
  CalibrationConfig,
  SectionScore,
  SuggestResponse,
} from "./types";

const API_BASE = "/api";

export async function fetchSampleResume(): Promise<string> {
  const res = await fetch(`${API_BASE}/sample-resume`);
  if (!res.ok) throw new Error("Failed to load sample resume");
  const data = await res.json();
  return data.resume_text;
}

export async function uploadPdfResume(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/parse-pdf`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to parse PDF");
  }
  const data = await res.json();
  return data.resume_text;
}

export async function analyzeResume(
  resumeText: string,
  calibration: CalibrationConfig,
  previousScores?: Record<string, number>,
  previousOverall?: number
): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_text: resumeText,
      calibration,
      previous_scores: previousScores ?? null,
      previous_overall: previousOverall ?? null,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Analysis failed");
  }
  return res.json();
}

export async function fetchSuggestions(
  resumeText: string,
  calibration: CalibrationConfig,
  sections: SectionScore[],
  geminiApiKey?: string
): Promise<SuggestResponse> {
  const res = await fetch(`${API_BASE}/suggest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_text: resumeText,
      calibration,
      sections,
      gemini_api_key: geminiApiKey || null,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Suggestion fetch failed");
  }
  return res.json();
}
