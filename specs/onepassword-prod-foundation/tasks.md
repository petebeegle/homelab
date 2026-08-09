# Tasks: onepassword-prod-foundation

**Input**: `specs/onepassword-prod-foundation/spec.md` and `plan.md`

## Phase A - Gates and tests

- [x] T001 Establish the isolated worktree/branch, stage ignored production inputs without output, and record the completed development gate.
- [x] T002 Complete specification, clarification review, plan, research, data model, contracts, quickstart, and requirement/security checklists.
- [x] T003 Run read-only Spec Kit analysis and resolve all critical/high findings before implementation.
- [x] T004 Add failing focused policy tests for production operator activation, dual bootstrap isolation, monitoring metadata/RBAC, ten-minute alerts, and unchanged SOPS consumers.

## Phase B - Production foundation

- [x] T005 Add production Terraform dual-bootstrap wiring and production-only non-secret `op://` reference with replacement trigger.
- [x] T006 Add the production Flux Kustomization for the shared operator after CRDs.
- [x] T007 Extend kube-state-metrics RBAC/custom resource metrics for metadata-only `OnePasswordItem` readiness.
- [x] T008 Add dedicated Grafana alerts for missing/unavailable operator and unready items, both pending ten minutes.
- [x] T009 Update generated Terraform docs, production runbook, and generated architecture.

## Phase C - Validation and evidence

- [x] T010 Run focused and existing unit tests, Terraform checks, strict dual-cluster renders/substitution, kubeconform, chart policy, architecture, harness, and affected repository checks.
- [x] T011 Prove the diff changes no existing SOPS manifest, decryption block, or consumer Secret reference.
- [x] T012 Bootstrap the separate production token through authenticated `op read`, verify both trust-root object identities, and record metadata-only evidence.
- [ ] T013 Reconcile the exact production branch revision and record Flux/operator readiness.
- [ ] T014 Run the production-vault canary through rotation and confirm default namespace cleanup.
- [ ] T015 Run Spec Kit converge, complete appended tasks, update evidence, commit, push, and open the gated PR.
