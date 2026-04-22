"""
Hotel Tool
====================
Custom tool for the Hotel Agent in the Sri Lanka Travel Planner MAS.
Provides structured lookup of hotels for supported destinations.

Author: Dilshan Anupriya (Hotel Agent Module)
"""

import json
import os
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _load_travel_data() -> dict[str, Any]:
    path = os.path.join(os.getcwd(), "data", "travel_data.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_hotels(destination: str) -> dict[str, Any]:
    """
    Retrieve hotel information for a destination.
    """
    logger.info("[HotelTool] Fetching hotels for: %s", destination)

    data = _load_travel_data()

    matched_key = None
    for key in data:
        if key.lower() == destination.lower():
            matched_key = key
            break

    if not matched_key:
        return {
            "destination": destination,
            "hotels": [],
            "error": "Destination not found"
        }

    return {
        "destination": matched_key,
        "hotels": data[matched_key].get("hotels", []),
        "error": None
    }


def format_hotels(destination: str) -> str:
    """
    Format hotel list nicely for LLM output.
    """
    result = get_hotels(destination)

    if result["error"]:
        return f"Error: {result['error']}"

    hotels = result["hotels"]

    lines = [f"# Hotel Options in {destination}\n"]

    for i, h in enumerate(hotels, 1):
        lines.append(f"### {i}. {h['name']}")
        lines.append(f"- Type: {h.get('type')}")
        lines.append(f"- Rating: {h.get('rating')}/5.0")
        lines.append(f"- Price: ${h.get('price_per_night_usd')} per night\n")

    return "\n".join(lines)