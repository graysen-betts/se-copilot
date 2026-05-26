# SE Co-Pilot — Architecture

## Skill Graph

```mermaid
graph TD
    subgraph Triggers
        T1[Salesforce Stage Change — S2 through S6]
        T2[Calendar Event < 24h]
        T3[Daily Sweep Cron]
    end

    subgraph Orchestrator
        O[SE Co-Pilot Orchestrator]
    end

    subgraph "Existing Systems (read-only)"
        DH[Deal Health Monitor — 22-dim weekly scorecard]
        SC[Sales Claw — AE pre-call briefs]
    end

    subgraph Data Layer
        SF[Snowflake — SFDC + Blueprint + Deal Health tables]
        AT[Atlan MCP — Metadata, Lineage, Governance]
        GL[Glean — Docs, Gong transcripts, Slack threads]
        GC[Google Calendar — Meeting detection]
    end

    subgraph Skills
        S1[se-call-prep]
        S2[blueprint-accelerator]
        S3[demo-planner]
        S4[sprint-success-criteria]
        S5[connector-docs-generator]
        S6[architecture-diagram-generator]
        S7[stage-readiness-checker]
        S8[gap-flagger]
    end

    subgraph Output
        SL[Slack — Flags & Drafts to SE]
    end

    T1 --> O
    T2 --> O
    T3 --> O

    O --> S7
    S7 -->|reads| DH
    S7 -->|missing materials| S1 & S2 & S3 & S4 & S5 & S6
    S7 -->|gaps found| S8

    S1 -->|reads| SC
    S1 & S2 & S3 & S4 & S5 & S6 --> SF & AT & GL
    T2 --> GC

    S8 --> SL
    S1 & S2 & S3 & S4 & S5 & S6 --> SL
```

## Execution Flow

```mermaid
sequenceDiagram
    participant Trigger as Trigger (SF/Cal/Cron)
    participant Orch as Orchestrator
    participant DH as Deal Health Monitor
    participant SC as Sales Claw
    participant Readiness as stage-readiness-checker
    participant Skills as Material Skills
    participant Data as Data Layer (SF + Atlan + Glean)
    participant Slack as Slack

    Trigger->>Orch: Event fires (stage change / calendar / daily)
    Orch->>Data: Fetch account context (stage, stakeholders, deal size)
    Orch->>DH: Read Deal Health scorecard (22 dims, grade, red flags)
    Orch->>Readiness: Check SE material readiness for current stage

    alt Materials missing
        Readiness->>Orch: Gap list (which materials, what data is missing)
        Orch->>Skills: Dispatch relevant material skill(s)
        Skills->>Data: Pull Snowflake (Blueprint tables + SFDC) → Atlan → Glean
        Skills->>Skills: Apply fallback rules (generate / caveat / skeleton)
        Skills->>Slack: Post draft + confidence level
    end

    alt Call prep triggered
        Orch->>SC: Read Sales Claw brief (AE-focused)
        Orch->>Skills: Dispatch se-call-prep (layer SE technical depth on top)
        Skills->>Slack: Post SE-specific call prep
    end

    alt Gaps or risks found
        Readiness->>Orch: Blocking items + Deal Health red flags
        Orch->>Slack: Post actionable flag with next steps
    end

    Note over Slack: SE reviews, validates, corrects
    Slack-->>Orch: SE correction (e.g., maturity override)
    Orch->>Skills: Re-generate with corrected context
    Skills->>Slack: Updated draft
```

## Sales Stages (S2–S6)

| Stage | Name | SE-Owned Materials Required |
|-------|------|----------------------------|
| **S2** | Why Change? | Account research, initial call prep, persona mapping |
| **S3** | Why Now? | Business case alignment, user interviews (3+ before POV), Blueprint started, people readiness |
| **S4** | Why Atlan? | Blueprint tech tab complete, tailored demo, competitive positioning, POV success criteria, whiteboarding |
| **S5** | Selection | Production architecture diagram (signed off), connector docs, sprint success criteria, internal knowledge transfer |
| **S6** | Contract | Final documentation package, handoff materials for CX/IE |

## Architecture Decisions

