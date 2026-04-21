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
    # Stage 1: Research Agent (your part) gathers places & activities
    research = create_research_task(destination, llm, days)

    # TODO (other members): add plan_task, budget_task, hotel_task, report_task
    tasks = [research]

    # ── Crew ──────────────────────────────────────────────────────────────────
    crew = Crew(
        tasks=tasks,
        process=Process.sequential,  # State flows left-to-right
        verbose=True,
    )

    logger.info("[Crew] Crew built with %d task(s).", len(tasks))
    return crew