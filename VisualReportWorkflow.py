"""Generate a self-contained HTML report from normalized analytics."""

from __future__ import annotations

import html
import json
from pathlib import Path

from AnalyticalCore import load_records, run_analysis


def generate_html_report(
    csv_path: str | Path,
    json_path: str | Path,
    output_html: str | Path,
) -> Path:
    summary = run_analysis(csv_path, json_path)
    records = load_records(csv_path)

    rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item['ticket']))}</td>"
        f"<td>{html.escape(str(item['plate']))}</td>"
        f"<td>{float(item['weight_kg']):,.2f}</td>"
        f"<td>{html.escape(str(item['date']))}</td>"
        "</tr>"
        for item in records
    )

    document = f"""<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Waste Operations Summary</title>
<style>
body{{font:15px system-ui;margin:40px;color:#16332b;background:#f4f8f6}}
main{{max-width:960px;margin:auto;background:white;padding:32px;border-radius:18px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.card{{padding:18px;background:#e9f5ef;border-radius:12px}} .value{{font-size:1.7rem;font-weight:700}}
table{{width:100%;border-collapse:collapse;margin-top:24px}} th,td{{padding:10px;border-bottom:1px solid #dce8e2;text-align:left}}
@media(max-width:700px){{.cards{{grid-template-columns:1fr}}}}
</style>
<main>
<h1>Waste Operations Summary</h1>
<p>Privacy-safe operational overview generated from normalized weighing records.</p>
<section class="cards">
<div class="card"><div>Trips</div><div class="value">{summary['total_trips']}</div></div>
<div class="card"><div>Total weight</div><div class="value">{summary['total_weight_kg']:,.2f} kg</div></div>
<div class="card"><div>Average load</div><div class="value">{summary['average_weight_kg']:,.2f} kg</div></div>
</section>
<table><thead><tr><th>Ticket</th><th>Vehicle</th><th>Weight (kg)</th><th>Date</th></tr></thead><tbody>{rows}</tbody></table>
<script type="application/json" id="summary">{html.escape(json.dumps(summary))}</script>
</main>
</html>"""

    destination = Path(output_html)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document, encoding="utf-8")
    return destination.resolve()
