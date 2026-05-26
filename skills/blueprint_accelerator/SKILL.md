# blueprint-accelerator

Monitor Blueprint technology tab completeness and pre-populate from Atlan metadata.

## Input
- Blueprint technology tab (current state from Confluence)
- Atlan tenant metadata (connector inventory, table/column metadata)
- Account stage from Snowflake

## Output
1. **Completeness report** — which fields are filled, which are empty, percentage complete
2. **Pre-populated fields** — if Atlan shows connectors the customer has, pre-fill connector type, table counts. Mark as "pre-populated from Atlan — SE please validate"
3. **Gap flags** — for each empty field, suggest a specific question for the SE to ask in the next discovery call
4. **Stage urgency** — if account is at S4+ and tech tab is <50% complete, flag as blocking

## Rules
- NEVER guess authentication methods — these are security-sensitive
- NEVER overwrite SE-entered data with Atlan data — SE input is source of truth
- Pre-populated fields are suggestions, not assertions

## Trigger
- Salesforce stage change (check if tech tab readiness matches stage requirements)
- Daily sweep (flag accounts where tech tab is stale relative to stage)
