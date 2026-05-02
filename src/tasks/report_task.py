"""
Report Task
===========
Defines the task assigned to the Report Agent within the CrewAI pipeline.

The report task instructs the agent to:
  - Read all the context from previous tasks (Research, Hotel, Planner, etc.).
  - Format it into a clean, professional Markdown report.
  - Call the tool to save the report to the filesystem.

Author: Hirun Athukorala (Report Agent Module)
"""

import logging
from crewai import Task
from agents.report_agent import create_report_agent

logger = logging.getLogger(__name__)


def create_report_task(destination: str, days: int, llm) -> Task:
    """
    Build and return the report generation task.

    Args:
        destination (str): Travel destination (e.g., "Ella", "Kandy").
        days (int): Number of days for the trip.
        llm: CrewAI-compatible LLM instance.

    Returns:
        Task: Configured CrewAI Task for creating the final report.
    """
    logger.info("[ReportTask] Creating report task for destination: %s", destination)

    agent = create_report_agent(llm)

    task = Task(
        description=f"""
You are the Executive Travel Report Editor finalizing the {days}-day itinerary for **{destination}**.

Your job is to:
1. Review all the information provided by the previous agents in the pipeline.
2. Compile this information into a single, beautifully formatted Markdown document.
3. Structure the document elegantly:
   - Add a catchy Title and a brief Introduction.
   - Include the "Overall Recommendation" and "Hotel Recommendations" in clear sections.
   - Present the detailed Day-by-Day itinerary cleanly.
4. Once you have generated the full markdown content, YOU MUST call the 'Save Report To File' tool.
   - Pass the entire markdown string as the `content` argument.
   - Pass `{destination}_travel_plan.md` as the `filename` argument.

STRICT RULES:
- Do not lose any details (prices, ratings, descriptions) from the previous agents' outputs.
- Ensure the formatting uses appropriate Markdown headers (`#`, `##`, `###`), bold text (`**`), and lists (`-`).
- You MUST save the file using the provided tool.
""",
        expected_output=f"""
The final, perfectly formatted Markdown travel report for {destination}, which has been successfully saved to '{destination}_travel_plan.md'.
""",
        agent=agent,
    )

    logger.info("[ReportTask] Report task created for '%s'.", destination)
    return task
