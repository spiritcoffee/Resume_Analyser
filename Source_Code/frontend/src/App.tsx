import React, { useEffect, useRef, useState } from "react";
import {
  Download,
  FileText,
  KeyRound,
  RefreshCw,
  SlidersHorizontal,
  Upload,
} from "lucide-react";
import {
  analyzeResume,
  fetchSampleResume,
  fetchSuggestions,
  uploadPdfResume,
} from "./api";
import { AnalysisPanel } from "./components/AnalysisPanel";
import { CalibrationModal } from "./components/CalibrationModal";
import { ResumeEditor } from "./components/ResumeEditor";
import { AnalyzeResponse, CalibrationConfig, SuggestResponse } from "./types";

export default function App() {
  const [calibration, setCalibration] = useState<CalibrationConfig>({
    experience_level: "fresher",
    target_domain: "software",
    target_role: "",
  });
  const [showCalibration, setShowCalibration] = useState(true);
  const [resumeText, setResumeText] = useState("");
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [suggestions, setSuggestions] = useState<SuggestResponse | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [showKeyInput, setShowKeyInput] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const runAnalysis = async (
    textToAnalyze: string,
    trackDelta: boolean,
    calOverride?: CalibrationConfig
  ) => {
    if (!textToAnalyze.trim()) return;
    const activeCal = calOverride ?? calibration;
    setLoading(true);
    setError(null);
    setSuggestions(null);
    try {
      const prevMap =
        trackDelta && analysis
          ? Object.fromEntries(analysis.sections.map((s) => [s.name, s.score]))
          : undefined;
      const prevOverall = trackDelta && analysis ? analysis.overall_score : undefined;

      const res = await analyzeResume(textToAnalyze, activeCal, prevMap, prevOverall);
      setAnalysis(res);
      setIsDirty(false);

      const sug = await fetchSuggestions(
        textToAnalyze,
        activeCal,
        res.sections,
        apiKey || undefined
      );
      setSuggestions(sug);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  // Load sample resume on first mount
  useEffect(() => {
    fetchSampleResume()
      .then((text) => {
        setResumeText(text);
        return runAnalysis(text, false);
      })
      .catch(() => {});
  }, []);

  const handleLoadSample = async () => {
    try {
      const text = await fetchSampleResume();
      setResumeText(text);
      await runAnalysis(text, false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sample");
    }
  };

  const handlePdfUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const extracted = await uploadPdfResume(file);
      setResumeText(extracted);
      await runAnalysis(extracted, false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to parse PDF");
      setLoading(false);
    } finally {
      e.target.value = "";
    }
  };

  const handleTextChange = (updated: string) => {
    setResumeText(updated);
    setIsDirty(true);
  };

  const handleReplaceText = (original: string, replacement: string): boolean => {
    if (!original || !resumeText.includes(original)) {
      return false;
    }
    setResumeText(resumeText.replace(original, () => replacement));
    setIsDirty(true);
    setError(null);
    return true;
  };

  const handleDownloadTxt = () => {
    const blob = new Blob([resumeText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "resume_updated.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-shell">
      <header className="toolbar">
        <div className="brand">
          <FileText size={20} color="#10b981" />
          <span>ATS Resume Analyser</span>
          <span className="badge-pill">
            {calibration.experience_level} · {calibration.target_domain}
          </span>
        </div>

        <div className="toolbar-actions">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            style={{ display: "none" }}
            onChange={handlePdfUpload}
          />
          <button
            type="button"
            className="btn"
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={14} /> Upload PDF
          </button>

          <button type="button" className="btn" onClick={handleLoadSample}>
            Load Sample
          </button>

          <button type="button" className="btn" onClick={() => setShowCalibration(true)}>
            <SlidersHorizontal size={14} /> Recalibrate
          </button>

          <button
            type="button"
            className="btn"
            onClick={() => setShowKeyInput((v) => !v)}
            title="Optional Gemini API Key"
          >
            <KeyRound size={14} /> {apiKey ? "Key Set" : "Gemini Key"}
          </button>

          <button type="button" className="btn" onClick={handleDownloadTxt}>
            <Download size={14} /> .txt
          </button>

          <button
            type="button"
            className={`btn btn-primary ${isDirty ? "btn-pulse" : ""}`}
            disabled={loading || !resumeText.trim()}
            onClick={() => runAnalysis(resumeText, true)}
          >
            <RefreshCw size={14} />
            {loading ? "Checking..." : isDirty ? "Recheck (Edited)" : "Recheck Score"}
          </button>
        </div>
      </header>

      {showKeyInput && (
        <div
          style={{
            padding: "8px 16px",
            background: "#162032",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            alignItems: "center",
            gap: 10,
            fontSize: 13,
          }}
        >
          <span>Optional Gemini API Key:</span>
          <input
            type="password"
            className="input-field"
            style={{ maxWidth: 340, marginTop: 0 }}
            placeholder="Paste GEMINI_API_KEY (leave empty for rule-based advice)"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
          <button type="button" className="btn" onClick={() => setShowKeyInput(false)}>
            Done
          </button>
        </div>
      )}

      {error && (
        <div
          style={{
            padding: "8px 16px",
            background: "rgba(239, 68, 68, 0.15)",
            color: "#fca5a5",
            fontSize: 13,
            borderBottom: "1px solid rgba(239, 68, 68, 0.3)",
          }}
        >
          {error}
        </div>
      )}

      <main className="workspace">
        <ResumeEditor
          value={resumeText}
          onChange={handleTextChange}
          wordCount={analysis?.word_count}
          dirty={isDirty}
        />
        <AnalysisPanel
          analysis={analysis}
          suggestions={suggestions?.suggestions ?? []}
          suggestionSource={suggestions?.source ?? null}
          loading={loading}
          onReplaceText={handleReplaceText}
        />
      </main>

      {showCalibration && (
        <CalibrationModal
          initialConfig={calibration}
          onSave={(nextCal) => {
            setCalibration(nextCal);
            setShowCalibration(false);
            if (resumeText.trim()) {
              runAnalysis(resumeText, false, nextCal);
            }
          }}
          onClose={() => setShowCalibration(false)}
        />
      )}
    </div>
  );
}
