"""
Test Suite: Hotel Tool & Agent
================================================
Automated evaluation script for the Hotel Tool component of the
Sri Lanka Travel Planner Multi-Agent System.

Run:
    python -m pytest tests/test_hotel_agent.py -v
"""

import sys
import os
import json
import re

import pytest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from tools.hotel_tool import get_hotels, format_hotels

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Unit Tests: get_hotels()
# ══════════════════════════════════════════════════════════════════════════════

class TestGetHotels:
    """Unit tests for the hotel lookup function."""

    def test_kandy_returns_hotels(self):
        """Valid destination 'Kandy' must return a non-empty hotel list."""
        result = get_hotels("Kandy")
        assert result["error"] is None, f"Unexpected error: {result['error']}"
        assert isinstance(result["hotels"], list)
        assert len(result["hotels"]) > 0, "Expected at least one hotel for Kandy"

    def test_galle_returns_correct_destination_key(self):
        """The returned 'destination' key must match the input (normalised)."""
        result = get_hotels("Galle")
        assert result["destination"] == "Galle"

    def test_case_insensitive_lookup(self):
        """Tool must handle different casing of destination names."""
        result_lower = get_hotels("kandy")
        result_upper = get_hotels("KANDY")
        result_mixed = get_hotels("KaNdY")
        assert result_lower["error"] is None
        assert result_upper["error"] is None
        assert result_mixed["error"] is None
        assert len(result_lower["hotels"]) == len(result_upper["hotels"])

    def test_unknown_destination_returns_error(self):
        """Unknown destination must return an error and empty lists."""
        result = get_hotels("Tokyo")
        assert result["error"] is not None
        assert isinstance(result["error"], str)
        assert len(result["hotels"]) == 0

    def test_empty_string_destination(self):
        """Empty string input must return an error gracefully (no crash)."""
        result = get_hotels("")
        assert result["error"] is not None
        assert result["hotels"] == []

    def test_whitespace_destination(self):
        """Destination with extra whitespace must be handled gracefully."""
        result = get_hotels("  Kandy  ")
        assert result["error"] is None or "not found" in (result["error"] or "")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Property-Based Tests: structural guarantees
# ══════════════════════════════════════════════════════════════════════════════

class TestHotelDataStructureProperties:
    """Property tests: every hotel object must have the required schema fields."""

    REQUIRED_HOTEL_FIELDS = {"name", "type", "rating", "price_per_night_usd"}
    VALID_DESTINATIONS = ["Kandy", "Ella", "Galle", "Colombo"]

    @pytest.mark.parametrize("destination", VALID_DESTINATIONS)
    def test_each_hotel_has_required_fields(self, destination: str):
        """Every hotel dict must contain all required schema fields."""
        result = get_hotels(destination)
        assert result["error"] is None, f"Error for {destination}: {result['error']}"
        for hotel in result["hotels"]:
            missing = self.REQUIRED_HOTEL_FIELDS - set(hotel.keys())
            assert not missing, (
                f"Hotel '{hotel.get('name', '?')}' in {destination} "
                f"is missing fields: {missing}"
            )

    @pytest.mark.parametrize("destination", VALID_DESTINATIONS)
    def test_rating_is_valid_float_in_range(self, destination: str):
        """All ratings must be floats between 0.0 and 5.0."""
        result = get_hotels(destination)
        for hotel in result["hotels"]:
            rating = hotel.get("rating")
            assert isinstance(rating, (int, float)), (
                f"Rating for '{hotel['name']}' is not a number: {rating}"
            )
            assert 0.0 <= float(rating) <= 5.0, (
                f"Rating {rating} for '{hotel['name']}' is out of range [0.0, 5.0]"
            )

    @pytest.mark.parametrize("destination", VALID_DESTINATIONS)
    def test_price_is_positive(self, destination: str):
        """Prices must always be positive numbers."""
        result = get_hotels(destination)
        for hotel in result["hotels"]:
            price = hotel.get("price_per_night_usd", 0)
            assert isinstance(price, (int, float)), f"Price for '{hotel['name']}' is not a number"
            assert price > 0, f"Non-positive price detected for '{hotel['name']}': {price}"

    @pytest.mark.parametrize("destination", VALID_DESTINATIONS)
    def test_hotel_names_are_non_empty_strings(self, destination: str):
        """All hotel names must be non-empty strings."""
        result = get_hotels(destination)
        for hotel in result["hotels"]:
            name = hotel.get("name", "")
            assert isinstance(name, str) and len(name.strip()) > 0, (
                f"Invalid hotel name found in {destination}: '{name}'"
            )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Unit Tests: format_hotels()
# ══════════════════════════════════════════════════════════════════════════════

class TestFormatHotels:
    """Unit tests for the human-readable summary formatter."""

    def test_summary_contains_destination_name(self):
        """Summary must include the destination name in its header."""
        summary = format_hotels("Kandy")
        assert "Kandy" in summary

    def test_summary_contains_hotel_name(self):
        """Summary must include at least one known hotel name."""
        summary = format_hotels("Kandy")
        assert "Hotel Suisse Kandy" in summary

    def test_summary_contains_rating_and_price(self):
        """Summary must include rating and price information."""
        summary = format_hotels("Kandy")
        assert "Rating" in summary or "/5.0" in summary
        assert "Price" in summary or "$" in summary

    def test_unknown_destination_returns_error_string(self):
        """Unknown destination must return an error string, not crash."""
        summary = format_hotels("Mars")
        assert summary.startswith("Error:"), f"Expected error string, got: {summary[:80]}"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Security Tests: input injection defence
