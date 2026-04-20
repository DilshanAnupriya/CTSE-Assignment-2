"""
Travel Research Tool
====================
Custom tool for the Travel Research Agent in the Sri Lanka Travel Planner MAS.
Provides structured lookup of tourist places and activities for supported destinations.

Author: Dilshan Anupriya (Research Agent Module)
"""

import json
import os
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _load_travel_data() -> dict[str, Any]:
    """
    Load the travel data JSON from the data directory.

    Resolves the path relative to the project root regardless of the
    current working directory, making it robust to how the project is invoked.

    Returns:
        dict[str, Any]: Parsed travel data dictionary keyed by destination name.

    Raises:
        FileNotFoundError: If travel_data.json cannot be located.
        json.JSONDecodeError: If the JSON file is malformed.
    """
    # Support running from project root OR from src/
    candidates = [
        os.path.join(os.getcwd(), "data", "travel_data.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "travel_data.json"),
    ]
    for path in candidates:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            with open(abs_path, "r", encoding="utf-8") as f:
                return json.load(f)

    raise FileNotFoundError(
        "travel_data.json not found. Searched: " + ", ".join(os.path.abspath(p) for p in candidates)
    )


def get_places_and_activities(destination: str) -> dict[str, Any]:
    """
    Retrieve tourist attractions and activities for a given destination.

    This tool reads from a local curated travel database (travel_data.json)
    and returns a structured dictionary containing:
      - A list of top tourist places with name, type, description, rating,
        entry fee, best visiting time, and recommended duration.
      - A list of recommended local activities (unique experiences).

    This tool does NOT return hotel or budget data — use the hotel_tool
    for accommodation lookups.

    Args:
        destination (str): The destination city name (e.g., "Kandy", "Ella",
                           "Galle", "Colombo"). Case-insensitive matching is
                           applied automatically.

    Returns:
        dict[str, Any]: A dictionary with two keys:
            - "places"     (list[dict]): Top tourist attractions.
            - "activities" (list[str]):  Recommended activities.
            - "destination" (str):       Normalized destination name.
            - "error"      (str | None): Error message if destination not found.

    Example:
        >>> result = get_places_and_activities("Ella")
        >>> result["places"][0]["name"]
        'Nine Arch Bridge (Demodara Bridge)'
        >>> "Hiking" in result["places"][1]["type"]
        True
    """
    logger.info("[TravelTool] Looking up places for destination: '%s'", destination)

    try:
        data = _load_travel_data()
    except FileNotFoundError as e:
        logger.error("[TravelTool] Data file error: %s", str(e))
        return {
            "destination": destination,
            "places": [],
            "activities": [],
            "error": f"Data source unavailable: {str(e)}",
        }
    except json.JSONDecodeError as e:
        logger.error("[TravelTool] JSON parse error: %s", str(e))
        return {
            "destination": destination,
            "places": [],
            "activities": [],
            "error": f"Invalid data format: {str(e)}",
        }

    # Case-insensitive key lookup
    matched_key: str | None = None
    for key in data:
        if key.lower() == destination.strip().lower():
            matched_key = key
            break

    if matched_key is None:
        available = ", ".join(data.keys())
        logger.warning("[TravelTool] Destination '%s' not found. Available: %s", destination, available)
        return {
            "destination": destination,
            "places": [],
            "activities": [],
            "error": (
                f"Destination '{destination}' not found in travel database. "
                f"Available destinations: {available}"
            ),
        }

    destination_data = data[matched_key]
    places: list[dict[str, Any]] = destination_data.get("places", [])
    activities: list[str] = destination_data.get("activities", [])

    logger.info(
        "[TravelTool] Found %d places and %d activities for '%s'",
        len(places),
        len(activities),
        matched_key,
    )

    return {
        "destination": matched_key,
        "places": places,
        "activities": activities,
        "error": None,
    }


def get_top_rated_places(destination: str, top_n: int = 3) -> list[dict[str, Any]]:
    """
    Return the top-N highest-rated tourist places for a destination.

    Internally calls get_places_and_activities() and sorts by the 'rating'
    field in descending order.

    Args:
        destination (str): The destination city name (e.g., "Kandy", "Ella").
        top_n      (int):  Number of top places to return. Defaults to 3.
                           Must be a positive integer.

    Returns:
        list[dict[str, Any]]: Sorted list of place dictionaries, limited to top_n.
                              Returns an empty list if destination is not found.

    Example:
        >>> top = get_top_rated_places("Galle", top_n=2)
        >>> top[0]["rating"] >= top[1]["rating"]
        True
    """
    if top_n <= 0:
        logger.warning("[TravelTool] top_n must be positive, got %d. Defaulting to 3.", top_n)
        top_n = 3

    result = get_places_and_activities(destination)

    if result.get("error"):
        logger.warning("[TravelTool] Cannot get top-rated places: %s", result["error"])
        return []

    places = result["places"]
    sorted_places = sorted(places, key=lambda p: p.get("rating", 0), reverse=True)

    logger.info("[TravelTool] Returning top %d places for '%s'", top_n, destination)
    return sorted_places[:top_n]


def list_available_destinations() -> list[str]:
    """
    Return all supported destination names from the travel database.

    Useful for validation and displaying options to the user before lookup.

    Returns:
        list[str]: Alphabetically sorted list of destination names.

    Example:
        >>> destinations = list_available_destinations()
        >>> "Kandy" in destinations
        True
    """
    try:
        data = _load_travel_data()
        destinations = sorted(data.keys())
        logger.info("[TravelTool] Available destinations: %s", destinations)
        return destinations
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("[TravelTool] Could not load destinations: %s", str(e))
        return []


def format_places_summary(destination: str) -> str:
    """
    Generate a human-readable text summary of places and activities.

    This formats the raw data into a clean markdown-style report string
    that the LLM agent can directly use in its output or pass to the next agent.

    Args:
        destination (str): The destination city name.

    Returns:
        str: A formatted multi-line string summarising the places and activities.
             Returns an error message string if the destination is not found.

    Example:
        >>> summary = format_places_summary("Ella")
        >>> "Nine Arch Bridge" in summary
        True
    """
    result = get_places_and_activities(destination)

    if result.get("error"):
        return f"Error: {result['error']}"

    dest = result["destination"]
    places = result["places"]
    activities = result["activities"]

    lines: list[str] = [
        f"# Travel Research Report: {dest}",
        f"Total attractions found: {len(places)}",
        "",
        "## Top Tourist Places",
    ]

    for i, place in enumerate(places, start=1):
        lines.append(f"\n### {i}. {place['name']}")
        lines.append(f"- **Type:** {place.get('type', 'N/A')}")
        lines.append(f"- **Rating:** {place.get('rating', 'N/A')} / 5.0")
        lines.append(f"- **Entry Fee:** ${place.get('entry_fee_usd', 0)} USD")
        lines.append(f"- **Best Time to Visit:** {place.get('best_time', 'N/A')}")
        lines.append(f"- **Recommended Duration:** {place.get('duration_hours', 'N/A')} hours")
        lines.append(f"- **Description:** {place.get('description', '')}")

    lines.append("\n## Recommended Activities")
    for activity in activities:
        lines.append(f"- {activity}")

    summary = "\n".join(lines)
    logger.info("[TravelTool] Generated summary for '%s' (%d chars)", dest, len(summary))
    return summary