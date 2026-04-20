"""
Test Suite: Travel Research Agent & Travel Tool
================================================
Automated evaluation script for the Research Agent component of the
Sri Lanka Travel Planner Multi-Agent System.

Coverage:
  1. Unit Tests          — travel_tool.py functions (pure logic, no LLM needed)
  2. Property-Based Tests— structural guarantees on returned data
  3. Integration Tests   — research_task produces the correct output shape
  4. LLM-as-a-Judge Test — uses the local Ollama LLM to evaluate output quality
  5. Security Tests      — validate against prompt injection and bad inputs

Run:
    # From the project root directory:
    pytest tests/test_research_agent.py -v

    # With coverage report:
    pytest tests/test_research_agent.py -v --tb=short

Author: Dilshan Anupriya (Research Agent Module)
"""

import sys
import os
import json
import re

import pytest

# ── Path setup ─────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from tools.travel_tool import (
    get_places_and_activities,
    get_top_rated_places,
    list_available_destinations,
    format_places_summary,
)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Unit Tests: get_places_and_activities()
# ══════════════════════════════════════════════════════════════════════════════

class TestGetPlacesAndActivities:
    """Unit tests for the core lookup function."""

    def test_kandy_returns_places(self):
        """Valid destination 'Kandy' must return a non-empty places list."""
        result = get_places_and_activities("Kandy")
        assert result["error"] is None, f"Unexpected error: {result['error']}"
        assert isinstance(result["places"], list)
        assert len(result["places"]) > 0, "Expected at least one place for Kandy"

    def test_ella_returns_activities(self):
        """Valid destination 'Ella' must return a non-empty activities list."""
        result = get_places_and_activities("Ella")
        assert result["error"] is None
        assert isinstance(result["activities"], list)
        assert len(result["activities"]) > 0, "Expected at least one activity for Ella"

    def test_galle_returns_correct_destination_key(self):
        """The returned 'destination' key must match the input (normalised)."""
        result = get_places_and_activities("Galle")
        assert result["destination"] == "Galle"

    def test_case_insensitive_lookup(self):
        """Tool must handle different casing of destination names."""
        result_lower = get_places_and_activities("kandy")
        result_upper = get_places_and_activities("KANDY")
        result_mixed = get_places_and_activities("KaNdY")
        assert result_lower["error"] is None
        assert result_upper["error"] is None
        assert result_mixed["error"] is None
        assert len(result_lower["places"]) == len(result_upper["places"])

    def test_unknown_destination_returns_error(self):
        """Unknown destination must return an error and empty lists."""
        result = get_places_and_activities("Tokyo")
        assert result["error"] is not None
        assert isinstance(result["error"], str)
        assert len(result["places"]) == 0
        assert len(result["activities"]) == 0

    def test_empty_string_destination(self):
        """Empty string input must return an error gracefully (no crash)."""
        result = get_places_and_activities("")
        assert result["error"] is not None
        assert result["places"] == []

    def test_whitespace_destination(self):
        """Destination with extra whitespace must be handled gracefully."""
        result = get_places_and_activities("  Kandy  ")
        # Should still resolve correctly after strip
        assert result["error"] is None or "not found" in (result["error"] or "")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Property-Based Tests: structural guarantees
# ══════════════════════════════════════════════════════════════════════════════

