# connector-docs

Generate connector setup and networking documentation for a customer.

## Input
- Blueprint technology tab (connector types, auth methods, connection methods, volume, priorities)
- Atlan metadata (connector inventory, table/column counts, lineage)
- Salesforce account context

## Output
Per-connector documentation including:
1. **Connector type** and version
2. **Authentication method** — ONLY if documented in Blueprint
3. **Connection method** (direct, tunneled, VPN)
4. **Network requirements** (ports, IPs, firewall rules)
5. **Volume estimates** and sync frequency
6. **Priority** and dependencies on other connectors
7. **Setup steps** — standard Atlan connector setup instructions

## Fallback behavior
- Blueprint has connector + auth: generate full docs (HIGH confidence)
- Blueprint has connector, no auth: document connector, flag auth as "UNKNOWN — ask SE" (CAVEATED)
- Atlan has connector, no Blueprint: note connector exists, flag all details as needing validation (CAVEATED)
- Neither source: produce skeleton template with placeholders (SKELETON)

## Rules
- NEVER guess authentication methods — security-sensitive field
- NEVER generate confident-looking docs from insufficient data
- Cross-reference Blueprint and Atlan to validate connector list completeness
- Flag any discrepancies between Blueprint and Atlan data

## Trigger
- Stage change to S5
- Daily sweep for S5 accounts without connector docs
