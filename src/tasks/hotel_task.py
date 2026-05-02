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
        preferences_section = "\n\n**USER HOTEL PREFERENCES:**\n" + "\n".join(preferences_text)

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
5. VERY IMPORTANT GEOGRAPHIC RULES:
   - You MUST group your hotel recommendations geographically using ONLY the provided "Location" or "location_cluster" field from the tool.
   - You MUST NOT infer proximity or geographic relationships unless the location data is explicitly provided in the tool output.
   - If no detailed geographic mapping or location match is available for a hotel to the activities, use exactly this fallback wording: "Recommended based on central accessibility to planned attractions."
   - NEVER output placeholder text such as "Nearby hotels not specified in the tool output".
6. VERY IMPORTANT DESCRIPTION RULES:
   - Your hotel descriptions MUST be grounded strictly in the provided dataset metadata.
   - Do NOT use exaggerated, hallucinated, or unsupported wording (e.g., do not call a hotel "luxurious" or "opulent" unless its Type/data explicitly supports a Luxury classification).
7. STRICT PREFERENCE ENFORCEMENT RULES:
   - Budget preference is a HARD FILTER, not a soft preference. If the user selects "Budget", prioritize ONLY budget-friendly properties first. Do NOT recommend luxury/high-price hotels unless there are insufficient matching budget options. If including fallback hotels due to insufficient matches, you MUST explicitly state in the reasoning: "Included as fallback due to limited exact budget matches."
   - Traveler Type is a HARD PRIORITY:
     * Couple -> prioritize romantic/private/boutique/hotel stays over hostels/business hotels where possible.
     * Solo -> prioritize solo-friendly / safe / affordable stays.
     * Family -> prioritize spacious/family-oriented stays.
     * Friends -> prioritize group-friendly/social stays.
   - Hostel should NOT be recommended for couples/families unless no better matching alternatives exist.
   - HOTEL PREFERENCE DISTINCTION: "Budget Hotel" and "Hostel" are distinctly different categories. If the user explicitly selects "Budget Hotel", you must prioritize properties that are actually classified as Budget Hotels or Guesthouses, NOT Hostels. Only recommend Hostels if the user selects "Hostel" or if there are absolutely no other budget options.
   - If a recommendation partially matches preferences, explain why it was included in your reasoning.

STRICT OUTPUT FORMAT:

### Hotel Recommendations for {destination}

For EACH recommended hotel, include:

- **Hotel Name**
- **Location** (from location_cluster)
- **Type**
- **Rating**
- **Price per Night (USD)**
- **Why Recommended** (2–3 sentences grounded strictly in metadata; use the geographic fallback wording if needed)
- **Best For** (e.g., luxury travelers, backpackers, couples, etc.)

RULES:
- Do NOT invent hotels. YOU MUST ONLY use the EXACT hotel names returned by your tool. Do not invent things like 'The Pod Hostel Colombo'. If a hotel is not in the tool output, it does not exist.
- ONLY use data from the provided hotel dataset.
- Prioritize high-rated hotels first.
- Ensure a mix of budget and premium options where possible.
- GEOGRAPHICAL GROUPING: Use only the explicit "Location" field. Apply fallback text if precise mapping is unavailable.
- NO HALLUCINATION: All praises must match the actual hotel Type and Rating. Do not hallucinate properties or amenities.
- HARD FILTERS: Budget and Traveler Type rules MUST be strictly followed or explicitly justified with the fallback string.
""",
        expected_output=f"""
A structured list of top hotel recommendations for {destination}, including:
- Top 3–5 hotels
- Ratings and prices
- Clear reasoning for each recommendation using strict metadata and accurate geographic location handling (or exact fallback wording)
- Traveler suitability classification
- No hallucinated descriptions or placeholder texts.
""",
        agent=agent,
    )

    logger.info("[HotelTask] Hotel task created for '%s'.", destination)
    return task