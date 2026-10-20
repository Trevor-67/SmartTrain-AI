
from datetime import date, timedelta

from flask import Flask, render_template, request, redirect, url_for

from database import get_db_connection

from services.ai_service import (
    parse_training_request,
    generate_clarification,
)

from services.scheduling import find_training_slots

from services.booking import create_booking

from services.timeline import (
    add_timeline_event,
    get_timeline,
)

from services.conversation import (
    add_message,
    get_conversations,
    update_case_from_message,
)

from services.human_review import (
    escalate_case as escalate_case_service,
    resolve_case,
)

from services.availability import get_calendar_for_date
from services.trainer_assignment import auto_assign_and_schedule


app = Flask(__name__)


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
@app.route("/dashboard")
def dashboard():
    connection = get_db_connection()

    cases = connection.execute("""
        SELECT *
        FROM training_cases
        ORDER BY id DESC
    """).fetchall()

    total_cases = connection.execute("""
        SELECT COUNT(*) AS count
        FROM training_cases
    """).fetchone()["count"]

    awaiting_customer = connection.execute("""
        SELECT COUNT(*) AS count
        FROM training_cases
        WHERE status = 'Awaiting Customer'
    """).fetchone()["count"]

    scheduled = connection.execute("""
        SELECT COUNT(*) AS count
        FROM training_cases
        WHERE status = 'Scheduled'
    """).fetchone()["count"]

    human_review = connection.execute("""
        SELECT COUNT(*) AS count
        FROM training_cases
        WHERE status = 'Human Review'
    """).fetchone()["count"]

    completed = connection.execute("""
        SELECT COUNT(*) AS count
        FROM training_cases
        WHERE status = 'Completed'
    """).fetchone()["count"]

    upcoming = connection.execute("""
        SELECT *
        FROM outlook_events
        WHERE status = 'Created'
        ORDER BY training_date ASC, start_time ASC
        LIMIT 5
    """).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        cases=cases,
        total_cases=total_cases,
        awaiting_customer=awaiting_customer,
        scheduled=scheduled,
        human_review=human_review,
        completed=completed,
        upcoming=upcoming,
    )


# =========================================================
# CREATE A TRAINING CASE
# =========================================================

@app.route("/case/new", methods=["GET", "POST"])
def create_case():
    if request.method == "POST":
        customer_name = request.form.get(
            "customer_name", ""
        ).strip()

        training_type = request.form.get(
            "training_type", ""
        ).strip()

        delivery_method = request.form.get(
            "delivery_method", ""
        ).strip()

        participants_text = request.form.get(
            "participants", ""
        ).strip()

        preferred_date = request.form.get(
            "preferred_date", ""
        ).strip()

        if not all([
            customer_name,
            training_type,
            delivery_method,
            participants_text,
            preferred_date,
        ]):
            return "Please complete every field.", 400

        try:
            participants = int(participants_text)
            requested_date = date.fromisoformat(preferred_date)

            if participants < 1:
                raise ValueError

            if requested_date < date.today():
                return "Choose today or a future date.", 400

        except ValueError:
            return "Enter a valid participant count and date.", 400

        connection = get_db_connection()

        cursor = connection.execute("""
            INSERT INTO training_cases (
                customer_name,
                training_type,
                delivery_method,
                participants,
                preferred_date,
                assigned_trainer,
                status
            )
            VALUES (?, ?, ?, ?, ?, NULL, ?)
        """, (
            customer_name,
            training_type,
            delivery_method,
            participants,
            preferred_date,
            "AI Processing",
        ))

        case_id = cursor.lastrowid
        connection.commit()
        connection.close()

        add_timeline_event(
            case_id,
            "CASE_CREATED",
            "Synthetic training case created in the SmartTrain prototype.",
        )

        result = auto_assign_and_schedule(case_id)

        if not result.get("success"):
            add_timeline_event(
                case_id,
                "HUMAN_REVIEW_REQUIRED",
                result.get("reason", "Automatic scheduling failed."),
            )

        return redirect(url_for("case_detail", case_id=case_id))

    return render_template(
        "create_case.html",
        today=date.today().isoformat(),
    )


