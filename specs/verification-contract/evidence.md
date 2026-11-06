# Evidence

Status: PENDING CI.

Reviewed: `.codex/config.toml`, `.codex/hooks/pre_commit_check.sh`, `.github/workflows/ci.yml`, `tests/browser/package.json`.

No local command execution or live development-cluster verification claimed. GitHub Actions is the independent verification authority for this change. New workflow must be observed passing before merge. Production and development cluster not mutated.

The existing pre-commit PostToolUse hook remains unchanged: removal requires a follow-up after CI equivalence is proven. Branch protection is not modified in this PR.
