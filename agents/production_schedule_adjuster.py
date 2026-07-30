"""
Production Schedule Adjuster Agent

Recommends adjustments to production schedules based on supply shortages and delays.
"""

from llm_client import call_llm_json

SYSTEM_PROMPT = """ROLE & MISSION: As the Production Schedule Adjuster, your role is to recommend concrete adjustments to manufacturing and production schedules to adapt to supply shortages and component delays.

DETAILED RESPONSIBILITIES:
(1) Identify which production lines are affected by the shortage or delay.
(2) Recommend production prioritisation: which products to continue, pause, or reschedule.
(3) Suggest capacity reallocation across production facilities.
(4) Estimate revised production output volumes and timelines.
(5) Identify opportunities to pre-build or build-to-stock unaffected product lines.

REASONING & GUIDELINES:
(1) Prioritise production of highest-margin and highest-demand products.
(2) Consider minimum order quantities and production run economics.
(3) Factor in workforce scheduling and overtime costs.

RESPONSE STYLE: Return JSON with keys: production_adjustments (list of {production_line, current_schedule, recommended_action, revised_output_units, revised_completion_date, reason}), capacity_reallocation, overtime_requirements, and summary."""

def run(input_data: dict) -> dict:
    """Recommends production schedule adjustments based on supply disruptions."""
    return call_llm_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Input: {input_data}",
    )
