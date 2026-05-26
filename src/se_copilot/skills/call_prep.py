"""SE Call Prep skill — layers technical depth on top of Sales Claw brief."""

from __future__ import annotations

import json
import os

import anthropic
from dotenv import load_dotenv

SYSTEM_PROMPT = """\
You are an SE Co-Pilot for Atlan, the Context Layer for AI. Your job is to generate \
a technical call prep for a Solutions Engineer before a customer meeting.

You are given:
1. The Sales Claw brief (AE-focused) — DO NOT duplicate this. Reference it briefly, then add SE depth.
2. Account context from Salesforce (stage, deal size, stakeholders, MEDDPICC).
3. Blueprint technology tab data (connectors, auth methods, gaps).
4. Blueprint success criteria (use cases, personas, measurements).
5. Deal Health Monitor scores (22-dimension scorecard, grade, red flags).
6. User interview summaries (persona-level friction points and "better world" views).
7. Upcoming meeting details (attendees, agenda).

Your output must be a structured SE call prep with these sections:

## Sales Claw Context (2-3 lines max)
One-line deal snapshot + reference that the AE has a separate brief.

## Meeting Attendees & What They Care About
For each attendee on the call: name, role, their specific pain points from interviews, \
and what Atlan feature matters most to them.

## Blueprint Status & Gaps
Tech tab completeness. Which connectors are documented, which have gaps. \
Specifically call out missing auth methods or connection details — these are blockers.

## Technical Talking Points
Persona-mapped, stage-appropriate. What to demo, discuss, or validate in THIS call. \
Be specific — not "discuss lineage" but "show column-level lineage from Snowflake \
through dbt to the Looker dashboard Elena uses for finance reporting."

## Outstanding SE Materials
What's overdue or needed for this account at its current stage. \
Reference the stage requirements (S2-S6).

## Suggested Questions to Fill Gaps
Specific questions the SE should ask in this call to close known gaps in the Blueprint \
or account understanding. Phrase them as actual questions, not descriptions.

## Deal Health Flags
Any yellow or red flags from Deal Health that the SE should be aware of. \
Recommended actions if relevant.

Rules:
- Be specific and actionable. Generic advice is useless.
- Reference actual data from the inputs — names, connector types, pain points.
- Never guess authentication methods — if missing, flag as a gap to ask about.
- Include a confidence assessment at the top: HIGH / CAVEATED / SKELETON with reason.
"""


def assess_confidence(ctx: dict) -> tuple[str, str]:
    has_sales_claw = bool(ctx.get("sales_claw_brief"))
    has_blueprint = bool(ctx.get("blueprint_tech_items"))
    has_interviews = bool(ctx.get("interview_summaries"))
    has_deal_health = bool(ctx.get("deal_health"))

    if has_sales_claw and has_blueprint and has_interviews and has_deal_health:
        return "HIGH", "Sales Claw brief + Blueprint data + interview summaries + Deal Health scores all available."
    if has_blueprint and (has_interviews or has_deal_health):
        return "CAVEATED", "Blueprint data present but some context sources missing."
    return "SKELETON", "Minimal data available — output will have significant gaps."


