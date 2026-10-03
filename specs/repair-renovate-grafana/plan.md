# Plan: Repair Renovate Grafana update

- Branch: `codex/repair-renovate-grafana`; SDD tier and workflow risk tier: high
  because the existing PR updates cluster-scoped CRDs and its controller.
- Approach: verify chart metadata and upstream CRD render; change only the
  operator chart pin to 5.25.0; preserve CRD install/upgrade Skip; regenerate
  `docs/architecture.md` using `python3 tools/architecture/render.py --write`.
- Tests: reproduce architecture-doc failure first; verify chart appVersion and
  rendered image; render controller, CRDs, production, and development;
  validate generated architecture and relevant pre-commit hooks.
- Smoke strategy: read-only development discovery first. Coordinate any shared
  cluster change with the parent lane before mutations. If Grafana coverage is
  absent and cannot safely be emulated, record smoke_profile none plus concrete
  substitute rendering and API dry-run checks; do not claim runtime smoke.
- Fanout targets: this lane owns #377; parent owns #378 and other lanes own
  separate PRs. Work within this worktree is sequential except independent
  read-only checks. Consolidate this lane's results in evidence.md.
- Exceptions: `/home/vscode/homelab-worktrees/repair-renovate-grafana` replaces
  the unwritable default worktree root. Local codex branch repairs the existing
  Renovate PR branch rather than creating a second PR. Existing user approval
  covers the previously reviewed repair; no repeated approval request needed.
- Rollback: revert the controller pin and CRD bump together through Git if
  subsequent development runtime validation identifies a regression.
