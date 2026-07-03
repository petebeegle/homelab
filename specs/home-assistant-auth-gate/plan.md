# Implementation Plan: home-assistant-auth-gate

**Branch**: `codex/home-assistant-auth-gate` | **Date**: 2026-07-03 | **Spec**:
`specs/home-assistant-auth-gate/spec.md`

**Input**: Feature specification from `specs/home-assistant-auth-gate/spec.md`

## Summary

Remove Home Assistant's production `gateway/external` parentRef until onboarding and Authentik OIDC are verified, rename the invalid package slug to `code_first`, and make synthetic smoke fail onboarding with an explicit safety message while keeping the OIDC/AuthentiK success path.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Kubernetes, Gateway API, Home Assistant app configuration, synthetic smoke, docs, generated architecture
**Dependencies**: kubectl, kustomize through kubectl, npm/Playwright, Python architecture renderer, development branch verifier if available
**Storage**: Existing Home Assistant PVC remains on `nfs-csi-storage`; no storage behavior change
**Ingress**: Gateway API HTTPRoute remains on `gateway/internal`; `gateway/external` is intentionally withheld
**Secrets**: No SOPS or plaintext secret changes
**Development Validation**: Run `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-auth-gate --slug home-assistant-auth-gate --push --include-cluster-base` if credentials/profile are available; otherwise record the blocker and substitutes

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Sibling clone ownership files validated before tracked edits.
- [x] Documentation impact identified; docs updated or no-docs rationale recorded.
- [x] Separate verifier approval required before PR creation.

## Project Structure

### SDD Artifacts

```text
specs/home-assistant-auth-gate/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
docs/architecture.md
docs/runbooks/home-assistant.md
kubernetes/apps/home-assistant/httproute.yaml
kubernetes/apps/home-assistant/kustomization.yaml
kubernetes/apps/home-assistant/config/packages/code_first.yaml
kubernetes/apps/home-assistant/branch/kustomization.yaml
kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml
kubernetes/apps/synthetics/smoke/routes.spec.js
specs/home-assistant-auth-gate/
```

## Tiered TDD And Validation Plan

**TDD expectation**: High-risk local-first verification. A useful pre-change failing test seam for the live onboarding page is not available without hitting production, so the synthetic assertion is strengthened and validated through the existing smoke suite plus targeted manifest/render checks.

**Local checks**:

- `kubectl kustomize kubernetes/apps/home-assistant`
- `kubectl kustomize kubernetes/apps/home-assistant/branch`
- `kubectl kustomize kubernetes/clusters/production/apps`
- `npm --prefix kubernetes/apps/synthetics/smoke test`
- `python3 tools/architecture/render.py --write`
- `python3 tools/architecture/render.py --check`
- Targeted grep/render checks for no Home Assistant `gateway/external` parentRef and no old hyphenated package slug

**Development smoke**: Home Assistant branch deploy with `--include-cluster-base` if available; otherwise record unavailable infrastructure or missing credentials and substitute local renders and smoke tests.

**Evidence destination**: `specs/home-assistant-auth-gate/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

Update `docs/runbooks/home-assistant.md` and refresh `docs/architecture.md` if the route table changes. SDD artifacts record durable implementation rationale and evidence.

## Implementation Steps

1. Rename Home Assistant package files and kustomize generator keys to `code_first`.
2. Remove the production Home Assistant `gateway/external` parentRef.
3. Add an explicit onboarding guard to production synthetic smoke.
4. Update Home Assistant docs and SDD evidence.
5. Run local renders, smoke tests, architecture renderer, targeted checks, and development validation or exception.
6. Commit with a conventional commit and stop before verifier approval or PR creation.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Home Assistant remains reachable where onboarding is exposed | Remove `gateway/external`, render-check parentRefs, and document withheld exposure |
| Smoke accidentally treats onboarding as healthy | Add explicit onboarding detection before OIDC/AuthentiK success assertion |
| Package slug warning persists | Rename source files and generated keys; grep repo and rendered output for the old hyphenated slug |
| Development validation cannot represent production Authentik | Record exception and rely on local renders plus production smoke expectation until onboarding/AuthentiK can be verified |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
