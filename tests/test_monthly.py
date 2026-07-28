import pytest

from extract_account_balance.monthly import (
    daily_balance_series,
    monthly_average_balances,
    statement_year,
)


def test_uses_last_balance_when_multiple_transactions_share_a_day():
    rows = [
        {"date": "2024-04-01", "balance": 10},
        {"date": "2024-04-01", "balance": 20},
        {"date": "2024-04-30", "balance": 50},
    ]

    result = monthly_average_balances(rows)

    assert result == [{"month": "2024-04", "balance": pytest.approx(49)}]


def test_missing_days_use_the_next_account_balance():
    rows = [
        {"date": "2024-01-01", "balance": 100},
        {"date": "2024-01-03", "balance": 300},
        {"date": "2024-01-31", "balance": 500},
    ]

    result = monthly_average_balances(rows)

    expected = (100 + 300 + 300 + (27 * 500) + 500) / 31
    assert result[0]["balance"] == pytest.approx(expected)


def test_divides_by_every_day_in_the_month_including_leap_day():
    rows = [
        {"date": "2024-02-01", "balance": 10},
        {"date": "2024-02-29", "balance": 39},
    ]

    result = monthly_average_balances(rows)

    assert result[0]["balance"] == pytest.approx((10 + 28 * 39) / 29)


def test_supports_statement_dates_without_a_year_when_year_is_known():
    rows = [{"date": "06/01", "balance": 50}, {"date": "06/30", "balance": 80}]

    result = monthly_average_balances(rows, default_year=2025)

    assert result == [{"month": "2025-06", "balance": pytest.approx(79)}]


def test_daily_series_includes_month_to_date_rolling_average():
    rows = [
        {"date": "2024-04-01", "balance": 10},
        {"date": "2024-04-03", "balance": 40},
        {"date": "2024-04-30", "balance": 70},
    ]

    result = daily_balance_series(rows)

    assert result[0] == {
        "date": "2024-04-01",
        "balance": 10,
        "rolling_average": 10,
    }
    assert result[1]["balance"] == 40
    assert result[1]["rolling_average"] == pytest.approx(25)
    assert result[-1]["rolling_average"] == pytest.approx(
        monthly_average_balances(rows)[0]["balance"]
    )


def test_legacy_statement_without_year_uses_fallback_instead_of_showing_no_data():
    statement = {
        "filename": "statement.pdf",
        "description": "Account activity",
        "records": [{"date": "06/01", "balance": 50}],
    }

    year = statement_year(statement, fallback_year=2026)
    result = daily_balance_series(statement["records"], default_year=year)

    assert year == 2026
    assert len(result) == 30
    assert result[0]["date"] == "2026-06-01"
