# Tasks: Nexus Hosted Docker Registry

**Branch**: `codex/nexus-hosted-registry`
**Input**: Approved `spec.md` and `plan.md` plus `research.md`, `data-model.md`, `contracts/registry.md`, and `quickstart.md` in this directory.

## Human Gate Status

**Spec Gate**: Approved by the user on 2026-10-03: “yep go for it.”
**Plan Gate**: Approved by the user on 2026-10-03: “go.”
**Analyze Requirement**: Run read-only cross-artifact analysis on this task list before implementation.
**Task/Analyze Gate**: Approved by the user on 2026-10-03: “ok”.
**Execution**: Inline in the dedicated worktree, with independent review where specified. No consumer-password reset is authorized.

## Task Format And Ownership

Each unchecked task is future work. `[P]` marks independent work that can run beside a peer at the same dependency level. `[US1]`, `[US2]`, and `[US3]` map to the approved stories. FR/SC references state acceptance obligations. Root owns integration and `evidence.md`; helpers must not concurrently edit the same files.

## Phase 1: Setup

- [x] T001 Confirm the task/analysis approval in `specs/nexus-hosted-registry/evidence.md`, retain branch `codex/nexus-hosted-registry` in `/home/vscode/homelab-worktrees/nexus-hosted-registry`, and record the initial revision and scoped baseline checks. Do not touch the unrelated checkout. (FR-011/012)
- [x] T002 Stage only necessary ignored Nexus/development tfvars and kubeconfig inputs through `/workspaces/homelab/.codex/tmp/implementation-secrets/nexus-hosted-registry/`, using `.codex/scripts/stage_implementation_secrets.sh` and `install_implementation_secrets.sh`; keep all generated state/auth files under protected `.codex/tmp/nexus-hosted-registry/`. Confirm the development kubeconfig server is `https://192.168.30.170:6443`; never print inputs. (FR-003/011)

## Phase 2: Shared Test Foundations

These prerequisites enable independent development work. Production state/password recovery is T018 and does not gate T003–T017.

- [x] T003 [P] Add failing tests in `tools/nexus/tests/test_verify_registry.py` for redacting raw/encoded credentials, rejecting production targets/state in development mode, distinguishing HTTP 401/403 denial from transport failure, rejecting digest mismatches, and validating relative/absolute realm/upload URLs against the expected HTTPS host. Run the focused unittest suite to establish the failing baseline before T005. (FR-003/007/010/011)
- [x] T004 [P] Update the exact supported-app assertion in `tools/development/tests/test_verify_branch_deploy.py` to require the new `nexus` profile and add assertions for its namespace, activation template, GitRepository, Kustomization and route names. Record the expected failing profile-discovery test before T007. (FR-011)
- [x] T005 Implement `tools/nexus/verify_registry.py` with the safety behavior tested by T003 and the CLI contract below. Use isolated client auth files and fresh OCI pull directories; do not count a shared Docker daemon's cached image as a clean-client pull. Run the focused tests and record the passing baseline in `specs/nexus-hosted-registry/evidence.md`. (FR-003/007/010/011)

## Phase 3: User Story 1 — Publish A Built Image (P1)

**Independent acceptance**: Publisher pushes a multi-layer image through hosted HTTPS; a clean client downloads matching content. Anonymous/invalid/consumer writes and publisher administration/deletion are denied. Tag replacement retains the old digest.

