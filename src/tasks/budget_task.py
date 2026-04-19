from crewai import Task
from agents.budget_agent import budget_agent

def create_budget_task(destination: str, days: int):

    return Task(
        description=f"Calculate budget for {destination} trip for {days} days",
        expected_output="Total estimated travel cost",
        agent=budget_agent
    )