import re
from pathlib import Path
from typing import List, Dict


def _split_transaction_details(text: str) -> tuple[str, float | None]:
    """Remove and parse a trailing transaction amount from row details."""
    cleaned = text.strip()
    amount_match = re.search(
        r"(?:^|\s)\$?([+-]?\d{1,3}(?:,\d{3})*\.\d{2}|[+-]?\d+\.\d{2})\s*$",
        cleaned,
    )
    if amount_match is None:
        return cleaned, None
    details = cleaned[: amount_match.start()].rstrip()
    amount = float(amount_match.group(1).replace(",", ""))
    return details, amount


def read_pdf_text(path: str | Path) -> str:
    """Read PDF text using an offline reader backend.

    The helper prefers PyMuPDF (fitz) and falls back to pypdf when needed.
    """
    pdf_path = Path(path)

    try:
        import fitz

        doc = fitz.open(str(pdf_path))
        try:
            return "\n".join(page.get_text() or "" for page in doc)
        finally:
            doc.close()
    except Exception:
        pass

    try:
        import pypdf

        reader = pypdf.PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise RuntimeError("No offline PDF reader is available") from exc


def extract_description_from_text(text: str) -> str:
    """Try to infer a human-readable statement description from PDF text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        lowered = line.lower()
        if any(token in lowered for token in ["statement", "account activity", "account summary", "transaction history"]):
            cleaned = re.sub(r"\s+", " ", line)
            return cleaned

    for line in lines[:20]:
        if re.search(r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b", line, re.IGNORECASE):
            cleaned = re.sub(r"\s+", " ", line)
            return cleaned

    for line in lines[:20]:
        if len(line) <= 80 and not re.search(r"\d", line):
            cleaned = re.sub(r"\s+", " ", line)
            if cleaned and cleaned.lower() not in {"account", "statement", "summary"}:
                return cleaned

    return ""


def extract_rows_from_text(text: str) -> List[Dict[str, float | str]]:
    """Extract balance rows from statement text.

    If the text contains the separator bar, parsing starts after that divider.
    Otherwise the parser scans the full text, which keeps simple tests working.
    """
    rows: List[Dict[str, float | str]] = []
    lines = text.splitlines()
    start_index = 0

    for index, line in enumerate(lines):
        if "*****************************************************************************************" in line:
            start_index = index + 1
            break

    for line in lines[start_index:]:
        stripped = line.strip()
        if not stripped:
            continue

        iso_date_match = re.match(r"^(\d{4}-\d{2}-\d{2})\b", stripped)
        if iso_date_match:
            balance_match = re.search(
                r"\$?([+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?|[+-]?\d+(?:\.\d+)?)$",
                stripped,
            )
            if balance_match:
                details_text = stripped[
                    iso_date_match.end() : balance_match.start()
                ]
                details, amount = _split_transaction_details(details_text)
                rows.append(
                    {
                        "date": iso_date_match.group(1),
                        "balance": float(balance_match.group(1).replace(",", "")),
                        "details": details,
                        "amount": amount,
                    }
                )
                continue

        date_match = re.match(r"^(\d{2}/\d{2})\b", stripped)
        if date_match:
            balance_match = re.search(r"([+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?|[+-]?\d+(?:\.\d+)?)$", stripped)
            if balance_match:
                balance_text = balance_match.group(1).replace(",", "")
                details_text = stripped[date_match.end() : balance_match.start()]
                details, amount = _split_transaction_details(details_text)
                rows.append(
                    {
                        "date": date_match.group(1),
                        "balance": float(balance_text),
                        "details": details,
                        "amount": amount,
                    }
                )
                continue

        balance_match = re.search(r"(Ending Balance|Balance Forward)\s*([+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?|[+-]?\d+(?:\.\d+)?)", stripped, re.IGNORECASE)
        if balance_match:
            rows.append({"date": "", "balance": float(balance_match.group(2).replace(",", ""))})

    return rows
