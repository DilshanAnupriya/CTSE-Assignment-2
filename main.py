import sys
import os

os.environ["CREWAI_TRACING_ENABLED"] = "true"

# Fix import path for src
sys.path.append(os.path.abspath("src"))

from services.planner_service import run_travel_planner


def main():
    print("=== Travel Planner MAS ===")

    # Required inputs
    destination = ""
    while not destination:
        destination = input("Enter destination (Kandy/Ella/Galle/Colombo) [Required]: ").strip()
        
    days_str = ""
    while not days_str.isdigit():
        days_str = input("Enter number of days [Required]: ").strip()
    days = int(days_str)

    # Optional inputs
    print("\n--- Optional Preferences ---")
    interests_input = input("Enter interests (comma separated, e.g., Adventure, Nature, Cultural, Relaxation, Food, Shopping, Mixed) [Optional]: ").strip()
    interests = [i.strip() for i in interests_input.split(",")] if interests_input else None
    
    trip_pace = input("Enter trip pace (e.g., Relaxed, Moderate, Packed Schedule) [Optional]: ").strip() or None
    transport_preference = input("Enter transport preference (e.g., Walking-friendly, Public Transport, Taxi/Tuk-Tuk, Private Vehicle) [Optional]: ").strip() or None

    result = run_travel_planner(destination, days, interests, trip_pace, transport_preference)

    print("\n===== FINAL TRAVEL PLAN =====\n")
    print(result)


if __name__ == "__main__":
    main()