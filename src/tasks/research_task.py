"""
Research Task
=============
Defines the task assigned to the Travel Research Agent within the CrewAI pipeline.

The research task instructs the agent to:
  - Use its tools to look up accurate information (not rely on LLM memory alone).
  - Produce a structured, detailed report as its output.
  - Pass the context forward to the Planner Agent.

Author: Nadeema Jayasinghe (Research Agent Module)
"""

import logging
from crewai import Task
from agents.research_agent import create_research_agent

logger = logging.getLogger(__name__)


def create_research_task(destination: str, llm, days: int, interests: list[str] = None, trip_pace: str = None, transport_preference: str = None) -> Task:
    """
    Build and return the research task for the given destination.

    This task is the first step in the sequential pipeline. Its output
    (a structured place & activity report) is automatically passed as
    context to subsequent tasks (Planner, Budget) by CrewAI.

    Args:
        destination (str): The travel destination (e.g., "Ella", "Kandy").
        llm:               A CrewAI-compatible LLM instance for the agent.

    Returns:
        Task: A configured CrewAI Task object ready for crew execution.
    """
    logger.info("[ResearchTask] Creating research task for destination: %s", destination)

    agent = create_research_agent(llm)

    preferences_text = []
    if interests:
        preferences_text.append(f"- **Interests:** {', '.join(interests)}")
    if trip_pace:
        preferences_text.append(f"- **Trip Pace:** {trip_pace}")
    if transport_preference:
        preferences_text.append(f"- **Transport Preference:** {transport_preference}")
    
    preferences_section = ""
    if preferences_text:
        preferences_section = "\n**USER PREFERENCES:**\n" + "\n".join(preferences_text) + "\n\nCRITICAL INSTRUCTION: You MUST filter and prioritize the places and activities based on these preferences! Only include places that align with the user's interests. Adjust the number of places per day according to the Trip Pace. Consider the Transport Preference when calculating feasibility."

    task = Task(
        description=f"""
You are researching tourist places and activities for the destination: **{destination}**.
You need to plan an itinerary for **{days} days**.{preferences_section}

Follow these exact steps:
1. Call the 'Get Places and Activities' tool with destination="{destination}" to retrieve
   real data from the travel database.
2. If you are unsure of the spelling, call 'List Available Destinations' first.
3. Call 'Get Top Rated Places' to identify the must-see highlights.
4. Compile ALL findings that match the user's preferences into a well-structured research report.
5. Create a day-by-day itinerary (e.g., Day 1, Day 2, up to Day {days}) distributing the 
   retrieved places and activities logically across the days. VERY IMPORTANT: You MUST group places geographically. For any given day, select places and activities that are nearest to each other to minimize travel time. The next day should focus on a different geographical cluster of nearby locations. Ensure the top-rated ones are prioritized within this geographical grouping.

STRICT FORMATTING RULES:
1. ALL content MUST begin with a brief overall recommendation sentence at the very TOP.
2. Following the recommendation, output ONLY the Day-by-Day Itinerary (Day 1, Day 2, etc.). 
   DO NOT create separate "Other Attractions" or "Recommended Activities" sections.
3. For EVERY place and EVERY activity, you MUST list ALL of the following fields without skipping any:
    - **Name**
    - **Type**
    - **Rating** out of 5.0 (Add [TOP RATED] if it is highly rated)
    - **Entry Fee:** (e.g., $xx USD)
    - **Best Time to Visit:**
    - **Recommended Duration:**
    - **Description:** (A full 2-3 sentence description)

Example Format:
### Overall Recommendation
[Your 1-2 sentence recommendation here]

**Day 1**
- **[Name of Place/Activity]**
  - Type: [Type]
  - Rating: [Rating]
  - Entry Fee: [Fee]
  - Best Time to Visit: [Time]
  - Recommended Duration: [Duration]
  - Description: [Description]
... (continue for the filtered places and activities across the {days} days)

Do NOT invent or hallucinate places. Only use data returned by your tools.
""",
        expected_output=f"""
A {days}-day structured travel itinerary for {destination} that STRICTLY MUST:
1. Have the overall recommendation at the very TOP.
2. Contain ONLY day-by-day sections (Day 1, Day 2, etc.) below the recommendation. No external lists of places/activities.
3. Show ALL required fields (Type, Rating, Entry Fee, Best Time, Duration, and Full Description) for EVERY place and EVERY activity.
""",
        agent=agent,
    )

    logger.info("[ResearchTask] Research task created for '%s'.", destination)
    return task