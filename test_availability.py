from services.availability import get_available_slots


trainer = "Trainer A"
date = "2026-09-30"

slots = get_available_slots(trainer, date)

print("Available slots:")
print("----------------")

for slot in slots:
    print(slot["start"], "-", slot["end"])