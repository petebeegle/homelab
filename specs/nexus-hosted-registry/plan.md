# Nexus Hosted Docker Registry Implementation Plan

> **For agentic workers:** Execute approved tasks with `superpowers:executing-plans` in this session. The repository's Spec Kit tasks and analysis gate must be completed first. Read this plan together with `spec.md`.

**Branch**: `codex/nexus-hosted-registry` | **Date**: 2026-10-03
**Spec**: `specs/nexus-hosted-registry/spec.md`
**Goal**: Publish and retrieve local container images through a private, trusted hosted registry while preserving the existing pull cache.
**Architecture**: Terraform adds hosted storage and scoped publishing credentials to Nexus on Synology. A selectorless Kubernetes Service and EndpointSlice connect a new LAN Gateway HTTPRoute to the NAS hosted connector; the existing Synology group endpoint continues serving pulls. A disposable development Nexus validates the same repository definitions and Gateway behavior before deployment.
**Tech Stack**: Terraform Nexus provider 2.8.0, random provider 3.9.0, existing Nexus Community 3.87.1-01, Synology Container Manager/Compose, Flux, Cilium Gateway API, Python and Docker-compatible clients.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Terraform, registry permissions, external container networking, Kubernetes Gateway routing, validation tooling and operator documentation.
**Dependencies**: Existing Nexus admin access, valid consumer credentials, recovered/imported Nexus Terraform state, development kubeconfig/tfvars, GitHub branch access, working development wildcard TLS, NAS container-management access.
**Storage**: Production adds a dedicated file blob store under the existing `/nexus-data` mount. The development fixture deliberately uses `emptyDir` because it is disposable; it must not use production storage. No persistent Kubernetes app storage is introduced.
**Ingress**: `HTTPRoute` attached only to `gateway/internal`, section `https-gateway`.
**Secrets**: Local ignored tfvars/state, sensitive Terraform publisher-password output, private scratch client auth files; any tracked Kubernetes Secret must be SOPS encrypted. Do not print passwords, tokens, kubeconfigs, or unredacted state/plan JSON.
**Smoke Strategy**: Development branch profile for deployment readiness followed by an automated exact-URL registry push/pull and authorization harness, then production verification after reviewed rollout.
**Fanout Targets**: Independent review of provider/state recovery and Gateway/smoke coverage. Read-only development workflow research was delegated during planning and is consolidated in `research.md` and `evidence.md`.
**Development Validation**: New `nexus` branch profile with `--keep`; no shared cluster-base changes and therefore no `--include-cluster-base`. Clean up the disposable fixture after acceptance.
**Post-Implementation SDD Conformance**: Check the local workflow, requirements traceability, converge results, and evidence. No changes to the Spec Kit framework itself.

## Human Gates

**Spec Gate**: Approved on 2026-10-03: “yep go for it.”
**Checklist Status**: `checklists/registry-plan.md` reviews requirement coverage, rollout boundaries, and credential/state recovery.
**Plan Gate**: Approved on 2026-10-03: “go,” in response to the linked plan and request to generate/analyze tasks. This approval does not authorize a consumer-password reset.
**Expected Task/Analyze Gate**: Generate dependency-ordered `tasks.md`, run analysis, and obtain the required task/analysis approval before implementation.
**Credential Recovery Decision**: A question is pending about the current working consumer-password location versus a coordinated reset. Default remains recovery without rotation, consistent with the approved spec. A reset would require an explicit scope amendment and coordinated consumer updates; it is not silently included in this plan.

## Global Constraints

- Final publishing endpoint: `docker-push.lab.petebeegle.com`; existing group: `docker-registry.petebeegle.com`.
- Preserve existing Nexus repositories, data volume, UI connector 8081, group connector 8082, consumer identities, and repaired certificate automation.
- New publisher: `docker-publisher`, scoped to `docker-hosted`, with browse/read/add/edit only.
- No PRO-dependent subdomain connector or group deployment, public exposure, Nexus upgrade, or TLS verification bypass.
- Production apply must not recreate an existing repository or silently change an existing password.
- A readiness check or registry authentication challenge does not prove image publication.

## Constitution Check

