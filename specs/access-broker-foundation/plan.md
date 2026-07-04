# Implementation Plan: access-broker-foundation

**Branch**: `codex/access-broker-foundation` | **Date**: 2026-07-04 | **Spec**:
`specs/access-broker-foundation/spec.md`

**Input**: Feature specification from `specs/access-broker-foundation/spec.md`

## Summary

Bootstrap the cross-repo foundation for the access broker. `homelab-access`
gets a Go service, tests, Dockerfile, and CI. This repo gets an inactive
Kubernetes app package that defines the deployment, storage, secret, service,
and public route contract without activating Flux or Cloudflare Tunnel routing.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Go app, Kubernetes, Gateway API, Flux preparation, storage,
secrets, SDD artifacts
**Dependencies**: Docker, Go container image, kubectl/kustomize, SOPS, Python 3
**Storage**: `nfs-csi-storage` PVC for future broker state
**Ingress**: Gateway API `HTTPRoute` to `gateway/public`, section `http-gateway`
**Secrets**: SOPS-encrypted `kubernetes/apps/access-broker/secret.yaml`
**Smoke Strategy**: none for live cluster because this foundation is inactive;
substitute checks are Go tests/build and Kubernetes render checks
**Fanout Targets**: app scaffold, Kubernetes package, SDD/evidence, render/build
validation
**Development Validation**: none with reason: no Flux activation or live route
is introduced in this PR
**Post-Implementation SDD Conformance**: local workflow docs reviewed

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/access-broker-foundation`; fallback worktree mode is
      intentional and recorded.
- [x] Documentation impact identified; SDD artifacts record activation deferral.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/access-broker-foundation/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/apps/access-broker/
.specify/feature.json
specs/access-broker-foundation/
```

External app repository changes:

```text
/home/vscode/homelab-access/
├── .github/workflows/ci.yml
├── Dockerfile
├── cmd/homelab-access/main.go
├── internal/config/config.go
├── internal/server/server.go
├── internal/server/server_test.go
├── go.mod
└── README.md
```

## Tiered TDD And Validation Plan

**TDD expectation**: Add handler tests for the app foundation before future
broker integrations. Kubernetes changes are validated with render checks and
secret encryption checks.

**Local checks**:

- `docker run --rm -v "$PWD":/src -w /src golang:1.23-alpine go test ./...`
- `docker build -t homelab-access:foundation .`
- `kubectl kustomize kubernetes/apps/access-broker`
- `python3 tools/architecture/render.py --check`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`

**Development smoke**: None. This implementation does not activate the app in
development or production and does not create a live route.

**Fanout plan**: App scaffold and Kubernetes package are independent; SDD and
evidence can be updated after both streams finish. Validation results are
consolidated into `specs/access-broker-foundation/evidence.md`.

**Evidence destination**: `specs/access-broker-foundation/evidence.md`.

## Documentation Impact

No generated architecture update is expected because the package is inactive and
not referenced by cluster Flux entrypoints. The SDD artifacts are the durable
documentation for this foundation slice.

## Implementation Steps

1. Bootstrap `homelab-access` with Go service, tests, Dockerfile, GitHub
   Actions, and README.
2. Add inactive `kubernetes/apps/access-broker` package with encrypted secret
   shape and public-route contract.
3. Run app tests/build and homelab render/workflow checks.
4. Record activation deferral, fallback worktree path, and verification results.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Placeholder deployment is accidentally activated | Do not add cluster-layer Flux Kustomization references in this PR |
| Secret placeholders leak or become confused with real values | Encrypt `secret.yaml` with SOPS and document activation deferral |
| wg-easy API behavior changes before integration work | Defer adapter implementation to a tested follow-up pinned to deployed wg-easy |
| Public route exists before one-time token implementation | Define route contract only; defer Cloudflare Tunnel and Flux activation |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
