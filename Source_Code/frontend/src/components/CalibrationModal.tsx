import React, { useState } from "react";
import { CalibrationConfig, ExperienceLevel, TargetDomain } from "../types";

interface Props {
  initialConfig: CalibrationConfig;
  onSave: (config: CalibrationConfig) => void;
  onClose?: () => void;
}

export const CalibrationModal: React.FC<Props> = ({ initialConfig, onSave, onClose }) => {
  const [config, setConfig] = useState<CalibrationConfig>(initialConfig);

  const levels: { value: ExperienceLevel; label: string }[] = [
    { value: "fresher", label: "Fresher / Student" },
    { value: "experienced", label: "Experienced Professional" },
  ];

  const domains: { value: TargetDomain; label: string }[] = [
    { value: "software", label: "Software / Tech" },
    { value: "data", label: "Data / AI / ML" },
    { value: "product", label: "Product / Mgmt" },
    { value: "general", label: "General / Other" },
  ];

  return (
    <div className="modal-backdrop">
      <div className="modal-box">
        <h2 style={{ marginTop: 0, marginBottom: 6 }}>Calibrate Your ATS Score</h2>
        <p style={{ color: "var(--text-muted)", fontSize: 13, marginTop: 0 }}>
          Two quick choices adjust the section weights and the ATS checks.
        </p>

        <div style={{ marginTop: 14 }}>
          <label style={{ fontSize: 13, fontWeight: 600 }}>1. Experience Level</label>
          <div className="option-grid">
            {levels.map((item) => (
              <button
                key={item.value}
                type="button"
                className={`option-btn ${config.experience_level === item.value ? "active" : ""}`}
                onClick={() => setConfig({ ...config, experience_level: item.value })}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginTop: 14 }}>
          <label style={{ fontSize: 13, fontWeight: 600 }}>2. Target Domain</label>
          <div className="option-grid">
            {domains.map((item) => (
              <button
                key={item.value}
                type="button"
                className={`option-btn ${config.target_domain === item.value ? "active" : ""}`}
                onClick={() => setConfig({ ...config, target_domain: item.value })}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginTop: 14 }}>
          <label style={{ fontSize: 13, fontWeight: 600 }}>
            3. Target Role <span style={{ color: "var(--text-muted)" }}>(optional)</span>
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="e.g., Backend Software Engineer"
            value={config.target_role}
            onChange={(e) => setConfig({ ...config, target_role: e.target.value })}
          />
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 18 }}>
          {onClose && (
            <button type="button" className="btn" onClick={onClose}>
              Cancel
            </button>
          )}
          <button type="button" className="btn btn-primary" onClick={() => onSave(config)}>
            Save &amp; Analyze
          </button>
        </div>
      </div>
    </div>
  );
};
