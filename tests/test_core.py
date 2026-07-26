from extract_account_balance import extract_balance
from extract_account_balance.app import sort_records_by_date


def test_extracts_balance_from_text():
    text = "Account balance is $1,234.56 as of today."
    assert extract_balance(text) == 1234.56


def test_returns_none_when_no_balance_present():
    assert extract_balance("No monetary value here") is None


def test_sort_records_by_date_newest_first():
    rows = [
        {"date": "2024-01-01", "balance": 100.0},
        {"date": "2024-02-01", "balance": 200.0},
    ]

    sorted_rows = sort_records_by_date(rows)

    assert [row["date"] for row in sorted_rows] == ["2024-02-01", "2024-01-01"]
