"""SE Co-Pilot Orchestrator — event-driven skill dispatch."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import anthropic


class Stage(str, Enum):
    S2 = "S2"  # Why Change?
    S3 = "S3"  # Why Now?
    S4 = "S4"  # Why Atlan?
    S5 = "S5"  # Selection
    S6 = "S6"  # Contract
    POST_SALE = "POST_SALE"


class MaterialType(str, Enum):
    CALL_PREP = "call_prep"
    BLUEPRINT_ACCELERATION = "blueprint_acceleration"
    DEMO_PLAN = "demo_plan"
    SPRINT_SUCCESS_CRITERIA = "sprint_success_criteria"
    CONNECTOR_DOCS = "connector_docs"
    ARCHITECTURE_DIAGRAM = "architecture_diagram"


class Confidence(str, Enum):
    HIGH = "high"
    CAVEATED = "caveated"
    SKELETON = "skeleton"


STAGE_REQUIRED_MATERIALS: dict[Stage, list[MaterialType]] = {
    Stage.S2: [
        MaterialType.CALL_PREP,
    ],
    Stage.S3: [
        MaterialType.CALL_PREP,
        MaterialType.BLUEPRINT_ACCELERATION,
    ],
    Stage.S4: [
        MaterialType.CALL_PREP,
        MaterialType.BLUEPRINT_ACCELERATION,
        MaterialType.DEMO_PLAN,
    ],
    Stage.S5: [
        MaterialType.CALL_PREP,
        MaterialType.BLUEPRINT_ACCELERATION,
        MaterialType.DEMO_PLAN,
        MaterialType.SPRINT_SUCCESS_CRITERIA,
        MaterialType.CONNECTOR_DOCS,
        MaterialType.ARCHITECTURE_DIAGRAM,
    ],
    Stage.S6: [
        MaterialType.CALL_PREP,
        MaterialType.CONNECTOR_DOCS,
        MaterialType.ARCHITECTURE_DIAGRAM,
    ],
}

STALENESS_THRESHOLDS = {
    "snowflake": 12 * 3600,
    "atlan": 24 * 3600,
    "atlan_arch_diagram": 48 * 3600,
    "blueprint": None,
}


@dataclass
class AccountContext:
    account_id: str
    account_name: str
    stage: Stage
    deal_size: float
    close_date: str
    stakeholders: list[dict[str, str]]
    product_interest: list[str]
    last_activity_notes: str | None = None
    blueprint_tech_tab: dict[str, Any] | None = None
    blueprint_success_criteria: list[dict[str, Any]] = field(default_factory=list)
    atlan_tenant: str | None = None
    atlan_connectors: list[dict[str, Any]] = field(default_factory=list)
    has_governance_tags: bool = False
    has_lineage: bool = False
    interview_summaries: list[str] = field(default_factory=list)
    data_freshness: dict[str, float] = field(default_factory=dict)
    deal_health: dict[str, Any] | None = None  # from DEAL_HEALTH_MONITORING
    sales_claw_brief: str | None = None  # from Sales Claw output


@dataclass
class MaterialResult:
    material_type: MaterialType
    account_id: str
    confidence: Confidence
    content: str
    gaps: list[str] = field(default_factory=list)
    staleness_warnings: list[str] = field(default_factory=list)
    suggested_next_steps: list[str] = field(default_factory=list)


@dataclass
class TriggerEvent:
    event_type: str  # "stage_change" | "calendar_event" | "daily_sweep"
    account_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


def infer_maturity(ctx: AccountContext) -> str:
    if not ctx.atlan_tenant or not ctx.atlan_connectors:
        return "net_new"
    has_ingested = any(
        c.get("ingested_assets", 0) > 0 for c in ctx.atlan_connectors
    )
    if not has_ingested:
        return "net_new"
    if ctx.has_governance_tags and ctx.has_lineage:
        return "mature_expansion"
    return "expansion"


def check_staleness(ctx: AccountContext, material_type: MaterialType) -> list[str]:
    warnings = []
    now = time.time()
    for source, threshold in STALENESS_THRESHOLDS.items():
        if threshold is None:
            continue
        if source == "atlan_arch_diagram" and material_type != MaterialType.ARCHITECTURE_DIAGRAM:
            continue
        if source == "atlan" and material_type == MaterialType.ARCHITECTURE_DIAGRAM:
            source = "atlan_arch_diagram"
            threshold = STALENESS_THRESHOLDS["atlan_arch_diagram"]

        last_sync = ctx.data_freshness.get(source.replace("_arch_diagram", ""), 0)
        if last_sync and (now - last_sync) > threshold:
            hours_stale = int((now - last_sync) / 3600)
            warnings.append(
                f"{source} data is {hours_stale}h old (threshold: {threshold // 3600}h)"
            )
    return warnings


def check_stage_readiness(ctx: AccountContext) -> list[dict[str, Any]]:
    """Return list of missing materials for the account's current stage."""
    required = STAGE_REQUIRED_MATERIALS.get(ctx.stage, [])
    # In production, check account_state store for existing materials.
    # For now, return all required materials as needing generation.
    return [{"material_type": m, "account_id": ctx.account_id} for m in required]


