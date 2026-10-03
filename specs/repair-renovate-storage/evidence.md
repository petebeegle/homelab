# Evidence: Repair Renovate storage documentation

**Branch**: `codex/repair-renovate-storage`
**Started**: 2026-10-03
**SDD tier**: low
**Workflow tier**: docs-only
**PR**: https://github.com/petebeegle/homelab/pull/383
**Original reviewed PR commit**: `c6e95a2998ecdaf393fc9f4264ff4089abe401f8`

## Human gates and exceptions

The user's “fix them fan out” instruction approves the reviewed narrow repair's
spec, plan, and tasks together. Artifacts were bootstrapped before generation.
Clarify skipped: the failed CI diff identifies the exact required correction.
Checklist skipped: three explicit acceptance requirements cover this small repair.
Analyze skipped: the spec, plan, and sequential tasks were directly reconciled
before edits. Converge skipped: the exact generated diff and completed tasks
suffice; no functionality is added. No Spec Kit scaffolding or integration changes.

The worktree is `/home/vscode/homelab-worktrees/repair-renovate-storage` because
the default `/workspaces/homelab-worktrees` parent was not writable. No secrets or
ignored local configuration are needed. The local codex branch and artifacts
will accompany repair of the existing Renovate PR instead of creating a new PR.

## Prior CI evidence

[Pre-commit failure](https://github.com/petebeegle/homelab/actions/runs/31287377526/job/93178554567)
reports only `architecture-doc` failing: `docs/architecture.md:129` retains
v0.0.36 while the source kustomization references v0.0.37.

## Validation

- `python3 tools/architecture/render.py --check` before regeneration: FAIL
  (exit 1), reproducing exactly the v0.0.36 to v0.0.37 row mismatch.
- `python3 tools/architecture/render.py --write`: PASS (exit 0). Inspection of
  `git diff -- docs/architecture.md` confirms exactly one generated row changed.
- `python3 tools/architecture/render.py --check` after regeneration: PASS
  (exit 0).
- `python3 tools/codex-harness/validate_sdd_context.py --root
  /home/vscode/homelab-worktrees/repair-renovate-storage --branch
  codex/repair-renovate-storage --require-plan-artifacts`: PASS (exit 0).
- `pre-commit run --files docs/architecture.md
  specs/repair-renovate-storage/spec.md specs/repair-renovate-storage/plan.md
  specs/repair-renovate-storage/tasks.md specs/repair-renovate-storage/evidence.md`:
  PASS (exit 0). Architecture, conflict, trailing-whitespace, large-file, and
  end-of-file checks passed; hooks without applicable changed files skipped.
- `git diff --check`: PASS (exit 0).

No executable code changed, so no new tests were added. The existing architecture
validator provides the failing-before/passing-after regression evidence.
Requirements FR-001 through FR-003 are satisfied by the generated diff, restricted
file scope, and recorded checks. Binding GitOps, SOPS, Gateway, NFS, and Talos
invariants remain unchanged. Local workflow conformance was checked against both
runbooks; upstream workflow review is inapplicable because this repair changes
neither Spec Kit nor workflow standards.

## Runtime limits

Smoke profile: none. ADR-0013 and the docs-only workflow do not require live
smoke for this generated-document repair. The original dependency upgrade's
provisioning, data persistence, and new health probes are not runtime-validated
by these checks. No deployment, Flux reconciliation, or live-resource change is
claimed. Parent owns pushing and normal GitHub PR/status review.
