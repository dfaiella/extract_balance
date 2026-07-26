import re
from typing import Optional


def extract_balance(text: str) -> Optional[float]:
    """Extract the first monetary value from the provided text.

    The function looks for a currency amount such as "$1,234.56" or "100.00".
    """
    match = re.search(r"(?:^|[^\d])(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)(?:$|[^\d])", text)
    if not match:
        return None

    value = match.group(1).replace(",", "")
    return float(value)
