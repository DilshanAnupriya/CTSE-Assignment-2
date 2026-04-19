from crewai import Agent

planner_agent = Agent(
    role="Travel Planner",
    goal="Create day-by-day travel itinerary",
    backstory="Expert trip planner who organizes schedules efficiently",
    verbose=True
)