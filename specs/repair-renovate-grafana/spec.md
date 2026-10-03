# Specification: Repair Renovate Grafana update

- Implementation: `repair-renovate-grafana`; SDD tier: high.
- Intent: repair PR #377's stale generated architecture and align the Grafana
  operator controller with the PR's 5.25.0 CRDs.
- Human approval: the user approved the reported fixes with "fix them fan out".
  This carries forward the reviewed scope and approach through spec, plan, and
  task gates; no new feature or broader Renovate refactor is proposed.
- Requirements: use a published chart with appVersion v5.25.0; preserve Flux
  CRD ownership; regenerate architecture using its renderer; keep Git desired
  state authoritative; document the exact validation boundary.
- Acceptance: chart and controller image match CRDs; focused manifests render;
  architecture check and relevant pre-commit checks pass; development evidence
  or a justified coverage exception is recorded.
- Non-goals: production mutations, a new Grafana installation, unrelated
  dependency changes, and changes to other PRs.
- Authority: `docs/decisions/codex-implementation-workflow.md`,
  `docs/decisions/tdd-and-development-smoke-evidence.md`,
  `docs/runbooks/spec-driven-development.md`, and
  `docs/runbooks/implementation-workflow.md`.