def build_user_prompt(ctx: dict) -> str:
    meeting = ctx["upcoming_meeting"]
    opp = ctx["opportunity"]
    account = ctx["account"]
    confidence, reason = assess_confidence(ctx)

    parts = [
        f"Generate an SE call prep for the following meeting.\n",
        f"**Confidence: {confidence}** — {reason}\n",
        f"## Meeting Details",
        f"Title: {meeting['title']}",
        f"Time: {meeting['start_time']}",
        f"Attendees: {', '.join(meeting['attendees'])}",
        f"Agenda: {meeting.get('description', 'No agenda provided')}\n",
        f"## Account & Opportunity",
        f"Account: {account['account_name']} ({account['industry']}, {account['employees']} employees)",
        f"Stage: {opp['stage']} (Day {opp['days_in_stage']} in stage)",
        f"ARR: ${opp['amount']:,}",
        f"Close Date: {opp['close_date']}",
        f"Owner: {opp['owner']}",
        f"Product Interest: {', '.join(opp['product_interest'])}",
    ]

    if opp.get("meddpicc"):
        parts.append("\n## MEDDPICC")
        for k, v in opp["meddpicc"].items():
            parts.append(f"- **{k.replace('_', ' ').title()}**: {v}")

    parts.append("\n## Contacts")
    for c in ctx.get("contacts", []):
        parts.append(
            f"- **{c['name']}** — {c['title']} ({c['role']})\n"
            f"  Last activity: {c['last_activity']}\n"
            f"  Notes: {c['notes']}"
        )

    if ctx.get("sales_claw_brief"):
        parts.append(f"\n## Sales Claw Brief (AE-focused — layer SE depth on top, do not duplicate)\n{ctx['sales_claw_brief']}")

    if ctx.get("blueprint_tech_items"):
        parts.append("\n## Blueprint Technology Tab")
        for item in ctx["blueprint_tech_items"]:
            gaps = []
            if not item.get("authentication_type"):
                gaps.append("AUTH METHOD MISSING")
            if not item.get("connection_method"):
                gaps.append("CONNECTION METHOD MISSING")
            gap_str = f" ⚠️ [{', '.join(gaps)}]" if gaps else ""
            parts.append(
                f"- **{item['name']}** ({item['category']}) — "
                f"Priority: {item['priority']}, "
                f"Auth: {item.get('authentication_type') or 'NOT CAPTURED'}, "
                f"POV Scope: {'Yes' if item.get('pov_scope') else 'No'}"
                f"{gap_str}"
            )

    if ctx.get("blueprint_success_criteria"):
        parts.append("\n## Blueprint Success Criteria")
        for sc in ctx["blueprint_success_criteria"]:
            parts.append(
                f"- **{sc['use_case']}** (Persona: {sc['persona']}, Priority: {sc['priority']})\n"
                f"  Feature: {sc['feature']}\n"
                f"  Measurement: {sc['measurement']}"
            )

    if ctx.get("deal_health"):
        dh = ctx["deal_health"]
        parts.append(f"\n## Deal Health Monitor ({dh['analysis_week']})")
        parts.append(f"Grade: {dh['overall_grade']} (Confidence: {dh['grade_confidence']})")
        parts.append(f"Key Red Flag: {dh['key_red_flag']}")
        parts.append(f"Recommended Actions: {dh['recommended_actions']}")
        parts.append(f"Week-over-Week: {dh['wow_changes']}")
        if dh.get("dimensions"):
            parts.append("\nDimension Highlights:")
            for dim, info in dh["dimensions"].items():
                if info["status"] in ("🟡 Weak Signal", "🔴 Failed", "⚪ No Evidence"):
                    parts.append(f"  - **{dim}**: {info['status']} — {info['commentary']}")

    if ctx.get("interview_summaries"):
        parts.append("\n## User Interview Summaries")
        for interview in ctx["interview_summaries"]:
            parts.append(f"- **{interview['interviewee']}** ({interview['date']}): {interview['summary']}")

    return "\n".join(parts)


def _get_client() -> anthropic.Anthropic:
    load_dotenv()
    base_url = os.environ.get("LITELLM_BASE_URL")
    api_key = os.environ.get("LITELLM_API_KEY")
    if base_url and api_key:
        return anthropic.Anthropic(base_url=base_url, api_key=api_key)
    return anthropic.Anthropic()


def generate_call_prep(ctx: dict, model: str = "claude-sonnet-4-6") -> dict:
    client = _get_client()
    user_prompt = build_user_prompt(ctx)
    confidence, reason = assess_confidence(ctx)

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return {
        "material_type": "se_call_prep",
        "account_name": ctx["account"]["account_name"],
        "stage": ctx["opportunity"]["stage"],
        "confidence": confidence,
        "confidence_reason": reason,
        "content": response.content[0].text,
        "model": model,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
