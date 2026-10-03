# Feature Specification: Nexus Hosted Docker Registry

**Feature Branch**: `codex/nexus-hosted-registry`
**Created**: 2026-10-03
**Status**: Approved
**Risk Tier**: high
**Input**: User requested adding the missing hosted Docker repository, push permissions, and HTTPS endpoint through the repository after an image push to the existing group failed with “Deploying to groups is a PRO-licensed feature.”

## Human Gate Status

**Intent Brief**: Enable the operator and build agents to publish locally built container images to the existing Nexus Community instance on Synology. Keep existing Docker Hub pulls working, manage desired state in Git, and prove a real image push and pull through trusted HTTPS.

**Clarify Status**: Resolved through the conversation and approved spec assumptions, including hostname, writer separation, tag replacement, and private LAN exposure. A separate clarification interview is skipped because no blocking ambiguity remains.

**Spec Gate**: Approved by the user on 2026-10-03: “yep go for it,” in response to the linked spec and request to proceed to planning.

## Summary

Provide a private hosted Docker registry that accepts authenticated image pushes without a Nexus PRO license. Operators receive a working HTTPS endpoint and scoped publishing credentials. Existing clients retain the current Docker Hub cache endpoint and can also retrieve hosted images through that group.

Proposed publication endpoint: `docker-push.lab.petebeegle.com`. This endpoint is not currently provisioned. Its lab hostname fits existing Gateway DNS and certificate conventions; planning must confirm those prerequisites.

## Binding Sources

