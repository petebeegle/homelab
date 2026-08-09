# Feature Specification: 1Password Development Foundation

**Feature Branch**: `codex/onepassword-dev-foundation`
**Created**: 2026-08-01
**Status**: Approved
**Risk Tier**: high
**Input**: User description: "Begin the approved phased replacement of SOPS Kubernetes credentials with the first-party 1Password Operator using direct service-account authentication and prove it in development before production."

## Human Gate Status

**Intent Brief**: The human supplied and approved a seven-phase migration plan. This first implementation must install only the development foundation, keep SOPS working, avoid 1Password Connect, and prove secret synchronization and Deployment restart behavior with a disposable canary before any production consumer changes.

**Clarify Status**: Skipped because the approved plan fixes the controller, authentication model, versions, rollout order, failure behavior, and validation expectations.

**Spec Gate**: Approved by the user through the explicit instruction to implement the supplied plan.

## Summary

Development-cluster operators can bootstrap and reconcile the first-party 1Password Operator alongside the existing SOPS path, then run a disposable canary that proves a 1Password item becomes a Kubernetes Secret and that rotating the item replaces the consuming Deployment pod. No production resources or existing application Secret references change in this implementation.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/sops-age-secrets.md`
- `docs/decisions/terraform-sensitive-values.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/runbooks/development-cluster.md`

## Scope

### In Scope

- Add the first-party 1Password Operator to the development Flux base using direct service-account authentication with 1Password Connect disabled.
- Add a dual bootstrap path that preserves `sops-age` while installing the development operator token from an authenticated 1Password CLI secret reference.
- Add pinned 1Password CLI tooling for the operator workstation/devcontainer.
- Add a temporary, cleanup-safe development canary and automated validation for initial sync, Ready status, Secret creation, item rotation, and Deployment pod replacement.
- Document exact bootstrap, canary, cleanup, evidence, and unavailable-credential behavior for this phase.

### Out Of Scope

- Installing the operator in production.
- Creating production or application vault items.
- Adding parallel `OnePasswordItem` resources for the 16 legacy SOPS manifests.
- Switching any existing Secret consumer or removing any SOPS resource, decryption block, tool, key, or policy.
- Migrating Terraform/provider credentials from ignored `*.tfvars` files.
- Adding production monitoring rules, which belongs to `onepassword-prod-foundation` after the CRD exists in production.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bootstrap Direct-Auth Operator (Priority: P1)

As a development-cluster operator, I can install the 1Password trust root without putting its service-account token in Git, Terraform state, command arguments, or logs, while the existing SOPS trust root continues to work.

**Why this priority**: The direct-auth operator and safe bootstrap are prerequisites for every later migration phase.

**Independent Test**: Render the development base and Helm chart, confirm that no Connect Deployment or token-valued Secret is present, then verify the development Flux Kustomization and HelmRelease become Ready when the bootstrap token exists.

**Acceptance Scenarios**:

1. **Given** an authenticated `op` CLI session and the configured bootstrap secret reference, **When** the dual bootstrap helper runs, **Then** it creates or updates both `flux-system/sops-age` and `onepassword-system/onepassword-service-account-token` without printing either value.
2. **Given** the development Flux base reconciles, **When** the operator HelmRelease renders, **Then** Connect is absent and exactly one direct-auth operator replica references the pre-created token Secret.
3. **Given** production still uses the shared bootstrap script, **When** its provider mode is not changed, **Then** its existing SOPS-only behavior remains unchanged.

### User Story 2 - Prove Secret Sync And Rotation (Priority: P2)

As a development-cluster operator, I can run a disposable canary that proves the full 1Password-to-Secret-to-workload path without revealing the canary value or leaving resources behind.

**Why this priority**: Production foundation work is gated on evidence that direct authentication, reconciliation, and rotation work on Talos/Kubernetes in development.

**Independent Test**: Run the dedicated canary verifier against a manually created development vault item with a `password` field and observe `OnePasswordItem Ready=True`, a generated Secret, a Ready pod, a Secret resource-version change, and a pod UID change after rotation.

**Acceptance Scenarios**:

1. **Given** a readable canary item, **When** validation starts, **Then** a temporary namespace, `OnePasswordItem`, and Deployment reconcile without logging Secret data.
2. **Given** the initial canary pod is Ready, **When** the canary field is changed to a new random value, **Then** the generated Secret changes within two polling intervals and the operator replaces the consuming Deployment pod.
3. **Given** validation succeeds or fails, **When** cleanup runs without `--keep`, **Then** the temporary namespace and all canary resources are removed.

### User Story 3 - Produce Reviewable Evidence (Priority: P3)

As a reviewer, I can distinguish locally rendered intent from live development proof and see any credential or infrastructure blocker without secret material in the evidence.

**Why this priority**: Secret-handling changes cannot advance to production on render-only evidence.

**Independent Test**: Review the implementation evidence for exact commands, tested HEAD, cluster context, readiness/rotation observations, cleanup state, and explicit exceptions.

**Acceptance Scenarios**:

1. **Given** local validation completes, **When** evidence is reviewed, **Then** it records chart rendering, manifest checks, unit tests, and architecture results separately from live cluster results.
2. **Given** 1Password authentication, item IDs, kubeconfig, or the development cluster is unavailable, **When** handoff occurs, **Then** the missing layer is marked blocked rather than reported as verified.

## Requirements *(mandatory)*

- **FR-001**: The development cluster MUST reconcile the official 1Password Operator with Connect disabled and direct service-account authentication enabled.
- **FR-002**: The chart MUST be pinned to `2.4.1`, the operator image/version to `1.12.0`, the polling interval to 300 seconds, auto-restart enabled, and one operator replica configured with explicit resources and info-level logs.
- **FR-003**: The service-account token MUST be obtained through `op read` into a permission-restricted temporary file and MUST NOT enter Git, Terraform state, rendered Helm values, command arguments, or command output.
- **FR-004**: Development bootstrap MUST support dual SOPS and 1Password trust roots, while the shared script MUST default to the existing SOPS-only behavior for production.
- **FR-005**: The development operator and bootstrap namespace MUST be expressed as durable GitOps state; canary resources MAY be temporary development validation state and MUST be cleaned up by default.
- **FR-006**: The canary verifier MUST resolve vault/item IDs through the authenticated CLI, create no durable credential file, and never request or print Kubernetes Secret data.
- **FR-007**: The canary verifier MUST prove `OnePasswordItem Ready=True`, generated Secret existence, active pod readiness, Secret resource-version change, and consuming pod UID change after rotation.
- **FR-008**: Local validation MUST prove the Helm render contains neither Connect workloads nor a token-valued Kubernetes Secret.
- **FR-009**: No existing SOPS manifest, Flux decryption block, application Secret reference, or production resource MAY be removed or switched in this implementation.
- **FR-010**: Documentation and evidence MUST state that live development validation is required before `onepassword-prod-foundation` begins and must record any unavailable external prerequisite precisely.
- **FR-011**: Tests MUST cover bootstrap mode validation, redaction/no-output behavior, canary cleanup, timeout/failure handling, and Connect-disabled Helm rendering.

## Edge Cases

- An empty, unreadable, or malformed 1Password secret reference fails before modifying the token Secret.
- Missing `op`, `kubectl`, `flux`, Age key, kubeconfig, vault, item, or canary `password` field produces an actionable error without printing values.
- Failure after canary rotation still attempts namespace cleanup; `--keep` is the only way to retain resources.
- A canary rotation that updates the Secret but not the pod is a failure, not partial success.
- Operator/1Password unavailability must leave an already-generated Secret intact; destructive outage simulation is deferred unless it can be performed without affecting other development resources.

## Success Criteria *(mandatory)*

- **SC-001**: Both cluster entrypoints render successfully and production output is unchanged except for shared non-behavioral tooling where explicitly documented.
- **SC-002**: Helm rendering contains zero Connect Deployments/Services and zero Secret manifests containing the operator token.
- **SC-003**: All focused bootstrap and canary unit tests pass without any fixture secret appearing in captured stdout or stderr.
- **SC-004**: On the development cluster, the operator and canary reach Ready, rotation is observed within 10 minutes, and the consuming pod UID changes.
- **SC-005**: Default cleanup leaves zero namespaces or canary resources associated with the validation slug.
- **SC-006**: No production Kustomization, existing Secret consumer, SOPS manifest, or decryption block changes behavior in the phase diff.

## Assumptions

- The user has a 1Password account with service-account support and can create the development vault, read-only service account, bootstrap token item, and canary item.
- The bootstrap token is stored at the documented admin-only 1Password reference; the canary is a disposable Login item with a non-empty built-in `password` field.
- Direct operator access to 1Password over the existing cluster egress path is allowed.
- The user instruction to implement the supplied detailed plan approves this phase's spec, plan, and task intent; live acceptance still gates the next PR.
- The worktree fallback under `/home/vscode/homelab-worktrees/` is used because `/workspaces/homelab-worktrees/` is not writable.

## Open Questions

- None.
