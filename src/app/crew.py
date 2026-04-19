from crewai import Crew, Process, LLM
from tasks.research_task import create_research_task

def create_crew(destination: str, days: int):

    llm = LLM(
        model="ollama/qwen2.5",
        base_url="http://localhost:11434"
    )

    tasks = [
        create_research_task(destination, llm)  # ✅ PASS LLM HERE
    ]

    crew = Crew(
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )

    return crew