# =========================================================
# TRAINER CALENDAR
# =========================================================

@app.route("/calendar")
def calendar():
    selected_date = request.args.get(
        "date",
        date.today().isoformat(),
    )

    try:
        date.fromisoformat(selected_date)
    except (ValueError, TypeError):
        selected_date = date.today().isoformat()

    trainers_calendar = get_calendar_for_date(selected_date)

    return render_template(
        "calendar.html",
        selected_date=selected_date,
        trainers_calendar=trainers_calendar,
    )


# =========================================================
# RESET DEMO DATA
# LOCAL PROTOTYPE ONLY
# =========================================================

@app.route("/demo/reset", methods=["POST"])
def reset_demo():
    connection = get_db_connection()

    tables = (
        "conversations",
        "case_timeline",
        "notifications",
        "outlook_events",
        "bookings",
        "training_cases",
    )

    for table in tables:
        connection.execute(f"DELETE FROM {table}")

    connection.commit()
    connection.close()

    return redirect(url_for("dashboard"))


# =========================================================
# LOAD SEVEN SYNTHETIC DEMO CASES
# =========================================================

@app.route("/demo/seed", methods=["POST"])
def seed_demo_cases():
    connection = get_db_connection()

    existing_count = connection.execute("""
        SELECT COUNT(*) AS total
        FROM training_cases
    """).fetchone()["total"]

    if existing_count:
        connection.close()

        return (
            "Reset the demo first before loading the seven sample cases.",
            400,
        )

    today = date.today()

    sample_cases = [
        ("Demo Coffee Shop", "Unity", "On-site", 5, 0),
        ("Demo Retail Store", "GAAP", "Virtual", 4, 0),
        ("Demo Service Centre", "POS", "Classroom", 8, 0),
        ("Demo Restaurant", "Unity", "Virtual", 6, 1),
        ("Demo Training Group", "GAAP", "On-site", 3, 1),
        ("Demo Payments Shop", "POS", "Virtual", 7, 2),
        ("Demo Specialist Request", "Other", "Classroom", 4, 0),
    ]

    created_ids = []

    for customer, training, delivery, participants, offset in sample_cases:
        requested_date = today + timedelta(days=offset)

        while requested_date.weekday() >= 5:
            requested_date += timedelta(days=1)

        cursor = connection.execute("""
            INSERT INTO training_cases (
                customer_name,
                training_type,
                delivery_method,
                participants,
                preferred_date,
                assigned_trainer,
                status
            )
            VALUES (?, ?, ?, ?, ?, NULL, ?)
        """, (
            customer,
            training,
            delivery,
            participants,
            requested_date.isoformat(),
            "AI Processing",
        ))

        created_ids.append(cursor.lastrowid)

    connection.commit()
    connection.close()

    for case_id in created_ids:
        add_timeline_event(
            case_id,
            "CASE_CREATED",
            "Synthetic demo case created.",
        )

        auto_assign_and_schedule(case_id)

    return redirect(url_for("dashboard"))


# =========================================================
# AI TEST PAGE
# =========================================================

@app.route("/ai-test", methods=["GET", "POST"])
def ai_test():
    result = None
    message = ""

    if request.method == "POST":
        message = request.form.get("message", "").strip()
        result = parse_training_request(message)

    return render_template(
        "ai_test.html",
        result=result,
        message=message,
    )


# =========================================================
# CASE DETAILS
# =========================================================

@app.route("/case/<int:case_id>")
def case_detail(case_id):
    connection = get_db_connection()

    case = connection.execute("""
        SELECT *
        FROM training_cases
        WHERE id = ?
    """, (case_id,)).fetchone()

    connection.close()

    if case is None:
        return "Case not found.", 404

    scheduling_result = None

    if (
        case["preferred_date"]
        and case["assigned_trainer"]
        and case["status"] != "Human Review"
    ):
        scheduling_result = find_training_slots(
            case["assigned_trainer"],
            case["preferred_date"],
        )

    conversations = get_conversations(case_id)
    timeline = get_timeline(case_id)

    return render_template(
        "case_detail.html",
        case=case,
        scheduling_result=scheduling_result,
        conversations=conversations,
        timeline=timeline,
    )


