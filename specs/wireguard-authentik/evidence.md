# Evidence: wireguard-authentik

**Branch**: `codex/wireguard-authentik`
**Risk Tier**: high
**Status**: implemented and locally validated; deployment verification pending

## Human Gates

- Intent/spec: approved by the request to plan the WireGuard Authentik fix.
- Plan: approved by the 2026-07-25 instruction to implement.
- Task/analyze: approved by the implementation instruction; Spec Kit analysis
  found no critical or high issues before source edits.
- Converge: complete with no remaining task.

## Worktree

- Preferred `/workspaces/homelab-worktrees/wireguard-authentik` could not be
  created because its parent is not writable in this environment.
- Allowed fallback:
  `/home/vscode/homelab-worktrees/wireguard-authentik`.

## TDD

- Spec Kit analysis: PASS. Fifteen numbered requirements/success criteria and
  all three user stories are covered by 18 correctly formatted tasks; no
  ambiguity, duplication, constitution conflict, or unmapped task blocks
  implementation.
- `npm --prefix tests/smoke test -- --grep "wireguard reaches Authentik"`:
  initial attempt could not start because dependencies were not installed.
- `npm --prefix tests/smoke ci`: PASS; 3 packages installed, 0 vulnerabilities.
- Re-run of the focused test: EXPECTED FAIL (2 tests). The root remained at
  `https://vpn.lab.petebeegle.com/login`, and `/api/client` remained at the
  direct `vpn` URL. Neither request reached Authentik, proving the test detects
  the reported gap before route implementation.

## Local Validation

- `git diff --exit-code origin/main --` for the wg-easy Deployment, UDP/HTTP
  Services, PVC, and access-broker ConfigMap: PASS. No changes.
- `git diff --name-only origin/main -- kubernetes/infra/network/vpn
  kubernetes/apps/access-broker/configmap.yaml`: PASS; only
  `kubernetes/infra/network/vpn/httproute.yaml` is changed.
- `python3 tools/architecture/render.py --write` followed by `--check`: PASS.
- `diff -u tests/smoke/routes.spec.js
  kubernetes/apps/synthetics/smoke/routes.spec.js`: PASS.
- `python3 tools/policy/check_synthetic_smoke_mirroring.py`: PASS, including
  wrapper/reporter unit checks.
- `npm test -- --list --grep "wireguard reaches Authentik"` from
  `tests/smoke`: PASS; both new tests are collected.
- `kubectl kustomize kubernetes/infra/authentik | flux envsubst --strict` with
  `cluster_domain=lab.petebeegle.com`: PASS.
- `kubectl kustomize kubernetes/infra/network/vpn | flux envsubst --strict`:
  PASS.
- `kubectl kustomize kubernetes/clusters/production | flux envsubst --strict`:
  PASS.
- Supplemental Authentik blueprint model/field comparison against the current
  upstream `blueprints/schema.json`: PASS for group, proxy provider,
  application, two policy bindings, and embedded outpost.
- Sensitive-pattern scan for plaintext wg-easy credentials, private keys,
  Basic Auth injection, unauthenticated proxy bypass, and traditional Ingress:
  PASS.
- `git diff --check`: PASS.
- `pre-commit run --all-files`: PASS, including yamllint, k8svalidate,
  generated architecture, and synthetic smoke mirroring.
- Checklist status: `requirements.md` 16/16 and `security.md` 16/16.
- Live read-only pre-change baseline: production `wireguard-ui` still uses
  `gateway/internal` and direct `wireguard-http`; `authentik-server` exposes
  Service port 80 to target port 9000. Production `authentik`, `vpn`, and
  `app-synthetics` Kustomizations were Ready at
  `main@sha1:46cb4fec04535bee28a4b3e1e9da85155c2ca205`.

## Development Validation

**smoke_profile**: `none`

The development base deliberately omits Authentik and VPN, so it cannot
represent the proxy provider, group policy, embedded outpost, wg-easy upstream,
or exact `vpn` hostname. A live read-only query confirmed there are no
`authentik` or `wireguard` namespaces and no `authentik` or `vpn` Flux
Kustomizations. The development `gateway` and `app-whoami` Kustomizations were
healthy at `main@sha1:46cb4fec04535bee28a4b3e1e9da85155c2ca205`.

This is an unavailable-infrastructure exception, not a waived failure.
Substitute evidence is the expected-failing production test, strict local
renders, k8svalidate, blueprint schema comparison, and the required post-merge
production checks below.

## Post-Merge Verification Handoff

Not run: the branch is not merged, pushed, or reconciled. Do not describe the
change as deployed until all layers below are recorded:

1. Record the merge SHA and confirm Flux source fetched that SHA.
2. Confirm `authentik`, then `vpn`, then `app-synthetics` applied that revision.
3. Confirm the Authentik blueprint is applied, the embedded outpost is healthy,
   and `wireguard-proxy` is assigned.
4. Confirm `wireguard-ui` has `Accepted=True` and `ResolvedRefs=True`, keeps only
   `gateway/internal`, and targets only `authentik/authentik-server:80`.
5. With no session, verify `/` and `/api/client` reach Authentik and expose no
   wg-easy response.
6. Verify a user in neither `WireGuard Admins` nor `authentik Admins` is denied.
7. Verify a member of either authorized group reaches the existing wg-easy
   login/UI; use built-in admins to populate `WireGuard Admins`.
8. Verify one existing peer reaches an already allowed service-plane target.
9. Verify the credentialed access-broker path still calls the unchanged
   `wireguard-http` ClusterIP successfully without logging secrets.
10. Run a one-off production synthetic Job and require one successful
    `SMOKE_RUN_SUMMARY`.

## Documentation Impact

- Updated `docs/runbooks/wireguard.md` with the Authentik and direct-machine
  boundaries, group policy, fail-closed behavior, validation, and rollback.
- Updated `docs/runbooks/synthetic-smoke-tests.md` with the root/API Authentik
  assertions.
- Regenerated `docs/architecture.md` for Flux dependencies, component
  resources, and the changed HTTPRoute backend.
- Updated `.gitignore` for local Node/Playwright artifacts required by the
  implementation test workflow.

## SDD Conformance

- Specify, plan, and both requirements/security checklists completed before
  source implementation.
- User approved implementation; tasks were generated and analyze found no
  blocking issue before source edits.
- High-risk validation and the development exception are recorded.
- Converge checked 10 functional requirements, 5 success criteria, 7 acceptance
  scenarios, the implementation-plan decisions, and all 7 constitution
  principles. It found no missing, partial, contradictory, or unrequested work
  requiring a task.
- All 18 implementation tasks are complete.

## Branch State

- Worktree branch: `codex/wireguard-authentik`.
- Base `HEAD`: `46cb4fec04535bee28a4b3e1e9da85155c2ca205`.
- The implementation is committed only to the local feature branch. It is not
  pushed, merged, applied, or user-path verified after reconciliation.
