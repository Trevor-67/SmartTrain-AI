from services.ai_service import parse_training_request


message = """
Hi, we need virtual Unity training for 6 employees next Wednesday.
"""


result = parse_training_request(message)


print("AI Extraction Result")
print("--------------------")

print("Training:", result["training_type"])
print("Delivery:", result["delivery_method"])
print("Participants:", result["participants"])
print("Preferred Date:", result["preferred_date"])

print()
print("Missing information:", result["missing_fields"])