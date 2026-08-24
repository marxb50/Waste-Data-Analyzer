"""CSV analytics for privacy-safe waste collection records."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping


COLUMN_ALIASES = {
    "ticket": ("Ticket", "ticket"),
    "plate": ("Placa", "plate", "vehicle"),
    "weight_kg": ("Peso Liquido", "Peso Líquido", "weight_kg", "weight"),
    "date": ("Data", "date"),
}


def _first(record: Mapping[str, str], aliases: Iterable[str]) -> str:
    for alias in aliases:
        value = record.get(alias)
        if value is not None and value.strip():
            return value.strip()
    return ""


def _number(value: str) -> float:
    normalized = value.strip().replace(" ", "")
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")
    return float(normalized)


def load_records(csv_path: str | Path) -> list[dict[str, str | float]]:
    """Normalize Portuguese or English CSV headers into one internal schema."""

    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        records: list[dict[str, str | float]] = []
        for row_number, row in enumerate(reader, start=2):
            weight = _first(row, COLUMN_ALIASES["weight_kg"])
            if not weight:
                raise ValueError(f"missing weight at CSV row {row_number}")
            try:
                parsed_weight = _number(weight)
            except ValueError as exc:
                raise ValueError(f"invalid weight at CSV row {row_number}: {weight}") from exc
            if parsed_weight < 0:
                raise ValueError(f"weight cannot be negative at CSV row {row_number}")

            records.append(
                {
                    "ticket": _first(row, COLUMN_ALIASES["ticket"]),
                    "plate": _first(row, COLUMN_ALIASES["plate"]) or "UNKNOWN",
                    "weight_kg": parsed_weight,
                    "date": _first(row, COLUMN_ALIASES["date"]) or "UNKNOWN",
                }
            )
    return records


def analyze_records(records: Iterable[Mapping[str, str | float]]) -> dict[str, Any]:
    """Calculate totals and breakdowns without exposing individual operators."""

    materialized = list(records)
    weights = [float(item["weight_kg"]) for item in materialized]
    by_vehicle: dict[str, float] = defaultdict(float)
    for item in materialized:
        by_vehicle[str(item["plate"])] += float(item["weight_kg"])

    by_date = Counter(str(item["date"]) for item in materialized)
    return {
        "total_trips": len(materialized),
        "total_weight_kg": round(sum(weights), 2),
        "average_weight_kg": round(mean(weights), 2) if weights else 0.0,
        "vehicle_count": len(by_vehicle),
        "weight_by_vehicle_kg": dict(sorted(by_vehicle.items())),
        "trips_by_date": dict(sorted(by_date.items())),
    }


def run_analysis(
    csv_path: str | Path,
    output_json: str | Path | None = None,
    charts_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Compatibility entry point used by the original automation workflow."""

    del charts_dir  # Chart adapters live outside this privacy-safe reference core.
    result = analyze_records(load_records(csv_path))
    if output_json:
        destination = Path(output_json)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze waste collection CSV data")
    parser.add_argument("csv_path")
    parser.add_argument("--output", default="summary.json")
    args = parser.parse_args()

    result = run_analysis(args.csv_path, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
