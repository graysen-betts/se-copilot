# demo-planner

Generate an opinionated demo plan recommending which Atlan features to highlight for a specific customer.

## Input
- User interview summaries (role-level friction points, "better world" view)
- Blueprint persona and pain point entries
- Atlan metadata (customer's data stack — which connectors, table counts)
- Salesforce opportunity data (deal size, product interest)

## Output
A demo plan document with:
1. **Recommended features** — each mapped to a specific persona and their stated pain point
2. **Demo narrative** — suggested flow and story arc
3. **Skip list** — features to skip and why (e.g., "skip playbooks — customer not mature enough for automation")
4. **Open questions** — things to validate with the customer before or during the demo

## Rules
- If no user interview summaries exist and account is at S4+, flag as a gap: "Process requires 3+ interviews before POV kickoff"
- Generate a generic plan based on deal size and industry when interviews are missing, clearly marked as incomplete
- The SE builds the demo environment — this skill produces the plan, not the environment

## Trigger
- Stage change to S4+
- Daily sweep for S4+ accounts without a demo plan
