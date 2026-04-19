import json

def travel_tool(destination: str):
    """Get travel places for a destination"""

    with open("data/travel_data.json", "r") as f:
        data = json.load(f)

    return data.get(destination, [])