from app.crew import create_crew

def run_travel_planner(destination: str, days: int, interests: list[str] = None, trip_pace: str = None, transport_preference: str = None, budget: str = None, traveler_type: str = None, hotel_preference: str = None):

    crew = create_crew(destination, days, interests, trip_pace, transport_preference, budget, traveler_type, hotel_preference)

    result = crew.kickoff()

    return result