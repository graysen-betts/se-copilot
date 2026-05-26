"""Sample account data mimicking Snowflake tables for demo purposes.

In production, these would be queries against:
- LANDING.SALESFORCE.OPPORTUNITY / ACCOUNT / CONTACT
- BLUEPRINT.EXTRACTOR.TECH_ITEMS
- BLUEPRINT.EXTRACTOR.SUCCESS_CRITERIA
- SALES_DB.PIPELINE.DEAL_HEALTH_MONITORING
"""

from __future__ import annotations

SAMPLE_ACCOUNT = {
    "account_id": "001ABC123",
    "account_name": "NovaTech Financial",
    "industry": "Financial Services",
    "employees": 4500,
    "arr_potential": 220_000,
}

SAMPLE_OPPORTUNITY = {
    "opp_id": "006OPP456",
    "account_id": "001ABC123",
    "name": "NovaTech Financial - Context Layer - New Business",
    "stage": "4 - Why Atlan?",
    "stage_code": "S4",
    "amount": 220_000,
    "close_date": "2026-07-31",
    "created_date": "2026-03-15",
    "days_in_stage": 18,
    "type": "New Business",
    "owner": "Graysen Betts",
    "sales_pod": "East",
    "product_interest": ["Data Governance", "Lineage", "AI Context Layer"],
    "meddpicc": {
        "identify_pain": "Data teams spend 30% of time finding and trusting data. No single source of truth for metric definitions.",
        "champion": "Priya Nair (Head of Data Engineering) — strong internal advocate, demoed Atlan to her VP",
        "economic_buyer": "Marcus Cole (VP Data & Analytics) — confirmed budget holder, met twice",
        "decision_criteria": "Must integrate with Snowflake + dbt + Looker stack. SSO required. SOC2 compliance.",
        "decision_process": "Technical eval → POV → Security review → VP sign-off → Procurement (6-8 weeks)",
        "compelling_event": "Board mandate: AI readiness initiative by Q3 2026. Need governed data foundation first.",
    },
}

SAMPLE_CONTACTS = [
    {
        "name": "Priya Nair",
        "title": "Head of Data Engineering",
        "role": "Technical Champion",
        "persona": "Data Engineer",
        "email": "priya.nair@novatech.example.com",
        "last_activity": "2026-05-20 — attended tailored demo, asked detailed lineage questions",
        "notes": "Very engaged. Wants column-level lineage across Snowflake → dbt → Looker. Concerned about PII classification for GDPR compliance.",
    },
    {
        "name": "Marcus Cole",
        "title": "VP Data & Analytics",
        "role": "Economic Buyer",
        "persona": "Executive",
        "email": "marcus.cole@novatech.example.com",
        "last_activity": "2026-05-15 — exec alignment meeting",
        "notes": "Focused on time-to-value and ROI. Wants to see governance automation reducing manual audit prep from weeks to days. Board is pushing AI readiness.",
    },
    {
        "name": "Jordan Liu",
        "title": "Data Governance Lead",
        "role": "Governance Champion",
        "persona": "Governance Lead",
        "email": "jordan.liu@novatech.example.com",
        "last_activity": "2026-05-22 — user interview completed",
        "notes": "Currently managing governance in spreadsheets. Wants automated PII tagging, policy enforcement, and audit trails. Key pain: manual classification of 2000+ tables.",
    },
    {
        "name": "Elena Vasquez",
        "title": "Senior Analytics Engineer",
        "role": "Technical Evaluator",
        "persona": "Analytics Engineer",
        "email": "elena.vasquez@novatech.example.com",
        "last_activity": "2026-05-18 — user interview completed",
        "notes": "Runs dbt models, builds Looker dashboards. Pain: no visibility into upstream changes breaking her models. Wants lineage + impact analysis.",
    },
]

