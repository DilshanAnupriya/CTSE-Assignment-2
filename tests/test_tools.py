import sys
import os

sys.path.append(os.path.abspath("src"))

from tools.cost_tool import cost_tool
from tools.travel_tool import travel_tool
from tools.hotel_tool import hotel_tool


def test_cost_tool():
    assert cost_tool(50, 2) == 100
    assert cost_tool(0, 5) == 0


def test_travel_tool():
    places = travel_tool("Kandy")
    assert isinstance(places, list)
    assert len(places) > 0


def test_hotel_tool():
    hotels = hotel_tool("Ella")
    assert isinstance(hotels, list)
    assert "name" in hotels[0]