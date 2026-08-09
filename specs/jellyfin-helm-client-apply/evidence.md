# Evidence: Jellyfin Helm Client Apply

**Branch**: `codex/jellyfin-helm-client-apply`
**Risk Tier**: medium
**Started**: 2026-08-09

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent/spec/plan | PASS | User directed continued iteration; exact apply-mode repair proven by dry-run. |
| Clarify | SKIP | Managed fields and full server dry-run remove ambiguity. |
| Checklist | PASS | 12/12 complete. |
| Tasks/analyze | PASS | Six requirements mapped; no conflict or uncovered task. |
| Converge | PASS | No remaining buildable gap across six requirements and the two user stories. |

## Baseline Production State

- PR #385 merged as `5ead112b964db1f5a786391e1669e0203688e297`;
  main CI passed at `01:19:54Z`.
- Flux fetched the SHA, then Helm exhausted four upgrades and terminally stalled
  at `01:23:47Z` with the unchanged rollingUpdate/Recreate SSA error.
- Rollback succeeded. At `01:24:54Z`, old Jellyfin remained Ready on NFS; local
  PVC remained Pending and migration had never started.
- Live values contained `rollingUpdate: null`, proving null rendering was
  insufficient.
- Managed fields showed API-defaulted `rollingUpdate` was not owned by Helm's
  SSA manager. A read-only full Helm 4 server dry-run with client-side apply
  succeeded; the strategic patch produced only `strategy.type=Recreate`.

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 -m unittest tools.development.tests.test_jellyfin_config_migration` at baseline | FAIL (expected) | Eight tests passed; apply-mode regression found zero of two required declarations. |
| Focused suite after repair | PASS | Nine tests passed, including two client-side action declarations, no force, strategy, storage/init/GPU, Flux substitution, and migration behavior. |
| Architecture check | PASS | Generated architecture remains current. |
| SDD context validator | PASS | Branch and artifacts are coherent. |
| `git diff --check` | PASS | No whitespace errors. |
| `pre-commit run --all-files` | PASS | All hooks passed. |

## Development Validation

Focused full render and migration execution substitute for routed dev because
the development cluster lacks the pinned GPU resource. User excluded that
infrastructure work.

## Cleanup Gate

Not eligible. Migration has not run; authenticated user/admin/native-login
acceptance is also unverified.