- [x] T006 [P] [US1] Create `kubernetes/apps/nexus/branch/kustomization.yaml` and `nexus.yaml`, with namespace `nexus-${branch_slug}`, a disposable Nexus Deployment, `emptyDir` data, Service-only admin API, hosted/group Services and internal HTTPS routes. Pin the deployed production Nexus image version/digest after read-only identification; use the plan's memory/startup limits and image-compatible UID/GID. Include external HTTPS header handling on the branch routes. (FR-005/007/011)
- [x] T007 [P] [US1] Create `kubernetes/clusters/development/branches/nexus-template.yaml`, register it in that directory's `kustomization.yaml`, and add `tools/development/smoke-profiles/nexus.json`. Use suspended GitRepository/Kustomization `branch-nexus-${branch_slug}`, namespace `nexus-${branch_slug}`, Gateway dependency, and the two planned development URLs. Make T004 pass; do not add the template to the live development root. (FR-005/011)
- [x] T008 [P] [US1] Create `terraform/external/nexus/docker-hosted.tf` with dedicated file blob store/repository `docker-hosted`, connector 8083, Docker v1 disabled, strict validation and ALLOW writes; add the exact four hosted privileges, role `docker-hosted-publish`, user `docker-publisher`, and independent 32-character password. Preserve current realm ownership and all existing addresses. Expose `nexus_docker_publisher_username`, `nexus_docker_publisher_password` (sensitive), and `nexus_docker_push_endpoint`. (FR-001/002/003/008)
- [x] T009 [P] [US1] Create `kubernetes/apps/external/nexus-registry.yaml` and include it from `kustomization.yaml`: selectorless Service/EndpointSlice `nexus-docker-hosted`, NAS `${nfs_server}` at port 8083, and HTTPRoute with `docker-push.${cluster_domain}`, internal HTTPS listener, prefix `/`, external HTTPS/host metadata, and 300-second timeouts. Preserve the existing group and DSM routes. Render strict substitutions and check the backend/route contract before runtime acceptance. (FR-005/007)
- [x] T010 [P] [US1] Add only `8083:8083` to `scripts/synology/nexus.docker-compose.yaml` and validate the Compose document. Preserve data mount, current connectors, image selection, UID/GID and resource limits; deployment must later use the captured running image without pulling `latest`. (FR-006/012)
- [x] T011 [US1] Extend `tools/nexus/verify_registry.py` and its tests with hosted publication checks: generate a uniquely named multi-layer image with a layer over 10 MiB; push using the publisher; download to fresh OCI storage and compare manifest/layer digests; replace the tag and retrieve both new and old digests. Assert denied anonymous/invalid/consumer pushes, denied publisher administrative listing, and denied publisher deletion of the test-owned component, followed by a successful read. Test failure paths before adding each orchestration branch. (FR-002/003/007/008/010; SC-001/003/004)

## Phase 4: User Story 2 — Preserve The Cache And Read Hosted Images (P1)

**Independent acceptance**: The existing consumer reads the hosted image through the group with the same digest, and still retrieves an upstream Docker Hub image. Hosted content wins a controlled name collision.

- [x] T012 [US2] Modify only member ordering in `terraform/external/nexus/docker-registry.tf` to put `nexus_repository_docker_hosted.hosted.name` before the current proxy. Preserve existing consumer password, role, realm, proxy, blob-store and connector declarations. Run scoped formatting/validation. (FR-004/012)
- [x] T013 [US2] Extend `tools/nexus/verify_registry.py` and tests with consumer group pull/digest comparison, an upstream-image regression pull, and hosted-first name-collision acceptance. Use a controlled collision only on the disposable fixture; never shadow a production upstream image for this test. Keep consumer credentials separate from publisher credentials. (FR-004/010; SC-002/003)
- [x] T014 [US2] Run scoped Terraform/Compose validation, relevant Python tests and strict production/branch renders; regenerate `docs/architecture.md` using `python3 tools/architecture/render.py --write`, then check it. Record outcomes and any actual failures in `specs/nexus-hosted-registry/evidence.md`; do not fabricate infrastructure exceptions. (FR-001/005/006/011/012)
- [x] T015 [US2] Commit the development-ready source and populated SDD artifacts with a conventional message, push branch `codex/nexus-hosted-registry`, then run `tools/development/verify_branch_deploy.py --app nexus --branch codex/nexus-hosted-registry --slug nexus-hosted-registry --kubeconfig <verified-development-config> --timeout 20m --keep`. Supply staged development tfvars; never pass `--terraform-apply`. Record the tested revision and fixture resource identities in `specs/nexus-hosted-registry/evidence.md`. (FR-011)
- [x] T016 [US2] Bootstrap only the fixture's generated admin password through a protected file/exec path and rotate that disposable admin credential. Copy `terraform/external/nexus/` source to a separate private scratch Terraform directory with development-only inputs/state; confirm its provider targets the development API port-forward. Apply the same proposed resources and run the full `tools/nexus/verify_registry.py` development acceptance matrix, including group/member ordering, role denials, TLS/realm/upload locations and clean-client content verification. (FR-001/002/003/004/005/007/008/010/011; SC-001/002/003/004)
- [x] T017 [US2] Record development results and cleanup in `specs/nexus-hosted-registry/evidence.md`: delete only the branch Flux Kustomization, wait for namespace deletion, then delete its GitRepository and private client/fixture scratch credentials. Prove the disposable data is gone and production state/NAS data were untouched; repeat failed checks only after a relevant fix. (FR-003/010/011; SC-005)

