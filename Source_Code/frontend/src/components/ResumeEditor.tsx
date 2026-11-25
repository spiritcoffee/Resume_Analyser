import React, { useRef, useState } from "react";
import { Code, Eye } from "lucide-react";

interface Props {
  value: string;
  onChange: (value: string) => void;
  wordCount?: number;
  dirty?: boolean;
}

export const ResumeEditor: React.FC<Props> = ({ value, onChange, wordCount, dirty }) => {
  const [mode, setMode] = useState<"source" | "preview">("source");
  const linesRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lines = value.split("\n");

  const handleScroll = () => {
    if (linesRef.current && textareaRef.current) {
      linesRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  };

  const renderPreview = () => {
    return lines.map((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) return <div key={idx} style={{ height: 8 }} />;
      if (trimmed.startsWith("## ")) {
        return <h2 key={idx}>{trimmed.replace(/^##\s*/, "")}</h2>;
      }
      if (trimmed.startsWith("- ")) {
        return (
          <div key={idx} style={{ paddingLeft: 14, fontSize: 13.5 }}>
            • {trimmed.slice(2)}
          </div>
        );
      }
      if (idx === 0) {
        return (
          <div key={idx} style={{ fontSize: 22, fontWeight: 800, marginBottom: 2 }}>
            {trimmed}
          </div>
        );
      }
      return (
        <div key={idx} style={{ fontSize: 13.5 }}>
          {trimmed}
        </div>
      );
    });
  };

  return (
    <div className="pane">
      <div className="pane-header">
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span>Resume Editor</span>
          {dirty && (
            <span style={{ fontSize: 11, color: "#fbbf24" }}>
              • Edited (click Recheck Score)
            </span>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {wordCount !== undefined && (
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
              {wordCount} words
            </span>
          )}
          <button
            type="button"
            className="btn"
            style={{ padding: "4px 8px", fontSize: 12 }}
            onClick={() => setMode(mode === "source" ? "preview" : "source")}
          >
            {mode === "source" ? <Eye size={13} /> : <Code size={13} />}
            {mode === "source" ? "Preview" : "Source"}
          </button>
        </div>
      </div>

      {mode === "source" ? (
        <div className="editor-container">
          <div ref={linesRef} className="line-numbers" aria-hidden="true">
            {lines.map((_, i) => (
              <div key={i}>{i + 1}</div>
            ))}
          </div>
          <textarea
            ref={textareaRef}
            className="resume-textarea"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onScroll={handleScroll}
            placeholder="Upload a PDF or paste your resume text here..."
            spellCheck={false}
          />
        </div>
      ) : (
        <div className="preview-sheet">{renderPreview()}</div>
      )}
    </div>
  );
};
