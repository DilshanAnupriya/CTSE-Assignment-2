from crewai import Task
from agents.research_agent import create_research_agent

def create_research_task(destination, llm):
    agent = create_research_agent(llm)

    return Task(
    description=f"""
    Find best tourist places in {destination}.
    Select top attractions and explain them.
    """,
    expected_output="A list of top tourist attractions with explanations.",
    agent=agent
)