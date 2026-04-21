"""
Research Task
=============
Defines the task assigned to the Travel Research Agent within the CrewAI pipeline.

The research task instructs the agent to:
  - Use its tools to look up accurate information (not rely on LLM memory alone).
  - Produce a structured, detailed report as its output.
  - Pass the context forward to the Planner Agent.

Author: Nadeema Jayasinghe (Research Agent Module)
"""

import logging
from crewai import Task
from agents.research_agent import create_research_agent

logger = logging.getLogger(__name__)


def create_research_task(destination: str, llm) -> Task:
    """
    Build and return the research task for the given destination.

    This task is the first step in the sequential pipeline. Its output
    (a structured place & activity report) is automatically passed as
    context to subsequent tasks (Planner, Budget) by CrewAI.

    Args:
        destination (str): The travel destination (e.g., "Ella", "Kandy").
        llm:               A CrewAI-compatible LLM instance for the agent.

    Returns:
        Task: A configured CrewAI Task object ready for crew execution.
    """
    logger.info("[ResearchTask] Creating research task for destination: %s", destination)

    agent = create_research_agent(llm)

    task = Task(
        description=f"""
You are researching tourist places and activities for the destination: **{destination}**.

Follow these exact steps:
1. Call the 'Get Places and Activities' tool with destination="{destination}" to retrieve
   real data from the travel database.
2. If you are unsure of the spelling, call 'List Available Destinations' first.
3. Call 'Get Top Rated Places' to identify the must-see highlights (top 3).
4. Compile ALL findings into a well-structured research report. Include EVERY place
   returned by the tool — do not truncate or drop any attraction.

Your report MUST include:
- The top 3 highest-rated attractions clearly marked as highlights at the top.
- ALL remaining attractions listed after the highlights (nothing omitted).
- For every place include:
    * Place name and type (e.g., Cultural, Nature, Adventure)
    * Rating out of 5.0
    * Entry fee in USD
    * Best time to visit
    * Recommended duration (hours)
    * A brief description (2-3 sentences)
- A list of unique local activities (at least 3)
- A brief overall recommendation sentence for this destination.

Do NOT invent or hallucinate places. Only use data returned by your tools.
""",
        expected_output=f"""
A comprehensive, structured travel research report for {destination} containing:
1. The top 3 highest-rated tourist attractions highlighted first, with full details
   (name, type, rating, entry fee, best time, duration, description).
2. ALL remaining attractions listed after the top-3 section — every place from the
   database must appear; nothing should be omitted.
3. A bulleted list of at least 3 recommended local activities.
4. A brief overall destination recommendation (1–2 sentences).
""",
        agent=agent,
    )

    logger.info("[ResearchTask] Research task created for '%s'.", destination)
    return task