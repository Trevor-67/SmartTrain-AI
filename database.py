import sqlite3


DATABASE = "smarttrain.db"


def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


def init_db():

    connection = get_db_connection()

    # -----------------------------
    # Training Cases
    # -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS training_cases (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_name TEXT NOT NULL,

            training_type TEXT NOT NULL,

            delivery_method TEXT NOT NULL,

            participants INTEGER,

            preferred_date TEXT,

            assigned_trainer TEXT,

            status TEXT NOT NULL DEFAULT 'New'

        )
    """)

    # -----------------------------
    # Bookings
    # -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS bookings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            case_id INTEGER NOT NULL,

            trainer_name TEXT NOT NULL,

            training_date TEXT NOT NULL,

            start_time TEXT NOT NULL,

            end_time TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'Confirmed'

        )
    """)

    # -----------------------------
    # Notifications
    # -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS notifications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            case_id INTEGER NOT NULL,

            channel TEXT NOT NULL,

            message TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'Pending'

        )
    """)

    # -----------------------------
    # Outlook Events
    # -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS outlook_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            case_id INTEGER NOT NULL,

            subject TEXT NOT NULL,

            customer_name TEXT NOT NULL,

            trainer_name TEXT NOT NULL,

            training_date TEXT NOT NULL,

            start_time TEXT NOT NULL,

            end_time TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'Created'

        )
    """)

    # -----------------------------
    # Case Timeline
    # -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS case_timeline (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            case_id INTEGER NOT NULL,

            event_type TEXT NOT NULL,

            message TEXT NOT NULL,

            created_at DATETIME DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # -----------------------------
    # Conversations
    # -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS conversations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            case_id INTEGER NOT NULL,

            sender TEXT NOT NULL,

            message TEXT NOT NULL,

            created_at DATETIME DEFAULT CURRENT_TIMESTAMP

        )
    """)


    connection.execute("""
        CREATE TABLE IF NOT EXISTS feedback (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            case_id INTEGER NOT NULL,

            rating INTEGER NOT NULL,

            comment TEXT,

            created_at DATETIME DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # -----------------------------
    # Add review_reason if missing
    # -----------------------------

    columns = connection.execute("""
        PRAGMA table_info(training_cases)
    """).fetchall()

    column_names = [
        column["name"]
        for column in columns
    ]

    if "review_reason" not in column_names:

        connection.execute("""
            ALTER TABLE training_cases
            ADD COLUMN review_reason TEXT
        """)

        # =========================
    # HUMAN REVIEW SUPPORT
    # =========================

    existing_columns = connection.execute("""
        PRAGMA table_info(training_cases)
    """).fetchall()

    column_names = [
        column["name"]
        for column in existing_columns
    ]

    if "review_reason" not in column_names:

        connection.execute("""
            ALTER TABLE training_cases
            ADD COLUMN review_reason TEXT
        """)

    connection.commit()

    connection.close()


if __name__ == "__main__":

    init_db()

    print("SmartTrain database ready.")