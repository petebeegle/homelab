# Feature Specification: 1Password Production Foundation

**Feature Branch**: `codex/onepassword-prod-foundation`
**Created**: 2026-08-09
**Status**: Approved
**Risk Tier**: high
**Input**: User-approved phase 2 of the SOPS-to-1Password migration: install the proven direct-auth operator in production, retain SOPS, and validate with a production-vault canary before any consumer cutover.

## Human Gate Status

**Intent Brief**: Reuse the development-proven operator configuration in production, bootstrap a separate production read-only service-account token without exposing it, retain `sops-age`, add operational alerts, and prove a disposable production-vault canary. No application Secret reference changes.

**Clarify Status**: No clarification questions were required. The approved phased plan and completed development evidence fix authentication, versions, vault isolation, rollout order, and acceptance.

**Spec Gate**: Approved by the user's supplied plan and instruction to continue after merging phase 1.

## Summary

Production reconciles the same Connect-disabled 1Password Operator configuration proven in development. Its token is bootstrapped from a separate 1Password service account with read-only access to `cluster production`, while SOPS remains active and all consumers remain unchanged. Monitoring alerts when the operator is unavailable or any `OnePasswordItem` is not Ready for ten minutes. A disposable production canary proves sync, rotation, and automatic restart without revealing values.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/terraform-sensitive-values.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `specs/onepassword-dev-foundation/evidence.md`

## Scope

### In Scope

- Reconcile the existing pinned, direct-service-account 1Password Operator in production with Connect disabled.
- Configure production bootstrap in `dual` mode using a non-secret `op://` reference for a production-only read-only service account.
- Preserve the production `sops-age` bootstrap Secret and all existing SOPS manifests, Flux decryption blocks, and consumer references.
- Export `OnePasswordItem` readiness through kube-state-metrics and add ten-minute alerts for operator unavailability and unready items.
- Run the existing disposable canary against `cluster production`, proving sync, rotation, Deployment restart, and cleanup with metadata-only evidence.
- Document bootstrap, validation, rollback, and evidence for this phase.

### Out Of Scope

- Creating application credential items or parallel application `OnePasswordItem` resources.
- Recovering Grafana credentials or comparing legacy/generated Secret bytes.
- Switching or removing any existing Secret consumer, SOPS manifest, decryption block, Age key, or SOPS tooling.
- Migrating Terraform/provider credentials from ignored `*.tfvars`.
- Deploying or using 1Password Connect.

## User Scenarios & Testing

### User Story 1 - Bootstrap Isolated Production Authentication (Priority: P1)

As a production operator, I can install the production 1Password trust root without exposing its token while retaining the existing SOPS trust root.

**Independent Test**: Run the production bootstrap-secret helper from an authenticated `op` session and inspect only resource metadata to verify both bootstrap Secrets exist; render the cluster and confirm no Connect resource or token-valued Secret is committed or rendered.

**Acceptance Scenarios**:

1. **Given** an authenticated account can read `op://cluster bootstrap/onepassword-production-operator/credential`, **When** production bootstrap runs, **Then** it creates or updates both trust roots without printing either value.
2. **Given** the production service account is restricted to `cluster production`, **When** the operator reconciles, **Then** the Kustomization, HelmRelease, and one-replica Deployment become Ready.
3. **Given** production bootstrap is rerun, **When** both trust roots already exist, **Then** the operation is idempotent and SOPS remains available.

### User Story 2 - Detect Production Reconciliation Failures (Priority: P2)

As an operator, I receive a critical alert if the 1Password Operator is unavailable or a managed item remains unready for ten minutes.

**Independent Test**: Render kube-state-metrics configuration and Grafana alert rules, verify RBAC and readiness metrics for `OnePasswordItem`, and evaluate that both rules have a ten-minute pending duration and safe no-data/error behavior.

**Acceptance Scenarios**:

1. **Given** the operator Deployment is missing or has fewer available than desired replicas, **When** that state persists for ten minutes, **Then** the operator-unavailable alert fires.
2. **Given** any `OnePasswordItem` reports a Ready status other than `True`, **When** it persists for ten minutes, **Then** the item-unready alert fires.
3. **Given** the monitoring query cannot execute, **When** Grafana evaluates the rule, **Then** the rule enters Error rather than silently reporting healthy.

### User Story 3 - Prove Production Sync Without Consumer Changes (Priority: P3)

