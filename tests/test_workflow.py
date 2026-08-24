from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from AnalyticalCore import analyze_records, load_records, run_analysis
from PDFExtractionEngine import parse_ticket_text
from VisualReportWorkflow import generate_html_report


class WasteWorkflowTests(unittest.TestCase):
    def test_analysis_supports_portuguese_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "records.csv"
            source.write_text(
                'Ticket,Placa,Peso Liquido,Data\nT-1,DEMO-1,"12.450,50",2026-08-20\n',
                encoding="utf-8",
            )
            result = analyze_records(load_records(source))
            self.assertEqual(1, result["total_trips"])
            self.assertEqual(12450.5, result["total_weight_kg"])

    def test_ticket_parser_extracts_expected_fields(self) -> None:
        parsed = parse_ticket_text(
            "Ticket: T-002\nPlaca: DEMO-02\nPeso Líquido: 9830,00\nData: 20/08/2026"
        )
        self.assertEqual("T-002", parsed["ticket"])
        self.assertEqual("DEMO-02", parsed["plate"])
        self.assertEqual("9830,00", parsed["weight_kg"])

    def test_pipeline_writes_json_and_html(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "records.csv"
            source.write_text(
                "Ticket,Placa,Peso Liquido,Data\nT-1,DEMO-1,1000,2026-08-20\n",
                encoding="utf-8",
            )
            summary_path = Path(folder) / "summary.json"
            report_path = Path(folder) / "report.html"
            run_analysis(source, summary_path)
            written = generate_html_report(source, summary_path, report_path)
            self.assertEqual(1000.0, json.loads(summary_path.read_text())["total_weight_kg"])
            self.assertIn("Waste Operations Summary", written.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

