from pathlib import Path

import fitz

from extract_account_balance.pdf_tools import extract_rows_from_text, read_pdf_text
from extract_account_balance.storage import load_records, save_records


def test_extract_rows_from_text():
    text = """Account statement
2024-01-01 Balance 1,234.56
2024-01-02 Balance 1,250.00
"""

    rows = extract_rows_from_text(text)

    assert rows[0]["date"] == "2024-01-01"
    assert rows[0]["balance"] == 1234.56
    assert rows[1]["balance"] == 1250.0
    assert rows[0]["date"] <= rows[1]["date"]


def test_extract_rows_from_transaction_style_text():
    text = """06/01 ID 01 REGULAR SHARE Balance Forward 5.00
06/30 Ending Balance 5.00
"""

    rows = extract_rows_from_text(text)

    assert rows[0]["date"] == "06/01"
    assert rows[0]["balance"] == 5.0
    assert rows[1]["date"] == "06/30"
    assert rows[1]["balance"] == 5.0


def test_save_and_load_records(tmp_path: Path):
    records = [{"date": "2024-01-01", "balance": 100.0}]
    path = tmp_path / "records.json"

    save_records(records, path)
    loaded = load_records(path)

    assert loaded == records


def test_read_pdf_text(tmp_path: Path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "2024-01-01 Balance 1,234.56")
    doc.save(pdf_path)
    doc.close()

    text = read_pdf_text(pdf_path)

    assert "2024-01-01" in text
    assert "1,234.56" in text
