# architecture-diagram

Generate a production architecture diagram description for customer sign-off.

## Input
- Blueprint technology tab (connectors, auth, connection methods, topology)
- Atlan lineage data (data flow between connectors and tables)
- Salesforce account context (product interest, deal stage)

## Output
A Mermaid diagram + prose description showing:
1. **Data sources** — customer's source systems and connectors
2. **Atlan tenant** — metadata flows, governance layer
3. **Data flow** — lineage from source through transformations to consumption
4. **Network topology** — connection methods, tunnels, firewall boundaries
5. **Authentication points** — where auth is required (only if documented)

## Confidence levels
- **HIGH:** Blueprint tech tab + Atlan lineage both present and consistent
- **CAVEATED:** One source present — generate with explicit "unverified" markers on inferred sections
- **SKELETON:** Neither source has sufficient data — generate a template with placeholders listing exactly what's missing

## Rules
- CRITICAL: Never generate a confident-looking diagram from insufficient data
- Bad technical artifacts are worse than no artifacts — they create false confidence
- If Atlan metadata is > 48h old and customer is in active production planning, add explicit staleness warning and recommend re-validation with customer
- Architecture diagrams are the HIGHEST STAKES material — apply the strictest data requirements

## Trigger
- Stage change to S5
- Daily sweep for S5 accounts without signed-off architecture diagrams
