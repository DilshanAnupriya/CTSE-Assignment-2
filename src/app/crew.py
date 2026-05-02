"""
Crew Builder
============
Constructs the CrewAI Crew that orchestrates all agents sequentially.

Builds the sequential workflow across the implemented project tasks.

Author: Project Team
"""

import logging
from crewai import Crew, Process, LLM
from tasks.research_task import create_research_task
from tasks.budget_task import create_budget_task
from tasks.hotel_task import create_hotel_task 
from tasks.report_task import create_report_task

logger = logging.getLogger(__name__)


def create_crew(destination: str, days: int, interests: list[str] = None, trip_pace: str = None, transport_preference: str = None, budget: str = None, traveler_type: str = None, hotel_preference: str = None) -> Crew:
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
    research = create_research_task(destination, llm, days, interests, trip_pace, transport_preference)
    hotel = create_hotel_task(destination, llm, budget, traveler_type, hotel_preference)
    budget_estimate = create_budget_task(destination, days, llm, budget, transport_preference, hotel_preference)
    report = create_report_task(destination, days, llm)
    tasks = [
        research,    #step 1: gather places & activities  (Nadeema)
        hotel,       #step 2: recommend hotels  (Dilshan)
        budget_estimate,  #step 3: estimate travel budget  (Vidura)
        report       #step 4: generate final report (Hirun)
    ]

    # ── Crew ──────────────────────────────────────────────────────────────────
    crew = Crew(
        tasks=tasks,
        process=Process.sequential,  # State flows left-to-right
        verbose=True,
    )

    logger.info("[Crew] Crew built with %d task(s).", len(tasks))
    return crew
