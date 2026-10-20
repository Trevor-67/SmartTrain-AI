from services.scheduling import find_training_slots


result = find_training_slots(
    "Trainer A",
    "2026-09-30"
)


print("SmartTrain Scheduling Result")
print("----------------------------")

print("Trainer:", result["trainer"])
print("Date:", result["date"])

if result["available"]:

    print("Status: Available")
    print()
    print("Available training slots:")

    for slot in result["slots"]:
        print(
            slot["start"],
            "-",
            slot["end"]
        )

else:

    print("Status: No availability")