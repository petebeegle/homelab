# Feature Specification: Hybrid AI harness handoff

**Feature Branch**: `codex/hybrid-ai-harness-handoff`
**Created**: 2026-11-07
**Status**: Draft handoff; no implementation or merge authorized by this PR
**Risk Tier**: low (docs-only)

## Human Gate Status

Intent: user requested a PR describing the discussed hybrid local/hosted AI harness plan and current open PR status, for handoff to a code agent. Explicit constraint: do not merge.
Clarify: skipped; existing conversation defines this documentation deliverable.
Spec/plan/task gates: combined authorization for drafting and opening this documentation PR only. Future infrastructure designs remain proposals requiring the repository's normal implementation workflow.

## Summary

Build toward a reproducible, privately reachable agent harness combining deterministic orchestration, isolated execution, a local model, and hosted reasoning when needed. Establish working private-network verification first. Do not confuse a model server, an agent, a runner, and the supervisor.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/decisions/codex-implementation-workflow.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/verification-contract.md`

## Scope and requirements

- FR-001: Record timestamped GitHub PR states, exact relevant heads, CI evidence, dependencies, and unverified live layers.
- FR-002: Describe staged implementation and measurable acceptance for runner infrastructure, supervisor, local inference, hybrid execution, and recovery.
- FR-003: Preserve private services, GitOps, encrypted secrets, Talos API management, isolated runners, and existing safety guards.
- FR-004: Publish documentation only; do not merge, deploy, purchase hardware, rotate credentials, or change existing PRs.
- FR-005: Separate observed state from proposed architecture and unconfirmed hardware/access assumptions.

## User story and acceptance

Given a code agent without this conversation, reading these artifacts must identify the first task, existing code to reuse, verification needed, and conditions preventing a completion claim. Verify via a source-backed status table and ordered tasks with acceptance criteria.

## Assumptions and open decisions

Proposed hardware is GMKtec EVO-X2, Ryzen AI Max+ 395, 128 GB unified RAM, 2 TB SSD; ownership and installation are not confirmed. Existing RTX 4090 remains reserved for gaming. Bare-metal Linux plus Ansible/container inference is a proposal, not an accepted ADR. Exact OS/kernel/runtime/model, network placement, management host, credential source, budgets, and latency thresholds require environment discovery and measurements. No automatic escalation into this ChatGPT thread: deployed escalation uses an explicitly configured hosted API.

## Success criteria

A draft documentation PR against main contains spec, plan, tasks, evidence, complete observed open-PR inventory, and a phased handoff. No runtime changes or merges occur.
