# Evidence: Repair Gateway API update documentation

**Branch**: `codex/repair-renovate-gateway`
**Risk Tier**: low / docs-only repair
**Started**: 2026-10-03
**Reviewed source commit**: `228b0a893bff5f49267f21d8f165bc8c78ef8baa`
**PR**: <https://github.com/petebeegle/homelab/pull/378>

## Human Gates And SDD Exceptions

User approved the previously described repair with "fix them fan out". This
single instruction covers spec, plan, and tasks for the clear low-risk repair.
Clarify skipped because the renderer determines the expected output. Separate
checklist and analyze workflows skipped for a single generated file; direct
requirements/diff review substitutes. Converge will use the same direct check.
No Spec Kit scaffolding changes or reinitialization are needed.

## Baseline

`python3 tools/architecture/render.py --check` reports stale
`docs/architecture.md`: its Gateway API CRD URLs still show v1.5.1 while sources
already select v1.6.2. The original CI Pre-commit job confirms the same failure:
<https://github.com/petebeegle/homelab/actions/runs/33824099940/job/100872938317>.

## Local Checks

- `python3 tools/architecture/render.py --write`: PASS; exactly one generated
  architecture row changes, replacing Gateway API v1.5.1 URLs with v1.6.2.
- `python3 tools/architecture/render.py --check`: PASS after generation.
- `python3 tools/codex-harness/validate_sdd_context.py --require-plan-artifacts
  --require-evidence`: PASS.
- `pre-commit run --files` covering the original PR's Kubernetes/Talos files,
  generated architecture document, and all four repair artifacts: PASS. YAML,
  Kubernetes validation, architecture, conflict, whitespace, large-file, and EOF
  checks passed; hooks without applicable files skipped.

Direct converge review confirms FR-001 through FR-003: the generated document
matches sources, original source changes are preserved, and validation limits
are explicit. No additional test code is appropriate for this deterministic
generated-document change. Local Spec Kit sources and constitution were reviewed;
no workflow changes require an upstream conformance audit.

The correction is ready for a fast-forward push to the existing PR. GitHub CI
results after that push are reported separately by the coordinating agent.

## Development Validation

Smoke profile: `none` for this documentation-only repair. The original Gateway
API upgrade's development rollout and routed behavior are not validated by this
repair. No production or development desired state is changed.

## Exceptions

The default worktree location returned permission denied. The writable fallback
is `/home/vscode/homelab-worktrees/repair-renovate-gateway`. Local work remains on
a matching codex branch with durable artifacts; the final commit will update the
existing Renovate PR branch as requested rather than create a duplicate PR.
