"""
Budget Agent
============
Budget estimation agent for the Sri Lanka Travel Planner Multi-Agent System.

This agent is responsible for:
  1. Calculating accommodation, meals, local transport, and entry-fee costs.
  2. Comparing budget tiers using verified dataset-backed hotel pricing.
  3. Producing a structured budget summary without overlapping with itinerary,
     hotel recommendation, or final reporting agents.

Author: Vidura Hewaduwa (Budget Agent Module)
"""

import logging

from crewai import Agent
from crewai.tools import tool

from tools.cost_tool import compare_budget_tiers, format_budget_summary, get_budget_breakdown

logger = logging.getLogger(__name__)


@tool("Calculate Budget Breakdown")
def tool_calculate_budget_breakdown(input_text: str) -> str:
    """
    Calculate a cost breakdown for a destination, day count, and tier.

    Input formats supported:
    - "Ella,3,standard"
    - "Ella|3|budget"
    - "Kandy,2"  -> defaults to standard tier
    """
    normalized = input_text.replace("|", ",")
    parts = [part.strip() for part in normalized.split(",") if part.strip()]

    if len(parts) < 2:
        return (
            "Error: input must include destination and days. "
            "Example: 'Ella,3,standard'"
        )

    destination = parts[0]
    try:
        days = int(parts[1])
    except ValueError:
        return "Error: days must be an integer."

    tier = parts[2] if len(parts) >= 3 else "standard"
    result = get_budget_breakdown(destination, days, tier)
    if result.get("error"):
        return f"Error: {result['error']}"

    return (
        f"{result['tier'].title()} budget for {result['destination']} ({result['days']} day(s))\n"
        f"- Accommodation: ${result['accommodation_cost_usd']:.2f}\n"
        f"- Meals: ${result['meal_cost_usd']:.2f}\n"
        f"- Local transport: ${result['local_transport_cost_usd']:.2f}\n"
        f"- Entry fees: ${result['attraction_fees_usd']:.2f}\n"
        f"- Contingency: ${result['contingency_cost_usd']:.2f}\n"
        f"- Total: ${result['total_cost_usd']:.2f}"
    )


@tool("Compare Budget Tiers")
def tool_compare_budget_tiers(input_text: str) -> str:
    """
    Compare budget, standard, and premium cost tiers.

    Input formats supported:
    - "Ella,3"
    - "Kandy|2"
    """
    normalized = input_text.replace("|", ",")
    parts = [part.strip() for part in normalized.split(",") if part.strip()]

    if len(parts) != 2:
        return "Error: input must be 'destination,days'. Example: 'Ella,3'"

    destination = parts[0]
    try:
        days = int(parts[1])
    except ValueError:
        return "Error: days must be an integer."

    result = compare_budget_tiers(destination, days)
    if result.get("error"):
        return f"Error: {result['error']}"

    lines = [f"Budget comparison for {result['destination']} ({days} day(s)):"]
    for tier in ("budget", "standard", "premium"):
        tier_result = result["tiers"][tier]
        lines.append(f"- {tier.title()}: ${tier_result['total_cost_usd']:.2f}")
    return "\n".join(lines)


@tool("Format Budget Summary")
def tool_format_budget_summary(input_text: str) -> str:
    """
    Generate the full markdown budget summary.

    Input formats supported:
    - "Ella,3"
    - "Galle|4"
    """
    normalized = input_text.replace("|", ",")
    parts = [part.strip() for part in normalized.split(",") if part.strip()]

    if len(parts) != 2:
        return "Error: input must be 'destination,days'. Example: 'Ella,3'"

    destination = parts[0]
    try:
        days = int(parts[1])
    except ValueError:
        return "Error: days must be an integer."

    return format_budget_summary(destination, days)


def create_budget_agent(llm) -> Agent:
    """
    Build and return the Budget Agent.
    """
    logger.info("[BudgetAgent] Creating Budget Agent...")

    agent = Agent(
        role="Travel Budget Analyst",
        goal=(
            "Estimate realistic trip costs for a destination using the provided "
            "budget tools only. Focus on accommodation, meals, local transport, "
            "entry fees, and overall affordability."
        ),
        backstory=(
            "You are a detail-oriented travel budget specialist for Sri Lanka. "
            "You turn verified place, activity, and hotel pricing data into clear "
            "cost estimates for travellers. You do not create itineraries, recommend "
            "hotels beyond cost calculations, or generate the final report."
        ),
        tools=[
            tool_calculate_budget_breakdown,
            tool_compare_budget_tiers,
            tool_format_budget_summary,
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )

    logger.info("[BudgetAgent] Budget Agent created successfully.")
    return agent
