# Tasks: immich-app

**Input**: `specs/immich-app/spec.md` and `specs/immich-app/plan.md`
**Risk Tier**: high
**Prerequisites**: Branch `codex/immich-app` and matching `specs/immich-app/`
artifacts.

## Phase 1: Spec And Plan

- [X] T001 [FR-SPEC] Create `specs/immich-app/spec.md`.
- [X] T002 [FR-PLAN] Create `specs/immich-app/plan.md`, including tiered TDD,
      development validation, smoke strategy, and fanout targets.
- [X] T003 [FR-DOCS] Create `specs/immich-app/evidence.md`.

## Phase 2: Shared Storage And Database Infra

- [X] T004 [FR-003] Add local-path provisioner manifests in `kubernetes/infra/controllers/local-path-provisioner/`.
- [X] T005 [FR-004] Add CloudNativePG operator manifests in `kubernetes/infra/controllers/cloudnative-pg/`.
- [X] T006 [FR-003] Wire production and development infra Flux Kustomizations under `kubernetes/clusters/*/infra/`.

## Phase 3: Immich App And Auth

- [X] T007 [FR-001] Add Immich HelmRelease, OCI source, values, PVCs, route, and kustomization under `kubernetes/apps/immich/`.
- [X] T008 [FR-004] Add Immich CloudNativePG cluster and database Secret references under `kubernetes/apps/immich/`.
- [X] T009 [FR-006] Add Authentik Immich blueprint under `kubernetes/infra/authentik/blueprints/`.
- [X] T010 [FR-006] Update SOPS-encrypted secrets in `kubernetes/apps/immich/secret.yaml` and `kubernetes/infra/authentik/secret.yaml`.
- [X] T011 [FR-001] Wire `kubernetes/clusters/production/apps/immich.yaml` and production app dependencies.

## Phase 4: Operations And Navigation

- [X] T012 [P] [FR-008] Add Immich Grafana folder/dashboard resources under `kubernetes/infra/monitoring/grafana/`.
- [X] T013 [P] [FR-009] Add Immich to Homepage config in `kubernetes/apps/homepage/base/configmap.yaml` and development override.
- [X] T014 [P] [FR-009] Add Immich synthetic smoke coverage in `kubernetes/apps/synthetics/smoke/routes.spec.js`.
- [X] T015 [P] [FR-010] Add Immich runbook in `docs/runbooks/immich.md`.

## Phase 5: Verification

- [X] T016 [P] [FR-010] Run SOPS decrypt checks for changed secrets.
- [X] T017 [P] [FR-010] Run Terraform validation for development and production.
- [X] T018 [P] [FR-010] Run production and development kustomize renders.
- [X] T019 [P] [FR-010] Run synthetic smoke unit tests.
- [X] T020 [FR-010] Refresh and check `docs/architecture.md`.
- [X] T021 [FR-010] Run development validation or record a precise unavailable-infrastructure exception.
- [X] T022 [FR-010] Record command outcomes, exceptions, and final state in `specs/immich-app/evidence.md`.

## Phase 6: Commit And PR

- [X] T023 [FR-PR] Commit with a conventional commit message.
- [X] T024 [FR-PR] Push branch `codex/immich-app` and open a PR if requested after validation.

## Fanout Notes

- `[P]` tasks are independent validation, docs, dashboard, Homepage, or smoke
  tasks and may be run as helper lanes.
- Tracked edits to shared infra and app wiring remain sequential.
- All fanout output is consolidated into `specs/immich-app/evidence.md`.