- [x] Desired state is in Git; Flux owns Kubernetes deployment.
- [x] Development fixture and complete push/pull checks precede production changes.
- [x] Gateway API and existing private LAN exposure conventions are preserved.
- [x] No plaintext tracked secrets; state and runtime credentials stay protected and ignored.
- [x] Existing NAS persistence is retained; ephemeral fixture storage is explicit.
- [x] No Talos SSH or node configuration changes are introduced by the default plan.
- [x] Dedicated branch/worktree and documentation scope are recorded.
- [x] PR review/status checks remain integration gates.

Recheck before implementation commits and before rollout. There is no infrastructure-unavailable exception at planning time: development is reachable. A failed development test is a failure to fix, not an exception.

## Design Decisions

### Nexus and Terraform

Add `terraform/external/nexus/docker-hosted.tf` for `nexus_blobstore_file.hosted`, `nexus_repository_docker_hosted.hosted`, `nexus_security_role.docker_hosted_publish`, `random_password.docker_publisher`, and `nexus_security_user.docker_publisher`.

Use blob store/repository name `docker-hosted`, blob path `/nexus-data/docker-hosted`, `online=true`, HTTP connector 8083, Docker v1 disabled, DockerToken realm authentication, strict content validation, and `write_policy="ALLOW"`. Do not set a Nexus HTTPS connector or PRO-only subdomain. Preserve existing security realms.

Use explicit privileges `nx-repository-view-docker-docker-hosted-browse`, `read`, `add`, and `edit`, with no wildcard actions or inherited administrator roles. Generate a separate 32-character publisher password; expose it only through a sensitive output. Add nonsensitive outputs for publisher username and final endpoint.

Modify only group membership in `docker-registry.tf` to `[hosted, proxy]`. Keep existing resource addresses and consumer-role permissions unchanged. Group read permission is used for existing consumer pulls; do not grant the consumer hosted write privileges.

### State and consumer credential recovery

No local Nexus state or backend metadata was found. Existing live resources already correspond to the root configuration. The existing `docker` user is active and has `docker-group-view`; saved production tfvars and Talos-state credentials both returned HTTP 401 during read-only checks.

Before any production plan/apply, locate an authoritative state backup and current consumer secret. If no state is recoverable, back up the live configuration and import existing blob store, proxy, group, role, user, and singleton realms (`active`) into protected local state. Import the existing random password only with an independently verified working consumer password. Review random-provider import defaults: they can propose password replacement when generation settings differ. Do not hand-edit state or accept replacement as an expedient; recover matching state first or make an explicit reviewed import-compatibility adjustment with no password change.

Produce and inspect a baseline plan before adding the feature to production. Stop production rollout if any existing password change, resource replacement, unknown drift, or invalid consumer credential remains. Development implementation and validation can proceed using isolated credentials/state. If a password reset is chosen, revise the spec and this section before implementing coordinated Nexus and consumer-secret changes.

### Private HTTPS path

Add `kubernetes/apps/external/nexus-registry.yaml`, included by the existing external kustomization, containing:

- Selectorless Service `nexus-docker-hosted` in namespace `external`, TCP port 8083.
- IPv4 EndpointSlice with matching service label and port, targeting `${nfs_server}` (the NAS currently at `192.168.30.99`).
- HTTPRoute `nexus-docker-hosted`, hostname `docker-push.${cluster_domain}`, parent `gateway/internal`/`https-gateway`, prefix `/`, backend Service port 8083.

Set forwarded protocol/host metadata to the external HTTPS identity with a RequestHeaderModifier; preserve the original Host and all Docker `/v2/` paths. Use route request/backend timeouts of 300 seconds and validate large layer transfer within that boundary. Development tests must prove challenge `realm` and upload `Location` URLs keep external HTTPS. Do not add nginx or an extra proxy unless the direct route fails a specific compatibility test and a plan amendment documents the need.

The existing lab wildcard certificate is cert-manager owned. DNS currently resolves the production hostname to `192.168.30.241`; the development branch hostname resolves to `192.168.30.225`. No new public DNS record or Synology certificate is planned. Verify these from the actual publishing client's LAN network during smoke.

### NAS connector and deployment

