"""
Test Suite: Budget Agent & Cost Tool
====================================
Automated tests for the Budget Agent module of the Sri Lanka Travel Planner.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from tools.cost_tool import compare_budget_tiers, format_budget_summary, get_budget_breakdown


class TestGetBudgetBreakdown:
    def test_valid_destination_returns_breakdown(self):
        result = get_budget_breakdown("Kandy", 2, "standard")
        assert result["error"] is None
        assert result["destination"] == "Kandy"
        assert result["days"] == 2
        assert result["total_cost_usd"] > 0

    def test_case_insensitive_lookup(self):
        result = get_budget_breakdown("ella", 3, "budget")
        assert result["error"] is None
        assert result["destination"] == "Ella"

    def test_invalid_destination_returns_error(self):
        result = get_budget_breakdown("Tokyo", 2, "standard")
        assert result["error"] is not None

    @pytest.mark.parametrize("days", [0, -1])
    def test_invalid_days_return_error(self, days: int):
        result = get_budget_breakdown("Galle", days, "standard")
        assert result["error"] is not None

    def test_invalid_tier_returns_error(self):
        result = get_budget_breakdown("Colombo", 2, "vip")
        assert result["error"] is not None

    def test_total_matches_sum_of_components(self):
        result = get_budget_breakdown("Ella", 3, "standard")
        subtotal = (
            result["accommodation_cost_usd"]
            + result["meal_cost_usd"]
            + result["local_transport_cost_usd"]
            + result["attraction_fees_usd"]
        )
        assert round(subtotal + result["contingency_cost_usd"], 2) == result["total_cost_usd"]


class TestCompareBudgetTiers:
    def test_compare_returns_all_tiers(self):
        result = compare_budget_tiers("Kandy", 2)
        assert result["error"] is None
        assert set(result["tiers"].keys()) == {"budget", "standard", "premium"}

    def test_costs_increase_across_tiers(self):
        result = compare_budget_tiers("Ella", 3)
        budget_total = result["tiers"]["budget"]["total_cost_usd"]
        standard_total = result["tiers"]["standard"]["total_cost_usd"]
        premium_total = result["tiers"]["premium"]["total_cost_usd"]
        assert budget_total <= standard_total <= premium_total


class TestFormatBudgetSummary:
    def test_summary_contains_destination(self):
        summary = format_budget_summary("Galle", 4)
        assert "Budget Estimate for Galle" in summary

    def test_summary_contains_required_sections(self):
        summary = format_budget_summary("Colombo", 2)
        assert "## Budget Option" in summary
        assert "## Standard Option" in summary
        assert "## Premium Option" in summary
        assert "## Assumptions" in summary

    def test_summary_returns_error_message_for_invalid_destination(self):
        summary = format_budget_summary("UnknownCity", 2)
        assert summary.startswith("Error:")
