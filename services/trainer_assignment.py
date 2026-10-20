
from datetime import date, timedelta

from database import get_db_connection

from services.availability import (
    TRAINERS,
    TRAINER_SKILLS,
    get_available_slots,
)

from services.booking import create_booking
from services.human_review import escalate_case
from services.timeline import add_timeline_event


def auto_assign_and_schedule(case_id):
    connection = get_db_connection()

    case = connection.execute("""
        SELECT *
        FROM training_cases
        WHERE id = ?
    """, (case_id,)).fetchone()

    if case is None:
        connection.close()

        return {
            "success": False,
            "reason": "Training case not found.",
        }

    training_type = (case["training_type"] or "").strip()
    preferred_date = case["preferred_date"]

    connection.close()

    if not training_type or not preferred_date:
        reason = "Training type or preferred date is missing."

        escalate_case(case_id, reason)

        return {
            "success": False,
            "reason": reason,
        }

    try:
        first_date = date.fromisoformat(preferred_date)
    except (ValueError, TypeError):
        reason = "The requested training date is invalid."

        escalate_case(case_id, reason)

        return {
            "success": False,
            "reason": reason,
        }

    eligible_trainers = [
        trainer
        for trainer in TRAINERS
        if training_type.lower() in {
            skill.lower()
            for skill in TRAINER_SKILLS.get(trainer, set())
        }
    ]

    if not eligible_trainers:
        reason = (
            f"No trainer is configured for "
            f"{training_type} training."
        )

        escalate_case(case_id, reason)

        return {
            "success": False,
            "reason": reason,
        }

    candidates = []

    # Check the requested date and the following seven days.
    for day_offset in range(8):
        candidate_date = (
            first_date + timedelta(days=day_offset)
        ).isoformat()

        # The availability service returns no slots on weekends.
        for trainer in eligible_trainers:
            available_slots = get_available_slots(
                trainer,
                candidate_date,
            )

            if not available_slots:
                continue

            connection = get_db_connection()

            workload = connection.execute("""
                SELECT COUNT(*) AS total
                FROM bookings
                WHERE trainer_name = ?
                  AND status = 'Confirmed'
            """, (trainer,)).fetchone()["total"]

            connection.close()

            for slot in available_slots:
                candidates.append({
                    "date": candidate_date,
                    "day_offset": day_offset,
                    "trainer": trainer,
                    "workload": workload,
                    "start": slot["start"],
                    "end": slot["end"],
                })

    if not candidates:
        reason = (
            "No eligible trainer has an available slot "
            "within the next seven days."
        )

        escalate_case(case_id, reason)

        return {
            "success": False,
            "reason": reason,
        }

    # Prioritise:
    # 1. Earliest date
    # 2. Trainer with the lowest current workload
    # 3. Earliest available time
    # 4. Trainer name as a stable tie-breaker
    candidates.sort(
        key=lambda item: (
            item["day_offset"],
            item["workload"],
            item["start"],
            item["trainer"],
        )
    )

    # Try candidates in order. The booking service should
    # recheck availability before committing a booking.
    for candidate in candidates:
        connection = get_db_connection()

        connection.execute("""
            UPDATE training_cases
            SET
                assigned_trainer = ?,
                preferred_date = ?,
                status = ?
            WHERE id = ?
        """, (
            candidate["trainer"],
            candidate["date"],
            "AI Processing",
            case_id,
        ))

        connection.commit()
        connection.close()

        booking_result = create_booking(
            case_id,
            candidate["trainer"],
            candidate["date"],
            candidate["start"],
            candidate["end"],
        )

        if booking_result.get("success"):
            add_timeline_event(
                case_id,
                "AI_AUTO_SCHEDULED",
                (
                    f"SmartTrain automatically assigned "
                    f"{candidate['trainer']} for "
                    f"{candidate['date']} from "
                    f"{candidate['start']} to "
                    f"{candidate['end']}."
                ),
            )

            return {
                "success": True,
                "trainer": candidate["trainer"],
                "date": candidate["date"],
                "start": candidate["start"],
                "end": candidate["end"],
                "booking": booking_result,
            }

    reason = (
        "All matching slots became unavailable "
        "while SmartTrain attempted to book."
    )

    escalate_case(case_id, reason)

    return {
        "success": False,
        "reason": reason,
    }