SAMPLE_BLUEPRINT_TECH_ITEMS = [
    {
        "name": "Snowflake",
        "category": "Data Warehouse",
        "hosting_type": "Cloud (AWS)",
        "authentication_type": "Key-pair",
        "connection_method": "Direct",
        "private_networking": False,
        "pov_scope": True,
        "priority": "P0",
        "validation_status": "Validated",
        "volume_estimate": "~800 tables, 15K columns, 2TB",
    },
    {
        "name": "dbt Cloud",
        "category": "Transformation",
        "hosting_type": "Cloud",
        "authentication_type": "API Token",
        "connection_method": "API",
        "private_networking": False,
        "pov_scope": True,
        "priority": "P0",
        "validation_status": "Validated",
        "volume_estimate": "~200 models",
    },
    {
        "name": "Looker",
        "category": "BI / Visualization",
        "hosting_type": "Cloud (GCP)",
        "authentication_type": None,  # Gap — not yet captured
        "connection_method": None,  # Gap — not yet captured
        "private_networking": None,
        "pov_scope": True,
        "priority": "P1",
        "validation_status": "Pending",
        "volume_estimate": "~50 dashboards, ~120 explores",
    },
    {
        "name": "Postgres (Application DB)",
        "category": "Operational Database",
        "hosting_type": "Cloud (AWS RDS)",
        "authentication_type": None,  # Gap
        "connection_method": None,  # Gap
        "private_networking": None,
        "pov_scope": False,
        "priority": "P2",
        "validation_status": "Not Started",
        "volume_estimate": "Unknown",
    },
]

SAMPLE_BLUEPRINT_SUCCESS_CRITERIA = [
    {
        "use_case": "Data Discovery & Trust",
        "persona": "Analytics Engineer",
        "feature": "Search + Asset 360 + Lineage",
        "measurement": "Time to find trusted data < 5 minutes (from current ~45 min)",
        "priority": "High",
        "outcome": "Self-serve data discovery for analytics team",
    },
    {
        "use_case": "PII Governance & Compliance",
        "persona": "Data Governance Lead",
        "feature": "Auto-classification + Playbooks + Audit Trail",
        "measurement": "80% of PII columns auto-classified within 30 days",
        "priority": "High",
        "outcome": "Automated GDPR compliance reporting",
    },
    {
        "use_case": "Impact Analysis",
        "persona": "Data Engineer",
        "feature": "Column-level lineage across Snowflake → dbt → Looker",
        "measurement": "Zero broken dashboards from unannounced upstream changes",
        "priority": "Medium",
        "outcome": "Proactive change management for data pipelines",
    },
]

SAMPLE_DEAL_HEALTH = {
    "analysis_week": "W21 2026",
    "overall_grade": "🟢 Green",
    "grade_confidence": "High",
    "deal_type": "Greenfield",
    "driver": "Prospect-driven",
    "key_red_flag": "Looker connector auth method not captured in Blueprint — potential blocker for full lineage POV",
    "recommended_actions": "1. Capture Looker auth method and connection details before next technical call. 2. Schedule security review kickoff — procurement timeline is 6-8 weeks.",
    "wow_changes": "New this week: Jordan Liu user interview completed (governance lead). Strong governance pain confirmed. POV success criteria now documented.",
    "dimensions": {
        "icp_fit": {"status": "🟢 Strong Signal", "commentary": "4500-person financial services company with active governance mandate and board-level AI initiative."},
        "tech_stack_fit": {"status": "🟢 Strong Signal", "commentary": "Snowflake + dbt + Looker is a core Atlan stack. All connectors supported."},
        "use_case_fit": {"status": "🟢 Strong Signal", "commentary": "Governance, lineage, and AI readiness align to top Atlan value drivers."},
        "governance_maturity": {"status": "🟡 Weak Signal", "commentary": "Dedicated governance lead (Jordan Liu) but currently managing in spreadsheets. No formal program yet."},
        "champion": {"status": "🟢 Strong Signal", "commentary": "Priya Nair actively advocating internally. Demoed Atlan to her VP."},
        "eb_engagement": {"status": "🟢 Strong Signal", "commentary": "Marcus Cole (VP) met twice. Budget confirmed. Board-level AI mandate creates urgency."},
        "sales_execution": {"status": "🟢 Strong Signal", "commentary": "User interviews on track (2/3 complete). Tailored demo delivered. Blueprint 70% complete."},
        "pov_experience": {"status": "⚪ No Evidence", "commentary": "POV not yet started — currently in evaluation stage."},
    },
}

