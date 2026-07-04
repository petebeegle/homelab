# Tasks: access-broker-foundation

**Input**: `specs/access-broker-foundation/spec.md` and
`specs/access-broker-foundation/plan.md`
**Risk Tier**: high
**Prerequisites**: Branch `codex/access-broker-foundation` and matching
`specs/access-broker-foundation/` artifacts.

## Format: `[ID] [P?] [Req] Description`

## Phase 1: Spec And Plan

- [x] T001 [FR-SPEC] Create `specs/access-broker-foundation/spec.md`.
- [x] T002 [FR-PLAN] Create `specs/access-broker-foundation/plan.md`,
      including tiered TDD and development validation expectations.
- [x] T003 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations in `specs/access-broker-foundation/evidence.md`.

## Phase 2: App Repository Foundation

- [x] T004 [P] [FR-001] Create Go service scaffold in `/home/vscode/homelab-access`.
- [x] T005 [P] [FR-002] Add Dockerfile, `.dockerignore`, `.gitignore`, CI, and
      README in `/home/vscode/homelab-access`.

## Phase 3: Homelab GitOps Foundation

- [x] T006 [P] [FR-003,FR-005] Add inactive Kubernetes app package under
      `kubernetes/apps/access-broker/`.
- [x] T007 [P] [FR-006] Add and SOPS-encrypt
      `kubernetes/apps/access-broker/secret.yaml`.
- [x] T008 [FR-004] Confirm no production or development Flux activation and no
      Kubernetes `Ingress` resources were added.
- [x] T009 [FR-IMPL] Re-check constitution gates after implementation edits.

## Phase 4: Verification

- [x] T010 [FR-TEST] Run app Go tests in the Go container.
- [x] T011 [FR-TEST] Run app Docker build.
- [x] T012 [FR-TEST] Run `kubectl kustomize kubernetes/apps/access-broker`.
- [x] T013 [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [x] T014 [FR-TEST] Run workflow/SDD context validator.
- [x] T015 [FR-SMOKE] Record no-live-smoke exception because the app is inactive.
- [x] T016 [FR-EVIDENCE] Record command outcomes, SHAs, skipped checks,
      exceptions, and final states in `specs/access-broker-foundation/evidence.md`.

## Phase 5: Commit And PR

- [x] T017 [FR-PR] Commit homelab changes with a conventional commit message.
- [x] T018 [FR-PR] Push branch `codex/access-broker-foundation` and open PRs for
      both repositories when credentials are available.
