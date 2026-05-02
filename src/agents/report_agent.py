"""
Report Agent
============
Report Generation Agent for the Sri Lanka Travel Planner Multi-Agent System.

This agent is responsible for:
  1. Receiving the raw context from the previous agents (Research, Hotel, Budget).
  2. Synthesizing everything into a beautifully formatted Markdown travel plan.
  3. Saving the final report to a file using the report_tool.

Author: Hirun Athukorala (Report Agent Module)
"""

import logging
from crewai import Agent
from crewai.tools import tool

from tools.report_tool import save_report_to_file

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  CrewAI-compatible tool wrappers
# ─────────────────────────────────────────────

@tool("Save Report To File")
def tool_save_report(content: str, filename: str) -> str:
    """
    Save the final generated travel report to a Markdown file.
    Always call this tool at the very end of your task to persist the itinerary.
    Provide the exact markdown text as 'content' and a filename like 'Destination_Plan.md' as 'filename'.
    """
    return save_report_to_file(content, filename)


# ─────────────────────────────────────────────
#  Agent factory
# ─────────────────────────────────────────────

def create_report_agent(llm) -> Agent:
    """
    Build and return the Travel Report Agent.

    Args:
        llm: CrewAI-compatible LLM instance.

    Returns:
        Agent: Configured CrewAI Agent for generating reports.
    """
    logger.info("[ReportAgent] Creating Travel Report Agent...")

    agent = Agent(
        role="Executive Travel Report Editor",
        goal=(
            "Synthesize the findings from all previous agents (places, activities, hotels, budget) "
            "into a cohesive, perfectly formatted Markdown travel itinerary, and save it to a file."
        ),
        backstory=(
            "You are an expert travel writer and editor who creates stunning, easy-to-read "
            "travel guides. You know how to structure day-by-day itineraries elegantly, "
            "highlighting the best hotels, attractions, and costs. "
            "You always ensure the final product is professional, free of errors, and saved correctly."
        ),
        tools=[tool_save_report],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    logger.info("[ReportAgent] Travel Report Agent created successfully.")
    return agent
