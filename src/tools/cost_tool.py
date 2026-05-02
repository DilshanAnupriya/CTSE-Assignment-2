"""
Cost Tool
=========
Custom tool for the Budget Agent in the Sri Lanka Travel Planner MAS.
Provides structured trip budget estimates using the shared travel dataset.

Author: Vidura Hewaduwa (Budget Agent Module)
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def _load_travel_data() -> dict[str, Any]:
    """
    Load travel_data.json safely from likely project locations.
    """

    candidates = [
        os.path.join(os.getcwd(), "data", "travel_data.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "travel_data.json"),
    ]

    for path in candidates:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            with open(abs_path, "r", encoding="utf-8") as file:
                return json.load(file)

    raise FileNotFoundError("travel_data.json not found in expected paths")


def _match_destination(data: dict[str, Any], destination: str) -> str | None:
    for key in data:
        if key.lower() == destination.strip().lower():
            return key
    return None


def _normalize_budget_tier(budget: str | None) -> str:
    if not budget:
        return "Mid-range"

    value = budget.strip().lower()
    if "lux" in value or "premium" in value:
        return "Luxury"
    if "budget" in value or "cheap" in value or "low" in value:
        return "Budget"
    return "Mid-range"


def _daily_meal_cost(budget_tier: str) -> int:
    return {
        "Budget": 18,
        "Mid-range": 35,
        "Luxury": 65,
    }.get(budget_tier, 35)


def _transport_cost_and_label(transport_preference: str | None) -> tuple[int, str]:
    if not transport_preference:
        return 20, "Mixed local transport"

    value = transport_preference.strip().lower()

    if "public" in value or "bus" in value:
        return 8, "Public transport"
    if "train" in value:
        return 12, "Train plus short local transfers"
    if "walk" in value:
        return 5, "Mostly walking with short local rides"
    if "tuk" in value or "three" in value:
        return 15, "Tuk-tuk travel"
    if "private" in value or "taxi" in value or "car" in value:
        return 35, "Private car or taxi travel"

    return 20, transport_preference


def _filter_hotels(
    hotels: list[dict[str, Any]],
    budget_tier: str,
    hotel_preference: str | None,
) -> list[dict[str, Any]]:
    """
    Filter hotels based on explicit hotel preference first, then by budget tier.
    """

    filtered: list[dict[str, Any]] = []
    preference = (hotel_preference or "").strip().lower()

    if preference:
        if "hostel" in preference:
            filtered = [hotel for hotel in hotels if "hostel" in hotel.get("type", "").lower()]
        elif "budget hotel" in preference:
            filtered = [
                hotel for hotel in hotels
                if hotel.get("budget_category") == "Budget"
                and "hostel" not in hotel.get("type", "").lower()
            ]
        elif "guesthouse" in preference:
            filtered = [hotel for hotel in hotels if "guesthouse" in hotel.get("type", "").lower()]
        elif "boutique" in preference:
            filtered = [hotel for hotel in hotels if "boutique" in hotel.get("type", "").lower()]
        elif "luxury" in preference:
            filtered = [hotel for hotel in hotels if "lux" in hotel.get("type", "").lower()]

    if not filtered:
        filtered = [hotel for hotel in hotels if hotel.get("budget_category") == budget_tier]

    if not filtered:
        filtered = hotels

    return sorted(
        filtered,
        key=lambda hotel: (-hotel.get("rating", 0), hotel.get("price_per_night_usd", 0)),
    )


def _average_hotel_price_by_tier(hotels: list[dict[str, Any]], tier: str) -> int | None:
    matches = [hotel.get("price_per_night_usd", 0) for hotel in hotels if hotel.get("budget_category") == tier]
    if not matches:
        return None
    return round(sum(matches) / len(matches))


def calculate_trip_budget(
    destination: str,
    days: int,
    budget: str | None = None,
    transport_preference: str | None = None,
    hotel_preference: str | None = None,
) -> dict[str, Any]:
    """
    Calculate an estimated trip budget for the requested destination.
    """

    logger.info(
        "[CostTool] Calculating budget for destination=%s, days=%s, budget=%s, transport=%s, hotel_pref=%s",
        destination,
        days,
        budget,
        transport_preference,
        hotel_preference,
    )

    if days <= 0:
        return {
            "destination": destination,
            "error": "Trip days must be greater than zero.",
        }

    try:
        data = _load_travel_data()
    except Exception as exc:
        return {
            "destination": destination,
            "error": f"Error loading dataset: {str(exc)}",
        }

    matched_key = _match_destination(data, destination)
    if not matched_key:
        return {
            "destination": destination,
            "error": f"Destination '{destination}' not found. Available: {', '.join(data.keys())}",
        }

    destination_data = data[matched_key]
    places = destination_data.get("places", [])
    activities = destination_data.get("activities", [])
    hotels = destination_data.get("hotels", [])

    if not hotels:
        return {
            "destination": matched_key,
            "error": "No hotel data available for budget estimation.",
        }

    budget_tier = _normalize_budget_tier(budget)
    transport_daily_cost, transport_label = _transport_cost_and_label(transport_preference)
    meal_daily_cost = _daily_meal_cost(budget_tier)
    hotel_options = _filter_hotels(hotels, budget_tier, hotel_preference)
    selected_hotel = hotel_options[0]
    nights = max(days - 1, 0)

    paid_places = [place.get("entry_fee_usd", 0) for place in places if place.get("entry_fee_usd", 0) > 0]
    paid_activities = [
        activity.get("entry_fee_usd", 0)
        for activity in activities
        if isinstance(activity, dict) and activity.get("entry_fee_usd", 0) > 0
    ]

    avg_place_fee = round(sum(paid_places) / len(paid_places)) if paid_places else 0
    avg_activity_fee = round(sum(paid_activities) / len(paid_activities)) if paid_activities else 0

    experience_multiplier = {
        "Budget": 0.8,
        "Mid-range": 1.0,
        "Luxury": 1.2,
    }[budget_tier]

    attraction_days = min(days, max(len(places), 1))
    activity_days = min(days, max(len(activities), 1))

    accommodation_total = selected_hotel.get("price_per_night_usd", 0) * nights
    attractions_total = round(avg_place_fee * attraction_days * 0.6)
    activities_total = round(avg_activity_fee * activity_days * 0.5 * experience_multiplier)
    food_total = meal_daily_cost * days
    transport_total = transport_daily_cost * days

    subtotal = accommodation_total + attractions_total + activities_total + food_total + transport_total
    contingency_total = round(subtotal * 0.10)
    grand_total = subtotal + contingency_total

    alternatives = {}
    for tier_name in ("Budget", "Mid-range", "Luxury"):
        average_price = _average_hotel_price_by_tier(hotels, tier_name)
        if average_price is None:
            continue

        alt_food_total = _daily_meal_cost(tier_name) * days
        alt_accommodation_total = average_price * nights
        alt_subtotal = (
            alt_accommodation_total
            + attractions_total
            + activities_total
            + transport_total
            + alt_food_total
        )
        alternatives[tier_name] = alt_subtotal + round(alt_subtotal * 0.10)

    return {
        "destination": matched_key,
        "days": days,
        "nights": nights,
        "selected_budget_tier": budget_tier,
        "selected_hotel": selected_hotel,
        "transport_label": transport_label,
        "assumptions": {
            "meal_daily_cost_usd": meal_daily_cost,
            "transport_daily_cost_usd": transport_daily_cost,
            "avg_place_fee_usd": avg_place_fee,
            "avg_activity_fee_usd": avg_activity_fee,
        },
        "breakdown": {
            "accommodation_usd": accommodation_total,
            "attractions_usd": attractions_total,
            "activities_usd": activities_total,
            "food_usd": food_total,
            "transport_usd": transport_total,
            "contingency_usd": contingency_total,
            "total_usd": grand_total,
            "estimated_daily_average_usd": round(grand_total / days),
        },
        "alternative_totals_usd": alternatives,
        "error": None,
    }


def format_budget_breakdown(
    destination: str,
    days: int,
    budget: str | None = None,
    transport_preference: str | None = None,
    hotel_preference: str | None = None,
) -> str:
    """
    Return a human-readable budget summary for the destination.
    """

    result = calculate_trip_budget(destination, days, budget, transport_preference, hotel_preference)

    if result.get("error"):
        return f"Error: {result['error']}"

    hotel = result["selected_hotel"]
    breakdown = result["breakdown"]
    assumptions = result["assumptions"]

    lines = [
        f"### Budget Estimate for {result['destination']}",
        f"- **Trip Duration:** {result['days']} day(s), {result['nights']} night(s)",
        f"- **Selected Budget Tier:** {result['selected_budget_tier']}",
        f"- **Sample Hotel Basis:** {hotel['name']} ({hotel.get('budget_category', 'N/A')} / ${hotel.get('price_per_night_usd', 0)} per night)",
        f"- **Transport Basis:** {result['transport_label']}",
        "",
        "#### Cost Breakdown",
        f"- **Accommodation:** ${breakdown['accommodation_usd']}",
        f"- **Attractions:** ${breakdown['attractions_usd']}",
        f"- **Activities:** ${breakdown['activities_usd']}",
        f"- **Food:** ${breakdown['food_usd']}",
        f"- **Local Transport:** ${breakdown['transport_usd']}",
        f"- **Contingency (10%):** ${breakdown['contingency_usd']}",
        f"- **Estimated Total:** ${breakdown['total_usd']}",
        f"- **Estimated Daily Average:** ${breakdown['estimated_daily_average_usd']} per day",
        "",
        "#### Assumptions",
        "- Hotel cost is calculated using the selected sample property from the dataset.",
        "- Accommodation assumes nights = days - 1.",
        (
            f"- Attraction estimate uses destination entry-fee averages "
            f"(avg place fee: ${assumptions['avg_place_fee_usd']}, "
            f"avg activity fee: ${assumptions['avg_activity_fee_usd']})."
        ),
        (
            f"- Food is estimated at ${assumptions['meal_daily_cost_usd']} per day "
            f"and transport at ${assumptions['transport_daily_cost_usd']} per day."
        ),
    ]

    alternatives = result.get("alternative_totals_usd", {})
    if alternatives:
        lines.extend(
            [
                "",
                "#### Alternative Budget Scenarios",
            ]
        )
        for tier_name, total in alternatives.items():
            lines.append(f"- **{tier_name}:** ${total}")

    return "\n".join(lines)
