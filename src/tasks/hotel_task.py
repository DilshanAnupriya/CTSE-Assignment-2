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


def create_hotel_task(destination: str, llm, budget: str = None, traveler_type: str = None, hotel_preference: str = None) -> Task:
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

    preferences_text = []
    if budget:
        preferences_text.append(f"- **Budget:** {budget}")
    if traveler_type:
        preferences_text.append(f"- **Traveler Type:** {traveler_type}")
    if hotel_preference:
        preferences_text.append(f"- **Hotel Preference:** {hotel_preference}")
    
    preferences_section = ""
    if preferences_text:
        preferences_section = "\n**USER HOTEL PREFERENCES:**\n" + "\n".join(preferences_text) + "\n\nCRITICAL INSTRUCTION: You MUST filter and prioritize the hotels based on these preferences! Select hotels that match the specified budget category, traveler type, and preferred hotel type."

    task = Task(
        description=f"""
You are a Hotel Recommendation Specialist for the destination: **{destination}**.

Your job is to:
1. Use your hotel data tool to retrieve all available hotels for "{destination}".
2. Analyze hotels based on:
   - Rating (most important)
   - Price per night (budget vs luxury balance)
   - Hotel type (luxury, boutique, budget, hostel)
   - Suitable traveler types{preferences_section}
3. Select the BEST 3–5 hotels suitable for different types of travellers, prioritizing those matching the user preferences above.
4. Match hotels with the travel experience of {destination} (e.g., adventure, nature, cultural tourism).
5. VERY IMPORTANT: Review the itinerary/context provided by the previous agent. You MUST group your hotel recommendations geographically. Suggest hotels that are nearest to the planned daily activities or main clusters of attractions in the itinerary to minimize daily travel time.

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
- GEOGRAPHICAL GROUPING: You MUST recommend and group hotels based on their proximity to the places and activities planned in the itinerary. Explain which day/activities each hotel is nearest to.
""",
        expected_output=f"""
A structured list of top hotel recommendations for {destination}, including:
- Top 3–5 hotels
- Ratings and prices
- Clear reasoning for each recommendation, including geographical proximity to planned activities
- Traveler suitability classification
""",
        agent=agent,
    )

    logger.info("[HotelTask] Hotel task created for '%s'.", destination)
    return task