
from database import get_db_connection
from services.ai_service import (
    parse_training_request,
    get_missing_fields,
)
from services.timeline import add_timeline_event


def add_message(case_id, sender, message):
    connection = get_db_connection()
    connection.execute(
        """
        INSERT INTO conversations (case_id, sender, message)
        VALUES (?, ?, ?)
        """,
        (case_id, sender, message),
    )
    connection.commit()
    connection.close()


def get_conversations(case_id):
    connection = get_db_connection()
    messages = connection.execute(
        """
        SELECT *
        FROM conversations
        WHERE case_id = ?
        ORDER BY created_at ASC, id ASC
        """,
        (case_id,),
    ).fetchall()
    connection.close()
    return messages


def update_case_from_message(case_id, message):
    parsed = parse_training_request(message)

    connection = get_db_connection()
    case = connection.execute(
        "SELECT * FROM training_cases WHERE id = ?",
        (case_id,),
    ).fetchone()

    if case is None:
        connection.close()
        return {"success": False, "message": "Case not found."}

    # Keep existing information unless the customer supplied a new value.
    training_type = parsed["training_type"] or case["training_type"]
    delivery_method = parsed["delivery_method"] or case["delivery_method"]
    participants = (
        parsed["participants"]
        if parsed["participants"] is not None
        else case["participants"]
    )
    preferred_date = parsed["preferred_date"] or case["preferred_date"]

    merged = {
        "training_type": training_type,
        "delivery_method": delivery_method,
        "participants": participants,
        "preferred_date": preferred_date,
    }

    missing_fields = get_missing_fields(merged)

    if missing_fields:
        status = "Awaiting Customer"
    else:
        status = "Complete"

    connection.execute(
        """
        UPDATE training_cases
        SET training_type = ?,
            delivery_method = ?,
            participants = ?,
            preferred_date = ?,
            status = ?
        WHERE id = ?
        """,
        (
            training_type,
            delivery_method,
            participants,
            preferred_date,
            status,
            case_id,
        ),
    )

    connection.commit()
    connection.close()

    add_timeline_event(
        case_id,
        "CUSTOMER_DETAILS_UPDATED",
        "SmartTrain processed a customer message and updated the case details.",
    )

    return {
        "success": True,
        "parsed": {
            **merged,
            "missing_fields": missing_fields,
        },
    }
