import React, { useEffect, useState } from "react";
import {
  Check,
  ChevronDown,
  ChevronRight,
  Copy,
  Replace,
  Sparkles,
} from "lucide-react";
import { AnalyzeResponse, SectionScore, Suggestion } from "../types";

interface Props {
  analysis: AnalyzeResponse | null;
  suggestions: Suggestion[];
  suggestionSource: "gemini" | "rule_based" | null;
  loading: boolean;
  onReplaceText: (original: string, replacement: string) => boolean;
}

type Tab = "scores" | "suggestions";

function scoreColor(score: number): string {
  if (score >= 80) return "#10b981";
  if (score >= 60) return "#f59e0b";
  return "#ef4444";
}

function DeltaBadge({ delta }: { delta?: number | null }) {
  if (delta === undefined || delta === null) return null;
  if (delta > 0) return <span className="delta-badge delta-up">+{delta}</span>;
  if (delta < 0) return <span className="delta-badge delta-down">{delta}</span>;
  return <span className="delta-badge delta-flat">0</span>;
}

const SuggestionCard: React.FC<{
  sug: Suggestion;
  onReplace: (original: string, replacement: string) => boolean;
}> = ({ sug, onReplace }) => {
  const [editedText, setEditedText] = useState(sug.replacement_text);
  const [replaced, setReplaced] = useState(false);
  const [copied, setCopied] = useState(false);
  const [replaceError, setReplaceError] = useState<string | null>(null);

  useEffect(() => {
    setEditedText(sug.replacement_text);
    setReplaced(false);
    setCopied(false);
    setReplaceError(null);
  }, [sug.id, sug.replacement_text]);

  const handleReplace = () => {
    const success = onReplace(sug.original_text, editedText);
    if (success) {
      setReplaceError(null);
      setReplaced(true);
      setTimeout(() => setReplaced(false), 2000);
    } else {
      setReplaceError(
        "That original text is no longer in the resume. Copy the suggestion instead."
      );
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(editedText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setReplaceError("Clipboard access failed. Select and copy the text manually.");
    }
  };

  return (
    <div className="suggestion-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
        <strong style={{ fontSize: 13 }}>{sug.title}</strong>
        <span
          style={{
            fontSize: 11,
            padding: "2px 7px",
            borderRadius: 999,
            background: "rgba(59,130,246,0.15)",
            color: "#93c5fd",
            whiteSpace: "nowrap",
          }}
        >
          {sug.section}
        </span>
      </div>

      <div style={{ fontSize: 12.5, color: "#fbbf24", marginTop: 4 }}>{sug.reason}</div>

      {sug.original_text && (
        <div
          style={{
            marginTop: 8,
            padding: "7px 9px",
            borderRadius: 6,
            background: "#0b1120",
            border: "1px solid var(--border)",
            color: "var(--text-muted)",
            fontSize: 11.5,
            maxHeight: 90,
            overflowY: "auto",
            whiteSpace: "pre-wrap",
          }}
        >
          <strong style={{ color: "#cbd5e1" }}>Replaces:</strong> {sug.original_text}
        </div>
      )}

      <div style={{ marginTop: 8, fontSize: 11, color: "var(--text-muted)" }}>
        {sug.replaceable
          ? "Edit the rewrite below, then apply it directly to the resume."
          : "Copy this rewrite into the relevant section. No safe source snippet was found."}
      </div>
      <textarea
        className="edit-suggestion-box"
        rows={Math.min(12, (editedText.match(/\n/g) || []).length + 3)}
        value={editedText}
        onChange={(e) => setEditedText(e.target.value)}
      />

      <div style={{ display: "flex", gap: 8, marginTop: 6, alignItems: "center", flexWrap: "wrap" }}>
        {sug.replaceable && (
          <button
            type="button"
            className="btn replace-btn"
            style={{ padding: "5px 11px", fontSize: 12 }}
            onClick={handleReplace}
            disabled={!editedText.trim()}
          >
            <Replace size={13} />
            {replaced ? "Replaced ✓" : "Replace in Resume"}
          </button>
        )}
        <button
          type="button"
          className="btn"
          style={{ padding: "5px 11px", fontSize: 12 }}
          onClick={handleCopy}
          disabled={!editedText.trim()}
        >
          {copied ? <Check size={13} /> : <Copy size={13} />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>

      {replaceError && (
        <div style={{ marginTop: 6, fontSize: 11.5, color: "#fca5a5" }}>{replaceError}</div>
      )}
    </div>
  );
};

const SectionCard: React.FC<{ sec: SectionScore }> = ({ sec }) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="section-card">
      <div className="section-top" onClick={() => setOpen((value) => !value)}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {open ? <ChevronDown size={15} /> : <ChevronRight size={15} />}
          <span style={{ fontWeight: 600, fontSize: 14 }}>{sec.name}</span>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
            ({Math.round(sec.weight * 100)}%)
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <DeltaBadge delta={sec.delta} />
          <span style={{ fontWeight: 700, color: scoreColor(sec.score) }}>
            {sec.score}/100
          </span>
        </div>
      </div>

      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${sec.score}%`, background: scoreColor(sec.score) }}
        />
      </div>

      {open && (
        <div style={{ marginTop: 10, fontSize: 12.5, lineHeight: 1.55 }}>
          {sec.criteria.map((criterion) => (
            <div key={criterion.id} style={{ marginBottom: 6 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                <span style={{ color: criterion.passed ? "#34d399" : "#fbbf24" }}>
                  {criterion.passed ? "✓" : "!"} {criterion.label}
                </span>
                <span
                  style={{
                    color: criterion.passed ? "#34d399" : "var(--text-muted)",
                    whiteSpace: "nowrap",
                  }}
                >
                  {criterion.earned}/{criterion.max_points}
                </span>
              </div>
              {!criterion.passed && criterion.advice && (
                <div style={{ color: "var(--text-muted)", fontSize: 11.5, paddingLeft: 16 }}>
                  {criterion.advice}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const AnalysisPanel: React.FC<Props> = ({
  analysis,
  suggestions,
  suggestionSource,
  loading,
  onReplaceText,
}) => {
  const [tab, setTab] = useState<Tab>("scores");

  return (
    <div className="pane">
      <div className="tab-bar">
        <button
          type="button"
          className={`tab-btn ${tab === "scores" ? "active" : ""}`}
          onClick={() => setTab("scores")}
        >
          📊 ATS Score
        </button>
        <button
          type="button"
          className={`tab-btn ${tab === "suggestions" ? "active" : ""}`}
          onClick={() => setTab("suggestions")}
        >
          <Sparkles size={13} style={{ marginRight: 4 }} />
          Suggestions {suggestions.length > 0 ? `(${suggestions.length})` : ""}
        </button>
      </div>

      {tab === "scores" && (
        <div className="analysis-scroll">
          {!analysis ? (
            <div style={{ color: "var(--text-muted)", fontSize: 14, padding: 20, textAlign: "center" }}>
              {loading
                ? "Analyzing..."
                : "Upload a PDF or load the sample resume, then click Recheck Score."}
            </div>
          ) : (
            <>
              <div className="overall-card">
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", textTransform: "uppercase" }}>
                    ATS Readiness Score
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 4 }}>
                    <span className="score-big" style={{ color: scoreColor(analysis.overall_score) }}>
                      {analysis.overall_score}
                    </span>
                    <span style={{ color: "var(--text-muted)", fontSize: 15 }}>/ 100</span>
                    <DeltaBadge delta={analysis.overall_delta} />
                  </div>
                </div>
                <div style={{ textAlign: "right", fontSize: 12, color: "var(--text-muted)" }}>
                  <div>100% rule-based</div>
                  <div>{analysis.sections.length} sections</div>
                </div>
              </div>

              <div
                style={{
                  fontSize: 12,
                  fontWeight: 700,
                  color: "var(--text-muted)",
                  textTransform: "uppercase",
                  marginTop: 4,
                }}
              >
                Section Breakdown
              </div>
              {analysis.sections.map((sec) => (
                <SectionCard key={sec.name} sec={sec} />
              ))}
            </>
          )}
        </div>
      )}

      {tab === "suggestions" && (
        <div className="analysis-scroll">
          {suggestions.length === 0 ? (
            <div style={{ color: "var(--text-muted)", fontSize: 14, padding: 20, textAlign: "center" }}>
              {loading
                ? "Generating suggestions..."
                : analysis
                  ? "No major ATS issues found. Keep refining your bullets and recheck."
                  : "Run Recheck Score first to get improvement suggestions."}
            </div>
          ) : (
            <>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  Edit each rewrite before applying it.
                </span>
                {suggestionSource && (
                  <span className="badge-pill">
                    {suggestionSource === "gemini" ? "Gemini rewrite" : "Rule-based advice"}
                  </span>
                )}
              </div>
              {suggestions.map((sug) => (
                <SuggestionCard key={sug.id} sug={sug} onReplace={onReplaceText} />
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
};