SAMPLE_SALES_CLAW_BRIEF = """Pre-call brief: NovaTech Financial — Technical Deep-Dive at 2:00pm

Stage: 4 - Why Atlan? | ARR: $220K | Close: July 31
Champion: Priya Nair (Head of Data Engineering) | EB: Marcus Cole (VP D&A) — confirmed
Tech stack: Snowflake, dbt Cloud, Looker, Postgres | Blueprint coverage: 70%

Last call (May 20): Tailored demo focused on lineage and governance. Priya loved column-level lineage across dbt models. Jordan Liu (Governance Lead) asked about automated PII classification — we showed playbooks.

Deal health: 🟢 Green (W21) | Key flag: Looker connector details not in Blueprint
MEDDPICC: Pain identified (manual data discovery + compliance). Champion strong. EB engaged. Decision process mapped. Compelling event: board AI mandate Q3 2026.

Suggested focus today:
- Capture Looker auth method and connection details — needed for Blueprint + full lineage POV
- Discuss POV kickoff timeline and success criteria validation with Priya
- Float security review scheduling — 6-8 week procurement, need to start now for July close
"""

SAMPLE_INTERVIEW_SUMMARIES = [
    {
        "interviewee": "Jordan Liu — Data Governance Lead",
        "date": "2026-05-22",
        "summary": (
            "What we heard: Jordan manages governance for ~2000 tables across Snowflake using "
            "spreadsheets and manual processes. Classification takes 2-3 weeks per audit cycle. "
            "Key friction: no automated PII detection, no audit trail, policy enforcement is "
            "tribal knowledge. Better world: automated classification, playbook-driven governance, "
            "audit-ready compliance reports on demand. Jordan is the internal owner of the GDPR "
            "compliance program and reports directly to Marcus Cole."
        ),
    },
    {
        "interviewee": "Elena Vasquez — Senior Analytics Engineer",
        "date": "2026-05-18",
        "summary": (
            "What we heard: Elena builds dbt models and Looker dashboards for the finance team. "
            "Spends ~40% of time on data discovery — finding the right table, understanding "
            "upstream dependencies, verifying if data is trustworthy. Key friction: upstream "
            "Snowflake schema changes break her dbt models with no warning. No column-level "
            "lineage visibility. Better world: search that finds trusted data in minutes, "
            "lineage that shows impact before changes ship, notifications when upstream "
            "changes affect her models."
        ),
    },
]

UPCOMING_MEETING = {
    "title": "NovaTech Financial — Technical Deep-Dive",
    "start_time": "2026-05-27T14:00:00",
    "duration_minutes": 60,
    "attendees": [
        "Priya Nair <priya.nair@novatech.example.com>",
        "Elena Vasquez <elena.vasquez@novatech.example.com>",
        "Graysen Betts <graysen.betts@atlan.com>",
    ],
    "location": "Zoom",
    "description": "Technical deep-dive on Atlan lineage and governance capabilities. Follow-up from May 20 demo.",
}


def get_account_context() -> dict:
    return {
        "account": SAMPLE_ACCOUNT,
        "opportunity": SAMPLE_OPPORTUNITY,
        "contacts": SAMPLE_CONTACTS,
        "blueprint_tech_items": SAMPLE_BLUEPRINT_TECH_ITEMS,
        "blueprint_success_criteria": SAMPLE_BLUEPRINT_SUCCESS_CRITERIA,
        "deal_health": SAMPLE_DEAL_HEALTH,
        "sales_claw_brief": SAMPLE_SALES_CLAW_BRIEF,
        "interview_summaries": SAMPLE_INTERVIEW_SUMMARIES,
        "upcoming_meeting": UPCOMING_MEETING,
    }
