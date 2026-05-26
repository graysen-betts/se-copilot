# sprint-success-criteria

Auto-generate maturity-aware success criteria for a customer's Atlan deployment sprint.

## Input
- Atlan tenant state (connector count, ingested assets, governance tags, lineage)
- Stated use cases from user interviews and Blueprint
- Account stage and deal context from Snowflake
- Best-practice templates (generalized, not customer-specific)

## Maturity inference
- **Net-new:** No Atlan tenant OR tenant with zero connectors / zero ingested assets
- **Expansion:** >= 1 connector with ingested metadata (tables or columns)
- **Mature expansion:** Governance tags + lineage present

## Output
Concrete, measurable success criteria for Sprint 1. Example:
- "Glossary setup covering 80% of high-traffic tables"
- "Lineage ingestion for Snowflake and Databricks connectors"
- "Governance tagging for PII columns across 3 critical schemas"

Format: criteria list with metric, owner, and dependency for each.

## Rules
- Generate fresh criteria enriched by best-practice templates (not template-first)
- Surface only the generated criteria to the SE — do not expose the maturity inference logic
- If SE corrects maturity in Slack, immediately re-generate with corrected context
- Net-new: foundational (connector setup, glossary, initial lineage)
- Expansion: advanced (new connectors, deeper governance, playbooks)
- Mature expansion: optimization (automation, advanced lineage, compliance workflows)

## Trigger
- Auto-trigger on stage change to S5
