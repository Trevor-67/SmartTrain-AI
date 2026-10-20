def create_training_invitation(
    customer_name,
    trainer_name,
    training_type,
    training_date,
    start_time,
    end_time
):

    invitation = {

        "subject": f"{training_type} Training - {customer_name}",

        "customer": customer_name,

        "trainer": trainer_name,

        "date": training_date,

        "start_time": start_time,

        "end_time": end_time,

        "status": "Created"

    }

    return invitation