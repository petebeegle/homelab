# Implementation Plan: adopt-speckit-worktree-flow

**Branch**: `codex/adopt-speckit-worktree-flow` | **Date**: 2026-07-03 |
**Spec**: `specs/adopt-speckit-worktree-flow/spec.md`

## Summary

Make Spec Kit the canonical implementation workflow and use worktrees as the
default concurrency model. Remove local attestation requirements from hooks,
push guards, PR automation, templates, and binding guidance.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: docs/tooling
**Primary Files**: `.codex/hooks/implementation_workflow_guard.sh`,
`.codex/hooks/user_prompt_submit.sh`, `.codex/hooks/verifier_push_guard.sh`,
`.codex/scripts/create_implementation_pr.sh`, `.specify/templates/*`, docs,
and Codex harness tests.
**Development Validation**: not required; this changes local workflow tooling
and documentation only.

## Constitution Check

- Git remains the source of truth; no live cluster mutation.
- Spec Kit artifacts remain durable implementation evidence.
- Runtime scratch under `.codex/tmp/` remains ignored and non-durable.
- Branch isolation remains mandatory through `codex/<implementation>`.

## Approach

1. Update repo guidance and templates to describe Spec Kit plus default
   worktree mode.
2. Simplify workflow guards to enforce branch and SDD artifact invariants.
3. Simplify push and PR automation to require evidence but not verifier files.
4. Update harness tests to cover the new guard contract.
5. Record command results and exceptions in evidence.

## Validation

- `python3 -m pytest tools/codex-harness/tests`
- `python3 tools/architecture/render.py --check`
- `pre-commit run --all-files` if practical

## Risks

- Guard changes could become too permissive around tracked edits.
- Existing docs may retain stale attestation language.
- PR automation still depends on `gh` in environments that use it.
