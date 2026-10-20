from database import get_db_connection


def update_case_status(case_id, status):

    connection = get_db_connection()

    connection.execute("""
        UPDATE training_cases
        SET status = ?
        WHERE id = ?
    """, (
        status,
        case_id
    ))

    connection.commit()

    connection.close()


    return {

        "success": True,

        "case_id": case_id,

        "status": status

    }