from app.services.delay_model import calculate_delay


print("LOW:", calculate_delay("LOW"))

print("MEDIUM:", calculate_delay("MEDIUM"))

print("HIGH:", calculate_delay("HIGH"))

print(
    "HIGH + missed connection:",
    calculate_delay("HIGH", True)
)