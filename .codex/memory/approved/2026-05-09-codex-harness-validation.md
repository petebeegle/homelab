---
status: approved
created: 2026-05-09
source: codex-harness-migration
kind: agent-operational-learning
---

# Codex Harness Validation Learning

When changing this repo's Codex harness, validate the harness itself before handoff:

- Run `agnix .` and, when practical, `agnix --strict .`.
- Run `codex -C /workspaces/homelab mcp list` to confirm `.codex/config.toml` loads.
- Run `.codex/hooks/stop_self_verify.sh` and shell syntax checks for `.codex/hooks/*.sh`.
- Run the memory-agent tests with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests` from `tools/agent-memory`.
- Treat generated memory as local until reviewed; only commit approved memory under `.codex/memory/approved/`.
- Use `[features].hooks = true`; `[features].codex_hooks` is deprecated.
- Keep `bubblewrap` installed in the devcontainer image because Codex sandboxing expects `bwrap` on PATH.
