from crewai import Agent

def create_research_agent(llm):
    return Agent(
        role="Travel Research Agent",
        goal="Find best tourist places",
        backstory="Expert in travel planning",
        llm=llm   # ✅ THIS IS THE KEY FIX
    )