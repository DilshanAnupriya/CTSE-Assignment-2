"""
Budget Task
===========
Defines the task assigned to the Budget Agent within the CrewAI pipeline.

The budget task is responsible for:
  - Reading destination pricing signals from the shared dataset.
  - Estimating accommodation, food, transport, and activity costs.
  - Producing a structured budget breakdown for the final travel report.

Author: Vidura Hewaduwa (Budget Agent Module)
"""

import logging

from crewai import Task

from agents.budget_agent import create_budget_agent

logger = logging.getLogger(__name__)


def create_budget_task(
    destination: str,
    days: int,
    llm,
    budget: str = None,
    transport_preference: str = None,
    hotel_preference: str = None,
) -> Task:
    """
    Build and return the budget estimation task.

    Args:
        destination (str): Travel destination (e.g., "Ella", "Kandy").
        days (int): Number of days for the trip.
        llm: CrewAI-compatible LLM instance.

    Returns:
        Task: Configured CrewAI Task for budget estimation.
    """

    logger.info("[BudgetTask] Creating budget task for destination: %s", destination)

    agent = create_budget_agent(llm)

    preferences_text = []
    if budget:
        preferences_text.append(f"- **Budget Preference:** {budget}")
    if transport_preference:
        preferences_text.append(f"- **Transport Preference:** {transport_preference}")
    if hotel_preference:
        preferences_text.append(f"- **Hotel Preference:** {hotel_preference}")

    preferences_section = ""
    if preferences_text:
        preferences_section = "\n\n**USER BUDGET PREFERENCES:**\n" + "\n".join(preferences_text)

    task = Task(
        description=f"""
You are the Travel Budget Analyst for **{destination}** planning a **{days}-day** trip.{preferences_section}

Your job is to:
1. Call the 'Calculate Trip Budget' tool using:
   - destination="{destination}"
   - days={days}
   - budget="{budget or ''}"
   - transport_preference="{transport_preference or ''}"
   - hotel_preference="{hotel_preference or ''}"
2. Use the tool output to prepare a clean, structured budget estimate.
3. Present the cost breakdown clearly so downstream agents can include it in the final report.
4. Keep the estimate practical and transparent by preserving the assumptions from the tool output.

STRICT OUTPUT FORMAT:

### Budget Estimate for {destination}
- **Trip Duration**
- **Selected Budget Tier**
- **Sample Hotel Basis**
- **Transport Basis**

#### Cost Breakdown
- **Accommodation**
- **Attractions**
- **Activities**
- **Food**
- **Local Transport**
- **Contingency (10%)**
- **Estimated Total**
- **Estimated Daily Average**

#### Assumptions
- Clearly list the assumptions used for hotel nights, meals, transport, and attraction/activity averages.

#### Alternative Budget Scenarios
- Include the Budget, Mid-range, and Luxury totals if they are available from the tool.

RULES:
- Use ONLY the data returned by your budget tool.
- Do NOT invent prices or hotel names.
- Make the estimate easy to read and professional.
- Keep the wording practical and concise.
""",
        expected_output=f"""
A structured travel budget estimate for {destination}, including:
- Accommodation, food, transport, attractions, and activities costs
- A clear total estimated trip cost
- Transparent assumptions
- Alternative budget scenarios where available
""",
        agent=agent,
    )

    logger.info("[BudgetTask] Budget task created for '%s'.", destination)
    return task
