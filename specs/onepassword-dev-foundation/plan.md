# Implementation Plan: onepassword-dev-foundation

**Branch**: `codex/onepassword-dev-foundation` | **Date**: 2026-08-01 | **Spec**: `specs/onepassword-dev-foundation/spec.md`

**Input**: Feature specification from `specs/onepassword-dev-foundation/spec.md`

## Summary

Install the official 1Password Operator only in the development Flux base with 1Password Connect disabled and direct service-account authentication. Extend bootstrap with an explicit dual-provider mode that obtains the operator token through an authenticated pinned `op` CLI without exposing it. Add a temporary development canary verifier that proves `OnePasswordItem` readiness, generated Secret existence, rotation, automatic Deployment restart, and cleanup. Preserve all existing SOPS and production behavior.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Kubernetes, Flux, Terraform bootstrap tooling, secrets, development validation, devcontainer, documentation
**Dependencies**: Flux Helm/Kustomize controllers, Kubernetes 1.35, 1Password Helm chart `connect` 2.4.1, 1Password Operator 1.12.0, 1Password CLI 2.35.0, Python 3 standard library, kubectl, Helm, kubeconform
**Storage**: N/A; Connect is disabled and the operator/canary require no PVC
**Ingress**: N/A; the operator and canary have no Gateway route
**Secrets**: Existing SOPS/Age remains active. The new operator service-account token is an out-of-band bootstrap Secret loaded from an `op://` reference into a mode-0600 temporary file and never rendered by Helm or stored in Terraform state.
**Smoke Strategy**: Dedicated development-only operator canary plus `verify_branch_deploy.py --app whoami --include-cluster-base` to prove the changed development base reconciles without regressions
**Fanout Targets**: N/A; no sub-agent fanout was requested, and tracked changes share manifests/tooling that are safer to execute sequentially
**Development Validation**: Manual canary rotation plus whoami profile with `--include-cluster-base`; record `smoke_profile: none` only if authenticated 1Password prerequisites or development infrastructure are unavailable
**Post-Implementation SDD Conformance**: Local and upstream Spec Kit conformance review required because durable SDD artifacts and a high-risk workflow are used; no Spec Kit template behavior changes

## Human Gates

**Spec Gate**: Approved by the user through the explicit request to implement the supplied decision-complete migration plan.

**Checklist Status**: Requirements checklist and `checklists/security.md` completed before tasks.

**Plan Gate**: Approved by the same user instruction; this plan is the first bounded implementation of the supplied phased design and does not broaden production scope.

**Expected Task/Analyze Gate**: Tasks plus read-only analyze required before implementation; the user's implementation instruction approves proceeding when analyze reports no critical or high gaps.

## Constitution Check

*GATE: Passed before tracked implementation edits and must be re-checked before commit.*

- [x] GitOps source of truth preserved; operator/namespace/HelmRelease are durable Git state, while canary and bootstrap credentials are explicitly temporary/bootstrap state.
- [x] No production-first mutation; development operator/canary and base smoke precede phase 2.
- [x] Gateway API invariant preserved; no route or Kubernetes `Ingress` is added.
- [x] SOPS invariant preserved; all existing encrypted Secrets and `sops-age` remain, and no plaintext Secret manifest is staged.
- [x] NFS default considered; no persistence is introduced.
- [x] Talos boundary preserved; validation uses Kubernetes/Flux APIs and no SSH.
- [x] Branch is `codex/onepassword-dev-foundation`; approved sibling worktree fallback is recorded because the default parent is not writable.
- [x] Documentation impact identified in the development runbook, architecture output, SDD artifacts, and evidence.
- [x] PR review/status checks remain the review gate.

## Project Structure

### SDD Artifacts

```text
specs/onepassword-dev-foundation/
├── checklists/
├── contracts/
├── data-model.md
├── evidence.md
├── plan.md
├── quickstart.md
├── research.md
├── spec.md
└── tasks.md
```

### Source Or Documentation Changes

```text
.devcontainer/Dockerfile
terraform/development/{main.tf,variables.tf}
terraform/scripts/{flux-install.sh,install-flux-bootstrap-secrets.sh}
kubernetes/infra/controllers/onepassword-operator/
kubernetes/clusters/development/infra/{kustomization.yaml,onepassword-operator.yaml}
kubernetes/apps/onepassword-canary/smoke/
tools/development/{verify_onepassword_operator.py,tests/test_verify_onepassword_operator.py}
docs/runbooks/development-cluster.md
docs/architecture.md
```

