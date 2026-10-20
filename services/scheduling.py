
from datetime import date, timedelta
from services.availability import get_available_slots


def find_training_slots(trainer_name, preferred_date):
    if not trainer_name or not preferred_date:
        return {
            "available": False,
            "trainer": trainer_name,
            "date": preferred_date,
            "slots": [],
            "alternatives": [],
        }

    primary_slots = get_available_slots(
        trainer_name,
        preferred_date,
    )
from datetime import date, timedelta
from services.availability import get_available_slots


def find_training_slots(trainer_name, preferred_date):
    result = {
        "available": False,
        "trainer": trainer_name,
        "date": preferred_date,
        "requested_date": preferred_date,
        "slots": [],
        "alternatives": [],
        "is_alternative": False,
    }

    if not trainer_name or not preferred_date:
        return result

    try:
        start_date = date.fromisoformat(preferred_date)
    except (TypeError, ValueError):
        return result

    preferred_slots = get_available_slots(
        trainer_name,
        preferred_date,
    )

    if preferred_slots:
        result["available"] = True
        result["slots"] = preferred_slots
    else:
        # Search the next seven days for the first available date.
        for offset in range(1, 8):
            candidate_date = (
                start_date + timedelta(days=offset)
            ).isoformat()

            candidate_slots = get_available_slots(
                trainer_name,
                candidate_date,
            )

            if candidate_slots:
                result["available"] = True
                result["date"] = candidate_date
                result["slots"] = candidate_slots
                result["is_alternative"] = True
                break

    # Collect additional alternatives for display or future selection.
    for offset in range(1, 8):
        candidate_date = (
            start_date + timedelta(days=offset)
        ).isoformat()

        candidate_slots = get_available_slots(
            trainer_name,
            candidate_date,
        )

        for slot in candidate_slots:
            result["alternatives"].append({
                "date": candidate_date,
                "start": slot["start"],
                "end": slot["end"],
                "trainer": trainer_name,
            })

        if len(result["alternatives"]) >= 5:
            break

    result["alternatives"] = result["alternatives"][:5]
    return result


    alternatives = []

    try:
        start_date = date.fromisoformat(preferred_date)
    except (TypeError, ValueError):
        return {
            "available": False,
            "trainer": trainer_name,
            "date": preferred_date,
            "slots": [],
            "alternatives": [],
        }

    # Search up to seven days after the preferred date.
    for offset in range(1, 8):
        candidate_date = start_date + timedelta(days=offset)
        candidate_text = candidate_date.isoformat()

        candidate_slots = get_available_slots(
            trainer_name,
            candidate_text,
        )

        for slot in candidate_slots:
            alternatives.append({
                "date": candidate_text,
                "start": slot["start"],
                "end": slot["end"],
                "trainer": trainer_name,
            })

        if len(alternatives) >= 5:
            break

    return {
        "available": bool(primary_slots),
        "trainer": trainer_name,
        "date": preferred_date,
        "slots": primary_slots,
        "alternatives": alternatives[:5],
    }
