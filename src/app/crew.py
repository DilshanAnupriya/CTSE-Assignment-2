"""
Crew Builder
============
Constructs the CrewAI Crew that orchestrates all agents sequentially.

Currently wires up the Research Task as the first pipeline stage.
Other group members' tasks (plan_task, budget_task, hotel_task, report_task)
will be added here as they are implemented.

Author: Project Team
"""

import logging
from crewai import Crew, Process, LLM
from tasks.research_task import create_research_task
from tasks.hotel_task import create_hotel_task 
from tasks.report_task import create_report_task

logger = logging.getLogger(__name__)


def create_crew(destination: str, days: int) -> Crew:
    """
    Build and return the travel planner Crew.

    Args:
        destination (str): Target travel destination.
        days        (int): Number of travel days.

    Returns:
        Crew: Configured CrewAI Crew ready for kickoff.
    """
    logger.info("[Crew] Building crew for destination='%s', days=%d", destination, days)

    # ── LLM (local Ollama — zero cost, no API key required) ─────────────────
    llm = LLM(
        model="ollama/qwen2.5",
        base_url="http://localhost:11434",
    )

    # ── Task pipeline ─────────────────────────────────────────────────────────
    # Stage 1: Research Agent (Nadeema) gathers places & activities
    research = create_research_task(destination, llm, days)
    # Stage 2: Hotel Agent (Dilshan) recommends hotels
    hotel = create_hotel_task(destination, llm)
    # Stage 3: Report Agent (Hirun) compiles and saves the final plan
    report = create_report_task(destination, days, llm)

    # TODO (other members): add plan_task, budget_task
    tasks = [
        research,    #step 1: gather places & activities  (Nadeema)
        hotel,       #step 2: recommend hotels  (Dilshan)
        report       #step 3: generate final report (Hirun)
    ]

    # ── Crew ──────────────────────────────────────────────────────────────────
    crew = Crew(
        tasks=tasks,
        process=Process.sequential,  # State flows left-to-right
        verbose=True,
    )

    logger.info("[Crew] Crew built with %d task(s).", len(tasks))
    return crew