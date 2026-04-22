"""
Hotel Task
==========
Defines the task assigned to the Hotel Agent within the CrewAI pipeline.

The hotel task is responsible for:
  - Reading hotel data for the given destination from the travel database.
  - Filtering and ranking hotels based on rating, price, and suitability.
  - Recommending the best hotels for the travel itinerary.

Author: Dilshan Anupriya (Hotel Agent Module)
"""

import logging
from crewai import Task
from agents.hotel_agent import create_hotel_agent

logger = logging.getLogger(__name__)


def create_hotel_task(destination: str, llm) -> Task:
    """
    Build and return the hotel recommendation task.

    Args:
        destination (str): Travel destination (e.g., "Ella", "Kandy").
        llm: CrewAI-compatible LLM instance.

    Returns:
        Task: Configured CrewAI Task for hotel recommendations.
    """

    logger.info("[HotelTask] Creating hotel task for destination: %s", destination)

    agent = create_hotel_agent(llm)

    task = Task(
        description=f"""
You are a Hotel Recommendation Specialist for the destination: **{destination}**.

Your job is to:
1. Use your hotel data tool to retrieve all available hotels for "{destination}".
2. Analyze hotels based on:
   - Rating (most important)
   - Price per night (budget vs luxury balance)
   - Hotel type (luxury, boutique, budget, hostel)
3. Select the BEST 3–5 hotels suitable for different types of travellers.
4. Match hotels with the travel experience of {destination} (e.g., adventure, nature, cultural tourism).

STRICT OUTPUT FORMAT:

### Hotel Recommendations for {destination}

For EACH recommended hotel, include:

- **Hotel Name**
- **Type**
- **Rating**
- **Price per Night (USD)**
- **Why Recommended** (2–3 sentences explanation)
- **Best For** (e.g., luxury travelers, backpackers, couples, etc.)

RULES:
- Do NOT invent hotels.
- ONLY use data from the provided hotel dataset.
- Prioritize high-rated hotels first.
- Ensure a mix of budget and premium options where possible.
""",
        expected_output=f"""
A structured list of top hotel recommendations for {destination}, including:
- Top 3–5 hotels
- Ratings and prices
- Clear reasoning for each recommendation
- Traveler suitability classification
""",
        agent=agent,
    )

    logger.info("[HotelTask] Hotel task created for '%s'.", destination)
    return task