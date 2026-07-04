# Implementation Plan: access-broker-manual-smoke

**Branch**: `codex/access-broker-manual-smoke` | **Date**: 2026-07-04 |
**Spec**: `specs/access-broker-manual-smoke/spec.md`

**Input**: Feature specification from
`specs/access-broker-manual-smoke/spec.md`

## Summary

Activate access-broker in production for a narrow Discord manual smoke: public
Cloudflare ingress, Gateway HTTPRoute, SOPS-protected Discord app identity, and
PVC-backed request storage. The app still only handles signed Discord PING and
`/access request`.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Kubernetes, Flux, Gateway API, Cloudflare Tunnel, SOPS,
storage
**Dependencies**: `homelab-access` readiness PR, Flux, kubectl/kustomize, SOPS,
architecture renderer
**Storage**: `nfs-csi-storage`
**Ingress**: Cloudflare Tunnel to `gateway/public` and app `HTTPRoute`
**Secrets**: SOPS-encrypted `kubernetes/apps/access-broker/secret.yaml`
**Smoke Strategy**: manual production Discord smoke after merge
**Fanout Targets**: app readiness, manifest render, SOPS/secret scan,
Cloudflare route scan
**Development Validation**: none with documented exception because development
does not run Cloudflare Tunnel or receive public Discord webhooks
**Post-Implementation SDD Conformance**: local workflow docs reviewed

## Constitution Check

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation without exception; Cloudflare/Discord public
      smoke cannot be represented in development and is recorded.
- [x] Gateway API invariant preserved; no Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; Discord identity is in encrypted `secret.yaml`.
- [x] NFS default considered for PVC-backed workload.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/access-broker-manual-smoke`; fallback worktree recorded.
- [x] Documentation impact identified; generated architecture checked/updated.
- [x] PR review/status checks are the review gate.

## Project Structure

```text
specs/access-broker-manual-smoke/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

```text
kubernetes/apps/access-broker/
kubernetes/apps/cloudflare-tunnels/deployment.yaml
kubernetes/clusters/production/apps/access-broker.yaml
kubernetes/clusters/production/apps/kustomization.yaml
docs/architecture.md
```

## Tiered TDD And Validation Plan

**TDD expectation**: App readiness behavior is covered in `homelab-access`;
homelab changes are validated with render, SOPS, and route checks.

**Local checks**:

- `kubectl kustomize kubernetes/apps/access-broker`
- `kubectl kustomize kubernetes/apps/cloudflare-tunnels`
- `kubectl kustomize kubernetes/clusters/production`
- `python3 tools/architecture/render.py --check`
- Secret placeholder scan for `access-broker`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`

**Development smoke**: None. Development cluster omits Cloudflare Tunnel and
cannot receive Discord public webhook validation.

**Completion evidence**: Record local checks, PRs, and manual smoke instructions
for Discord Developer Portal and `#test`.

**Fanout plan**: Manifest edits, app readiness PR, and validation can proceed
independently; evidence consolidates results.

**Evidence destination**: `specs/access-broker-manual-smoke/evidence.md`.

## Documentation Impact

Generated `docs/architecture.md` must be refreshed if the active production
Kustomization inventory changes.

## Implementation Steps

1. Update `homelab-access` readiness so current smoke does not require future
   Authentik/wg-easy/bot-token settings.
2. Configure access-broker hostname, store path, and encrypted Discord identity.
3. Add Cloudflare Tunnel ingress and production Flux activation.
4. Run local render/secret/architecture checks.
5. Publish PRs and provide manual smoke instructions.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Public route exposed before provisioning is complete | Only `/discord/interactions` and placeholder `/download/` route; app only creates local pending requests |
| Pod not Ready because future credentials are absent | App readiness PR requires only implemented Discord fields |
| Discord command unavailable | User must register `/access request`; provide command guidance |
| Cloudflare DNS missing | Record as manual smoke prerequisite |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| Production manual smoke before development smoke | Discord must reach public Cloudflare ingress; development cluster intentionally omits it | Local-only render cannot validate Discord endpoint URL |
