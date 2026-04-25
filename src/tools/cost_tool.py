"""
Budget / Cost Tool
==================
Custom budgeting tool for the Sri Lanka Travel Planner MAS.
Calculates trip cost estimates using the shared local travel dataset plus a
small set of transparent budgeting assumptions for meals and local transport.

Author: Vidura Hewaduwa (Budget Agent Module)
"""

import json
import logging
import os
from statistics import mean
from typing import Any

logger = logging.getLogger(__name__)


MEAL_COSTS_PER_DAY_USD = {
    "budget": 18.0,
    "standard": 30.0,
    "premium": 45.0,
}

LOCAL_TRANSPORT_PER_DAY_USD = {
    "Kandy": 8.0,
    "Ella": 10.0,
    "Galle": 9.0,
    "Colombo": 12.0,
}

CONTINGENCY_RATE = 0.10


def _load_travel_data() -> dict[str, Any]:
    """
    Load the shared travel dataset safely from the project.
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


def _match_destination(data: dict[str, Any], destination: str) -> str | None:
    for key in data:
        if key.lower() == destination.strip().lower():
            return key
    return None


def _sum_entry_fees(items: list[dict[str, Any]]) -> float:
    return float(sum(item.get("entry_fee_usd", 0) for item in items))


def _select_hotel_rate(hotels: list[dict[str, Any]], tier: str) -> float:
    if not hotels:
        return 0.0

    prices = sorted(float(hotel.get("price_per_night_usd", 0)) for hotel in hotels)
    tier_key = tier.strip().lower()

    if tier_key == "budget":
        return prices[0]
    if tier_key == "premium":
        return prices[-1]
    return round(mean(prices), 2)


def get_budget_breakdown(
    destination: str,
    days: int,
    tier: str = "standard",
) -> dict[str, Any]:
    """
    Calculate a single-traveler budget estimate for the requested destination.

    The budget covers only the Budget Agent's scope:
    - accommodation
    - meals
    - local transport
    - sightseeing / activity entry fees
    - contingency buffer

    It deliberately does NOT create itineraries, recommend hotels, or generate
    the final report because those belong to other agents.
    """
    logger.info(
        "[CostTool] Calculating budget for destination='%s', days=%s, tier='%s'",
        destination,
        days,
        tier,
    )

    if days <= 0:
        return {
            "destination": destination,
            "days": days,
            "tier": tier,
            "error": "Days must be a positive integer.",
        }

    if tier.strip().lower() not in MEAL_COSTS_PER_DAY_USD:
        return {
            "destination": destination,
            "days": days,
            "tier": tier,
            "error": "Tier must be one of: budget, standard, premium.",
        }

    try:
        data = _load_travel_data()
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return {
            "destination": destination,
            "days": days,
            "tier": tier,
            "error": f"Could not load travel dataset: {exc}",
        }

    matched_key = _match_destination(data, destination)
    if not matched_key:
        return {
            "destination": destination,
            "days": days,
            "tier": tier,
            "error": (
                f"Destination '{destination}' not found. "
                f"Available: {', '.join(sorted(data.keys()))}"
            ),
        }

    destination_data = data[matched_key]
    places = destination_data.get("places", [])
    activities = destination_data.get("activities", [])
    hotels = destination_data.get("hotels", [])

    hotel_rate = _select_hotel_rate(hotels, tier)
    accommodation_cost = round(hotel_rate * days, 2)
    meal_cost = round(MEAL_COSTS_PER_DAY_USD[tier.strip().lower()] * days, 2)
    local_transport_cost = round(
        LOCAL_TRANSPORT_PER_DAY_USD.get(matched_key, 10.0) * days,
        2,
    )
    attraction_cost = round(
        _sum_entry_fees(places) + _sum_entry_fees(activities),
        2,
    )

    subtotal = round(
        accommodation_cost + meal_cost + local_transport_cost + attraction_cost,
        2,
    )
    contingency_cost = round(subtotal * CONTINGENCY_RATE, 2)
    grand_total = round(subtotal + contingency_cost, 2)

    return {
        "destination": matched_key,
        "days": days,
        "tier": tier.strip().lower(),
        "hotel_price_per_night_usd": hotel_rate,
        "accommodation_cost_usd": accommodation_cost,
        "meal_cost_usd": meal_cost,
        "local_transport_cost_usd": local_transport_cost,
        "attraction_fees_usd": attraction_cost,
        "contingency_cost_usd": contingency_cost,
        "total_cost_usd": grand_total,
        "hotel_count_considered": len(hotels),
        "place_count_considered": len(places),
        "activity_count_considered": len(activities),
        "assumptions": {
            "traveler_count": 1,
            "budget_scope": (
                "Includes accommodation, meals, local transport, and all listed "
                "place/activity entry fees for the destination."
            ),
            "meal_cost_per_day_usd": MEAL_COSTS_PER_DAY_USD[tier.strip().lower()],
            "local_transport_per_day_usd": LOCAL_TRANSPORT_PER_DAY_USD.get(matched_key, 10.0),
            "contingency_rate": CONTINGENCY_RATE,
            "hotel_pricing_rule": {
                "budget": "Cheapest hotel in the dataset",
                "standard": "Average nightly rate across available hotels",
                "premium": "Most expensive hotel in the dataset",
            }[tier.strip().lower()],
        },
        "error": None,
    }


def compare_budget_tiers(destination: str, days: int) -> dict[str, Any]:
    """
    Compare budget, standard, and premium trip costs for a destination.
    """
    logger.info("[CostTool] Comparing budget tiers for '%s' over %d day(s)", destination, days)

    comparisons = {
        tier: get_budget_breakdown(destination, days, tier)
        for tier in ("budget", "standard", "premium")
    }

    errors = [value["error"] for value in comparisons.values() if value.get("error")]
    if errors:
        return {
            "destination": destination,
            "days": days,
            "tiers": comparisons,
            "error": errors[0],
        }

    return {
        "destination": comparisons["standard"]["destination"],
        "days": days,
        "tiers": comparisons,
        "error": None,
    }


def format_budget_summary(destination: str, days: int) -> str:
    """
    Produce a readable markdown summary for the Budget Agent.
    """
    comparison = compare_budget_tiers(destination, days)
    if comparison.get("error"):
        return f"Error: {comparison['error']}"

    dest = comparison["destination"]
    lines = [
        f"# Budget Estimate for {dest}",
        f"Trip length: {days} day(s)",
        "Traveller profile: single traveller",
        "",
    ]

    for tier in ("budget", "standard", "premium"):
        item = comparison["tiers"][tier]
        lines.extend(
            [
                f"## {tier.title()} Option",
                f"- Hotel price per night: ${item['hotel_price_per_night_usd']:.2f}",
                f"- Accommodation: ${item['accommodation_cost_usd']:.2f}",
                f"- Meals: ${item['meal_cost_usd']:.2f}",
                f"- Local transport: ${item['local_transport_cost_usd']:.2f}",
                f"- Entry fees: ${item['attraction_fees_usd']:.2f}",
                f"- Contingency (10%): ${item['contingency_cost_usd']:.2f}",
                f"- Total estimate: ${item['total_cost_usd']:.2f}",
                "",
            ]
        )

    standard = comparison["tiers"]["standard"]
    lines.extend(
        [
            "## Assumptions",
            f"- Hotels considered: {standard['hotel_count_considered']}",
            f"- Attractions considered: {standard['place_count_considered']}",
            f"- Activities considered: {standard['activity_count_considered']}",
            f"- Meals per day (standard): ${standard['assumptions']['meal_cost_per_day_usd']:.2f}",
            (
                f"- Local transport per day in {dest}: "
                f"${standard['assumptions']['local_transport_per_day_usd']:.2f}"
            ),
            "- This budget covers budgeting only and does not replace hotel selection or itinerary design.",
        ]
    )

    return "\n".join(lines)