# =========================================================
# MANUAL BOOKING ENDPOINT
# RETAINED FOR EXISTING CASE DETAIL FUNCTIONALITY
# =========================================================

@app.route("/book/<int:case_id>", methods=["POST"])
def book_training(case_id):
    trainer_name = request.form.get("trainer_name", "")
    training_date = request.form.get("training_date", "")
    start_time = request.form.get("start_time", "")
    end_time = request.form.get("end_time", "")

    result = create_booking(
        case_id,
        trainer_name,
        training_date,
        start_time,
        end_time,
    )

    if result.get("success"):
        return redirect(
            url_for("booking_confirmation", case_id=case_id)
        )

    return result.get("message", "Booking failed."), 409


# =========================================================
# BOOKING CONFIRMATION
# =========================================================

@app.route("/booking-confirmation/<int:case_id>")
def booking_confirmation(case_id):
    connection = get_db_connection()

    case = connection.execute("""
        SELECT *
        FROM training_cases
        WHERE id = ?
    """, (case_id,)).fetchone()

    booking = connection.execute("""
        SELECT *
        FROM bookings
        WHERE case_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (case_id,)).fetchone()

    outlook_event = connection.execute("""
        SELECT *
        FROM outlook_events
        WHERE case_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (case_id,)).fetchone()

    notification = connection.execute("""
        SELECT *
        FROM notifications
        WHERE case_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (case_id,)).fetchone()

    connection.close()

    if case is None:
        return "Case not found.", 404

    return render_template(
        "booking_confirmation.html",
        case=case,
        booking=booking,
        outlook_event=outlook_event,
        notification=notification,
    )


# =========================================================
# CUSTOMER MESSAGE / CLARIFICATION
# =========================================================

@app.route("/case/<int:case_id>/message", methods=["POST"])
def case_message(case_id):
    message = request.form.get("message", "").strip()

    if not message:
        return redirect(url_for("case_detail", case_id=case_id))

    connection = get_db_connection()
    case_exists = connection.execute("""
        SELECT id
        FROM training_cases
        WHERE id = ?
    """, (case_id,)).fetchone()
    connection.close()

    if case_exists is None:
        return "Case not found.", 404

    add_message(case_id, "Customer", message)

    result = update_case_from_message(case_id, message)

    if not result.get("success"):
        return result.get("message", "Could not update case."), 400

    parsed = result.get("parsed", {})
    missing_fields = parsed.get(
        "missing_fields",
        result.get("missing_fields", []),
    )

    if missing_fields:
        clarification = generate_clarification({
            "missing_fields": missing_fields,
        })

        add_message(case_id, "SmartTrain AI", clarification)

        connection = get_db_connection()
        connection.execute("""
            UPDATE training_cases
            SET status = ?
            WHERE id = ?
        """, ("Awaiting Customer", case_id))
        connection.commit()
        connection.close()

        add_timeline_event(
            case_id,
            "INFORMATION_MISSING",
            "SmartTrain requested additional information.",
        )

        return redirect(url_for("case_detail", case_id=case_id))

    assignment = auto_assign_and_schedule(case_id)

    if not assignment.get("success"):
        reason = assignment.get(
            "reason",
            "Automatic scheduling could not be completed.",
        )

        add_message(
            case_id,
            "SmartTrain AI",
            "This request needs Human Review. Reason: " + reason,
        )

        return redirect(url_for("case_detail", case_id=case_id))

    add_message(
        case_id,
        "SmartTrain AI",
        (
            f"Training has been automatically scheduled with "
            f"{assignment['trainer']} on {assignment['date']} "
            f"from {assignment['start']} to {assignment['end']}."
        ),
    )

    return redirect(url_for("case_detail", case_id=case_id))


# =========================================================
# HUMAN REVIEW QUEUE
# =========================================================

@app.route("/human-review")
def human_review():
    connection = get_db_connection()

    cases = connection.execute("""
        SELECT *
        FROM training_cases
        WHERE status = 'Human Review'
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "human_review.html",
        cases=cases,
    )


