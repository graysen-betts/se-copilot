"""SE Co-Pilot Orchestrator — event-driven skill dispatch."""

from __future__ import annotations

from enum import Enum

from se_copilot.skills.call_prep import generate_call_prep


class TriggerType(str, Enum):
    STAGE_CHANGE = "stage_change"
    CALENDAR_EVENT = "calendar_event"
    DAILY_SWEEP = "daily_sweep"


STAGE_MATERIAL_MAP = {
    "S2": ["call_prep"],
    "S3": ["call_prep", "blueprint_acceleration"],
    "S4": ["call_prep", "blueprint_acceleration", "demo_plan"],
    "S5": ["call_prep", "blueprint_acceleration", "demo_plan", "sprint_success_criteria", "connector_docs", "architecture_diagram"],
    "S6": ["call_prep", "connector_docs", "architecture_diagram"],
}


def handle_trigger(trigger_type: TriggerType, account_ctx: dict) -> list[dict]:
    if trigger_type == TriggerType.CALENDAR_EVENT:
        return [generate_call_prep(account_ctx)]

    if trigger_type == TriggerType.STAGE_CHANGE:
        stage_code = account_ctx["opportunity"].get("stage_code", "S4")
        required = STAGE_MATERIAL_MAP.get(stage_code, [])
        results = []
        if "call_prep" in required:
            results.append(generate_call_prep(account_ctx))
        return results

    if trigger_type == TriggerType.DAILY_SWEEP:
        return [generate_call_prep(account_ctx)]

    return []


def format_slack_message(result: dict) -> str:
    confidence_tag = {
        "HIGH": "✅ HIGH",
        "CAVEATED": "⚠️ CAVEATED",
        "SKELETON": "🔴 SKELETON",
    }
    tag = confidence_tag.get(result["confidence"], result["confidence"])

    return (
        f"*{result['account_name']}* — SE Call Prep\n"
        f"Stage: {result['stage']} | Confidence: {tag}\n"
        f"_{result['confidence_reason']}_\n\n"
        f"{result['content']}"
    )
