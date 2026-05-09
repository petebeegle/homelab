---
status: approved
created: 2026-05-09
source: codex-follow-up-migration
kind: agent-operational-learning
---

# Devcontainer And Runbook Placement Learning

For this repo, keep Codex runtime prerequisites explicit in the devcontainer
instead of assuming the base image includes them.

- Use the Noble devcontainer base image plus a repo Dockerfile for OS packages.
- Install `bubblewrap` during image build so Codex sandboxing has `bwrap` on PATH before Codex starts.
- Keep older operator-only notes under `.codex/runbooks/` when they are useful for Codex context but are not durable architecture decisions.
- If Agnix lags behind current Codex config fields, document narrow temporary rule suppressions in `.agnix.toml` instead of reverting to deprecated Codex settings.
