"""
Budget Task
===========
Defines the task assigned to the Budget Agent within the CrewAI pipeline.

The budget task is responsible for:
  - Calculating cost estimates for the requested destination and day count.
  - Comparing budget tiers using verified dataset-backed hotel prices.
  - Producing a structured budget report for downstream use.

Author: Vidura Hewaduwa (Budget Agent Module)
"""

import logging

from crewai import Task

from agents.budget_agent import create_budget_agent

logger = logging.getLogger(__name__)


def create_budget_task(destination: str, days: int, llm) -> Task:
    """
    Build and return the budget estimation task.
    """
    logger.info(
        "[BudgetTask] Creating budget task for destination='%s', days=%d",
        destination,
        days,
    )

    agent = create_budget_agent(llm)

    task = Task(
        description=f"""
You are the Budget Agent for the destination **{destination}** and trip duration of **{days} day(s)**.

Your scope is STRICTLY budgeting only. Do not create the itinerary, do not recommend hotels in narrative form,
and do not generate the final report because those belong to other agents.

Follow these exact steps:
1. Call the 'Compare Budget Tiers' tool with "{destination},{days}" to calculate budget, standard, and premium totals.
2. Call the 'Calculate Budget Breakdown' tool at least once for the standard tier using "{destination},{days},standard".
3. Call the 'Format Budget Summary' tool with "{destination},{days}".
4. Produce a clean budget report that includes:
   - Destination and trip duration
   - Budget, Standard, and Premium total estimates
   - Itemized standard breakdown for accommodation, meals, local transport, entry fees, and contingency
   - A short affordability note on which tier is the balanced recommendation
   - A brief assumptions section

RULES:
- Use the tools only; do not invent pricing.
- Keep the focus on costs, not planning or hotel marketing.
- Make it clear this estimate is for a single traveller.
""",
        expected_output=f"""
A structured budget report for {destination} covering {days} day(s) that includes:
- Budget / Standard / Premium total estimates
- Itemized standard-tier breakdown
- Explicit assumptions
- No itinerary writing, no hotel recommendation writeup, and no final summary report generation
""",
        agent=agent,
    )

    logger.info("[BudgetTask] Budget task created successfully.")
    return task
