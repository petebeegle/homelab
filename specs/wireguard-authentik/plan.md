# Implementation Plan: wireguard-authentik

**Branch**: `codex/wireguard-authentik` | **Date**: 2026-07-25 | **Spec**:
`specs/wireguard-authentik/spec.md`

**Input**: Feature specification from `specs/wireguard-authentik/spec.md`

## Summary

Protect the LAN-only wg-easy UI by replacing the `vpn.${cluster_domain}`
HTTPRoute's direct backend with Authentik's embedded proxy outpost. Add a
GitOps-managed proxy provider whose external host is the existing `vpn` URL and
whose internal host is the existing wg-easy ClusterIP Service. Bind the
Authentik application to a dedicated `WireGuard Admins` group with built-in
`authentik Admins` retained for break-glass access, leave wg-easy's own
authentication in place, and preserve direct in-cluster Service access for the
access-broker. Add exact-host synthetic smoke, dependency ordering, and operator
documentation.

## Technical Context

**Risk Tier**: high
**Workflow Tier**: high
**Primary Areas**: Kubernetes, Flux dependency ordering, Gateway API,
Authentik blueprints, synthetic smoke, generated architecture, runbook
**Dependencies**: Kustomize, Flux envsubst/build, kubectl, Authentik 2026.5.0,
wg-easy 15.3.0, npm/Playwright, architecture renderer
**Storage**: Existing `wireguard-pvc` and Authentik PostgreSQL storage remain
unchanged on `nfs-csi-storage`
**Ingress**: Keep `gateway/internal` / `https-gateway`; route
`vpn.${cluster_domain}` to `authentik/authentik-server:80` through an explicit
cross-namespace backend reference authorized by a ReferenceGrant
**Secrets**: No new secret is expected. Existing wg-easy and Authentik secrets
remain SOPS-encrypted and are never copied into the proxy blueprint.
**Smoke Strategy**: Add mirrored Playwright coverage that asserts the exact
unauthenticated `vpn` URL reaches Authentik, then run a production one-off
synthetic Job plus authorized and unauthorized browser checks
**Fanout Targets**: Read-only routed-app audit (completed separately at user
request); post-implementation manifest review and exact-path smoke may run as
independent read-only lanes, with all evidence consolidated in `evidence.md`
**Development Validation**: `smoke_profile: none` for the full path because the
development base deliberately omits Authentik and VPN. Substitute local
production renders, schema/policy checks, a pre-change expected-failing
synthetic assertion, and post-reconcile production synthetic/user-path checks.
If a safe temporary development deployment of both components becomes
available during implementation, use it and supersede this exception.
**Post-Implementation SDD Conformance**: local repository workflow review only;
this does not change Spec Kit behavior or standards. The upstream plan workflow's
agent-context update step is unavailable because this repository does not ship
an `update-agent-context` script; no agent guidance changes are needed for this
feature.

## Human Gates

**Spec Gate**: approved by the user's explicit request to plan the named
WireGuard/Authentik fix; assumptions are documented in the spec

**Checklist Status**: run; requirements checklist passed and focused security
checklist is at `specs/wireguard-authentik/checklists/security.md`

**Plan Gate**: approved by the user's 2026-07-25 instruction to implement

**Expected Task/Analyze Gate**: task list approved by the implementation
instruction, with analyze required and no unresolved critical or high finding
before source implementation

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is
      recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/wireguard-authentik`; the prescribed `/workspaces`
      worktree parent was not writable, so the documented sibling fallback
      `/home/vscode/homelab-worktrees/wireguard-authentik` is intentional.
- [x] Documentation impact identified; update the WireGuard and synthetic smoke
      runbooks and regenerate architecture documentation.
- [x] PR review/status checks are the review gate.

## Project Structure

### SDD Artifacts

```text
specs/wireguard-authentik/
├── checklists/
│   ├── requirements.md
│   └── security.md
├── contracts/
│   └── access-path.md
├── data-model.md
├── quickstart.md
├── research.md
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
kubernetes/
├── clusters/production/
│   ├── apps/synthetics.yaml
│   └── infra/vpn.yaml
├── infra/
│   ├── authentik/
│   │   ├── blueprints/
│   │   │   ├── kustomization.yaml
│   │   │   └── wireguard-proxy.yaml
│   │   ├── kustomization.yaml
│   │   └── referencegrant.yaml
│   └── network/vpn/httproute.yaml
└── apps/synthetics/smoke/routes.spec.js

