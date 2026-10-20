
from database import get_db_connection
from services.availability import get_available_slots
from services.outlook import create_training_invitation
from services.notifications import create_notification
from services.timeline import add_timeline_event


def create_booking(
    case_id,
    trainer_name,
    training_date,
    start_time,
    end_time,
):
    # Confirm that the selected slot is one of the mock calendar's
    # currently available options.
    available_slots = get_available_slots(
        trainer_name,
        training_date,
    )

    slot_is_available = any(
        slot["start"] == start_time
        and slot["end"] == end_time
        for slot in available_slots
    )

    if not slot_is_available:
        return {
            "success": False,
            "message": (
                "This slot is no longer available. "
                "Please select another option."
            ),
        }

    connection = get_db_connection()

    try:
        # Serialise concurrent booking attempts in SQLite.
        connection.execute("BEGIN IMMEDIATE")

        case = connection.execute(
            """
            SELECT *
            FROM training_cases
            WHERE id = ?
            """,
            (case_id,),
        ).fetchone()

        if case is None:
            connection.rollback()
            return {
                "success": False,
                "message": "Training case not found.",
            }

        if case["assigned_trainer"] != trainer_name:
            connection.rollback()
            return {
                "success": False,
                "message": (
                    "The selected trainer does not match "
                    "the trainer assigned to this case."
                ),
            }

        # Reject overlapping bookings, not only identical start times.
        conflict = connection.execute(
            """
            SELECT id
            FROM bookings
            WHERE trainer_name = ?
              AND training_date = ?
              AND status = 'Confirmed'
              AND start_time < ?
              AND end_time > ?
            LIMIT 1
            """,
            (
                trainer_name,
                training_date,
                end_time,
                start_time,
            ),
        ).fetchone()

        if conflict:
            connection.rollback()
            return {
                "success": False,
                "message": (
                    "This slot has just been booked. "
                    "Please select another option."
                ),
            }

        # Do not create a second confirmed booking for this case.
        existing_case_booking = connection.execute(
            """
            SELECT id
            FROM bookings
            WHERE case_id = ?
              AND status = 'Confirmed'
            LIMIT 1
            """,
            (case_id,),
        ).fetchone()

        if existing_case_booking:
            connection.rollback()
            return {
                "success": False,
                "message": (
                    "This case already has a confirmed booking."
                ),
            }

        invitation = create_training_invitation(
            case["customer_name"],
            trainer_name,
            case["training_type"],
            training_date,
            start_time,
            end_time,
        )

        connection.execute(
            """
            INSERT INTO bookings (
                case_id,
                trainer_name,
                training_date,
                start_time,
                end_time,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                trainer_name,
                training_date,
                start_time,
                end_time,
                "Confirmed",
            ),
        )

        connection.execute(
            """
            INSERT INTO outlook_events (
                case_id,
                subject,
                customer_name,
                trainer_name,
                training_date,
                start_time,
                end_time,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                invitation["subject"],
                case["customer_name"],
                trainer_name,
                training_date,
                start_time,
                end_time,
                "Created",
            ),
        )

        connection.execute(
            """
            UPDATE training_cases
            SET status = ?
            WHERE id = ?
            """,
            ("Scheduled", case_id),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    message = (
        f"Training confirmed for {case['customer_name']} "
        f"on {training_date}, from {start_time} to {end_time}."
    )

    create_notification(case_id, "Email", message)

    add_timeline_event(
        case_id,
        "BOOKING_CONFIRMED",
        f"Training booked with {trainer_name} on {training_date}, "
        f"{start_time}-{end_time}.",
    )

    add_timeline_event(
        case_id,
        "OUTLOOK_EVENT_CREATED",
        "A simulated Outlook training event was created.",
    )

    add_timeline_event(
        case_id,
        "SALESFORCE_UPDATED",
        "The local prototype case status was updated to Scheduled.",
    )

    add_timeline_event(
        case_id,
        "CUSTOMER_NOTIFIED",
        "A simulated email notification was recorded.",
    )

    return {
        "success": True,
        "message": "Training successfully scheduled.",
        "outlook_event": invitation,
    }
