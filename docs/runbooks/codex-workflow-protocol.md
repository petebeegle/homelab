---
status: current
scope:
  - codex-harness
  - implementation-workflow
authority: reference
created: 2026-05-12
last_verified: 2026-05-12
---

# Codex Workflow Protocol Reference

This reference records the machine-readable evidence used by `docs/runbooks/implementation-workflow.md`.

## Delegation Tokens

Implementation and verifier attestations must include `delegation_token` and `delegation_token_path`. Token paths must be relative paths under `.codex/tmp/delegation-tokens/`; absolute paths and paths outside that directory are invalid.

Each token file contains:

```yaml
delegation_token: <role-specific-token>
implementation: <implementation>
role: implementation-agent|verifier-agent
agent_id: <role-prefixed-agent-id>
created_at: <UTC timestamp>
```

The token fields must match the corresponding attestation. Verifier token values and paths must be distinct from the implementation owner evidence.

## Prompt Intent Marker

The `UserPromptSubmit` hook may write `.codex/tmp/repo-change-intent` when a prompt appears to request repository changes. This marker is advisory and exists to surface workflow reminders before tracked files change; mutation, push, and PR guards remain the authoritative enforcement points.
