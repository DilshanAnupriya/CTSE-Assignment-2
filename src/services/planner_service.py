from app.crew import create_crew

def run_travel_planner(destination: str, days: int):

    crew = create_crew(destination, days)

    result = crew.kickoff()

    return result