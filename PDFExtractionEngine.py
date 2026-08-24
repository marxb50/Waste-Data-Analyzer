"""Extract a small, auditable ticket schema from text-based PDF files."""

from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader


PATTERNS = {
    "ticket": re.compile(r"(?:ticket|bilhete)\s*[:#-]?\s*([A-Z0-9-]+)", re.IGNORECASE),
    "plate": re.compile(r"(?:placa|plate)\s*[:#-]?\s*([A-Z0-9-]+)", re.IGNORECASE),
    "weight_kg": re.compile(
        r"(?:peso\s*l[ií]quido|net\s*weight)\s*[:#-]?\s*([0-9.,]+)",
        re.IGNORECASE,
    ),
    "date": re.compile(r"(?:data|date)\s*[:#-]?\s*([0-9/.-]+)", re.IGNORECASE),
}


def parse_ticket_text(text: str) -> dict[str, str]:
    """Parse recognized labels while leaving unavailable fields empty."""

    result: dict[str, str] = {}
    for field, pattern in PATTERNS.items():
        match = pattern.search(text)
        result[field] = match.group(1).strip() if match else ""
    return result


def extract_ticket_data(pdf_path: str | Path) -> dict[str, str]:
    """Extract text from every page and parse the normalized ticket fields."""

    source = Path(pdf_path)
    reader = PdfReader(str(source))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not text.strip():
        raise ValueError(f"no text found in {source.name}; OCR may be required")
    return parse_ticket_text(text)
