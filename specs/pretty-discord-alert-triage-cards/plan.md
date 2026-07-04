# Implementation Plan: pretty-discord-alert-triage-cards

**Branch**: `codex/pretty-discord-alert-triage-cards` | **Date**: 2026-07-04 | **Spec**:
`specs/pretty-discord-alert-triage-cards/spec.md`

**Input**: Feature specification from `specs/pretty-discord-alert-triage-cards/spec.md`

## Summary

Apply the already-approved upstream relay release to homelab desired state by updating the pretty-discord-alerts Deployment image to v1.4.0 and lowering normal log verbosity to info. Keep the change narrow, validate local render and workflow gates, and record that a real Grafana-to-relay Discord test alert remains required before verifier approval or merge readiness.

## Technical Context

**Risk Tier**: medium
**Workflow Tier**: medium
**Primary Areas**: Kubernetes, monitoring, Grafana alert delivery, SDD artifacts
**Dependencies**: Git, kubectl/kustomize, Python 3, Docker buildx evidence from upstream verification
**Storage**: N/A; relay is stateless and does not use PVCs
**Ingress**: N/A; no Gateway API or Ingress changes
**Secrets**: Existing SOPS-encrypted `grafana-env` secret reference is preserved; no plaintext secret edits
**Development Validation**: Manual smoke expected when kube context and credentials are available; otherwise record blocker and substitute local checks. One operator-visible Grafana/relay test alert is required before verifier approval or merge readiness.

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads; not applicable to this stateless relay.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/pretty-discord-alert-triage-cards`; sibling clone mode is explicitly requested and recorded.
- [x] Documentation impact identified; durable SDD evidence updated and generated architecture check required.
- [x] PR review/status checks are the review gate; no verifier approval, push, or PR will be created by the implementation owner.

## Project Structure

### SDD Artifacts

```text
specs/pretty-discord-alert-triage-cards/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/infra/monitoring/pretty-discord-alerts/deployment.yaml
specs/pretty-discord-alert-triage-cards/spec.md
specs/pretty-discord-alert-triage-cards/plan.md
specs/pretty-discord-alert-triage-cards/tasks.md
specs/pretty-discord-alert-triage-cards/evidence.md
```

## Tiered TDD And Validation Plan

**TDD expectation**: No code-level TDD seam exists for this manifest-only image/config bump. Use render validation, workflow validators, architecture check, and manual development smoke or a documented unavailable-infrastructure exception.

**Local checks**:

- `python3 tools/codex-harness/validate_active_implementation.py`
- `python3 tools/codex-harness/validate_implementation_plan.py --branch codex/pretty-discord-alert-triage-cards`
- `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner`
- `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --require-evidence`
- `kubectl kustomize kubernetes/infra/monitoring/pretty-discord-alerts`
- `python3 tools/architecture/render.py --check`

**Development smoke**: Manual. Attempt to inspect kube context availability and, if a development context is available, validate the Deployment path and trigger a Grafana test alert through the relay. If unavailable, record the blocker and leave the operator-visible alert gate pending for verifier approval.

**Evidence destination**: `specs/pretty-discord-alert-triage-cards/evidence.md`.

## Documentation Impact

No runbook, ADR, or generated architecture source change is required. `docs/architecture.md` is checked because Kubernetes source changes can affect generated architecture, but this image/env bump is expected not to require a rendered documentation update.

## Implementation Steps

1. Create the requested sibling clone from `origin/main` on branch `codex/pretty-discord-alert-triage-cards`.
2. Create and validate local owner workflow marker, implementation plan, attestation, and delegation token files under `.codex/tmp`.
3. Create durable SDD artifacts under `specs/pretty-discord-alert-triage-cards/`.
4. Update the pretty-discord-alerts Deployment image and log level.
5. Record upstream PR, tag, workflow, GHCR digest, and platform evidence.
6. Run local workflow, render, architecture, and SDD context checks.
7. Attempt development-cluster validation; record exact blocker or results.
8. Commit with a conventional commit message and stop before verifier approval, push, or PR creation.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| GHCR image tag is missing or multi-arch support is incomplete | Record upstream image verification including digest and platforms. |
| YAML render passes but Discord card formatting is wrong | Require one operator-visible Grafana/relay test alert before verifier approval or merge readiness. |
| Development kube context or credentials are unavailable to this agent | Record exact blocker and substitute local checks; leave merge readiness pending. |
| Accidentally changing unrelated desired state | Keep tracked edits limited to the Deployment and SDD artifacts; inspect git diff before commit. |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
