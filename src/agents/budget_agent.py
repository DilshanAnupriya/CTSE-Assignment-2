"""
Budget Agent
============
Budget estimation agent for the Sri Lanka Travel Planner Multi-Agent System.

This agent is responsible for:
  1. Reading destination cost data from the shared travel dataset.
  2. Estimating accommodation, attractions, food, and transport costs.
  3. Returning a structured budget breakdown for downstream reporting.

Author: Vidura Hewaduwa (Budget Agent Module)
"""

import logging

from crewai import Agent
from crewai.tools import tool

from tools.cost_tool import format_budget_breakdown

logger = logging.getLogger(__name__)


@tool("Calculate Trip Budget")
def tool_calculate_trip_budget(
    destination: str,
    days: int,
    budget: str = "",
    transport_preference: str = "",
    hotel_preference: str = "",
) -> str:
    """
    Calculate an estimated trip budget using the local travel dataset.
    Inputs:
    - destination: city name
    - days: number of trip days
    - budget: preferred budget level (Budget, Mid-range, Luxury)
    - transport_preference: public transport, train, tuk-tuk, taxi, etc.
    - hotel_preference: hostel, budget hotel, boutique, luxury, etc.
    """
    return format_budget_breakdown(
        destination=destination,
        days=days,
        budget=budget or None,
        transport_preference=transport_preference or None,
        hotel_preference=hotel_preference or None,
    )


def create_budget_agent(llm) -> Agent:
    """
    Create and return the Travel Budget Agent.

    Args:
        llm: CrewAI-compatible LLM instance.

    Returns:
        Agent: Configured Budget Agent.
    """

    logger.info("[BudgetAgent] Creating Travel Budget Agent...")

    agent = Agent(
        role="Travel Budget Analyst",
        goal=(
            "Estimate a realistic travel budget for the requested destination using only "
            "verified local dataset information and clearly stated assumptions."
        ),
        backstory=(
            "You are a careful travel cost analyst who builds practical trip budgets for travelers. "
            "You break costs into accommodation, attractions, activities, food, and transport. "
            "You never invent prices and always ground your estimate in the provided data tool."
        ),
        tools=[tool_calculate_trip_budget],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )

    logger.info("[BudgetAgent] Travel Budget Agent created successfully.")
    return agent
