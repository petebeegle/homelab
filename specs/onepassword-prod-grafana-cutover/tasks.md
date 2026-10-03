# Tasks: Production Grafana Credential Cutover

**Input**: `specs/onepassword-prod-grafana-cutover/spec.md` and
`specs/onepassword-prod-grafana-cutover/plan.md`
**Risk Tier**: high
**Prerequisites**: Branch `codex/onepassword-prod-grafana-cutover` and matching
`specs/onepassword-prod-grafana-cutover/` artifacts. The spec and plan are
approved inputs to this task list.

## Human Gate Status

**Spec Gate**: Approved by the user with “get going” after review of the
Grafana-only scope.

**Plan Gate**: Approved by the user with “go” on 2026-08-29.

**Analyze Requirement**: Run before implementation because this is a
high-risk production authentication change.

## Phase 1: Setup

- [x] T001 Confirm branch, worktree fallback, approved gates, exact four-reference scope, and documentation expectations in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [x] T002 Capture the current production Grafana revision, readiness, generated-item Ready state, live reference names, no-output credential parity, and synthetic route health in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [x] T003 Run Spec Kit analysis against `specs/onepassword-prod-grafana-cutover/spec.md`, `specs/onepassword-prod-grafana-cutover/plan.md`, and `specs/onepassword-prod-grafana-cutover/tasks.md`, then resolve any blocking findings before implementation.

---

## Phase 2: User Story 1 - Use Grafana After Isolated Credential Cutover (Priority: P1)

**Goal**: Make all four Grafana administrator/OAuth consumers use the existing
generated credential while preserving the notification credential and legacy
rollback resources.

**Independent Test**: Strictly render production and prove exactly four
Grafana references use `grafana-credentials-onepassword`, `envFromSecret`
still uses `grafana-env`, legacy encrypted manifests/decryption remain present,
and no unrelated consumer reference changes.

- [x] T004 [US1] Add a failing cutover-boundary unit test covering all four generated references plus preserved `grafana-env` and legacy SOPS wiring in `tools/policy/tests/test_check_onepassword_production_foundation.py`.
- [x] T005 [US1] Extend the production 1Password policy to enforce the exact Grafana generated/legacy reference boundary in `tools/policy/check_onepassword_production_foundation.py`.
- [x] T006 [US1] Switch the Grafana Helm admin and OAuth mount references, while preserving `envFromSecret: grafana-env`, in `kubernetes/infra/monitoring/grafana/app.yaml`.
- [x] T007 [US1] Switch the Grafana external admin username and password references in `kubernetes/infra/monitoring/grafana/grafana-instance.yaml`.
- [x] T008 [US1] Run the focused policy unit test and policy executable, then record the red/green result in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [x] T009 [US1] Confirm the source diff contains only the four intended credential-reference changes and leaves routes, alerts, data sources, dashboards, `grafana-env`, SOPS manifests, Flux decryption, and non-Grafana consumers unchanged; record the review in `specs/onepassword-prod-grafana-cutover/evidence.md`.

---

## Phase 3: User Story 2 - Roll Back Only Grafana (Priority: P2)

**Goal**: Preserve a one-change Grafana-only rollback without deleting either
credential or the `OnePasswordItem`.

**Independent Test**: Review the resulting patch and verify one revert restores
all four references to `grafana-credentials` while both Secret publication paths
remain intact.

- [x] T010 [US2] Verify the four-reference revert boundary and retained legacy/generated resources against `kubernetes/infra/monitoring/grafana/app.yaml`, `kubernetes/infra/monitoring/grafana/grafana-instance.yaml`, and `kubernetes/clusters/production/infra/monitoring.yaml`, then record the rollback procedure in `specs/onepassword-prod-grafana-cutover/evidence.md`.

---

## Phase 4: Verification And PR

- [x] T011 Run strict production render/substitution, Kubernetes schema validation, architecture validation, the full Codex harness suite, and pre-commit; record exact commands and outcomes in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [x] T012 Record the documented development-monitoring coverage exception and substitute validation results in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [x] T013 Repeat the production read-only generated-item readiness, no-output parity, current Grafana health, operator-resource health, and synthetic route checks immediately before PR handoff; record timestamped results in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [x] T014 Run Spec Kit converge, incorporate any newly discovered work into `specs/onepassword-prod-grafana-cutover/tasks.md`, and finalize pre-merge evidence in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [x] T015 Re-check constitution gates and confirm every completed task is marked in `specs/onepassword-prod-grafana-cutover/tasks.md`.
- [x] T016 Commit the atomic implementation with a conventional commit message and record the commit SHA in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [x] T017 Push `codex/onepassword-prod-grafana-cutover` and open a gated PR containing the completed `specs/onepassword-prod-grafana-cutover/evidence.md`.

---

## Phase 5: Post-Merge Acceptance

- [ ] T018 After explicit merge approval, merge the PR and record the merge SHA in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [ ] T019 Reconcile production through Flux and record fetched/applied revisions, live four-reference state, Grafana rollout/pod UID, HelmRelease, Grafana/dashboard/data-source resources, HTTPRoute, `/api/health`, and synthetic results in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [ ] T020 Have the user complete Authentik login and a known dashboard refresh/time-range smoke with live data, then record the result without sensitive content in `specs/onepassword-prod-grafana-cutover/evidence.md`.
- [ ] T021 If any acceptance check fails, revert only the Grafana cutover commit through Git, reconcile production, and record recovery without deleting the generated Secret or `OnePasswordItem` in `specs/onepassword-prod-grafana-cutover/evidence.md`.

## Dependencies

- Setup tasks T001-T003 block implementation.
- User Story 1 tasks T004-T009 are sequential because the test must fail before
  policy and manifest changes and the source-boundary review depends on them.
- User Story 2 task T010 depends on the completed User Story 1 patch.
- Verification and PR tasks T011-T017 depend on both user stories.
- Post-merge tasks T018-T021 are gated by PR review and explicit merge approval;
  T021 runs only if T019 or T020 fails.

## Parallel Opportunities

No implementation fanout is planned. The four-reference change and its policy
invariant are deliberately kept sequential and atomic. Read-only live checks
may overlap local validation only when their results are consolidated into
`specs/onepassword-prod-grafana-cutover/evidence.md`.

## Implementation Strategy

The minimum viable increment is User Story 1 with User Story 2's retained
rollback verified before PR creation. Merge does not equal acceptance: automated
post-merge production checks must pass before the user performs the exact
authenticated Grafana smoke, and failure triggers the single-consumer revert.
