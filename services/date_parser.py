
import re
from datetime import date, datetime, timedelta


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def parse_preferred_date(message, today=None):
    """
    Parse common date phrases into YYYY-MM-DD.
    'next Wednesday' means Wednesday in the following week.
    """

    if not message:
        return None

    today = today or date.today()
    text = message.lower().strip()

    if "day after tomorrow" in text:
        return (today + timedelta(days=2)).isoformat()

    if "tomorrow" in text:
        return (today + timedelta(days=1)).isoformat()

    if re.search(r"\btoday\b", text):
        return today.isoformat()

    # ISO date, e.g. 2026-10-22
    match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if match:
        try:
            return date.fromisoformat(match.group(1)).isoformat()
        except ValueError:
            return None

    # Numeric date, e.g. 22/10/2026 or 22-10-2026
    match = re.search(
        r"\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b",
        text,
    )
    if match:
        day, month, year = map(int, match.groups())
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return None

    # Named date, e.g. 22 October or October 22.
    months = (
        "january february march april may june july august "
        "september october november december"
    ).split()
    month_pattern = "|".join(months)

    match = re.search(
        rf"\b(\d{{1,2}})\s+({month_pattern})"
        rf"(?:\s+(20\d{{2}}))?\b",
        text,
    )

    if not match:
        match = re.search(
            rf"\b({month_pattern})\s+(\d{{1,2}})"
            rf"(?:,?\s+(20\d{{2}}))?\b",
            text,
        )

        if match:
            month_name, day_text, year_text = match.groups()
        else:
            month_name = day_text = year_text = None
    else:
        day_text, month_name, year_text = match.groups()

    if month_name:
        month = months.index(month_name) + 1
        year = int(year_text) if year_text else today.year

        try:
            candidate = date(year, month, int(day_text))
        except ValueError:
            return None

        if not year_text and candidate < today:
            try:
                candidate = date(year + 1, month, int(day_text))
            except ValueError:
                return None

        return candidate.isoformat()

    # Weekday phrases: Wednesday, next Wednesday, this Wednesday.
    for weekday_name, weekday_number in WEEKDAYS.items():
        if re.search(rf"\b{weekday_name}\b", text):
            days_ahead = (weekday_number - today.weekday()) % 7

            if re.search(rf"\bnext\s+{weekday_name}\b", text):
                days_ahead = days_ahead + 7 if days_ahead else 7
            elif days_ahead == 0:
                # A bare weekday means the next occurrence, not today.
                days_ahead = 7

            return (today + timedelta(days=days_ahead)).isoformat()

    return None
