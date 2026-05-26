# SE Co-Pilot — Design Rationale

## Workload Classification

| Axis | Classification | Rationale |
|------|---------------|-----------|
| **Interaction shape** | Event-driven batch | Three triggers (stage change, calendar, cron) each produce a batch of materials. No real-time conversation loop. |
| **Decision complexity** | Low-medium | Decisions are rule-based (stage → required materials, fallback priority order). The only inference is maturity detection from Atlan tenant state. |
| **Data intensity** | Medium | Reads from 4-5 data sources per run, but queries are scoped to single accounts. No large-scale aggregation. |

## Composing with existing systems

### Deal Health Monitor (consume, don't rebuild)

A 22-dimension weekly deal health scorecard already runs in Snowflake Cortex (`SALES_DB.PIPELINE.DEAL_HEALTH_MONITORING`). It scores qualification, stakeholder engagement, competitive position, commercial alignment, sales execution, and deal timing for every active New Business opportunity in S2–S6. It runs every Sunday at 7 PM EST.

**What we consume:** Overall deal grade (Green/Yellow/Red), key red flag, recommended actions, dimension-level scores (especially Sales Execution Quality, Tech Stack Fit, POV Experience), and week-over-week changes.

**What we add:** SE-specific material readiness. Deal Health doesn't know whether the Blueprint tech tab is complete, whether connector docs exist, or whether an architecture diagram has been signed off. That's our layer.

### Sales Claw (extend, don't duplicate)

Sales Claw already generates pre-call briefs for AEs using Google Calendar + Salesforce + Gong + Glean + Snowflake (Blueprint tech, Deal Health). It DMs the AE before every external meeting with: account snapshot, prior call summary, persona-specific failure modes, tailored discovery questions, competitive context, and a walk-away goal.

**What we read:** The Sales Claw brief for the same account/meeting.

**What we add:** SE technical depth layered on top — Blueprint completeness status, connector gaps, architecture readiness, persona-specific technical talking points, and outstanding SE-owned materials. The SE gets a brief that complements what the AE sees, not a separate parallel document.

## Why S2–S6 (not S3–S5)

The original design covered S3–S5, missing the deal's entry point (S2: Why Change?) and close (S6: Contract). The Deal Health Monitor scores S2–S6. The SE is engaged throughout:

- **S2 (Why Change?):** SE does initial account research and persona mapping — the agent can generate this from Salesforce + Glean.
- **S3 (Why Now?):** Business case, user interviews, Blueprint starts — material generation begins in earnest.
- **S4 (Why Atlan?):** Blueprint tech tab, demos, POV criteria — highest material volume stage.
- **S5 (Selection):** Production architecture, connector docs, knowledge transfer — highest-stakes materials.
- **S6 (Contract):** Documentation package and CX handoff — ensures nothing falls through the cracks at close.

## Why Blueprint through Snowflake (not Confluence)

Blueprint data already flows into Snowflake via structured extractors:
- `BLUEPRINT.EXTRACTOR.TECH_ITEMS` — tech stack per account (11K+ items): name, category, hosting type, POV scope, connection method, authentication type, networking requirements, validation status
- `BLUEPRINT.EXTRACTOR.SUCCESS_CRITERIA` — POV success criteria: use case, persona, feature, measurement, priority, outcome, owner, blockers

Reading Blueprint through Snowflake is faster, more structured, and doesn't require a separate Confluence MCP server. The Blueprint MCP also exists and can be used as a secondary source if the Snowflake tables lag.

## Skill design principles

Each skill follows the same contract:
- **Input:** Account context (stage, stakeholders, deal size) + Deal Health scores + material-specific data
- **Output:** Structured material draft + confidence level + gap list
- **Fallback:** Blueprint (Snowflake) → Atlan → Glean → skeleton with placeholders

Skills don't call other skills. The orchestrator dispatches and collects results.

## Risk mitigations

| Risk | Mitigation |
|------|-----------|
| Hallucinated infrastructure in architecture diagrams | Skill refuses confident-looking diagrams from insufficient data. Skeleton with flagged placeholders instead. |
| Stale data creating false confidence | Every material includes data freshness timestamps. Architecture diagrams in production planning get explicit staleness warnings at 48h. Deal Health scores show which week they're from. |
| Agent autonomously moving Salesforce stages | Orchestrator has no write access to Salesforce. Advisory only — posts flags to Slack. |
| Auth method guessing in connector docs | Auth methods are security-sensitive. Never inferred — only populated from Blueprint or flagged as unknown. |
| Duplicating Sales Claw | se-call-prep reads Sales Claw output and adds SE-specific depth. Complementary, not competing. |
| Duplicating Deal Health scoring | stage-readiness-checker consumes Deal Health scores. Adds material readiness, doesn't re-score deal health. |

## Open questions for the builder

1. **Sales Claw output format:** How does Sales Claw deliver its briefs — Slack DM, structured JSON, or both? Need to know how se-call-prep reads it.
2. **Deal Health table access:** Confirm read access to `SALES_DB.PIPELINE.DEAL_HEALTH_MONITORING` from the agent's Snowflake service account.
3. **Blueprint extractor freshness:** How often do `BLUEPRINT.EXTRACTOR.*` tables refresh? Real-time on Blueprint save, or batch?
4. **Atlan API scope:** When credentials are provisioned for `home.atlan.com`, minimum read permissions needed: connector inventory, table/column metadata, lineage, glossary, governance tags.
5. **Slack workspace:** Dedicated SE channel vs. SE DMs? Bot permissions: `chat:write`, `reactions:read`, `reactions:write`, `channels:read`.
6. **Template library:** Where do best-practice templates for sprint success criteria live today? If they don't exist yet, the skill needs seed templates.