Add `8083:8083` to `scripts/synology/nexus.docker-compose.yaml`; preserve `8081`, `8082`, user/group, volume mount, and resource limits. Confirm port 8083 is unallocated in Container Manager before deployment; its current TCP probe is refused, which alone is not allocation proof.

Inspect the current Container Manager project path, effective Compose, mount, and image ID before changing it. Install the reviewed Compose change through the existing NAS project mechanism, preserving the runtime image: no `latest` pull or image upgrade. A controlled container recreation is required for the additional port and can briefly interrupt the existing cache. Back up effective project configuration first, verify `/volume2/Nexus/nexus-data` remains attached, and validate group/UI health after recreation. Never use `down -v` or delete the data directory.

### Development fixture

Add an isolated `kubernetes/apps/nexus/branch/` workload and suspended `kubernetes/clusters/development/branches/nexus-template.yaml`, registered in the branch template library. Use namespace `nexus-${branch_slug}`, GitRepository and Kustomization `branch-nexus-${branch_slug}`, matching verifier cleanup conventions.

Run the same Nexus version as production, pinned after checking the actual image reference/digest; use `emptyDir` for `/nexus-data`, UID/GID compatible with the image, a 2 GiB memory limit with an explicitly bounded JVM, and a startup budget up to 20 minutes. Do not expose its UI/API publicly. Bootstrap the generated initial admin password through a protected exec/file path, rotate only this disposable admin credential, and configure the instance with a separate copy of the Nexus Terraform root and separate state. Verify the provider URL is the development port-forward before every apply.

Provide hosted and group Services/HTTPRoutes at `docker-push-${branch_slug}.dev.lab.petebeegle.com` and `docker-group-${branch_slug}.dev.lab.petebeegle.com`. Reuse the production route's relevant settings. The fixture's selector-backed Service does not verify production NAS EndpointSlice reachability; final production smoke must cover that layer.

Add `tools/development/smoke-profiles/nexus.json` for readiness, Service, and route checks. Built-in probes cannot prove authenticated HTTPS registry behavior; use a separate acceptance script with disposable client auth directories and clean image storage. The verifier also runs development Terraform init/validate/plan; stage required ignored development inputs first, and never pass `--terraform-apply` for this feature.

## Project Structure

| Path | Responsibility |
| --- | --- |
| `terraform/external/nexus/docker-hosted.tf` | Hosted blob/repository, writer role/user/password and outputs |
| `terraform/external/nexus/docker-registry.tf` | Add hosted-first group membership; preserve existing addresses |
| `scripts/synology/nexus.docker-compose.yaml` | Expose connector 8083 without data/image changes |
| `kubernetes/apps/external/nexus-registry.yaml` and `kustomization.yaml` | Production Service, EndpointSlice and LAN route |
| `kubernetes/apps/nexus/branch/{kustomization,nexus}.yaml` | Disposable development Nexus, Services and routes |
| `kubernetes/clusters/development/branches/{nexus-template,kustomization}.yaml` | Isolated Flux branch activation |
| `tools/development/smoke-profiles/nexus.json` | Generic branch readiness checks |
| `tools/development/tests/test_verify_branch_deploy.py` | Add supported-profile coverage |
| `tools/nexus/verify_registry.py` and `tests/test_verify_registry.py` | Exact-endpoint smoke orchestration and credential/redaction/digest safety tests |
| `scripts/NEXUS.md` | Operator setup, credentials, deploy/recovery and image commands |
| `docs/architecture.md` | Generated update via renderer only |
| `specs/nexus-hosted-registry/` | Plan, contracts, tasks, checklist, research and evidence |

## Review Focus

1. Missing Terraform state and import defaults must not cause consumer-password rotation or recreation of existing resources; inspect before/after plans.
2. Forwarded headers, redirects and upload locations must retain the trusted external hostname through multipart/chunked uploads; test a multi-layer image with a layer over 10 MiB.
3. Consumer and anonymous tokens must not permit writes; distinguish authentication denial from transport failure in negative tests.
4. Tag replacement must not be mistaken for deleting old content; verify both the new tag digest and old digest remain retrievable during the test.
5. Development cleanup must not touch production state, credentials, NAS storage, or persistent data; verify context/server and isolated namespace before every mutation.

