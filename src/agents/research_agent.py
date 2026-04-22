"""
Research Agent
==============
Travel Research Agent for the Sri Lanka Travel Planner Multi-Agent System.

This agent is responsible for:
  1. Looking up tourist attractions and activities for the requested destination.
  2. Ranking and summarising the best places to visit.
  3. Passing the structured research findings downstream to the Planner Agent.

The agent uses the travel_tool to query a local curated travel database
instead of relying solely on the LLM's internal knowledge, ensuring accurate
and up-to-date information.

Author: Nadeema Jayasinghe (Research Agent Module)
"""

import logging
from crewai import Agent
from crewai.tools import tool
from tools.travel_tool import (
    get_places_and_activities,
    get_top_rated_places,
    format_places_summary,
    list_available_destinations,
)

from app.logger import get_logger

logger = get_logger("ResearchAgent")


# ─────────────────────────────────────────────
#  CrewAI-compatible tool wrappers
#  (@tool decorator exposes plain functions to CrewAI agents)
# ─────────────────────────────────────────────

@tool("Get Places and Activities")
def tool_get_places_and_activities(destination: str) -> str:
    """
    Retrieve all tourist places and activities for the given destination.
    Returns a structured summary of attractions, types, ratings, entry fees,
    best visiting times, and recommended local activities.
    Input: destination name (e.g., 'Kandy', 'Ella', 'Galle').
    """
    logger.info("[ResearchAgent-Tool] get_places_and_activities called for: %s", destination)
    result = get_places_and_activities(destination)
    if result.get("error"):
        return f"Error retrieving data: {result['error']}"
    return format_places_summary(destination)


@tool("Get Top Rated Places")
def tool_get_top_rated_places(destination: str) -> str:
    """
    Return only the top 3 highest-rated tourist places for the destination.
    Useful for creating a concise highlight list. Input: destination name.
    """
    logger.info("[ResearchAgent-Tool] get_top_rated_places called for: %s", destination)
    places = get_top_rated_places(destination, top_n=3)
    if not places:
        return f"No top-rated places found for '{destination}'."
    lines = [f"Top {len(places)} Rated Places in {destination}:"]
    for i, p in enumerate(places, 1):
        lines.append(
            f"{i}. {p['name']} (Rating: {p['rating']}/5.0) — {p.get('type', '')}"
        )
    return "\n".join(lines)


@tool("List Available Destinations")
def tool_list_available_destinations(_: str = "") -> str:
    """
    List all supported destination names in the travel database.
    Use this when the user's destination spelling is uncertain.
    """
    logger.info("[ResearchAgent-Tool] list_available_destinations called.")
    destinations = list_available_destinations()
    if not destinations:
        return "Could not retrieve destination list."
    return "Available destinations: " + ", ".join(destinations)


# ─────────────────────────────────────────────
#  Agent factory
# ─────────────────────────────────────────────

def create_research_agent(llm) -> Agent:
    """
    Build and return the Travel Research Agent.

    The agent is given three custom tools so it can look up accurate,
    structured travel data without hallucinating from its LLM weights.

    Args:
        llm: A CrewAI-compatible LLM instance (e.g., Ollama-backed LLM).

    Returns:
        Agent: Configured CrewAI Agent ready to be assigned a research task.
    """
    logger.info("[ResearchAgent] Creating Travel Research Agent...")

    agent = Agent(
        role="Senior Travel Research Specialist",
        goal=(
            "Research and compile a comprehensive list of tourist attractions, "
            "must-see places, and unique local activities for the requested destination. "
            "Prioritise accuracy using the provided tools over general LLM knowledge. "
            "Always use the 'Get Places and Activities' tool first to retrieve real data."
        ),
        backstory=(
            "You are a highly experienced travel researcher who has personally visited "
            "every major destination in Sri Lanka. You have an encyclopaedic knowledge "
            "of attractions, hidden gems, and authentic local experiences. "
            "You never make up places — you always verify information using your research tools. "
            "Your research reports serve as the foundation for the entire travel planning team, "
            "so accuracy and depth are your top priorities."
        ),
        tools=[
            tool_get_places_and_activities,
            tool_get_top_rated_places,
            tool_list_available_destinations,
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,  # Research agent focuses solely on its own task
        max_iter=5,              # Prevent infinite loops
    )

    logger.info("[ResearchAgent] Travel Research Agent created successfully.")
    return agent