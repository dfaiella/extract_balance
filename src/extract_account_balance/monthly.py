import calendar
import re
from collections import defaultdict
from datetime import date
from typing import Any, Dict, Iterable, List


def _record_date(value: object, default_year: int | None) -> date | None:
    text = str(value or "").strip()
    try:
        return date.fromisoformat(text)
    except ValueError:
        pass

    match = re.fullmatch(r"(\d{2})/(\d{2})", text)
    if match and default_year is not None:
        try:
            return date(default_year, int(match.group(1)), int(match.group(2)))
        except ValueError:
            return None
    return None


def year_from_description(description: object) -> int | None:
    match = re.search(r"\b(19|20)\d{2}\b", str(description or ""))
    return int(match.group(0)) if match else None


def statement_year(statement: Dict[str, Any], fallback_year: int) -> int:
    """Resolve a year for legacy MM/DD records that did not store one."""
    stored_year = statement.get("year")
    if stored_year is not None:
        try:
            return int(stored_year)
        except (TypeError, ValueError):
            pass

    year = year_from_description(
        f"{statement.get('description', '')} {statement.get('filename', '')}"
    )
    return year if year is not None else fallback_year


def monthly_average_balances(
    records: Iterable[Dict[str, Any]], default_year: int | None = None
) -> List[Dict[str, float | str]]:
    """Calculate average daily end-of-day balance for each represented month.

    The last record for a transaction date is that day's closing balance.
    A day without a transaction uses the next available closing balance. When
    there is no later balance, the most recent balance is carried to month end.
    """
    daily_rows = daily_balance_series(records, default_year)
    totals: Dict[str, list[float]] = defaultdict(list)
    for row in daily_rows:
        totals[str(row["date"])[:7]].append(float(row["balance"]))

    return [
        {"month": month, "balance": sum(balances) / len(balances)}
        for month, balances in sorted(totals.items())
    ]


def daily_balance_series(
    records: Iterable[Dict[str, Any]], default_year: int | None = None
) -> List[Dict[str, float | str]]:
    """Expand transactions into daily balances and month-to-date averages."""
    daily: Dict[date, float] = {}
    for record in records:
        record_date = _record_date(record.get("date"), default_year)
        if record_date is not None:
            daily[record_date] = float(record["balance"])

    if not daily:
        return []

    dates = sorted(daily)
    months: Dict[tuple[int, int], List[date]] = defaultdict(list)
    for record_date in dates:
        months[(record_date.year, record_date.month)].append(record_date)

    results: List[Dict[str, float | str]] = []
    for (year, month), month_dates in sorted(months.items()):
        days_in_month = calendar.monthrange(year, month)[1]
        total = 0.0
        next_index = 0
        last_balance: float | None = None

        for day_number in range(1, days_in_month + 1):
            current = date(year, month, day_number)
            while next_index < len(dates) and dates[next_index] < current:
                last_balance = daily[dates[next_index]]
                next_index += 1

            if current in daily:
                balance = daily[current]
            elif next_index < len(dates):
                balance = daily[dates[next_index]]
            elif last_balance is not None:
                balance = last_balance
            else:
                balance = daily[month_dates[-1]]
            total += balance
            results.append(
                {
                    "date": current.isoformat(),
                    "balance": balance,
                    "rolling_average": total / day_number,
                }
            )
    return results
