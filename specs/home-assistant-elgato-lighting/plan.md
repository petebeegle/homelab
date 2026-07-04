# Implementation Plan: home-assistant-elgato-lighting

**Branch**: `codex/home-assistant-elgato-lighting` | **Date**: 2026-07-04 | **Spec**:
`specs/home-assistant-elgato-lighting/spec.md`

**Input**: Feature specification from
`specs/home-assistant-elgato-lighting/spec.md`

## Summary

Document the safe Elgato Light onboarding path for Home Assistant. Elgato Light
is a runtime config-flow integration discovered through zeroconf or added
manually by host/IP, so this implementation updates operator guidance and SDD
evidence without adding declarative Home Assistant integration YAML or committing
runtime storage.

## Technical Context

**Risk Tier**: tiny
**Workflow Tier**: docs-only
**Primary Areas**: documentation, SDD artifacts
**Dependencies**: Home Assistant docs, existing Home Assistant kustomizations
**Storage**: Existing Home Assistant PVC remains unchanged; runtime integration
state stays under `/config/.storage`
**Ingress**: No Gateway API route changes
**Secrets**: No SOPS changes
**Development Validation**: none; docs-only change with local render checks as
substitute validation

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/home-assistant-elgato-lighting`; worktree/current-checkout mode is
      intentional and recorded when relevant.
- [x] Documentation impact identified; docs updated or no-docs rationale
      recorded.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/home-assistant-elgato-lighting/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
docs/runbooks/home-assistant.md
specs/home-assistant-elgato-lighting/
```

## Tiered TDD And Validation Plan

**TDD expectation**: Docs-only tiny change; no executable behavior or test seam
exists, so use review checks and cheap render validation.

**Local checks**:

- `kubectl kustomize kubernetes/apps/home-assistant`
- `kubectl kustomize kubernetes/apps/home-assistant/branch`
- `git diff --name-only`

**Development smoke**: none; no Kubernetes, Flux, Gateway, storage, secret, or
app behavior changes are made. Local render checks prove unchanged manifests
still parse.

**Evidence destination**: `specs/home-assistant-elgato-lighting/evidence.md`.

## Documentation Impact

Update `docs/runbooks/home-assistant.md` with Elgato-specific onboarding,
manual setup, inventory capture, and runtime-state safety guidance. No generated
architecture update is required because Kubernetes and Terraform sources do not
change.

## Implementation Steps

1. Create SDD artifacts for `home-assistant-elgato-lighting`.
2. Add an Elgato lighting section to the Home Assistant runbook.
3. Run local render checks and focused docs review.
4. Record command outcomes and docs-only smoke exception in evidence.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Operator commits runtime Home Assistant state later | Explicitly warn not to commit `.storage`, `config_entries`, credentials, or generated registries |
| Follow-up controls target guessed entity IDs | Require runtime inventory before adding Git-owned scenes, scripts, automations, or packages |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