### Pattern: Event-driven single orchestrator with skill dispatch

**Why:** Three discrete triggers (stage change, calendar, cron) each dispatch to the same set of material-generation skills. A single orchestrator with skill dispatch keeps routing logic in one place while skills stay independently testable.

**Key design choice: compose with existing systems, don't replace them.**
- **Deal Health Monitor** already scores 22 dimensions weekly per deal in Snowflake Cortex. The stage-readiness-checker reads these scores and layers SE-specific material readiness on top — it does not rebuild deal assessment from scratch.
- **Sales Claw** already generates AE-focused pre-call briefs (account snapshot, Gong summary, discovery questions). The se-call-prep skill reads the Sales Claw brief and adds SE technical depth: Blueprint status, connector gaps, architecture readiness, persona-specific technical talking points. SEs get a brief that builds on what the AE sees, not a separate one.

**Rejected alternatives:**
- **Multi-agent pipeline** — overkill. Materials are independent (call prep doesn't block architecture diagrams). No sequential dependency justifies chaining agents.
- **Pure ReAct loop** — decisions are deterministic (stage → required materials → generate), not exploratory.
- **Rebuilding Deal Health / Sales Claw** — wasteful. Both exist and work. The agent's unique value is material generation and SE-specific gap-flagging, not deal scoring or generic call prep.

### Runtime: Claude Agent SDK + Claude Sonnet

- **Claude Agent SDK** — native tool use, structured output. The orchestrator calls MCP servers (Snowflake, Atlan, Slack) and produces structured materials.
- **Claude Sonnet** — balances cost and capability for structured writing. Architecture diagrams use stricter validation prompts; upgrade path to Opus for that single skill if quality is insufficient.

### Data access: MCP servers + Snowflake tables

| Source | What it provides | Access method |
|--------|-----------------|---------------|
| **Snowflake** | SFDC mirror (opps, accounts, contacts, activities, stage history), Blueprint tables (`BLUEPRINT.EXTRACTOR.TECH_ITEMS`, `BLUEPRINT.EXTRACTOR.SUCCESS_CRITERIA`), Deal Health scores (`SALES_DB.PIPELINE.DEAL_HEALTH_MONITORING`) | Snowflake MCP, read-only |
| **Atlan** | Customer tenant metadata, lineage, glossary, governance tags, connector inventory | Atlan MCP — **BLOCKED: `home.atlan.com` credentials needed** |
| **Glean** | Gong transcripts, Confluence docs, Slack threads, internal knowledge | Glean MCP (search + chat) |
| **Slack** | Post drafts/flags, receive SE corrections | Slack MCP (chat:write, reactions) |
| **Google Calendar** | Meeting detection for call prep triggers | Calendar MCP, read-only |

Blueprint is no longer a separate Confluence integration — its structured data already flows into Snowflake as `BLUEPRINT.EXTRACTOR.*` tables. The agent reads Blueprint through Snowflake, not Confluence.

### Memory model

**Session state per account** stored in Snowflake (or local SQLite for v1):
- Last material generation timestamps per material type
- SE corrections (maturity overrides, manual gap closures)
- Data freshness timestamps per source
- Material draft versions and SE feedback

No long-term conversational memory. The agent is stateless between runs — it reads fresh context from data sources each trigger.

### Staleness handling

| Source | Threshold | Behavior |
|--------|-----------|----------|
| Salesforce → Snowflake | 12h | Generate with timestamp warning |
| Deal Health Monitor | 7 days (runs weekly Sunday) | Note which week's scores are shown |
| Atlan metadata | 24h (general), 48h (arch diagrams in prod planning) | Generate with staleness flag |
| Blueprint → Snowflake | Real-time (extractor) | Always read latest |

### Output surface

**V1: Slack only.** Drafts and flags posted to SE's DM or dedicated channel. Structured messages with:
- Account name + stage + Deal Health grade (Green/Yellow/Red)
- Material type + confidence level (high / caveated / skeleton)
- Specific gaps with suggested next steps
- Data freshness warnings if applicable

**V2: Dashboard** (Slack canvas or lightweight web view) — all accounts, stage, material readiness %, Deal Health grade, top blockers.
