# Evidence: Jellyfin Recreate Strategy

**Branch**: `codex/jellyfin-recreate-strategy`
**Risk Tier**: medium
**Started**: 2026-08-09

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent brief | PASS | User directed continued iteration and cleanup only after success. |
| Spec approval | PASS | The exact production blocker is within that authorization. |
| Clarify | SKIP | Production events and chart output identify one unambiguous field transition. |
| Plan approval | PASS | Narrow explicit-clear approach already reproduced in the pinned chart. |
| Checklist | PASS | `checklists/requirements.md`: 16/16 complete. |
| Tasks/analyze approval | PASS | Six requirements have task coverage; no ambiguity, conflict, or unmapped task remains. |
| Converge | PASS | No remaining buildable gap across six requirements, five success criteria, and four acceptance scenarios. |

## Baseline Production State

- PR #382 merged as `b01509171dac73b785ddfcd24747d58ef8a1ce8a`.
- Main CI run `31287600873` passed all six jobs at `2026-08-09T01:07:35Z`.
- Production Flux fetched the SHA at `01:06:53Z` and passed the prior envsubst
  blocker.
- `app-jellyfin` applied the generated ConfigMap, local PVC, and HelmRelease at
  `01:08:59Z`, then Helm failed four upgrade attempts and rolled back.
- Exact error: `spec.strategy.rollingUpdate: Forbidden: may not be specified
  when strategy type is 'Recreate'`.
- At `01:09:49Z`, the Kustomization was `Ready=False`,
  `HealthCheckFailed`; HelmRelease was `Stalled=True`, `RetriesExceeded`, with
  rollback successful.
- Live Jellyfin remained Ready on the old RollingUpdate deployment and
  `jellyfin-config-v2` NFS claim. The local claim was Pending under
  WaitForFirstConsumer. No migration pod, init logs, or marker existed.

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 -m unittest tools.development.tests.test_jellyfin_config_migration` at merged baseline | FAIL (expected) | Seven tests passed; the new strategy test failed because chart 3.2.0 rendered `type: Recreate` without `rollingUpdate: null`. |
| `python3 -m unittest tools.development.tests.test_jellyfin_config_migration` after repair | PASS | Eight tests passed: explicit strategy clear, Helm migration invariants, Flux script preservation/substitution, and four migration behaviors. |
| `helm template jellyfin jellyfin/jellyfin --version 3.2.0 -f kubernetes/apps/jellyfin/values.yaml` | PASS | Deployment strategy renders `rollingUpdate: null` followed by `type: Recreate`. |
| `python3 tools/architecture/render.py --check` | PASS | Generated architecture remains current. |
| SDD context validator | PASS | Branch and required artifacts are coherent. |
| `git diff --check` | PASS | No whitespace errors. |
| `pre-commit run --all-files` | PASS | All repository hooks passed. |

## GitHub Review Gate

- Draft PR: `https://github.com/petebeegle/homelab/pull/385`
- Initial head: `121e31e`
- Checks: PASS, 7/7 (`Agnix`, `GitGuardian Security Checks`, `Kubernetes`,
  `Pre-commit`, `Python`, `Secrets`, and `Terraform`).
- The Kubernetes job passed with Helm setup, the pinned chart render, and all
  eight focused Jellyfin tests in a clean runner.

## Development Validation

Exact chart rendering and focused migration execution substitute for routed
development smoke because the development environment lacks the pinned GPU
resource. The user explicitly directed us not to change that infrastructure.

## Documentation Impact

No canonical documentation or generated architecture change is expected. The
binding decision already requires Recreate; this implementation makes field
removal explicit.

## Exceptions And Follow-Ups

- Cleanup remains unsafe until the local volume binds, migration succeeds, the
  repaired application serves users, and binding authentication acceptance is
  satisfied.
- Anonymous smoke cannot prove existing user/admin mapping or native admin
  login.
