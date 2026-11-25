"""Render Documentation/SRS.md into a styled, print-ready Documentation/SRS.html.

Usage:
    python Documentation/build_docs.py

Requires the `markdown` package (pip install markdown). Open the generated HTML in a
browser and use Print -> Save as PDF to produce the submission copy.
"""

from __future__ import annotations

from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "SRS.md"
TARGET = ROOT / "SRS.html"

DOC_TITLE = "Software Requirements Specification"
DOC_SUBTITLE = "ATS Resume Analyser"
DOC_META = [
    ("Project", "ATS Resume Analyser (Resume Analysis and Improvement Tool)"),
    ("Group", "Group 1"),
    ("Version", "1.0"),
    ("Date", "25 November 2026"),
    ("Status", "Baseline — matches the implemented system"),
]

PAGE_CSS = """
@page {
  size: A4;
  margin: 20mm 18mm 22mm 18mm;
}

:root {
  --ink: #1a202c;
  --muted: #55607a;
  --line: #d7dce7;
  --accent: #0f766e;
  --accent-soft: #e6f4f1;
  --code-bg: #f4f6fa;
}

* { box-sizing: border-box; }

html { font-size: 15px; }

body {
  margin: 0;
  padding: 32px 20px 64px;
  background: #eef1f6;
  color: var(--ink);
  font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Inter, Roboto, Arial, sans-serif;
  line-height: 1.55;
}

.page {
  max-width: 210mm;
  margin: 0 auto;
  background: #ffffff;
  padding: 24mm 20mm;
  box-shadow: 0 10px 40px rgba(15, 23, 42, 0.12);
}

/* Cover */
.cover { min-height: 220mm; display: flex; flex-direction: column; justify-content: center; }
.cover .eyebrow {
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 700;
}
.cover h1 {
  font-size: 2.5rem;
  line-height: 1.15;
  margin: 10px 0 6px;
  border: 0;
  padding: 0;
  page-break-before: avoid;
}
.cover .subtitle { font-size: 1.3rem; color: var(--muted); margin: 0 0 28px; }
.cover .rule { height: 4px; width: 84px; background: var(--accent); border-radius: 2px; }
.cover table { margin-top: 36px; width: 100%; border: 0; }
.cover table td { border: 0; padding: 4px 0; font-size: 0.92rem; }
.cover table td:first-child { width: 130px; color: var(--muted); font-weight: 600; }

/* Headings */
h1, h2, h3, h4 { line-height: 1.25; color: #10233f; }
h1 {
  font-size: 1.55rem;
  margin: 2.4em 0 0.6em;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--line);
  page-break-before: always;
  page-break-after: avoid;
}
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 1.18rem; margin: 1.8em 0 0.5em; page-break-after: avoid; }
h3 { font-size: 1.02rem; margin: 1.4em 0 0.4em; page-break-after: avoid; }
h4 { font-size: 0.95rem; margin: 1.2em 0 0.3em; }

p { margin: 0.55em 0; }
ul, ol { margin: 0.5em 0 0.9em; padding-left: 1.5em; }
li { margin: 0.22em 0; }

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.9em 0 1.3em;
  font-size: 0.87rem;
  page-break-inside: auto;
}
thead { background: var(--accent-soft); }
th, td {
  border: 1px solid var(--line);
  padding: 6px 9px;
  text-align: left;
  vertical-align: top;
}
th { font-weight: 700; color: #0b3d38; }
tr { page-break-inside: avoid; }
tbody tr:nth-child(even) { background: #fafbfd; }

/* Code */
code {
  font-family: Consolas, "SF Mono", Menlo, monospace;
  font-size: 0.86em;
  background: var(--code-bg);
  padding: 1px 5px;
  border-radius: 4px;
  border: 1px solid #e3e8f2;
}
pre {
  background: var(--code-bg);
  border: 1px solid var(--line);
  border-left: 4px solid var(--accent);
  border-radius: 6px;
  padding: 12px 14px;
  overflow-x: auto;
  font-size: 0.8rem;
  line-height: 1.45;
  page-break-inside: avoid;
}
pre code { background: none; border: 0; padding: 0; font-size: inherit; }

blockquote {
  margin: 1em 0;
  padding: 10px 16px;
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
  border-radius: 0 6px 6px 0;
}
blockquote p { margin: 0; }

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

hr { border: 0; border-top: 1px solid var(--line); margin: 2em 0; }

/* Screen toolbar */
.screen-tools {
  max-width: 210mm;
  margin: 0 auto 14px;
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: flex-end;
  font-size: 0.82rem;
  color: var(--muted);
}
.screen-tools button {
  font: inherit;
  padding: 7px 13px;
  border-radius: 6px;
  border: 1px solid var(--accent);
  background: var(--accent);
  color: #ffffff;
  cursor: pointer;
}

@media print {
  html { font-size: 10.5pt; }
  body { background: #ffffff; padding: 0; }
  .page { box-shadow: none; padding: 0; max-width: none; }
  .screen-tools { display: none; }
  a { color: inherit; }
  .cover { min-height: 240mm; }
  pre, table, blockquote { page-break-inside: avoid; }
}
"""


def render() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    # The cover supplies the masthead, so the body starts at the revision history.
    marker = "## Revision History"
    start = source.find(marker)
    if start == -1:
        raise SystemExit(f"Marker {marker!r} not found in {SOURCE.name}")

    body_source = "# Document Control\n\n" + source[start:]
    # Standalone `---` rules would render above each page-broken H1.
    body_source = "\n".join(
        line for line in body_source.splitlines() if line.strip() != "---"
    )

    body = markdown.markdown(
        body_source,
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"],
        extension_configs={"toc": {"permalink": False}},
    )

    meta_rows = "\n".join(
        f"<tr><td>{label}</td><td>{value}</td></tr>" for label, value in DOC_META
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{DOC_SUBTITLE} — {DOC_TITLE}</title>
<style>{PAGE_CSS}</style>
</head>
<body>
<div class="screen-tools">
  <span>Use Print (Ctrl+P) → Save as PDF for the submission copy.</span>
  <button type="button" onclick="window.print()">Print / Save as PDF</button>
</div>

<div class="page">
  <section class="cover">
    <div class="eyebrow">Group 1 · Project Documentation</div>
    <h1>{DOC_TITLE}</h1>
    <p class="subtitle">{DOC_SUBTITLE}</p>
    <div class="rule"></div>
    <table>
      {meta_rows}
    </table>
  </section>

  {body}
</div>
</body>
</html>
"""

    TARGET.write_text(html, encoding="utf-8")
    print(f"Wrote {TARGET}")


if __name__ == "__main__":
    render()
