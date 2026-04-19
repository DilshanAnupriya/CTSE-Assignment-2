from crewai import Task
from agents.planner_agent import planner_agent

def create_plan_task(destination: str, days: int):

    return Task(
        description=f"Create a {days}-day itinerary for {destination}",
        expected_output="A structured day-by-day travel plan",
        agent=planner_agent
    )