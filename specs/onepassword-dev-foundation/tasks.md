# Tasks: onepassword-dev-foundation

**Input**: `specs/onepassword-dev-foundation/spec.md` and `specs/onepassword-dev-foundation/plan.md`
**Risk Tier**: high
**Prerequisites**: Branch `codex/onepassword-dev-foundation`, matching approved artifacts, and completed requirements/security checklists

## Human Gate Status

**Spec Gate**: Approved by the user through the explicit request to implement the supplied migration plan.

**Plan Gate**: Approved by the same instruction for the bounded development-foundation phase.

**Analyze Requirement**: Run before implementation; proceed only with no unresolved critical/high findings.

## Phase 1: Setup

- [x] T001 Confirm the branch, worktree fallback, approved artifacts, clean phase scope, and documentation expectations in `specs/onepassword-dev-foundation/evidence.md`.
- [x] T002 Validate the SDD artifacts and completed checklists with `tools/codex-harness/validate_sdd_context.py` and the Spec Kit prerequisite scripts.

## Phase 2: Foundational Tests

- [x] T003 [P] Add failing tests for bootstrap provider selection, missing prerequisites, idempotent Secret application, temporary-file cleanup, and redacted output in `tools/codex-harness/tests/test_flux_bootstrap_secrets.py`.
- [x] T004 [P] Add failing tests for canary ID resolution, manifest application, Ready checks, metadata-only rotation proof, timeout handling, cleanup, and `--keep` in `tools/development/tests/test_verify_onepassword_operator.py`.
- [x] T005 [P] Add a local chart-render assertion script/test proving `connect.create=false` renders no Connect workload and no token-valued Secret in `tools/policy/check_onepassword_operator_chart.sh`.

## Phase 3: User Story 1 - Bootstrap Direct-Auth Operator

**Goal**: Reconcile the pinned direct-auth operator in development while keeping production SOPS-only behavior unchanged.

**Independent test**: Bootstrap unit tests pass; development manifests and chart render; Connect and token-valued rendered Secrets are absent.

- [x] T006 [US1] Pin 1Password CLI 2.35.0 with checksum verification in `.devcontainer/Dockerfile` while retaining the existing SOPS feature/mount.
- [x] T007 [US1] Implement `sops|dual|onepassword` bootstrap behavior and secure `op read` temporary-file handling in `terraform/scripts/install-flux-bootstrap-secrets.sh` and call it from `terraform/scripts/flux-install.sh`.
- [x] T008 [US1] Configure only development Terraform to select dual mode and pass the non-secret bootstrap reference in `terraform/development/main.tf` and `terraform/development/variables.tf`.
- [x] T009 [US1] Add the pinned, Connect-disabled, direct-auth operator namespace/HelmRelease manifests under `kubernetes/infra/controllers/onepassword-operator/`.
- [x] T010 [US1] Wire a waiting development Flux Kustomization at `kubernetes/clusters/development/infra/onepassword-operator.yaml` into `kubernetes/clusters/development/infra/kustomization.yaml` without changing production.

## Phase 4: User Story 2 - Prove Secret Sync And Rotation

**Goal**: Provide a temporary canary that proves initial sync, rotation, Deployment restart, and default cleanup without reading Secret values.

**Independent test**: Unit tests pass with stubbed CLIs; live validation observes Ready state, resource-version change, pod UID change, and namespace cleanup.

- [x] T011 [US2] Add parameterized temporary canary Namespace, `OnePasswordItem`, and Deployment manifests under `kubernetes/apps/onepassword-canary/smoke/`.
- [x] T012 [US2] Implement the metadata-only canary workflow and cleanup contract in `tools/development/verify_onepassword_operator.py`.
- [x] T013 [US2] Add the canary verifier to `tools/development/README.md` with prerequisites and no-secret-output constraints.

## Phase 5: User Story 3 - Produce Reviewable Evidence

**Goal**: Document and record each validation layer without overstating unavailable live proof.

**Independent test**: Reviewers can reproduce local/live commands and identify the exact tested HEAD, readiness transitions, and cleanup result.

- [x] T014 [US3] Update dual bootstrap, existing-cluster installation, canary, rotation, and cleanup procedures in `docs/runbooks/development-cluster.md`.
- [x] T015 [US3] Regenerate `docs/architecture.md` with `python3 tools/architecture/render.py --write` and review the new development operator relationship.
- [x] T016 [US3] Re-check all constitution gates and record documentation/tooling decisions in `specs/onepassword-dev-foundation/evidence.md`.

## Phase 6: Verification And Convergence

- [x] T017 Run bootstrap/canary unit tests, shell syntax, Terraform fmt/validate, Kubernetes renders, kubeconform, the chart assertion, architecture check, and relevant repository tests; record exact outcomes in `specs/onepassword-dev-foundation/evidence.md`.
- [x] T018 Run `verify_branch_deploy.py --app whoami --include-cluster-base` and the live 1Password canary against the exact pushed HEAD, or record the unavailable-prerequisite blocker without advancing phase 2.
- [x] T019 Run Spec Kit converge against the implemented tree, complete any appended tasks, and update `specs/onepassword-dev-foundation/evidence.md` with final SDD conformance and live-validation status.

## Phase 7: Commit And PR

- [x] T020 Commit the complete phase with a conventional commit and record the exact commit/HEAD in `specs/onepassword-dev-foundation/evidence.md`.
- [x] T021 Push `codex/onepassword-dev-foundation` and open a draft PR only when required non-empty artifacts/evidence pass the repository guard; keep phase 2 gated on live development acceptance.

## Phase 8: Rebase And Live Acceptance

- [x] T022 Rebase onto current `origin/main`, preserve upstream CI changes, retain the 1Password chart-render gate, and resolve the active-feature pointer.
- [x] T023 Rerun focused unit tests, Terraform validation, strict renders, kubeconform, architecture, production-render parity, and all pre-commit hooks after the rebase.
- [x] T024 Force-update PR #381 with lease protection and require the full GitHub Actions suite to pass on the rebased commit.
- [ ] T025 Verify the `development` cluster context and authenticated 1Password prerequisites, install dual bootstrap secrets, run the exact-HEAD development base/whoami smoke, and run the live rotation canary.
- [ ] T026 Record fetched/applied revisions, metadata-only rotation evidence, cleanup, final CI state, and any remaining external blocker in `specs/onepassword-dev-foundation/evidence.md`.

## Dependencies

- T001-T002 precede all implementation.
- T003-T005 are TDD prerequisites for T006-T012 and can run in parallel because they touch distinct test files.
- T006-T010 complete User Story 1 before live canary work.
- T011-T013 complete the independently testable canary workflow after the operator manifests exist.
- T014-T016 document the final interfaces after implementation stabilizes.
- T017 precedes live T018; T019 follows both or a recorded live blocker.
- T020-T021 occur only after evidence and convergence are current.
- T022-T023 precede the rewritten branch push in T024.
- T024 precedes exact-HEAD live validation in T025; T026 closes the phase only after both CI and live evidence are current.

## Implementation Strategy

The minimum useful phase is User Story 1 plus local chart/render checks, but the implementation is not accepted for production progression until User Story 2 passes live in development. Production installation, dual publishing, consumer cutover, and SOPS retirement remain separate implementations/PRs.
