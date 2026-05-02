"""
Basic tool smoke tests — backwards-compatibility parity checks.
These run alongside the full test suite in test_research_agent.py.
"""
import sys
import os

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from tools.travel_tool import get_places_and_activities
from tools.hotel_tool import get_hotels


def test_travel_tool_returns_dict():
    """travel_tool should return a dict with 'places' and 'activities' keys."""
    result = get_places_and_activities("Kandy")
    assert isinstance(result, dict)
    assert "places" in result
    assert "activities" in result


def test_travel_tool_places_is_list():
    """The 'places' value must be a list."""
    result = get_places_and_activities("Kandy")
    assert isinstance(result["places"], list)
    assert len(result["places"]) > 0


def test_travel_tool_unknown_destination():
    """Unknown destinations must return a non-None error."""
    result = get_places_and_activities("UnknownCity")
    assert result["error"] is not None


def test_hotel_tool_returns_dict():
    """hotel_tool should return a dict with 'hotels' key."""
    result = get_hotels("Kandy")
    assert isinstance(result, dict)
    assert "hotels" in result


def test_hotel_tool_hotels_is_list():
    """The 'hotels' value must be a list."""
    result = get_hotels("Kandy")
    assert isinstance(result["hotels"], list)
    assert len(result["hotels"]) > 0


def test_hotel_tool_unknown_destination():
    """Unknown destinations must return a non-None error."""
    result = get_hotels("UnknownCity")
    assert result["error"] is not None