- `AGENTS.md`
- `.specify/memory/constitution.md`
- `docs/runbooks/spec-driven-development.md`
- `docs/runbooks/implementation-workflow.md`
- `docs/decisions/terraform-sensitive-values.md`
- `docs/decisions/cilium-gateway-api-ingress.md`
- `docs/decisions/flux-gitops-source-of-truth.md`
- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/development-cluster.md`
- `scripts/NEXUS.md` and `scripts/SYNOLOGY.md` for the existing external service deployment procedures; their legacy ingress examples do not supersede Gateway decisions.

## Scope

### In Scope

- A persistent hosted Docker repository in the existing Nexus instance, managed by Terraform.
- A dedicated publishing identity with credentials and permissions limited to the required hosted repository operations.
- Read access to the hosted images for existing registry consumers through the existing repository group.
- A trusted HTTPS publishing endpoint using the established private LAN Gateway exposure, with working DNS, certificate renewal, authentication challenges, and uploads.
- Repository-controlled Nexus container connector publication and deployment instructions.
- Operator documentation covering credentials, image tagging, push, pull, validation, deployment order, and recovery.
- Development validation and final exact-endpoint image push/pull evidence.

### Out Of Scope

- A Nexus edition change, PRO license, registry replacement, or Nexus version upgrade.
- Public internet exposure or new WireGuard exposure.
- Migrating the existing pull-cache hostname or its recently repaired Synology certificate automation.
- Migrating Nexus data to Kubernetes, redesigning storage, or general image retention/garbage-collection policies.
- Publishing the other agent's particular application image as the registry smoke test; that agent can retry after endpoint handoff.

## User Scenarios & Testing

### User Story 1 - Publish a built image (Priority: P1)

An operator or build agent authenticates with a dedicated registry publisher, tags a local image for the documented hosted endpoint, and pushes it using a standard Docker-compatible client.

**Why this priority**: The blocked image push is the user's immediate problem.

**Independent Test**: Publish a uniquely tagged disposable image containing multiple layers through the exact HTTPS endpoint, then retrieve it with a separate clean client and compare manifest digests. A login or `/v2/` authentication challenge alone does not satisfy this test.

**Acceptance Scenarios**:

1. **Given** valid publishing credentials and a locally built image, **when** the client pushes to the hosted endpoint, **then** all layers and the manifest are stored without a group-deployment license error.
2. **Given** a published image, **when** a separately authenticated clean client pulls it from the hosted endpoint, **then** the received manifest digest matches the published digest.
3. **Given** an existing tag and valid publisher credentials, **when** the operator intentionally republishes that tag, **then** the new manifest is retrievable; previously referenced immutable digests remain valid unless separately removed by an administrator.
4. **Given** missing credentials, invalid credentials, or the existing pull-only identity, **when** a client attempts to push, **then** publication is denied.

### User Story 2 - Preserve the pull cache and consume hosted images (Priority: P1)

Existing consumers continue pulling Docker Hub images through `docker-registry.petebeegle.com` and can pull locally published images through the same group.

**Why this priority**: Changing a shared registry must not break existing cluster image pulls or require write privileges on cluster consumers.

**Independent Test**: With the existing consumer identity, pull a known Docker Hub image and the disposable hosted image through the group; compare the hosted image digest with the direct hosted-endpoint digest.

**Acceptance Scenarios**:

1. **Given** the existing consumer credentials, **when** a client pulls a Docker Hub image through the group, **then** the pull succeeds without client reconfiguration.
2. **Given** a hosted image under the homelab namespace, **when** the consumer pulls it through the group, **then** it receives the same image published through the hosted endpoint.
3. **Given** a name present in both hosted storage and the upstream cache, **when** the group resolves that name, **then** the local hosted repository has precedence.

### User Story 3 - Reproduce and operate the registry (Priority: P2)

An operator can reproduce the configuration from reviewed repository changes and follow documented deployment and verification steps without discovering hidden manual setup.

**Why this priority**: The user explicitly identified Terraform as the management boundary; the previous certificate incident also demonstrated the cost of undocumented operational prerequisites.

**Independent Test**: Validate the configuration, review its plan, apply only the approved changes in the documented order, and confirm a follow-up plan contains no unexpected changes to the managed registry resources. Document any unsupported provider behavior explicitly.

**Acceptance Scenarios**:

1. **Given** the repository and authorized local credentials, **when** an operator follows the runbook, **then** the hosted repository, publisher, container connectivity, private DNS, and trusted endpoint are available.
2. **Given** invalid publishing credentials, **when** a login or push fails, **then** the documentation distinguishes authentication, authorization, DNS, TLS, connector, and group-versus-hosted failures.
3. **Given** existing persistent Nexus data, **when** the container configuration is updated or restarted, **then** the data volume and existing repositories are preserved.

## Requirements

- **FR-001**: Terraform MUST declare the hosted repository and its persistent storage configuration in the existing Nexus root; image pushes MUST work with the deployed Community edition.
- **FR-002**: A dedicated publisher MUST have hosted browse, read, add, and edit capabilities required by normal push/pull workflows, without administrative, repository-management, or delete permissions. Existing consumer identities MUST NOT gain hosted write access.
- **FR-003**: Anonymous writes MUST be rejected. Publisher secrets MUST remain out of tracked plaintext files, logs, and nonsensitive outputs, following the Terraform and Kubernetes secret policies.
- **FR-004**: The hosted repository MUST be included before the upstream proxy in the existing group. Existing cache pulls and group authentication MUST remain functional.
- **FR-005**: The publishing endpoint MUST use trusted HTTPS with automatic certificate renewal on the private LAN. New ingress MUST follow the Cilium Gateway API decisions and GitOps reconciliation rules. Internet-public exposure MUST NOT be added.
- **FR-006**: Repository-controlled runtime configuration MUST expose the hosted connector on the NAS while preserving the existing UI and group connectors, data mounts, and repository contents.
- **FR-007**: Registry authentication realms and upload locations returned to clients MUST use the reachable external HTTPS endpoint, without requiring TLS verification bypasses or an insecure-registry setting.
- **FR-008**: The implementation MUST support intentional tag replacement and image retrieval by digest, subject to normal storage availability.
- **FR-009**: Operator documentation MUST provide the actual endpoint, secure credential retrieval, login/tag/push/pull examples, deployment order, smoke checks, and rollback considerations for persistent data.
- **FR-010**: Validation MUST include authenticated multi-layer push and clean-client pull through the hosted URL, group pull of that image, regression pull of an upstream image, and denied anonymous/consumer writes. Status-only probes MUST NOT be reported as push validation.
- **FR-011**: Covered changes MUST pass development validation before production-oriented completion. Any unavailable-infrastructure exception MUST identify the unavailable layer and substitute checks; the plan MUST declare it before implementation if known.
- **FR-012**: Terraform plans MUST preserve existing repositories, users, and unrelated Synology resources; unrelated changes or destructive replacements MUST be resolved before apply.

## Risk And Validation Expectations

High risk because this adds authentication permissions and a production registry traffic path. The plan must declare SDD and workflow tiers, smoke strategy, review/fanout targets, and any infrastructure exceptions. It must address persistent storage preservation, container restart impact, routing headers for the Docker API, scoped secret handling, and rollback after images have been published.

Use development infrastructure for the registry behavior and Gateway path where available. Do not send development writes to production as a substitute without identifying that limitation and the approved deployment sequence. Planning must determine how to validate the external Nexus root safely when a second Nexus instance is unavailable.

Final acceptance requires a real push and matching-digest pull on the production user path, with the tested identity and client network recorded. Generated architecture documentation must be regenerated if Kubernetes or Terraform changes affect it.

## Success Criteria

- **SC-001**: An authorized publisher pushes one disposable multi-layer image and a clean client pulls the identical digest through the new trusted endpoint.
- **SC-002**: Existing consumers successfully retrieve both the disposable hosted image and a Docker Hub image through the existing group endpoint.
- **SC-003**: Anonymous, invalid-credential, and existing consumer publication attempts all fail; the publisher cannot administer repositories or delete stored artifacts.
- **SC-004**: The endpoint certificate is trusted without client exceptions, DNS resolves from the documented client network, and automatic renewal ownership is recorded.
- **SC-005**: Reviewed configuration and deployment instructions reproduce the registry setup, preserve existing data and cache access, and include evidence for each validation layer.

## Assumptions

- Proposed hosted repository name: `docker-hosted`; proposed publisher identity: `docker-publisher`.
- Proposed publication hostname: `docker-push.lab.petebeegle.com`, selected to reuse the established lab Gateway DNS and certificate conventions. Reachability must be checked during planning and smoke testing.
- The existing Nexus instance remains on Synology. Terraform manages its repository and authorization configuration; Flux manages any new Kubernetes routing resources.
- Local image names use a `homelab/` prefix to reduce collisions with Docker Hub content.
- Tags may be intentionally replaced for iterative development; deployment consumers can pin digests when immutability is required.
- Existing credentials are not rotated as part of adding the publisher.

## Open Questions

None blocking the spec draft. The stated assumptions are subject to the human spec gate; provider capabilities, connector allocation, runtime deployment mechanism, and development validation topology are planning work.

## Delivery status

Deployed and verified on 2026-10-03 through merged PR #420 (23b09eadf79bf9ba9b86639c8e0cff79fb22e0c0). All 25 tasks complete. Development13/13 and production12/12 acceptance checks passed; final Terraform plan has no changes. See evidence.md and the redacted reports.