def prioritize_accounts(accounts: list[AccountContext]) -> list[AccountContext]:
    stage_order = {Stage.S6: 0, Stage.S5: 1, Stage.S4: 2, Stage.S3: 3, Stage.S2: 4, Stage.POST_SALE: 5}
    return sorted(accounts, key=lambda a: (stage_order.get(a.stage, 9), -a.deal_size))


class SECoPilot:
    def __init__(self, anthropic_client: anthropic.Anthropic | None = None):
        self.client = anthropic_client or anthropic.Anthropic()
        self.model = "claude-sonnet-4-6"
        self.skills: dict[MaterialType, str] = {
            MaterialType.CALL_PREP: "skills/call_prep/SKILL.md",
            MaterialType.BLUEPRINT_ACCELERATION: "skills/blueprint_accelerator/SKILL.md",
            MaterialType.DEMO_PLAN: "skills/demo_planner/SKILL.md",
            MaterialType.SPRINT_SUCCESS_CRITERIA: "skills/sprint_success_criteria/SKILL.md",
            MaterialType.CONNECTOR_DOCS: "skills/connector_docs/SKILL.md",
            MaterialType.ARCHITECTURE_DIAGRAM: "skills/architecture_diagram/SKILL.md",
        }

    def handle_trigger(self, event: TriggerEvent, accounts: list[AccountContext]) -> list[MaterialResult]:
        if event.event_type == "stage_change":
            target = [a for a in accounts if a.account_id == event.account_id]
            return self._process_accounts(target)

        if event.event_type == "calendar_event":
            target = [a for a in accounts if a.account_id == event.account_id]
            return self._generate_call_prep(target)

        if event.event_type == "daily_sweep":
            ordered = prioritize_accounts(accounts)
            return self._process_accounts(ordered)

        return []

    def _process_accounts(self, accounts: list[AccountContext]) -> list[MaterialResult]:
        results = []
        for ctx in accounts:
            missing = check_stage_readiness(ctx)
            for item in missing:
                result = self._generate_material(ctx, item["material_type"])
                results.append(result)
        return results

    def _generate_call_prep(self, accounts: list[AccountContext]) -> list[MaterialResult]:
        return [
            self._generate_material(ctx, MaterialType.CALL_PREP) for ctx in accounts
        ]

    def _generate_material(self, ctx: AccountContext, material_type: MaterialType) -> MaterialResult:
        staleness = check_staleness(ctx, material_type)
        maturity = infer_maturity(ctx)

        prompt = self._build_prompt(ctx, material_type, maturity, staleness)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text
        confidence = self._assess_confidence(ctx, material_type)
        gaps = self._identify_gaps(ctx, material_type)

        return MaterialResult(
            material_type=material_type,
            account_id=ctx.account_id,
            confidence=confidence,
            content=content,
            gaps=gaps,
            staleness_warnings=staleness,
            suggested_next_steps=self._suggest_next_steps(gaps, ctx),
        )

    def _build_prompt(
        self,
        ctx: AccountContext,
        material_type: MaterialType,
        maturity: str,
        staleness: list[str],
    ) -> str:
        base = (
            f"Generate a {material_type.value} for account '{ctx.account_name}' "
            f"(stage: {ctx.stage.value}, deal size: ${ctx.deal_size:,.0f}).\n\n"
        )

        if ctx.stakeholders:
            base += "Stakeholders:\n"
            for s in ctx.stakeholders:
                base += f"- {s.get('name', 'Unknown')}: {s.get('role', 'Unknown')}\n"

        if ctx.blueprint_tech_tab:
            base += f"\nBlueprint technology tab:\n{json.dumps(ctx.blueprint_tech_tab, indent=2)}\n"

        if ctx.atlan_connectors:
            base += f"\nAtlan connectors ({maturity} customer):\n{json.dumps(ctx.atlan_connectors, indent=2)}\n"

        if ctx.last_activity_notes:
            base += f"\nLast activity notes:\n{ctx.last_activity_notes}\n"

        if ctx.interview_summaries:
            base += f"\nUser interview summaries:\n"
            for i, s in enumerate(ctx.interview_summaries, 1):
                base += f"\n--- Interview {i} ---\n{s}\n"

        if ctx.deal_health:
            grade = ctx.deal_health.get("overall_grade", "Unknown")
            red_flag = ctx.deal_health.get("key_red_flag", "None")
            week = ctx.deal_health.get("analysis_week", "Unknown")
            base += (
                f"\nDeal Health Monitor ({week}):\n"
                f"  Grade: {grade}\n"
                f"  Key red flag: {red_flag}\n"
            )
            if ctx.deal_health.get("recommended_actions"):
                base += f"  Recommended actions: {ctx.deal_health['recommended_actions']}\n"

        if ctx.sales_claw_brief and material_type == MaterialType.CALL_PREP:
            base += (
                f"\nSales Claw brief (AE-focused — layer SE technical depth on top, "
                f"do not duplicate):\n{ctx.sales_claw_brief}\n"
            )

        if staleness:
            base += f"\nDATA FRESHNESS WARNINGS:\n"
            for w in staleness:
                base += f"- {w}\n"
            base += "Include these warnings in your output.\n"

        # Skill-specific instructions loaded from SKILL.md in production
        base += self._get_skill_instructions(material_type, maturity)

        return base

    def _get_skill_instructions(self, material_type: MaterialType, maturity: str) -> str:
        """In production, load from SKILL.md files. Inline for scaffold."""
        instructions = {
            MaterialType.CALL_PREP: (
                "\nProduce a structured one-pager with: attendees and roles, "
                "pipeline position, last discussion summary, pain points by persona, "
                "outstanding materials, and suggested talking points for the current stage. "
                "80% accuracy is acceptable — the SE will fill gaps."
            ),
            MaterialType.BLUEPRINT_ACCELERATION: (
                "\nReview the Blueprint technology tab. Identify incomplete fields. "
                "If Atlan metadata is available, pre-populate connector fields and mark "
                "them as 'pre-populated from Atlan — SE please validate'. "
                "For each missing field, suggest a specific question for the SE to ask "
                "in their next customer call. Never guess authentication methods."
            ),
            MaterialType.DEMO_PLAN: (
                "\nRecommend Atlan features to demo based on customer personas and pain points. "
                "Map each recommendation to a specific persona and their stated challenge. "
                "If no user interview summaries exist, flag this gap and generate a generic "
                "plan based on deal context, clearly marked as incomplete."
            ),
            MaterialType.SPRINT_SUCCESS_CRITERIA: (
                f"\nCustomer maturity: {maturity}. "
                "Generate concrete, measurable success criteria for Sprint 1. "
                "Tie each criterion to a stated use case. "
                "Net-new: foundational (connector setup, glossary, initial lineage). "
                "Expansion: advanced (new connectors, deeper governance, playbooks). "
                "Mature expansion: optimization (automation, advanced lineage, compliance). "
                "Use best-practice templates as enrichment, not as the primary source."
            ),
            MaterialType.CONNECTOR_DOCS: (
                "\nGenerate connector setup documentation. "
                "Source of truth: Blueprint technology tab. "
                "Cross-reference with Atlan metadata if available. "
                "NEVER guess authentication methods — flag as unknown if not in Blueprint. "
                "If insufficient data, produce a skeleton with clearly marked placeholders."
            ),
            MaterialType.ARCHITECTURE_DIAGRAM: (
                "\nGenerate a production architecture diagram description. "
                "Primary sources: Blueprint tech tab + Atlan lineage. "
                "CRITICAL: Never generate a confident-looking diagram from insufficient data. "
                "If data is partial, produce a skeleton with explicit placeholders and list "
                "exactly what data is missing. Recommend re-validation with customer "
                "before any sign-off."
            ),
        }
        return instructions.get(material_type, "")

    def _assess_confidence(self, ctx: AccountContext, material_type: MaterialType) -> Confidence:
        has_blueprint = bool(ctx.blueprint_tech_tab)
        has_atlan = bool(ctx.atlan_connectors)

        if material_type == MaterialType.ARCHITECTURE_DIAGRAM:
            if has_blueprint and has_atlan:
                return Confidence.HIGH
            if has_blueprint or has_atlan:
                return Confidence.CAVEATED
            return Confidence.SKELETON

        if material_type == MaterialType.CONNECTOR_DOCS:
            if has_blueprint:
                return Confidence.HIGH
            if has_atlan:
                return Confidence.CAVEATED
            return Confidence.SKELETON

        if material_type in (MaterialType.CALL_PREP, MaterialType.DEMO_PLAN):
            return Confidence.HIGH if ctx.last_activity_notes else Confidence.CAVEATED

        return Confidence.HIGH

    def _identify_gaps(self, ctx: AccountContext, material_type: MaterialType) -> list[str]:
        gaps = []

        if material_type == MaterialType.DEMO_PLAN and not ctx.interview_summaries:
            gaps.append(
                "No user interview summaries found. Process requires 3+ interviews "
                "before POV kickoff. Demo plan is generic until interviews are documented."
            )

        if material_type in (MaterialType.CONNECTOR_DOCS, MaterialType.ARCHITECTURE_DIAGRAM):
            if not ctx.blueprint_tech_tab:
                gaps.append("Blueprint technology tab is empty — cannot generate confident technical docs.")
            if not ctx.atlan_connectors:
                gaps.append(
                    "No Atlan metadata available. Requires ATLAN_API_KEY for home.atlan.com "
                    "(not yet provisioned)."
                )

        if material_type == MaterialType.BLUEPRINT_ACCELERATION and not ctx.atlan_connectors:
            gaps.append(
                "Cannot pre-populate Blueprint from Atlan — no tenant metadata available. "
                "SE must fill manually until Atlan credentials are provisioned."
            )

        return gaps

    def _suggest_next_steps(self, gaps: list[str], ctx: AccountContext) -> list[str]:
        steps = []
        for gap in gaps:
            if "interview" in gap.lower():
                steps.append(
                    "Schedule user interviews with technical personas "
                    "(data engineers, architects, governance leads)."
                )
            if "blueprint" in gap.lower() and "empty" in gap.lower():
                steps.append(
                    f"Complete Blueprint technology tab for {ctx.account_name} — "
                    "ask about connector types, auth methods, and volume in next discovery call."
                )
            if "atlan" in gap.lower() and "credential" in gap.lower():
                steps.append(
                    "Provision ATLAN_API_KEY for home.atlan.com with read scope "
                    "(connector inventory, metadata, lineage, glossary, governance tags)."
                )
        return steps

    def format_slack_message(self, result: MaterialResult, account_name: str) -> str:
        confidence_emoji = {
            Confidence.HIGH: "[HIGH]",
            Confidence.CAVEATED: "[CAVEATED]",
            Confidence.SKELETON: "[SKELETON]",
        }

        msg = (
            f"*{account_name}* — {result.material_type.value}\n"
            f"Confidence: {confidence_emoji[result.confidence]}\n\n"
        )

        if result.staleness_warnings:
            msg += "Data freshness warnings:\n"
            for w in result.staleness_warnings:
                msg += f"  - {w}\n"
            msg += "\n"

        msg += result.content + "\n"

        if result.gaps:
            msg += "\n*Gaps:*\n"
            for g in result.gaps:
                msg += f"  - {g}\n"

        if result.suggested_next_steps:
            msg += "\n*Suggested next steps:*\n"
            for s in result.suggested_next_steps:
                msg += f"  - {s}\n"

        return msg
