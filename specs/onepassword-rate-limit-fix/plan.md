# Implementation Plan: 1Password Rate-Limit Fix

**Branch**: `codex/onepassword-rate-limit-fix` | **Date**: 2026-08-11 | **Spec**: `specs/onepassword-rate-limit-fix/spec.md`

## Summary

Parameterize the shared direct-auth polling interval, set production to 3600 seconds, and set development to 31536000 seconds as an effective manual-refresh mode. Operator 1.12.0 passes the value to `time.NewTicker`, so zero would panic and is not a supported disable value. Existing alerts remain unchanged because they correctly detected the outage.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Kubernetes, Flux, 1Password authentication, policy, runbook
**Dependencies**: Helm, Flux, kubectl, pytest, 1Password CLI
**Storage**: N/A
**Ingress**: N/A
**Secrets**: Values remain unread and uncommitted; SOPS consumers remain active.
**Smoke Strategy**: Exact-branch development base reconciliation, operator readiness, and rendered environment inspection.
**Fanout Targets**: N/A; no subagents were requested.
**Development Validation**: Shared development base reconciliation.
**Post-Implementation SDD Conformance**: Local workflow sources only.

## Human Gates

**Spec Gate**: Approved through the user's explicit incident-fix instruction.

**Checklist Status**: `checklists/requirements.md` completed before implementation.

**Plan Gate**: Expedited approval is covered by the direct request after the measured root cause and corrective interval were reported.

**Expected Task/Analyze Gate**: Manual cross-artifact review; the correction is narrow and time-sensitive.

## Constitution Check

- [x] GitOps source of truth preserved.
- [x] No production-first mutation; development validation is planned.
- [x] Gateway API invariant preserved.
- [x] SOPS invariant preserved.
- [x] NFS default is not applicable.
- [x] Talos boundary preserved.
- [x] Branch is `codex/onepassword-rate-limit-fix`; `/home/vscode/homelab-worktrees/` is used because the preferred path is not writable.
- [x] Documentation impact is addressed in the operator runbook.
- [x] PR review/status checks remain the review gate.

## Project Structure

### SDD Artifacts

`specs/onepassword-rate-limit-fix/` contains the spec, plan, tasks, evidence, and checklist.

### Source Or Documentation Changes

- `kubernetes/infra/controllers/onepassword-operator/values.yaml`
- `tools/policy/check_onepassword_production_foundation.py`
- `tools/policy/tests/test_check_onepassword_production_foundation.py`
- `docs/runbooks/onepassword-operator.md`

## Tiered TDD And Validation Plan

**TDD expectation**: Add a failing policy test that rejects a 300-second production interval and verifies the development manual-refresh interval.

**Local checks**:

- `pytest -q tools/policy/tests/test_check_onepassword_production_foundation.py`
- `bash tools/policy/check_onepassword_operator_chart.sh`
- `python3 tools/policy/check_onepassword_production_foundation.py`
- strict development and production entrypoint render/substitution checks
- `python3 tools/architecture/render.py --check`
- affected harness/SDD validation

**Development smoke**: Push the branch, reconcile the shared development base, then inspect operator availability and polling interval.

**Fanout plan**: N/A.

**Evidence destination**: `specs/onepassword-rate-limit-fix/evidence.md`.

## Documentation Impact

Update `docs/runbooks/onepassword-operator.md`. Check generated architecture; no topology change is expected.

## Implementation Steps

1. Add a policy assertion and regression test.
2. Change shared chart values to 3600 seconds.
3. Document quota diagnosis, recovery, and latency.
4. Run local validation and exact-branch development smoke.
5. Commit, push, and open a PR.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Automatic production rotations take longer | Document the one-hour bound and deliberate urgent-rotation procedure. |
| Zero interval crashes operator 1.12.0 | Use a one-year development interval and explicit annotation-triggered reconciliation. |
| A lower interval returns | Enforce the minimum in policy tests. |
| Alerts remain during lockout | Record the provider reset dependency; preserve Secrets and SOPS consumers. |
| Shared rollout affects both clusters | Validate development first and use Flux GitOps. |

## Complexity Tracking

No constitution violations.