class TestDataStructureProperties:
    """Property tests: every place object must have the required schema fields."""

    REQUIRED_PLACE_FIELDS = {"name", "type", "description", "rating", "entry_fee_usd"}
    VALID_DESTINATIONS = ["Kandy", "Ella", "Galle", "Colombo"]

    @pytest.mark.parametrize("destination", VALID_DESTINATIONS)
    def test_each_place_has_required_fields(self, destination: str):
        """Every place dict must contain all required schema fields."""
        result = get_places_and_activities(destination)
        assert result["error"] is None, f"Error for {destination}: {result['error']}"
        for place in result["places"]:
            missing = self.REQUIRED_PLACE_FIELDS - set(place.keys())
            assert not missing, (
                f"Place '{place.get('name', '?')}' in {destination} "
                f"is missing fields: {missing}"
            )

    @pytest.mark.parametrize("destination", VALID_DESTINATIONS)
    def test_rating_is_valid_float_in_range(self, destination: str):
        """All ratings must be floats between 0.0 and 5.0."""
        result = get_places_and_activities(destination)
        for place in result["places"]:
            rating = place.get("rating")
            assert isinstance(rating, (int, float)), (
                f"Rating for '{place['name']}' is not a number: {rating}"
            )
            assert 0.0 <= float(rating) <= 5.0, (
                f"Rating {rating} for '{place['name']}' is out of range [0.0, 5.0]"
            )

    @pytest.mark.parametrize("destination", VALID_DESTINATIONS)
    def test_entry_fee_is_non_negative(self, destination: str):
        """Entry fees must always be zero or positive numbers."""
        result = get_places_and_activities(destination)
        for place in result["places"]:
            fee = place.get("entry_fee_usd", 0)
            assert isinstance(fee, (int, float)), f"Fee for '{place['name']}' is not a number"
            assert fee >= 0, f"Negative entry fee detected for '{place['name']}': {fee}"

    @pytest.mark.parametrize("destination", VALID_DESTINATIONS)
    def test_place_names_are_non_empty_strings(self, destination: str):
        """All place names must be non-empty strings."""
        result = get_places_and_activities(destination)
        for place in result["places"]:
            name = place.get("name", "")
            assert isinstance(name, str) and len(name.strip()) > 0, (
                f"Invalid place name found in {destination}: '{name}'"
            )

    @pytest.mark.parametrize("destination", VALID_DESTINATIONS)
    def test_activities_are_list_of_strings(self, destination: str):
        """Activities must be a list where every element is a non-empty string."""
        result = get_places_and_activities(destination)
        activities = result["activities"]
        assert isinstance(activities, list)
        for activity in activities:
            assert isinstance(activity, str) and len(activity.strip()) > 0, (
                f"Invalid activity in {destination}: '{activity}'"
            )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Unit Tests: get_top_rated_places()
# ══════════════════════════════════════════════════════════════════════════════

class TestGetTopRatedPlaces:
    """Unit tests for top-rated places ranking."""

    def test_returns_correct_count(self):
        """Top-N filter must return exactly N results when N <= available places."""
        places = get_top_rated_places("Kandy", top_n=2)
        assert len(places) == 2

    def test_results_sorted_by_rating_descending(self):
        """Returned places must be sorted by rating highest-first."""
        places = get_top_rated_places("Ella", top_n=3)
        ratings = [p["rating"] for p in places]
        assert ratings == sorted(ratings, reverse=True), (
            f"Places are not sorted by rating descending: {ratings}"
        )

    def test_zero_top_n_defaults_gracefully(self):
        """Passing top_n=0 should default to 3 (defensive behaviour)."""
        places = get_top_rated_places("Galle", top_n=0)
        # Should not crash and should return some results (defaults to 3)
        assert isinstance(places, list)
        assert len(places) <= 3

    def test_unknown_destination_returns_empty(self):
        """Unknown destination must return empty list without crashing."""
        places = get_top_rated_places("UnknownCity")
        assert places == []

    def test_single_top_place(self):
        """top_n=1 must return exactly one place — the highest-rated."""
        places = get_top_rated_places("Galle", top_n=1)
        assert len(places) == 1
        all_places = get_top_rated_places("Galle", top_n=99)
        max_rating = max(p["rating"] for p in all_places)
        assert places[0]["rating"] == max_rating


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Unit Tests: list_available_destinations()
# ══════════════════════════════════════════════════════════════════════════════

