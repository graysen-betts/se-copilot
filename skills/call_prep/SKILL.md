# se-call-prep

Generate an SE-specific call prep that layers technical depth on top of the Sales Claw brief.

## Relationship to Sales Claw

Sales Claw already generates AE-focused pre-call briefs with: account snapshot, prior Gong summary, persona-specific failure modes, discovery questions, competitive context, and walk-away goals. **This skill does not duplicate that.** It reads the Sales Claw brief and adds SE-specific depth.

## What this skill adds on top of Sales Claw

1. **Blueprint status** — tech tab completeness %, which fields are missing, what to ask about
2. **Connector readiness** — which connectors are documented, which have gaps (especially auth)
3. **Architecture readiness** — has a diagram been drafted? Is it signed off? Stale?
4. **Persona-specific technical talking points** — based on interview summaries and Blueprint personas
5. **Outstanding SE-owned materials** — what's overdue for this account's stage
6. **Deal Health technical dimensions** — Tech Stack Fit, POV Experience scores from Deal Health Monitor

## Input
- Sales Claw brief for this account/meeting (read, don't regenerate)
- Account context from Snowflake (stage S2–S6, deal size, stakeholders, activity)
- Blueprint data from Snowflake (`BLUEPRINT.EXTRACTOR.TECH_ITEMS`, `SUCCESS_CRITERIA`)
- Deal Health scores from Snowflake (`DEAL_HEALTH_MONITORING`)
- Atlan metadata if customer tenant exists
- User interview summaries from Glean/Gong

## Output
An SE-specific call prep addendum with:
1. **Sales Claw brief summary** — one-line reference so the SE knows the AE context
2. **SE technical prep** — Blueprint gaps, connector status, architecture status
3. **Technical talking points** — persona-mapped, stage-appropriate
4. **Outstanding materials** — what the SE needs to close before or after this call
5. **Suggested technical questions** — specific gaps to fill in this conversation

## Confidence levels
- **HIGH:** Sales Claw brief available + Blueprint data + interview summaries
- **CAVEATED:** Sales Claw brief available but Blueprint gaps or no interviews
- **SKELETON:** No Sales Claw brief, minimal Salesforce data

## Trigger
Calendar event with customer contact detected < 24 hours away.
