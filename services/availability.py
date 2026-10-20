
from datetime import date

from database import get_db_connection


TRAINERS = [
    "Trainer A",
    "Trainer B",
    "Trainer C",
    "Trainer D",
    "Trainer E",
]


TRAINER_SKILLS = {
    "Trainer A": {"Unity", "POS"},
    "Trainer B": {"GAAP", "POS"},
    "Trainer C": {"Unity", "GAAP"},
    "Trainer D": {"Unity", "GAAP", "POS"},
    "Trainer E": {"GAAP", "POS"},
}


DAILY_SLOTS = [
    ("09:00", "10:00"),
    ("10:00", "11:00"),
    ("11:00", "12:00"),
    ("13:00", "14:00"),
    ("14:00", "15:00"),
    ("15:00", "16:00"),
]


# Synthetic busy periods for the prototype.
# These are not live Outlook calendar events.
BUSY_PERIODS = {
    "Trainer A": {("10:00", "11:00")},
    "Trainer B": {("09:00", "10:00")},
    "Trainer C": {("13:00", "14:00")},
    "Trainer D": {("11:00", "12:00")},
    "Trainer E": {("14:00", "15:00")},
}


def get_available_slots(trainer_name, training_date):
    if trainer_name not in TRAINERS:
        return []

    try:
        requested_date = date.fromisoformat(training_date)
    except (ValueError, TypeError):
        return []

    # No training sessions on weekends.
    if requested_date.weekday() >= 5:
        return []

    connection = get_db_connection()

    booked = connection.execute("""
        SELECT start_time, end_time
        FROM bookings
        WHERE trainer_name = ?
          AND training_date = ?
          AND status = 'Confirmed'
    """, (trainer_name, training_date)).fetchall()

    connection.close()

    occupied = {
        (row["start_time"], row["end_time"])
        for row in booked
    }

    unavailable = occupied | BUSY_PERIODS.get(
        trainer_name,
        set(),
    )

    return [
        {"start": start, "end": end}
        for start, end in DAILY_SLOTS
        if (start, end) not in unavailable
    ]


def get_calendar_for_date(training_date):
    try:
        date.fromisoformat(training_date)
    except (ValueError, TypeError):
        training_date = date.today().isoformat()

    connection = get_db_connection()

    events = connection.execute("""
        SELECT
            trainer_name,
            subject,
            customer_name,
            training_date,
            start_time,
            end_time,
            status
        FROM outlook_events
        WHERE training_date = ?
          AND status = 'Created'
        ORDER BY start_time ASC
    """, (training_date,)).fetchall()

    connection.close()

    calendar_data = []

    for trainer in TRAINERS:
        trainer_events = [
            dict(event)
            for event in events
            if event["trainer_name"] == trainer
        ]

        calendar_data.append({
            "name": trainer,
            "skills": sorted(TRAINER_SKILLS[trainer]),
            "available_slots": get_available_slots(
                trainer,
                training_date,
            ),
            "events": trainer_events,
        })

    return calendar_data