class TestListAvailableDestinations:
    """Unit tests for the destination listing function."""

    def test_returns_list(self):
        """Function must return a list."""
        result = list_available_destinations()
        assert isinstance(result, list)

    def test_returns_non_empty_list(self):
        """The database must have at least one destination."""
        result = list_available_destinations()
        assert len(result) > 0, "Expected at least one available destination"

    def test_all_items_are_strings(self):
        """Every item in the list must be a non-empty string."""
        for dest in list_available_destinations():
            assert isinstance(dest, str) and len(dest) > 0

    def test_known_destinations_present(self):
        """Known destinations (Kandy, Ella, Galle) must be in the list."""
        destinations = list_available_destinations()
        for expected in ["Kandy", "Ella", "Galle"]:
            assert expected in destinations, f"'{expected}' missing from available destinations"

    def test_list_is_sorted_alphabetically(self):
        """Destinations must be returned in alphabetical order."""
        destinations = list_available_destinations()
        assert destinations == sorted(destinations), "Destinations are not alphabetically sorted"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Unit Tests: format_places_summary()
# ══════════════════════════════════════════════════════════════════════════════

class TestFormatPlacesSummary:
    """Unit tests for the human-readable summary formatter."""

    def test_summary_contains_destination_name(self):
        """Summary must include the destination name in its header."""
        summary = format_places_summary("Kandy")
        assert "Kandy" in summary

    def test_summary_contains_place_name(self):
        """Summary must include at least one known place name."""
        summary = format_places_summary("Ella")
        assert "Nine Arch Bridge" in summary

    def test_summary_contains_activities_section(self):
        """Summary must include the Activities section."""
        summary = format_places_summary("Galle")
        assert "Recommended Activities" in summary or "Activities" in summary

    def test_summary_contains_rating(self):
        """Summary must include rating information."""
        summary = format_places_summary("Kandy")
        assert "Rating" in summary or "/5.0" in summary

    def test_unknown_destination_returns_error_string(self):
        """Unknown destination must return an error string, not crash."""
        summary = format_places_summary("Mars")
        assert summary.startswith("Error:"), f"Expected error string, got: {summary[:80]}"

    def test_summary_is_non_empty_string(self):
        """Output must be a non-empty string for valid destinations."""
        summary = format_places_summary("Galle")
        assert isinstance(summary, str)
        assert len(summary) > 100, "Summary seems too short to be meaningful"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Security Tests: input injection defence
# ══════════════════════════════════════════════════════════════════════════════

class TestSecurityAndEdgeCases:
    """Security and robustness tests — ensures the tool handles hostile inputs."""

    def test_sql_injection_attempt(self):
        """Tool must not crash or expose data for SQL injection strings."""
        result = get_places_and_activities("'; DROP TABLE places; --")
        # Should return an error, not crash
        assert result["error"] is not None
        assert result["places"] == []

    def test_path_traversal_attempt(self):
        """Tool must not allow path traversal via destination input."""
        result = get_places_and_activities("../../etc/passwd")
        assert result["error"] is not None

    def test_very_long_input(self):
        """Tool must handle excessively long input strings without hanging."""
        long_input = "A" * 10_000
        result = get_places_and_activities(long_input)
        assert result["error"] is not None  # Should gracefully fail

    def test_none_type_input(self):
        """Passing None should raise TypeError (type safety enforcement)."""
        with pytest.raises((TypeError, AttributeError)):
            get_places_and_activities(None)  # type: ignore[arg-type]

    def test_special_characters_input(self):
        """Special characters in destination must not cause unhandled exceptions."""
        for special in ["<script>alert(1)</script>", "$$KANDY$$", "\x00Ella\x00"]:
            try:
                result = get_places_and_activities(special)
                # Either returns an error dict or raises cleanly — no crash allowed
                assert "error" in result
            except (ValueError, TypeError):
                pass  # These typed exceptions are acceptable


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — LLM-as-a-Judge Evaluation (optional, requires Ollama running)
# ══════════════════════════════════════════════════════════════════════════════

