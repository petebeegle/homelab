---
status: draft
scope:
  - codex-harness
  - agent-operations
authority: operational
created: 2026-11-06
last_verified: 2026-11-06
---

# Supervisor session operations (first increment)

## Inventory
From the repository checkout, run:

```bash
python3 tools/agent_work/status.py
python3 tools/agent_work/status.py --json
```

The output is an inventory of local Git worktrees, **not** a live-session monitor. `codex/<slug>` branches map to implementation IDs; other branches and detached HEADs are reported without pretending to be active agents.

## Operating model
1. Define the desired outcome and risk.
2. Use a dedicated `codex/<implementation>` worktree for tracked edits, following ADR-0012.
3. Keep one integration owner for the implementation's evidence and PR.
4. Parallelize read-only investigations freely; only delegate non-conflicting writes with explicit ownership.
5. Validate against the development cluster where required, then review and merge through existing PR controls.
6. If status is missing, show `unknown`; do not claim an agent is running or finished.

## Future supervisor contract
A coordinator will track `implementation_id`, `session_id`, `run_id`, owner, dependencies, status, last heartbeat, blocked reason, and human-review requests. A worktree alone cannot supply this. No session IDs, heartbeats, dispatch, or resource leases are implemented in the initial CLI.

## Security
Do not ingest prompt bodies, MCP payloads, stdout, or secrets into coordination records. Never give workers direct production mutation authority merely because the supervisor assigned a task.