## Phase 5: User Story 3 — Reproduce And Operate The Registry (P2)

**Independent acceptance**: Reviewed plans preserve existing resources/data, operator instructions reproduce the configuration, and the production user path passes the same publication/consumer checks after safe rollout.

- [x] T018 [P] [US3] Recover the authoritative Nexus state backup and current consumer password from the approved source, without printing secrets. If state must be imported, use protected scratch backups and provider-supported imports for existing resources; account for random-password import defaults. Verify the current consumer password, obtain a no-destructive-change baseline, and save redacted evidence under `specs/nexus-hosted-registry/evidence.md`. This is a production gate: if recovery fails, leave it incomplete and do not reset credentials without an approved spec/plan amendment. (FR-003/012; SC-005)
- [x] T019 [P] [US3] Update `scripts/NEXUS.md` and `specs/nexus-hosted-registry/quickstart.md` with secure publisher-output retrieval, isolated client configuration, exact image examples, consumer versus publisher roles, state recovery, development commands, ordered production rollout, diagnostic failure layers, and rollback that retains populated hosted storage. Document that gateway/cert-manager owns the new endpoint's renewal. (FR-009; SC-004/005)
- [x] T020 [US3] After T014–T019, review a saved production plan for `terraform/external/nexus/` using recovered state and verified credentials. Accept only new hosted/publisher resources, intended outputs, and hosted-first group membership; block password rotation, existing-resource replacement, unexplained drift or deletion. Inspect Container Manager read-only for the effective project path, running image ID/digest, mount, UID/GID and connector allocations; record the exact reviewed deployment procedure and expected restart impact in `specs/nexus-hosted-registry/evidence.md`. (FR-006/009/012; SC-005)

## Phase 6: Review, Rollout And Final Evidence

- [x] T021 Obtain independent read-only review of the implemented Terraform permission/state handling and Gateway/smoke behavior; consolidate findings in `specs/nexus-hosted-registry/evidence.md`, fix authorized implementation defects, rerun only affected checks, and run Spec Kit converge to reconcile all approved requirements and unchecked tasks. (FR-001–012)
- [ ] T022 Commit the reviewed source/docs/evidence, validate complete SDD artifacts, push the branch, and create/update the single implementation PR with development results and remaining production rollout status. Use normal GitHub review/status gates before integration; do not mark production validation complete at PR creation. Record the PR/revision in `specs/nexus-hosted-registry/evidence.md`. (FR-009/011/012; SC-005)
- [ ] T023 Once T018/T020 and required integration/review gates are satisfied, apply the reviewed Nexus plan, install the reviewed `scripts/synology/nexus.docker-compose.yaml` port change through the inspected Container Manager project mechanism, and recreate the container using its existing image/data mount. Confirm UI/group health, existing repositories and data remain available, then let Flux apply the reviewed Gateway resources. Record separate Terraform, NAS, Git-source and Flux-applied states in `specs/nexus-hosted-registry/evidence.md`. (FR-001/002/003/004/005/006/012)
- [ ] T024 Run `tools/nexus/verify_registry.py` against `docker-push.lab.petebeegle.com` and `docker-registry.petebeegle.com` from the publishing LAN, using recovered consumer and new publisher credentials. Verify trusted TLS, actual parent/current route conditions, multi-layer push, clean-client content/digest match, tag replacement, authorization denials and upstream regression. Do not perform the development-only upstream-name collision in production. Clean up only uniquely owned smoke artifacts and record exact evidence in `specs/nexus-hosted-registry/evidence.md`. (FR-004/005/007/008/010; SC-001/002/003/004)
- [ ] T025 Verify the follow-up production Terraform plan has no unexpected changes, run final converge, update `specs/nexus-hosted-registry/{spec,plan,tasks,evidence}.md` with actual deployment/cleanup status, and hand off the working endpoint plus secure credential-retrieval command. Leave any blocked task unchecked and identify the unverified layer; never include the password in the response. (FR-009/011/012; SC-005)