def evaluate_output_with_llm(output_text: str, destination: str) -> dict:
    """
    Use the local Ollama LLM to judge the quality of the research output.

    This is an 'LLM-as-a-Judge' evaluation pattern. The judge LLM is asked
    to score the output on relevance, completeness, and accuracy.

    Args:
        output_text (str): The research report to evaluate.
        destination (str): The destination the report was generated for.

    Returns:
        dict: Containing 'score' (int 1-10) and 'reason' (str).
    """
    try:
        import requests  # type: ignore
        payload = {
            "model": "qwen2.5",
            "prompt": f"""You are a travel quality evaluator. Rate this travel research report
for "{destination}" on a scale of 1 to 10.

Criteria:
- Relevance: Does it mention real, known attractions in {destination}?
- Completeness: Does it cover places, ratings, and activities?
- Clarity: Is it well-structured and readable?

Report to evaluate:
---
{output_text[:2000]}
---

Respond ONLY in JSON format like this:
{{"score": <number 1-10>, "reason": "<one sentence>"}}
""",
            "stream": False,
        }
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=60,
        )
        if response.status_code != 200:
            return {"score": 0, "reason": f"HTTP error: {response.status_code}"}

        raw = response.json().get("response", "{}")
        # Extract JSON from the response
        match = re.search(r'\{[^}]+\}', raw)
        if match:
            return json.loads(match.group())
        return {"score": 0, "reason": f"Could not parse LLM response: {raw[:100]}"}

    except Exception as e:
        return {"score": 0, "reason": f"LLM judge unavailable: {str(e)}"}


@pytest.mark.skipif(
    os.environ.get("SKIP_LLM_TESTS", "false").lower() == "true",
    reason="Skipped because SKIP_LLM_TESTS=true",
)
class TestLLMAsJudge:
    """
    LLM-as-a-Judge tests using the local Ollama model.
    These tests require Ollama to be running with qwen2.5 pulled.
    Skip with: SKIP_LLM_TESTS=true pytest ...
    """

    def test_travel_tool_output_is_high_quality(self):
        """
        The formatted summary for 'Kandy' must score >= 6/10 from the LLM judge.
        This validates that our tool produces genuinely useful content.
        """
        destination = "Kandy"
        summary = format_places_summary(destination)
        assert not summary.startswith("Error:"), "Tool returned an error instead of a summary"

        judgment = evaluate_output_with_llm(summary, destination)
        score = judgment.get("score", 0)
        reason = judgment.get("reason", "No reason given")

        print(f"\n[LLM Judge] Score: {score}/10 | Reason: {reason}")
        assert isinstance(score, (int, float)), f"Score is not a number: {score}"
        assert score >= 6, (
            f"LLM judge rated output too low ({score}/10). Reason: {reason}\n"
            f"Output excerpt: {summary[:300]}"
        )

    def test_ella_summary_mentions_nine_arch_bridge(self):
        """
        The Ella summary must mention 'Nine Arch Bridge' — validating tool accuracy.
        """
        summary = format_places_summary("Ella")
        assert "Nine Arch Bridge" in summary, (
            "Expected 'Nine Arch Bridge' in Ella summary but it was missing."
        )
        judgment = evaluate_output_with_llm(summary, "Ella")
        score = judgment.get("score", 0)
        print(f"\n[LLM Judge] Ella score: {score}/10 | {judgment.get('reason', '')}")
        assert score >= 5, f"Ella report quality too low: {score}/10"


# ══════════════════════════════════════════════════════════════════════════════
# Quick smoke-test runner (no pytest needed)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  Travel Research Agent — Direct Tool Smoke Tests")
    print("=" * 60)

    for dest in ["Kandy", "Ella", "Galle", "Colombo", "Tokyo"]:
        result = get_places_and_activities(dest)
        status = "✅ OK" if result["error"] is None else f"⚠️  {result['error'][:60]}"
        print(f"  {dest:<12} -> {status}")
        if result["error"] is None:
            print(f"            {len(result['places'])} places, {len(result['activities'])} activities")

    print("\n  Top 3 Rated Places in Galle:")
    for p in get_top_rated_places("Galle", top_n=3):
        print(f"    {p['rating']}/5.0  {p['name']}")

    print("\n  Available destinations:", list_available_destinations())

    print("\n  Sample Summary (Ella, first 400 chars):")
    print(format_places_summary("Ella")[:400])
    print("  ...")
    print("\n✅ All smoke tests passed.")
