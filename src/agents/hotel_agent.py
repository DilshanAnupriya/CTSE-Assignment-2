"""
Hotel Agent
===========
Hotel Recommendation Agent for the Sri Lanka Travel Planner Multi-Agent System.

This agent is responsible for:
  1. Receiving a destination (Kandy, Ella, Galle, Colombo).
  2. Fetching hotel data from the shared travel dataset (travel_data.json).
  3. Ranking hotels based on rating (highest first).
  4. Returning structured hotel recommendations for downstream agents.

IMPORTANT:
- This agent MUST use tools (not LLM memory) to retrieve hotel data.
- It follows the same dataset used by the Research Agent for consistency.

Author: Project Team (Hotel Agent Module)
"""

import json
import os
import logging
from typing import Any

from crewai import Agent
from crewai.tools import tool

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# DATA LOADER (Safe + Robust Path Handling)
# ─────────────────────────────────────────────

def _load_travel_data() -> dict[str, Any]:
    """
    Load travel_data.json safely from different possible paths.
    This avoids issues when running from different directories.
    """

    candidates = [
        os.path.join(os.getcwd(), "data", "travel_data.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "travel_data.json"),
    ]

    for path in candidates:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            with open(abs_path, "r", encoding="utf-8") as f:
                return json.load(f)

    raise FileNotFoundError("travel_data.json not found in expected paths")


# ─────────────────────────────────────────────
# TOOL: Get Hotels by Destination
# ─────────────────────────────────────────────

@tool("Get Hotels by Destination")
def tool_get_hotels(destination: str) -> str:
    """
    Retrieve hotel recommendations for a given destination.

    Steps:
    1. Load travel dataset.
    2. Match destination (case-insensitive).
    3. Extract hotel list.
    4. Sort hotels by rating (descending).
    5. Format structured output.

    Args:
        destination (str): City name (Kandy, Ella, Galle, Colombo)

    Returns:
        str: Formatted hotel recommendation list.
    """

    logger.info("[HotelTool] Fetching hotels for destination: %s", destination)

    try:
        data = _load_travel_data()
    except Exception as e:
        return f"Error loading dataset: {str(e)}"

    # ── Case-insensitive destination matching ──
    matched_key = None
    for key in data:
        if key.lower() == destination.strip().lower():
            matched_key = key
            break

    if not matched_key:
        available = ", ".join(data.keys())
        return f"Destination '{destination}' not found. Available: {available}"

    hotels = data[matched_key]["hotels"]

    # ── Rank hotels by rating (best first) ──
    sorted_hotels = sorted(hotels, key=lambda x: x["rating"], reverse=True)

    # ── Format output ──
    result_lines = [
        f"🏨 Hotel Recommendations in {matched_key}",
        "-" * 40,
    ]

    for i, hotel in enumerate(sorted_hotels, 1):
        result_lines.append(
            f"{i}. {hotel['name']}\n"
            f"   • Type: {hotel['type']}\n"
            f"   • Rating: ⭐ {hotel['rating']}/5.0\n"
            f"   • Price per night: ${hotel['price_per_night_usd']}\n"
        )

    logger.info(
        "[HotelTool] Found %d hotels for %s",
        len(sorted_hotels),
        matched_key
    )

    return "\n".join(result_lines)


# ─────────────────────────────────────────────
# AGENT CREATION
# ─────────────────────────────────────────────

def create_hotel_agent(llm) -> Agent:
    """
    Create and return the Hotel Recommendation Agent.

    This agent:
    - Uses ONLY the hotel tool (no hallucination allowed)
    - Focuses on ranking and recommending hotels
    - Works as part of sequential CrewAI pipeline

    Args:
        llm: CrewAI-compatible LLM instance

    Returns:
        Agent: Configured Hotel Agent
    """

    logger.info("[HotelAgent] Creating Hotel Recommendation Agent...")

    agent = Agent(
        role="Hotel Recommendation Specialist",

        goal=(
            "Recommend the best hotels for travelers based on destination "
            "using ONLY verified data from the travel dataset. "
            "Rank hotels based on rating and provide structured output."
        ),

        backstory=(
            "You are a professional travel accommodation expert specializing in "
            "Sri Lankan hotels. You carefully analyze hotel ratings, prices, and types "
            "to recommend the most suitable stays for travelers. "
            "You NEVER hallucinate hotel names and always rely on tools."
        ),

        tools=[tool_get_hotels],

        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )

    logger.info("[HotelAgent] Hotel Agent created successfully.")

    return agent