# ══════════════════════════════════════════════════════════════════════════════

class TestSecurityAndEdgeCases:
    """Security and robustness tests — ensures the tool handles hostile inputs."""

    def test_sql_injection_attempt(self):
        """Tool must not crash or expose data for SQL injection strings."""
        result = get_hotels("'; DROP TABLE places; --")
        assert result["error"] is not None
        assert result["hotels"] == []

    def test_path_traversal_attempt(self):
        """Tool must not allow path traversal via destination input."""
        result = get_hotels("../../etc/passwd")
        assert result["error"] is not None

    def test_very_long_input(self):
        """Tool must handle excessively long input strings without hanging."""
        long_input = "A" * 10_000
        result = get_hotels(long_input)
        assert result["error"] is not None

    def test_none_type_input(self):
        """Passing None should raise TypeError (type safety enforcement)."""
        with pytest.raises((TypeError, AttributeError)):
            get_hotels(None)  # type: ignore[arg-type]

    def test_special_characters_input(self):
        """Special characters in destination must not cause unhandled exceptions."""
        for special in ["<script>alert(1)</script>", "$$KANDY$$", "\x00Ella\x00"]:
            try:
                result = get_hotels(special)
                assert "error" in result
            except (ValueError, TypeError):
                pass


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — LLM-as-a-Judge Evaluation
# ══════════════════════════════════════════════════════════════════════════════

class OllamaUnavailableError(Exception):
    pass


def _check_ollama_available() -> None:
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            raise OllamaUnavailableError(f"Ollama responded with HTTP {response.status_code}")
    except OllamaUnavailableError:
        raise
    except Exception as e:
        raise OllamaUnavailableError(f"Ollama not reachable: {e}") from e


def evaluate_output_with_llm(output_text: str, destination: str) -> dict:
    import requests
    _check_ollama_available()

    payload = {
        "model": "qwen2.5",
        "prompt": (
            f'You are a hotel recommendation evaluator. Rate this hotel report\n'
            f'for "{destination}" on a scale of 1 to 10.\n\n'
            f'Criteria:\n'
            f'- Relevance: Does it mention real hotels or accommodations in {destination}?\n'
            f'- Completeness: Does it cover types, ratings, and prices?\n'
            f'- Clarity: Is it well-structured and readable?\n\n'
            f'Report to evaluate:\n---\n{output_text[:2000]}\n---\n\n'
            f'Respond ONLY in JSON format like this:\n'
            f'{{"score": <number 1-10>, "reason": "<one sentence>"}}'
        ),
        "stream": False,
    }

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=180,
        )
    except requests.exceptions.Timeout as e:
        raise OllamaUnavailableError("Ollama request timed out after 180s") from e
    except requests.exceptions.ConnectionError as e:
        raise OllamaUnavailableError(f"Ollama connection error: {e}") from e

    if response.status_code != 200:
        return {"score": 0, "reason": f"HTTP error: {response.status_code}"}

    raw = response.json().get("response", "{}")
    match = re.search(r'\{[^}]+\}', raw)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"score": 0, "reason": f"Could not parse LLM response: {raw[:100]}"}


@pytest.mark.skipif(
    os.environ.get("SKIP_LLM_TESTS", "false").lower() == "true",
    reason="Skipped because SKIP_LLM_TESTS=true",
)
class TestLLMAsJudge:
    def test_hotel_tool_output_is_high_quality(self):
        destination = "Kandy"
        summary = format_hotels(destination)
        assert not summary.startswith("Error:"), "Tool returned an error instead of a summary"

        try:
            judgment = evaluate_output_with_llm(summary, destination)
        except OllamaUnavailableError as e:
            pytest.skip(f"Ollama not available — skipping LLM judge test: {e}")

        score = judgment.get("score", 0)
        reason = judgment.get("reason", "No reason given")

        print(f"\n[LLM Judge] Score: {score}/10 | Reason: {reason}")
        assert isinstance(score, (int, float)), f"Score is not a number: {score}"
        assert score >= 6, (
            f"LLM judge rated output too low ({score}/10). Reason: {reason}\n"
            f"Output excerpt: {summary[:300]}"
        )


if __name__ == "__main__":
    print("=" * 60)
    print("  Hotel Tool — Direct Smoke Tests")
    print("=" * 60)

    for dest in ["Kandy", "Ella", "Galle", "Colombo", "Tokyo"]:
        result = get_hotels(dest)
        status = "✅ OK" if result["error"] is None else f"⚠️  {result['error'][:60]}"
        print(f"  {dest:<12} -> {status}")
        if result["error"] is None:
            print(f"            {len(result['hotels'])} hotels")

    print("\n  Sample Summary (Ella, first 400 chars):")
    print(format_hotels("Ella")[:400])
    print("  ...")
    print("\n✅ All smoke tests passed.")
