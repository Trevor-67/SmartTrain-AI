from database import get_db_connection


def create_notification(case_id, channel, message):

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO notifications
        (
            case_id,
            channel,
            message,
            status
        )
        VALUES (?, ?, ?, ?)
    """, (
        case_id,
        channel,
        message,
        "Pending"
    ))

    connection.commit()

    connection.close()


    return {
        "success": True,
        "channel": channel,
        "message": message
    }