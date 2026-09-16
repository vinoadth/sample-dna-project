from __future__ import annotations

import json
from pathlib import Path

STATIC_DIR = Path(__file__).resolve().parent / "static"


def render_report_html(payload: dict) -> str:
    """Standalone HTML report with the same charts as the live dashboard."""
    css = (STATIC_DIR / "app.css").read_text(encoding="utf-8")
    js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    title = payload.get("source_filename") or "SNP comparison"
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{_escape(title)}</title>
    <style>{css}</style>
  </head>
  <body>
    <div class="page">
      <header class="hero">
        <h1>SNP comparison</h1>
        <p>Embedded analysis of {_escape(str(title))}. Mixture weights use overlapping AADR Human Origins SNPs.</p>
      </header>
      <div id="results"></div>
    </div>
    <script>window.ANALYSIS_PAYLOAD = {data};</script>
    <script>{js}</script>
  </body>
</html>
"""


def write_report(payload: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report_html(payload), encoding="utf-8")
    return path


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
