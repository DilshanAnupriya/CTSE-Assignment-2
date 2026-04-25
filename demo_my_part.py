"""
=============================================================================
  DEMO: Budget Agent & Cost Tool
  Author: Vidura Hewaduwa (Budget Agent Module)
  Assignment: CTSE - Multi-Agent System (MAS) - Sri Lanka Travel Planner
=============================================================================

Run this file to demonstrate the Budget Agent module:
    python demo_my_part.py
"""

import logging
import os
import sys
import time

logging.disable(logging.CRITICAL)

sys.path.insert(0, os.path.abspath("src"))

from tools.cost_tool import compare_budget_tiers, format_budget_summary, get_budget_breakdown


def divider(title: str = ""):
    print("\n" + "=" * 65)
    if title:
        print(f"  {title}")
        print("=" * 65)


def pause(msg: str = ""):
    if msg:
        print(f"\n  >>> {msg}")
    time.sleep(0.4)


def main():
    print()
    print("=" * 65)
    print("   BUDGET AGENT - LIVE DEMO")
    print("   Author : Vidura Hewaduwa")
    print("   Module : Budget Agent & Cost Tool")
    print("   MAS    : Sri Lanka Travel Planner (CrewAI + Ollama)")
    print("=" * 65)

    divider("STEP 1 - Standard Budget Breakdown")
    result = get_budget_breakdown("Ella", 3, "standard")
    print(f"  Destination      : {result['destination']}")
    print(f"  Days             : {result['days']}")
    print(f"  Tier             : {result['tier']}")
    print(f"  Accommodation    : ${result['accommodation_cost_usd']:.2f}")
    print(f"  Meals            : ${result['meal_cost_usd']:.2f}")
    print(f"  Local transport  : ${result['local_transport_cost_usd']:.2f}")
    print(f"  Entry fees       : ${result['attraction_fees_usd']:.2f}")
    print(f"  Contingency      : ${result['contingency_cost_usd']:.2f}")
    print(f"  Total            : ${result['total_cost_usd']:.2f}")
    pause("Budget breakdown verified using local dataset-backed hotel and activity pricing.")

    divider("STEP 2 - Tier Comparison")
    comparison = compare_budget_tiers("Kandy", 2)
    for tier in ("budget", "standard", "premium"):
        tier_result = comparison["tiers"][tier]
        print(f"  {tier.title():<9}: ${tier_result['total_cost_usd']:.2f}")
    pause("The tool compares budget, standard, and premium trip options cleanly.")

    divider("STEP 3 - Error Handling")
    bad_destination = get_budget_breakdown("Tokyo", 3, "standard")
    bad_days = get_budget_breakdown("Ella", 0, "standard")
    print(f"  Unknown destination error : {bad_destination['error']}")
    print(f"  Invalid days error        : {bad_days['error']}")
    pause("Invalid inputs are handled safely without crashing.")

    divider("STEP 4 - Agent-Ready Summary")
    summary = format_budget_summary("Galle", 4)
    print(summary[:1000])
    print("  ... [truncated for demo]")
    pause("This is the formatted output the Budget Agent can use inside the CrewAI pipeline.")

    divider("STEP 5 - Running Budget Tests")
    print(f"  Command: {sys.executable} -m pytest tests/test_budget_agent.py -q")
    print()
    os.system(f'"{sys.executable}" -m pytest tests/test_budget_agent.py -q')

    divider("DEMO COMPLETE")
    print("  MY CONTRIBUTION SUMMARY:")
    print()
    print("  1. AGENT  : src/agents/budget_agent.py")
    print("              -> Travel Budget Analyst")
    print("              -> 3 CrewAI tool wrappers attached")
    print()
    print("  2. TOOL   : src/tools/cost_tool.py")
    print("              -> Dataset-backed cost calculations")
    print("              -> Budget tier comparison")
    print("              -> Formatted budget summary")
    print()
    print("  3. TASK   : src/tasks/budget_task.py")
    print("              -> Strict budgeting-only task prompt")
    print("              -> No overlap with itinerary, hotel, or report modules")
    print()
    print("  4. TESTS  : tests/test_budget_agent.py")
    print("              -> Validates totals, tiers, formatting, and error handling")
    print("=" * 65)


if __name__ == "__main__":
    main()
