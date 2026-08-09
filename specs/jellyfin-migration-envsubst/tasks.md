# Tasks: Jellyfin Migration Envsubst

**Input**: `spec.md`, `plan.md`, `research.md`, `data-model.md`,
`contracts/migration-configmap.md`, and `quickstart.md`

**Tests**: Required. The failure is in a rendered integration boundary and the
existing behavioral test currently bypasses that boundary.

## Phase 1: Baseline and failing regression

- [X] T001 Record the merged production BuildFailed baseline and the still-live
  pre-migration workload in `specs/jellyfin-migration-envsubst/evidence.md`.
- [X] T002 [FR-001] [FR-002] [FR-003] Update
  `tools/development/tests/test_jellyfin_config_migration.py` to run a strict
  local Flux Kustomization build, extract the generated
  migration script, compare it to the source, and execute all migration cases
  against the rendered script.
- [X] T003 Run the focused test at the merged baseline and record the expected
  `bad substitution` failure in `specs/jellyfin-migration-envsubst/evidence.md`.
- [X] T004 Add pinned Flux CLI setup and the focused migration regression to the
  Kubernetes job in `.github/workflows/ci.yml`.

## Phase 2: Focused repair

- [X] T005 [FR-001] [FR-002] [FR-004] Add the documented
  `kustomize.toolkit.fluxcd.io/substitute: disabled` annotation only to the
  `jellyfin-config-migration` generator in
  `kubernetes/apps/jellyfin/kustomization.yaml`.
- [X] T006 [FR-003] Run the focused migration suite and confirm all existing
  copy, retry, and fail-closed cases pass against the rendered script.
- [X] T007 [FR-001] [FR-002] [FR-004] Run a strict full Jellyfin render and
  confirm the migration script is preserved while intended application values
  substitution remains enabled.

## Phase 3: Repository validation and review gate

- [X] T008 Run `python3 tools/architecture/render.py --check` and confirm no
  generated architecture update is required.
- [X] T009 Run `pre-commit run --all-files` and resolve only failures caused by
  this implementation.
- [X] T010 Re-check the constitution and inspect the final diff for unrelated,
  secret, storage, GPU, authentication, and route changes.
- [X] T011 Create `specs/jellyfin-migration-envsubst/evidence.md` with the
  consolidated results from all fanout lanes and local validation.
- [X] T012 Push the branch, open the focused PR, and require all GitHub status
  checks to pass before merge.

## Phase 4: Post-merge production acceptance

- [ ] T013 [P] [FR-005] Verify GitHub merge SHA, production Flux source fetched
  SHA, and `app-jellyfin` applied SHA; record timestamps and conditions.
- [ ] T014 [P] [FR-004] [FR-005] Verify the live Jellyfin deployment uses
  `Recreate`, the local target PVC, the retained read-only NFS source, and the
  expected migration-before-SSO init ordering.
- [ ] T015 [P] [FR-005] Verify migration init completion/logs and inspect
  relevant storage, database, authentication, and application errors.
- [ ] T016 [P] [FR-005] Probe the exact HTTPS web, public-info, branding, and SSO
  start/redirect paths without exposing OIDC state or secrets.
- [ ] T017 [FR-005] Consolidate production acceptance, known anonymous-auth
  limitations, and the development GPU exception into `evidence.md`.

## Phase 5: Cleanup decision

- [ ] T018 [FR-006] If every production acceptance layer passes, record that
  migration/rollback cleanup is eligible for a separate implementation; if any
  layer fails, iterate on the failure and leave all migration assets intact.

## Dependencies

- T001-T003 establish the failing test before T004-T005.
- T005 blocks T006-T012.
- T012 and PR merge block T013-T018.
- T013-T016 are independent read-only verification lanes and may run in
  parallel; T017 consolidates their evidence.
- T018 is last and never removes assets in this implementation.

## Parallel execution examples

- After merge, T013 can inspect GitHub and Flux revisions while T014-T015
  inspect Kubernetes state and T016 exercises exact user paths.
- All tracked repository edits remain owned by the main implementation lane;
  helpers return evidence only.