As a reviewer, I can see metadata-only evidence that production direct authentication, synchronization, rotation, and automatic restart work before dual-publish begins.

**Independent Test**: Run the existing canary verifier against the production vault/item and kubeconfig; observe Ready, Secret resource-version change, pod UID change, and cleanup.

**Acceptance Scenarios**:

1. **Given** the production-vault canary exists with a built-in password field, **When** verification runs, **Then** the temporary item produces a Secret and Ready pod without value output.
2. **Given** the verifier rotates the disposable item field, **When** the polling window elapses, **Then** both Secret resource version and consuming pod UID change.
3. **Given** validation succeeds or fails, **When** cleanup runs without `--keep`, **Then** the temporary namespace is absent and existing production consumers remain unchanged.

## Requirements

- **FR-001**: Production MUST reconcile the official chart `connect` 2.4.1 with `connect.create=false`, operator 1.12.0, direct service-account auth, auto-restart, 300-second polling, info logging, one replica, CRD replacement upgrades, and explicit resources.
- **FR-002**: Production bootstrap MUST use `dual` mode and obtain the operator token through authenticated `op read` using only a non-secret `op://` reference in Terraform configuration.
- **FR-003**: The production token MUST NOT enter Git, Terraform state, Helm values, logs, evidence, or command arguments and MUST be distinct from the development token.
- **FR-004**: The production operator service account MUST be read-only and scoped only to `cluster production`; the bootstrap token item remains in the administrative `cluster bootstrap` vault.
- **FR-005**: All existing SOPS bootstrap state, manifests, decryption blocks, and workload Secret references MUST remain active and unchanged.
- **FR-006**: kube-state-metrics MUST have least-privilege list/watch/get access to `OnePasswordItem` and expose each item's Ready condition without Secret data.
- **FR-007**: Grafana MUST alert after ten minutes when the operator Deployment is missing/unavailable or at least one `OnePasswordItem` is not Ready.
- **FR-008**: Live production acceptance MUST prove Kustomization, HelmRelease, operator Deployment, canary item, generated Secret, initial pod readiness, Secret resource-version transition, pod UID transition, and default cleanup.
- **FR-009**: Validation and evidence MUST use metadata only and MUST not request or print Secret values.
- **FR-010**: Local checks MUST render and validate both cluster entrypoints, assert no Connect/token Secret render, validate Terraform and alert configuration, check architecture, and run affected unit/policy tests.
- **FR-011**: Failure to access the isolated production vault, bootstrap token, production kubeconfig, or required monitoring path MUST be recorded as a blocker; it MUST NOT weaken acceptance.

## Edge Cases

- An unauthenticated or wrong-account `op` session fails before the Kubernetes token Secret changes.
- A production token that can access the development vault violates isolation and blocks acceptance.
- A missing operator Deployment must alert rather than be treated as zero unavailable replicas.
- A new item with no Ready condition must count as unready.
- A rotation that updates the generated Secret but not the pod is a failed canary.
- Deleting a `OnePasswordItem` deletes its generated Secret and is treated as destructive; only the disposable canary namespace is automatically deleted.
- A 1Password outage may prevent refresh but must not delete an existing generated Secret or disrupt already-running workloads.

## Success Criteria

- **SC-001**: Both cluster entrypoints render and conform; production adds only the operator foundation and monitoring support, with no consumer reference changes.
- **SC-002**: Helm/policy validation reports zero Connect workloads and zero rendered token-valued Secrets.
- **SC-003**: Production has both bootstrap Secret objects, and the operator Kustomization, HelmRelease, and Deployment report Ready using the production-only service account.
- **SC-004**: Both alert rules are present with `for: 10m`, and the item readiness metric/RBAC contains no Secret field data.
- **SC-005**: The production canary observes a Secret resource-version and pod UID transition within ten minutes and removes its namespace.
- **SC-006**: The phase diff changes zero existing SOPS manifests, Flux decryption blocks, and live consumer Secret references.

## Assumptions

- The user can create a production-only read-only service account, store its token as the built-in `credential` field at `op://cluster bootstrap/onepassword-production-operator/credential`, and create `k8s--onepassword-system--canary` in `cluster production` with a non-empty built-in password field.
- Phase-1 development sync and rotation evidence satisfies the development-first gate.
- The existing canary verifier is cluster/vault parameterized and reusable without production-specific code.
- The user's instruction to continue approves this bounded phase's spec, plan, and task gates when analysis finds no critical or high gaps.

## Open Questions

- None.
