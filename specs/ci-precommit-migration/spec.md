# Move broad post-tool pre-commit validation to CI

## Acceptance
- The Codex PostToolUse hook no longer runs pre-commit after each edit/tool call.
- GitHub Actions continues to run `pre-commit run --all-files` on every PR and push to main, failing closed.
- Agents have an explicit local command for fast targeted validation.
- A regression test verifies the hook is absent and the independent CI pre-commit gate exists.
- SOPS, Terraform, implementation-workflow, and stop hooks remain unchanged.
- No production or cluster changes.