tests/smoke/routes.spec.js
docs/runbooks/wireguard.md
docs/runbooks/synthetic-smoke-tests.md
docs/architecture.md
```

## Tiered TDD And Validation Plan

**TDD expectation**: First add a mirrored Playwright assertion that requires an
unauthenticated `vpn` request to land on Authentik. Against the current direct
route, the assertion should fail because wg-easy responds. Then implement the
blueprint/route change and retain the same assertion as regression coverage.
Static render and cross-namespace reference checks supplement, but do not
replace, the exact user-path test.

**Local checks**:

- `diff -u tests/smoke/routes.spec.js kubernetes/apps/synthetics/smoke/routes.spec.js`
- `python3 tools/policy/check_synthetic_smoke_mirroring.py`
- `npm --prefix tests/smoke test -- --grep "wireguard reaches Authentik"`
- `kubectl kustomize kubernetes/infra/authentik | flux envsubst --strict`
- `kubectl kustomize kubernetes/infra/network/vpn | flux envsubst --strict`
- `kubectl kustomize kubernetes/clusters/production | flux envsubst --strict`
- `python3 tools/architecture/render.py --check`
- `pre-commit run --all-files`

**Development smoke**: No standard branch profile applies, and the development
base intentionally omits both production-only components. Record
`smoke_profile: none` with that blocker. If server-side dry-run can safely
validate the rendered objects without introducing live state, run it as an
additional schema/reference check. Completion still requires a post-merge
production one-off synthetic Job, an authorized browser session, an
authenticated non-member denial, an existing-peer tunnel check, and a
credentialed in-cluster API probe.

**Automated smoke preference**: For user-facing, routed, deployed, or
operational changes, prefer automated smoke in this order: development branch
profile; production synthetic smoke or one-off in-cluster Job; scriptable
Gateway/DNS/browser smoke against the exact user URL; manual browser checks only
as supplemental evidence.

**Completion evidence**: For deploy follow-up, record source fetched SHA, target
kustomization or HelmRelease applied SHA, live resource spec, Gateway/listener
match when applicable, and exact user-facing URL result.

**Fanout plan**: The user-requested separate read-only exposure audit is complete
and summarized in `research.md`. During implementation, an independent
read-only reviewer may inspect the blueprint, cross-namespace route, and
fail-closed behavior while another lane runs local renders or post-reconcile
smoke. No helper edits the same tracked files. The implementation owner records
all results in `specs/wireguard-authentik/evidence.md`.

**Evidence destination**: `specs/wireguard-authentik/evidence.md`.

## Documentation Impact

Update `docs/runbooks/wireguard.md` to describe the Authentik group, double-auth
behavior, direct Service boundary, verification, and rollback. Update
`docs/runbooks/synthetic-smoke-tests.md` to list the `vpn` target and its
expected Authentik behavior. Regenerate `docs/architecture.md` because an
HTTPRoute backend, Authentik blueprint, ReferenceGrant, and Flux dependency
change affect generated architecture. No ADR is required because the design
uses the existing GitOps, Gateway API, and evidence decisions without changing
their authority.

## Implementation Steps

1. Add the failing mirrored synthetic smoke scenario for unauthenticated
   `https://vpn.${cluster_domain}` and record the current direct-wg-easy result.
2. Add `wireguard-proxy.yaml` to the Authentik blueprint set. Define the
   `WireGuard Admins` group, proxy provider (`proxy` mode, external `vpn` host,
   internal wg-easy Service URL), Authentik application, group policy binding,
   the `WireGuard Admins` and break-glass `authentik Admins` policy bindings,
   and embedded-outpost provider assignment without any embedded credential.
3. Add an Authentik-namespace ReferenceGrant that permits HTTPRoutes from only
   the `wireguard` namespace to reference only the `authentik-server` Service.
   Gateway API ReferenceGrant cannot narrow the source to one HTTPRoute name.
4. Change the WireGuard HTTPRoute backend from `wireguard-http:51821` to
   `authentik-server:80` in namespace `authentik`, preserving the hostname and
   LAN-only parentRef.
5. Make the production `vpn` Flux Kustomization depend on `authentik`, and make
   `app-synthetics` depend on `vpn`, so reconciliation and smoke ordering match
   the traffic path.
6. Update runbooks and regenerate architecture documentation.
7. Run local render, mirror, focused test, architecture, and pre-commit checks;
   record the development-cluster exception and any safe substitute dry-runs.
8. After review, merge, and Flux reconciliation, verify the applied SHA, route
   `Accepted`/`ResolvedRefs`, Authentik blueprint/outpost health,
   unauthenticated redirect, authorized access, non-member denial, existing
   WireGuard peer connectivity, direct access-broker/API behavior, and the
   one-off synthetic Job.
9. Roll back by reverting the Git commit if Authentik proxying blocks
   authorized operations; do not bypass GitOps with a durable live route edit.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Embedded outpost/provider is not ready when the route reconciles | Make `vpn` depend on `authentik`, verify blueprint and outpost state before user-path acceptance, and fail closed meanwhile |
| Cross-namespace backend is rejected | Add a least-privilege ReferenceGrant and require `ResolvedRefs=True` |
| Proxy mode breaks websocket/API behavior | Use Authentik's supported proxy mode and exercise the UI plus a representative API path after login |
| Authentik outage locks out wg-easy UI | Preserve wg-easy local authentication and direct ClusterIP access for trusted recovery; use a Git revert for durable rollback |
| Over-broad Authentik membership exposes peer configs | Bind `WireGuard Admins`, retain only built-in Authentik admins for break-glass, and test a user in neither group |
| Proxy protection breaks access-broker automation | Keep the in-cluster Service unchanged and verify the existing credentialed API path |
| Development cannot represent the production path | Record the explicit exception, run all safe local checks, then require layered post-reconcile production evidence |
| Blueprint outpost assignment overwrites an unmanaged live proxy provider | Treat Git as authoritative, inspect current outpost provider membership read-only before rollout, and include all Git-managed proxy providers in the declared assignment |

## Complexity Tracking

No constitution violations are planned.