# =========================================================
# MANUALLY ESCALATE A CASE
# =========================================================

@app.route("/case/<int:case_id>/escalate", methods=["POST"])
def escalate_case_route(case_id):
    reason = request.form.get(
        "reason",
        "Manual escalation requested.",
    ).strip()

    result = escalate_case_service(case_id, reason)

    if not result.get("success"):
        return result.get("message", "Could not escalate case."), 404

    return redirect(url_for("case_detail", case_id=case_id))


# =========================================================
# RESOLVE HUMAN REVIEW
# =========================================================

@app.route("/case/<int:case_id>/resolve-review", methods=["POST"])
def resolve_review(case_id):
    result = resolve_case(case_id)

    if not result.get("success"):
        return result.get("message", "Could not resolve case."), 404

    return redirect(url_for("case_detail", case_id=case_id))


# =========================================================
# CHECK TRAINER AVAILABILITY
# =========================================================

@app.route(
    "/case/<int:case_id>/check-availability",
    methods=["POST"],
)
def check_case_availability(case_id):
    connection = get_db_connection()

    case = connection.execute("""
        SELECT *
        FROM training_cases
        WHERE id = ?
    """, (case_id,)).fetchone()

    connection.close()

    if case is None:
        return "Case not found.", 404

    if not case["assigned_trainer"]:
        return "No trainer assigned to this case.", 400

    result = find_training_slots(
        case["assigned_trainer"],
        case["preferred_date"],
    )

    if not result["available"]:
        reason = (
            f"No availability found for {case['assigned_trainer']} "
            f"on {case['preferred_date']}."
        )

        escalate_case_service(case_id, reason)

        add_message(
            case_id,
            "SmartTrain AI",
            "No available slot was found. This case has been sent "
            "for Human Review.",
        )

        add_timeline_event(
            case_id,
            "NO_AVAILABILITY",
            reason,
        )

    return redirect(url_for("case_detail", case_id=case_id))


# =========================================================
# MARK TRAINING AS COMPLETED
# =========================================================

@app.route(
    "/case/<int:case_id>/complete-training",
    methods=["POST"],
)
def complete_training(case_id):
    connection = get_db_connection()

    case = connection.execute("""
        SELECT id
        FROM training_cases
        WHERE id = ?
    """, (case_id,)).fetchone()

    if case is None:
        connection.close()
        return "Case not found.", 404

    connection.execute("""
        UPDATE training_cases
        SET status = ?
        WHERE id = ?
    """, ("Completed", case_id))

    connection.commit()
    connection.close()

    add_message(
        case_id,
        "System",
        "Training session has been marked as completed.",
    )

    add_timeline_event(
        case_id,
        "TRAINING_COMPLETED",
        "Trainer marked the training session as completed.",
    )

    return redirect(url_for("case_detail", case_id=case_id))


# =========================================================
# CUSTOMER FEEDBACK
# =========================================================

@app.route("/case/<int:case_id>/feedback", methods=["POST"])
def submit_feedback(case_id):
    rating_text = request.form.get("rating")
    comment = request.form.get("comment", "").strip()

    try:
        rating = int(rating_text)
    except (TypeError, ValueError):
        return "Invalid rating.", 400

    if rating < 1 or rating > 5:
        return "Rating must be between 1 and 5.", 400

    connection = get_db_connection()

    case = connection.execute("""
        SELECT id
        FROM training_cases
        WHERE id = ?
    """, (case_id,)).fetchone()

    if case is None:
        connection.close()
        return "Case not found.", 404

    connection.execute("""
        INSERT INTO feedback (case_id, rating, comment)
        VALUES (?, ?, ?)
    """, (case_id, rating, comment))

    connection.commit()
    connection.close()

    add_timeline_event(
        case_id,
        "FEEDBACK_RECEIVED",
        f"Customer submitted a {rating}/5 training rating.",
    )

    return redirect(url_for("case_detail", case_id=case_id))


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
