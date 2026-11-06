# Plan

Risk: low. SDD: low. Smoke: CI-only, no cluster changes. No fanout. Remove only the redundant `pre_commit_check` PostToolUse stanza from `.codex/config.toml`; preserve other hooks. Keep the existing `CI / Pre-commit` job as authoritative. Add a lightweight repository contract test and run it in the shared verification profile. Document local targeted pre-commit invocation.

The user's 'Continue' authorizes this next bounded step; spec/plan/task human approvals consolidated. CI results and evidence gate merging.
