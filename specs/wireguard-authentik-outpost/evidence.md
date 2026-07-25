# Evidence: wireguard-authentik-outpost

**Branch**: `codex/wireguard-authentik-outpost`
**Date**: 2026-07-25

## Diagnosis

- Live `ProxyProvider` state contains `wireguard-proxy` with external host
  `https://vpn.lab.petebeegle.com` and the wg-easy internal Service URL.
- Live embedded-outpost membership contains the six pre-existing proxy
  providers but not `wireguard-proxy`.
- `wireguard-proxy-setup` applied successfully at `16:33:47Z`.
- `private-app-proxy-setup` applied successfully at `16:34:24Z`, after which
  WireGuard was absent from the full provider list.
- Requests for the VPN hostname are logged by `authentik.asgi`, while working
  proxy applications are logged by `authentik.outpost.proxyv2.application`.
- Post-merge verification of the first private correction found a second race:
  `private-apps` and `app-sabnzbd` both wrote
  `Secret/private-authentik-blueprints`. The later apply left only
  `private-app-icons.yaml`, removing the mounted proxy blueprint key.

## Workflow

- The user explicitly approved the desired corrective outcome by reporting that
  the merged behavior did not hand off to WireGuard.
- Clarify found no material ambiguity.
- Checklist is represented by the explicit requirements and validation tasks
  for this narrow production regression.
- Default `/workspaces/homelab-worktrees` is unavailable; the established
  writable fallback `/home/vscode/homelab-worktrees` is used.
- Development exception: development does not deploy the production
  Authentik/private proxy blueprint or VPN application.

## Analyze

- 9 functional requirements and 5 success criteria map to T001-T014.
- No critical ambiguity, duplicate requirement, unmapped task, or constitution
  conflict was found before implementation.

## Command Evidence

| Command | Result | Notes |
| ------- | ------ | ----- |
| Live Authentik read-only Django query | FAIL before fix | Provider existed, but embedded outpost contained six other providers and omitted `wireguard-proxy`. |
| Live blueprint instance query | PASS diagnosis | Public WireGuard blueprint applied at `16:33:47Z`; private full-list blueprint applied later at `16:34:24Z`. |
| Public Authentik, VPN, synthetics, and production `kubectl kustomize` renders | PASS | All affected desired-state entrypoints render. |
| Private production apps `kubectl kustomize` render | PASS | Encrypted private blueprint Secret renders. |
| `sops filestatus kubernetes/apps/sabnzbd/private-authentik-blueprint-secret.yaml` | PASS | Reported `encrypted: true`. |
| Non-content-emitting decrypted provider count | PASS | Seven total embedded-outpost provider references; WireGuard appears exactly once. |
| Unified private blueprint Secret render | PASS | Exactly one Secret document contains both `private-app-proxy.yaml` and `private-app-icons.yaml`. |
| `cmp tests/smoke/routes.spec.js kubernetes/apps/synthetics/smoke/routes.spec.js` | PASS | Smoke source and deployed mirror are identical. |
| `npm test -- --grep 'wireguard reaches Authentik'` | PASS | Two focused unauthenticated browser tests passed against the current live path. |
| `python3 tools/architecture/render.py --check` | PASS | Generated architecture remains current. |
| `pre-commit run --all-files` | PASS | All public repository checks passed. |
| `git diff --check` in both repositories | PASS | No whitespace errors. |

## Convergence

Clean: the implementation satisfies FR-001 through FR-008 and SC-001,
SC-004, and SC-005 at render/test level. SC-001 through SC-004 require
post-merge live verification; SC-003 specifically requires an authorized
operator browser session.

No additional convergence tasks were required.

## Development Validation Exception

Development does not deploy the production Authentik instance, private proxy
blueprint, or VPN application. Substitute evidence consists of both repository
renders, SOPS validation, provider-list preservation/count checks, the exact
production unauthenticated browser smoke, and required post-merge live checks.