## Dependency Graph And Parallel Opportunities

- T001 → T002 → independent T003/T004 → T005 after T003.
- After setup, T006/T007/T008/T009/T010 can proceed independently; T007 also requires T004. Keep their separate file ownership explicit.
- T011 follows T005. T012 follows T008. T013 follows T011 and T012 because it extends the same smoke utility; do not edit it concurrently.
- T014 follows T006–T013. T015 → T016 → T017 follows passing local validation.
- T018 and T019 can proceed independently alongside development work. T018 blocks production planning/apply, not the fixture implementation or development tests.
- T020 requires passing development acceptance, completed T018 and operator documentation. T021 may review development-ready work while T018 is pending, but cannot clear the production gate.
- T022 requires completed local/development checks and review. A draft PR may explicitly remain blocked on T018/T020; a production-complete claim may not.
- T023 requires safe state/credentials, the reviewed production plan, and integration/review gates. T024 follows rollout. T025 follows successful exact-endpoint acceptance.

Example safe fanout: one worker owns `docker-hosted.tf` (T008), a second owns `nexus-registry.yaml` and its kustomization entry (T009), and the root owns the fixture/smoke utility. Alternatively execute inline and delegate only T021 review. No concurrent edits to `docker-registry.tf`, shared branch kustomization, the smoke utility, or evidence.

## Smoke Utility Interface And Safety

`tools/nexus/verify_registry.py` takes `--environment development|production`, `--hosted-url`, `--group-url`, `--publisher-credentials-file`, `--consumer-credentials-file`, `--admin-credentials-file`, `--work-dir`, and `--report`. Credential files contain a JSON `username`/`password` pair and are mode 0600. Environment selection validates expected hostname suffixes and rejects accidental production endpoints during development. No credentials appear in process arguments.

Use a standard image client for pushes and a fresh OCI destination for independent pull verification (native Skopeo or a pinned Skopeo container, selected and recorded during implementation). Do not implement a new registry client unnecessarily. Capture returned auth/upload URLs using bounded protocol probes, and never log Authorization headers. The JSON report includes check names, outcomes, tags/digests, HTTP statuses and cleanup status, not response bodies containing credentials or tokens.

The development Terraform scratch directory/state is validated separately from production state paths before apply. A fixture port-forward alone is not proof of isolation: also verify kube API server, namespace, workload and provider URL.

## Requirement And Success-Criterion Coverage

| Requirement | Tasks |
| --- | --- |
| FR-001 | T008, T014, T016, T020, T023 |
| FR-002 | T008, T011, T016, T021, T023 |
| FR-003 | T002, T003, T005, T008, T011, T017, T018 |
| FR-004 | T012, T013, T016, T023, T024 |
| FR-005 | T006, T007, T009, T014, T016, T023, T024 |
| FR-006 | T010, T014, T020, T023 |
| FR-007 | T003, T005, T009, T011, T016, T024 |
| FR-008 | T008, T011, T016, T024 |
| FR-009 | T019, T020, T022, T025 |
| FR-010 | T003, T005, T011, T013, T016, T024 |
| FR-011 | T001, T002, T004, T006, T007, T014–T017, T022, T025 |
| FR-012 | T001, T008, T010, T012, T018, T020, T023, T025 |
| SC-001 | T011, T016, T024 |
| SC-002 | T013, T016, T024 |
| SC-003 | T011, T013, T016, T024 |
| SC-004 | T009, T016, T019, T024 |
| SC-005 | T017–T022, T025 |

## Delivery Strategy

The first demonstrable increment is US1 on disposable development infrastructure; US2 then proves compatibility with the group/cache. No production publication endpoint is handed off before US3 and final production acceptance. If recovery remains unavailable, complete permitted development work and document the production blocker without weakening the approved no-rotation constraint.
