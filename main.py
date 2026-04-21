import sys
import os

# Fix import path for src
sys.path.append(os.path.abspath("src"))

from services.planner_service import run_travel_planner


def main():
    print("=== Travel Planner MAS ===")

    destination = input("Enter destination (Kandy/Ella/Galle/Colombo): ")
    days = int(input("Enter number of days: "))

    result = run_travel_planner(destination, days)

    print("\n===== FINAL TRAVEL PLAN =====\n")
    print(result)


if __name__ == "__main__":
    main()