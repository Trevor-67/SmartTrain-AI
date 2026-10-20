from database import get_db_connection


def add_timeline_event(case_id, event_type, message):

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO case_timeline
        (
            case_id,
            event_type,
            message
        )
        VALUES (?, ?, ?)
    """, (
        case_id,
        event_type,
        message
    ))

    connection.commit()

    connection.close()


def get_timeline(case_id):

    connection = get_db_connection()

    events = connection.execute("""
        SELECT *
        FROM case_timeline
        WHERE case_id = ?
        ORDER BY created_at DESC, id DESC
    """, (
        case_id,
    )).fetchall()

    connection.close()

    return events