# Tasks: home-assistant-automation-yaml-writable

**Input**: `specs/home-assistant-automation-yaml-writable/spec.md` and
`specs/home-assistant-automation-yaml-writable/plan.md`
**Risk Tier**: medium
**Prerequisites**: Branch `codex/home-assistant-automation-yaml-writable` and matching
`specs/home-assistant-automation-yaml-writable/` artifacts.

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel or fan out to a helper lane because it touches
  different files or performs read-only validation and has no dependency on
  another incomplete task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.
- Keep fanout coordinated through this task list and consolidate all results
  into `specs/home-assistant-automation-yaml-writable/evidence.md`.

## Phase 1: Spec And Plan

- [x] T001 [FR-SPEC] Create `specs/home-assistant-automation-yaml-writable/spec.md`.
- [x] T002 [FR-PLAN] Create `specs/home-assistant-automation-yaml-writable/plan.md`, including medium risk tier and development validation expectations.
- [x] T003 [FR-DOCS] Confirm documentation impact for `docs/runbooks/home-assistant.md` and generated architecture expectations.
- [x] T004 [FR-OWN] Create and validate `.codex/tmp/active-implementation`, `.codex/tmp/implementation-plan.yaml`, `.codex/tmp/implementation-owner-attestation.yaml`, and `.codex/tmp/delegation-tokens/home-assistant-automation-yaml-writable-owner.yaml`.

## Phase 2: Implementation

- [x] T005 [P] [FR-001] Remove the `/config/automations.yaml` volumeMount and add conditional seed logic in `kubernetes/apps/home-assistant/deployment.yaml`.
- [x] T006 [P] [FR-001] Remove the `/config/automations.yaml` volumeMount and add conditional seed logic in `kubernetes/apps/home-assistant/branch/home-assistant.yaml`.
- [x] T007 [P] [FR-002] Remove `automations.yaml=config/automations.yaml` from `kubernetes/apps/home-assistant/kustomization.yaml`.
- [x] T008 [P] [FR-002] Remove `automations.yaml=config/automations.yaml` from `kubernetes/apps/home-assistant/branch/kustomization.yaml`.
- [x] T009 [P] [FR-003] Delete `kubernetes/apps/home-assistant/config/automations.yaml`.
- [x] T010 [P] [FR-003] Delete `kubernetes/apps/home-assistant/branch/config/automations.yaml`.
- [x] T011 [P] [FR-006] Update `docs/runbooks/home-assistant.md` with the PVC-writable UI automation invariant.
- [x] T012 [FR-IMPL] Re-check constitution gates after implementation edits.

## Phase 3: Verification

- [x] T013 [FR-TEST] Run `kubectl kustomize kubernetes/apps/home-assistant`.
- [x] T014 [FR-TEST] Run `kubectl kustomize kubernetes/apps/home-assistant/branch`.
- [x] T015 [P] [FR-TEST] Run source and render checks proving no `automations.yaml` ConfigMap key and no `/config/automations.yaml` volumeMount in base and branch.
- [x] T016 [P] [FR-TEST] Run source and render checks proving the init seed is present and `automation: !include automations.yaml` remains in base and branch.
- [x] T017 [P] [FR-TEST] Run `python3 tools/architecture/render.py --check`.
- [x] T018 [P] [FR-TEST] Run workflow validators for active implementation, implementation plan, owner attestation, and SDD context.
- [x] T019 [P] [FR-TEST] Run `git diff --check`.
- [x] T020 [FR-SMOKE] Stage development smoke secrets and run `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-automation-yaml-writable --slug home-assistant-automation-yaml-writable --kubeconfig ~/.kube/homelab-development.config --push` if feasible.
- [x] T021 [FR-EVIDENCE] Record command outcomes, smoke evidence or exception, changed files, branch state, and smoke-tested SHA in `specs/home-assistant-automation-yaml-writable/evidence.md`.

## Phase 4: Commit

- [x] T022 [FR-PR] Commit with a conventional commit message.
- [x] T023 [FR-PR] Do not create verifier approval and do not open a PR per user request.

## Dependencies

- Complete Phase 1 before implementation edits.
- Complete Phase 2 before render/source validation.
- Complete T013 and T014 before render assertions in T015 and T016.
- Complete all validation and evidence updates before T022.

## Parallel Execution Examples

- T005 through T011 are file-independent and safe to fan out with single-owner consolidation.
- T015 through T019 are read-only checks and safe to run independently after renders exist.

## Implementation Strategy

Deliver the P1 fix first by removing the read-only mount and ConfigMap key, then add the fresh-PVC seed and documentation guardrail. Treat development smoke as the final operational signal before commit when credentials and cluster access are available.