## Tiered TDD And Validation Plan

Write meaningful tests before the acceptance utility: redact credentials from errors/reports, reject identical production/development state paths, distinguish HTTP denial from network failure, fail on digest mismatch, and validate returned realm/upload URL schemes and hosts. Add profile discovery coverage before registering the new profile. Configuration-only changes use Terraform validation, rendered manifests, and integration smoke instead of tests that merely restate resource fields.

**Local checks**: scoped `terraform fmt -check`, `terraform -chdir=terraform/external/nexus init -backend=false -input=false`, `terraform ... validate`; relevant Python unit tests; `docker compose -f scripts/synology/nexus.docker-compose.yaml config --quiet`; external and branch Kustomize renders with strict Flux substitution; repository policy checks applicable to changed paths; `python3 tools/architecture/render.py --write` then `--check`; `git diff --check`.

**Development**: use `verify_branch_deploy.py --app nexus --branch codex/nexus-hosted-registry --slug nexus-hosted-registry --kubeconfig <development> --timeout 20m --keep`. Confirm the API server is `https://192.168.30.170:6443`. Apply the same Nexus definitions only through a development-scoped port-forward using disposable state. Then run the acceptance matrix in `contracts/registry.md`.

**Production**: after required gates/review, safe state recovery, passing development tests, and a reviewed production plan, add the hosted resources/group member, expose NAS connector 8083, and reconcile the Git-managed route through Flux. Record the merged/reconciled revision, current route parent and conditions, endpoint reachability, TLS, image digests, authorizations, group regression, and follow-up Terraform plan.

**Completion evidence**: include actual tested client network, identity roles only, endpoint, image tag/digest, expected negative results, cleanup, and any unverified layer. Do not declare the push blocker resolved before the exact production URL passes.

**Fanout plan**: use an independent review for Terraform state/permissions and routing/smoke safety when implementation artifacts are ready. Keep edits coordinated in one worktree and consolidate all findings in `evidence.md`.

## Implementation Steps

1. Resolve production credential/state prerequisites; independently prepare the isolated development fixture and smoke harness after the task gate.
2. Add hosted repository, publisher, sensitive output, and hosted-first group membership; validate with the disposable Nexus state.
3. Add connector publication and Gateway resources; render and validate the exact forwarded-header behavior in development.
4. Complete positive/negative image smoke, docs, generated architecture and independent review; reconcile requirements through analyze/converge.
5. Review the production plan, deploy in the stated order, perform final exact-URL acceptance and group regression, and hand off the endpoint and secure credential retrieval instructions.

These are plan work packages, not approval to implement. Detailed task dependencies and executable steps belong in `tasks.md` after plan approval.

## Risks And Recovery

| Risk | Mitigation/recovery |
| --- | --- |
| Missing state or invalid old consumer password | Recover authoritative state/working secret first; never permit an implicit rotation. A coordinated reset needs a spec amendment. |
| NAS recreation interrupts pull cache | Preserve image ID and data mount; short controlled recreation; restore prior Compose and container settings if connector setup fails. |
| Blob-store or hosted data deletion during rollback | Stop writes and remove route/new group membership if needed; keep hosted repository/blob store/data. Do not use Terraform destroy after images have been accepted. |
| Gateway sends incorrect auth/upload URLs | Development protocol checks and clean-client multi-layer push; amend route headers before rollout. |
| Fixture startup failure or registry rate limits | Record actual failure, resource availability, and upstream response; fix or retry deliberately, without claiming infrastructure unavailable. |
| Smoke leaves secrets or artifacts | Use private scratch credentials, redact reports, clean disposable client storage and fixture; remove only uniquely named smoke images with admin credentials. |

## Documentation Impact And Exceptions

Update `scripts/NEXUS.md`, generated architecture, and implementation evidence. Do not rewrite the unrelated Synology certificate runbook. The worktree is `/home/vscode/homelab-worktrees/nexus-hosted-registry` because the preferred location was unwritable. The bundled `update-agent-context.sh` does not exist; do not synthesize it or modify AGENTS.md for this feature. No development-infrastructure exception is claimed.
