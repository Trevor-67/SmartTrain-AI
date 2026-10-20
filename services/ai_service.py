
import re

from services.date_parser import parse_preferred_date


TRAINING_TYPES = {
    "unity": "Unity",
    "gaap": "GAAP",
    "pos": "POS",
}


def parse_training_request(message):
    """Extract supported training details from one customer message."""

    text = (message or "").strip().lower()

    result = {
        "training_type": None,
        "delivery_method": None,
        "participants": None,
        "preferred_date": None,
        "missing_fields": [],
    }

    for keyword, label in TRAINING_TYPES.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            result["training_type"] = label
            break

    if re.search(r"\b(virtual|online|remote|teams)\b", text):
        result["delivery_method"] = "Virtual"
    elif re.search(r"\b(on[\s-]?site|onsite|at our site)\b", text):
        result["delivery_method"] = "On-site"
    elif re.search(r"\b(classroom|in[- ]person class)\b", text):
        result["delivery_method"] = "Classroom"

    number_words = {
        "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8,
        "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    }

    participant_match = re.search(
        r"\b(\d+|one|two|three|four|five|six|seven|eight|"
        r"nine|ten|eleven|twelve)\s+"
        r"(?:people|employees|participants|users|staff|"
        r"managers|persons|colleagues|attendees)\b",
        text,
    )

    if participant_match:
        value = participant_match.group(1)
        result["participants"] = (
            int(value) if value.isdigit() else number_words[value]
        )

    result["preferred_date"] = parse_preferred_date(message)

    result["missing_fields"] = get_missing_fields(result)

    return result


def get_missing_fields(details):
    """Return required fields that are not yet supplied."""

    required = [
        ("training_type", "training type"),
        ("delivery_method", "delivery method"),
        ("participants", "number of participants"),
        ("preferred_date", "preferred date"),
    ]

    return [
        label for key, label in required
        if not details.get(key)
    ]


def generate_clarification(result):
    missing = result.get("missing_fields", [])

    if not missing:
        return None

    if len(missing) == 1:
        fields = missing[0]
    elif len(missing) == 2:
        fields = f"{missing[0]} and {missing[1]}"
    else:
        fields = ", ".join(missing[:-1]) + f", and {missing[-1]}"

    return (
        f"To continue scheduling, please provide your {fields}. "
        "You can send the details together in one message."
    )
