#!/usr/bin/env python3
"""Simple HTTP server that lists and serves evaluation reports."""

import http.server
import json
import os
import socketserver
from pathlib import Path
from urllib.parse import unquote

RESULTS_DIR = Path(__file__).parent / "results"
PORT = 8888


class ReportHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RESULTS_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_index()
        else:
            super().do_GET()

    def send_index(self):
        runs = sorted(
            [d.name for d in RESULTS_DIR.iterdir() if d.is_dir()],
            reverse=True,
        )

        rows = []
        for run in runs:
            run_dir = RESULTS_DIR / run
            report = run_dir / "report.html"
            results_json = run_dir / "results.json"

            if not report.exists():
                continue

            # Parse metadata from results.json if available
            summary = ""
            if results_json.exists():
                try:
                    data = json.loads(results_json.read_text())
                    total = data.get("total", 0)
                    passed = data.get("passed", 0)
                    summary = f"{passed}/{total} passed"
                except Exception:
                    summary = ""

            # Parse model and timestamp from directory name
            parts = run.split("_", 1)
            model = parts[0] if parts else run
            timestamp = parts[1] if len(parts) > 1 else ""
            # Format timestamp nicely
            display_time = timestamp
            if len(timestamp) >= 8:
                date_part = timestamp[:8]
                rest = timestamp[8:].lstrip("_")
                display_time = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                if rest:
                    # Could be HHMMSS or HHMMSS_suffix
                    time_and_suffix = rest.split("_", 1)
                    t = time_and_suffix[0]
                    suffix = time_and_suffix[1] if len(time_and_suffix) > 1 else ""
                    if len(t) >= 6:
                        display_time += f" {t[:2]}:{t[2:4]}:{t[4:6]}"
                    if suffix:
                        display_time += f" ({suffix})"

            badge = ""
            if summary:
                badge = f'<span class="summary">{summary}</span>'

            rows.append(
                f'<tr>'
                f'<td><a href="/{run}/report.html">{run}</a></td>'
                f'<td>{model}</td>'
                f'<td>{display_time}</td>'
                f'<td>{badge}</td>'
                f'</tr>'
            )

        html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Evaluation Reports</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 900px; margin: 0 auto; padding: 40px 20px; background: #f8f9fa;
    color: #1a1a2e;
  }}
  h1 {{ margin-bottom: 4px; }}
  .subtitle {{ color: #666; margin-bottom: 24px; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff;
           border-radius: 8px; overflow: hidden;
           box-shadow: 0 1px 3px rgba(0,0,0,.1); }}
  th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; }}
  th {{ background: #1a1a2e; color: #fff; }}
  tr:hover {{ background: #f1f3f5; }}
  a {{ color: #0066cc; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .summary {{ background: #e8f5e9; color: #2e7d32; padding: 3px 10px;
              border-radius: 12px; font-size: .85em; font-weight: 600; }}
</style>
</head>
<body>
<h1>Evaluation Reports</h1>
<p class="subtitle">{len(rows)} runs found</p>
<table>
  <tr><th>Run</th><th>Model</th><th>Date</th><th>Result</th></tr>
  {"".join(rows)}
</table>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html.encode())))
        self.end_headers()
        self.wfile.write(html.encode())


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ReportHandler) as httpd:
        print(f"Serving reports at http://localhost:{PORT}")
        print(f"Results directory: {RESULTS_DIR}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")