## Tiered TDD And Validation Plan

**TDD expectation**: Add failing unit tests first for bootstrap mode behavior and the canary command workflow, then implement scripts/manifests. Manifest behavior has local render/Helm assertions before live reconciliation.

**Local checks**:

- `bash -n terraform/scripts/flux-install.sh terraform/scripts/install-flux-bootstrap-secrets.sh`
- `python3 -m unittest tools.development.tests.test_verify_onepassword_operator`
- `terraform -chdir=terraform/development fmt -check && terraform -chdir=terraform/development validate`
- `kubectl kustomize kubernetes/infra/controllers/onepassword-operator`
- `kubectl kustomize kubernetes/clusters/development > /tmp/onepassword-development.yaml`
- `kubectl kustomize kubernetes/clusters/production > /tmp/onepassword-production.yaml`
- `kubeconform -summary -ignore-missing-schemas /tmp/onepassword-development.yaml /tmp/onepassword-production.yaml`
- `helm template onepassword-operator 1password/connect --version 2.4.1 --namespace onepassword-system` with the committed direct-auth values reproduced as `--set` flags; assert zero Connect workloads and zero token-valued Secret
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`
- Relevant CI-equivalent policy and repository unit tests

**Development smoke**: Install the dual bootstrap trust roots, push the exact branch, run `verify_branch_deploy.py --app whoami --branch codex/onepassword-dev-foundation --slug onepassword-dev-foundation --push --include-cluster-base`, then run the canary verifier with the development vault/item and confirm cleanup. The canary must observe rotation within 10 minutes and a new pod UID.

**Automated smoke preference**: The whoami profile proves branch fetch/base reconciliation; the dedicated canary proves the secret path. Neither is replaced by pod readiness alone.

**Completion evidence**: Record exact HEAD, bootstrap mode, token reference identifier without its value, Flux fetched/applied SHA, operator Kustomization/HelmRelease readiness, `OnePasswordItem` Ready state, Secret resource-version transition, old/new pod UIDs, and cleanup. Do not record Secret data.

**Fanout plan**: Sequential local execution; no helper lanes. All outcomes consolidate into `specs/onepassword-dev-foundation/evidence.md`.

**Evidence destination**: `specs/onepassword-dev-foundation/evidence.md`.

## Documentation Impact

- Extend `docs/runbooks/development-cluster.md` with dual bootstrap prerequisites, manual existing-cluster token installation, canary setup/validation, and cleanup.
- Regenerate `docs/architecture.md` because a development Flux Kustomization and controller are added.
- Defer the binding secret ADR/constitution/AGENTS changes until the retirement implementation; this phase still complies with the accepted SOPS decision and introduces no committed Secret manifest.

## Implementation Steps

1. Pin the operator workstation `op` CLI and add tests for bootstrap/canary safety behavior.
2. Implement explicit SOPS/dual/1Password bootstrap modes, enabling only development dual mode and leaving production default behavior unchanged.
3. Add the Connect-disabled direct-auth operator HelmRelease and development Flux dependency.
4. Add the temporary canary manifests and verifier, then complete documentation and generated architecture changes.
5. Run local validation, development base/canary smoke when credentials are available, converge, and record evidence. Do not start production foundation without live sync/rotation proof.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| The chart name implies Connect and defaults to deploying it | Pin the chart and explicitly set `connect.create=false`; render the chart and assert that no Connect workload exists. |
| The service-account token leaks through Terraform, Helm, logs, or process arguments | Pass only an `op://` reference through Terraform; `op read` writes directly to a protected temporary file used with `kubectl --from-file`; tests use sentinel values and assert redaction. |
| Shared bootstrap changes disrupt production | Default provider mode remains `sops`; only development Terraform sets `dual`; render and diff production behavior. |
| Auto-restart does not replace the consuming pod | Canary acceptance requires both Secret resource-version and pod UID transitions; otherwise the smoke fails. |
| External 1Password or development credentials are unavailable | Complete local implementation and record an explicit live-validation blocker; do not advance to phase 2. |
| Temporary canary resources remain after failure | The verifier uses `finally` cleanup by default and requires explicit `--keep` to retain the namespace. |

## Complexity Tracking

No constitution violations require justification.
