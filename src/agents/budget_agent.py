from crewai import Agent

budget_agent = Agent(
    role="Budget Analyst",
    goal="Calculate travel cost",
    backstory="Expert in travel budgeting and cost optimization",
    verbose=True
)