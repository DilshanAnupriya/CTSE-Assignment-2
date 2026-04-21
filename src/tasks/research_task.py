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


def create_research_task(destination: str, llm, days: int) -> Task:
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
You need to plan an itinerary for **{days} days**.

Follow these exact steps:
1. Call the 'Get Places and Activities' tool with destination="{destination}" to retrieve
   real data from the travel database.
2. If you are unsure of the spelling, call 'List Available Destinations' first.
3. Call 'Get Top Rated Places' to identify the must-see highlights (top 3).
4. Compile ALL findings into a well-structured research report. Include EVERY place
   returned by the tool.
5. Create a day-by-day itinerary (e.g., Day 1, Day 2, up to Day {days}) distributing the 
   retrieved places and activities logically across the days. Suggest which places to 
   visit on each day, ensuring the top-rated ones are prioritized.

Your report MUST include:
- A brief overall recommendation sentence for this destination at the top.
- A **Day-by-Day Itinerary** for exactly {days} days. For example:
    **Day 1**
    - Place 1 with full details
    - Place 2 with full details
    **Day 2**
    ...
- Ensure ALL retrieved attractions and recommended activities are distributed across the 
  {days} days. Do not omit any place from the tool's output.
- For every place include:
    * Place name and type (e.g., Cultural, Nature, Adventure)
    * Rating out of 5.0 (mention if it's a [TOP RATED] highlight)
    * Entry fee in USD
    * Best time to visit
    * Recommended duration (hours)
    * A brief description (2-3 sentences)
- Include the unique local activities within the days as well.

Do NOT invent or hallucinate places. Only use data returned by your tools.
""",
        expected_output=f"""
A comprehensive, structured travel research report for {destination} over {days} days containing:
1. A brief overall destination recommendation (1–2 sentences).
2. A day-by-day itinerary (Day 1 to Day {days}) distributing ALL retrieved attractions 
   and activities. Every place from the database must appear in the itinerary.
3. Full details for each place (name, type, rating, entry fee, best time, duration, description).
4. Identification of the top-rated highlights within the days they are allocated.
""",
        agent=agent,
    )

    logger.info("[ResearchTask] Research task created for '%s'.", destination)
    return task