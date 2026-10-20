from database import get_db_connection
from services.timeline import add_timeline_event


def escalate_case(case_id, reason):

    connection = get_db_connection()

    case = connection.execute("""
        SELECT *
        FROM training_cases
        WHERE id = ?
    """, (
        case_id,
    )).fetchone()

    if case is None:

        connection.close()

        return {
            "success": False,
            "message": "Training case not found."
        }


    connection.execute("""
        UPDATE training_cases

        SET
            status = ?,
            review_reason = ?

        WHERE id = ?
    """, (
        "Human Review",
        reason,
        case_id
    ))

    connection.commit()

    connection.close()


    add_timeline_event(
        case_id,
        "HUMAN_REVIEW",
        f"Case escalated to Human Review. Reason: {reason}"
    )


    return {
        "success": True,
        "message": "Case successfully sent to Human Review."
    }


def resolve_case(case_id):

    connection = get_db_connection()

    case = connection.execute("""
        SELECT *
        FROM training_cases
        WHERE id = ?
    """, (
        case_id,
    )).fetchone()

    if case is None:

        connection.close()

        return {
            "success": False,
            "message": "Training case not found."
        }


    connection.execute("""
        UPDATE training_cases

        SET
            status = ?,
            review_reason = NULL

        WHERE id = ?
    """, (
        "AI Processing",
        case_id
    ))

    connection.commit()

    connection.close()


    add_timeline_event(
        case_id,
        "HUMAN_REVIEW_RESOLVED",
        "Human Review completed. Case returned to AI Processing."
    )


    return {
        "success": True,
        "message": "Human Review resolved."
    }