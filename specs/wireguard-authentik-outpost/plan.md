# Implementation Plan: wireguard-authentik-outpost

**Branch**: `codex/wireguard-authentik-outpost` | **Date**: 2026-07-25 |
**Spec**: `specs/wireguard-authentik-outpost/spec.md`

## Summary

The public WireGuard blueprint and the existing private proxy blueprint both
write the embedded outpost's full many-to-many provider list. Live evidence
shows the public blueprint adds WireGuard, then the private blueprint reapplies
37 seconds later and removes it. Make the existing private blueprint the sole
owner of that list by adding WireGuard there and removing the competing outpost
entry from the public blueprint.

## Technical Context

**SDD Tier**: high
**Workflow Risk Tier**: high
**Primary Areas**: Authentik blueprints, SOPS Secret, synthetic browser tests
**Ingress**: Existing Gateway API route remains unchanged
**Secrets**: Edit only through SOPS; never log decrypted content
**Smoke Strategy**: Exact unauthenticated URL checks plus live authenticated
operator verification after merge
**Fanout Targets**: None; the provider-list edit and tests share one critical
authentication path
**Development Validation**: Exception expected because development omits the
production Authentik/private blueprint and VPN application. Use render,
blueprint schema, encryption, and production post-merge user-path checks.

## Human Gates

**Spec Gate**: Approved by the user's explicit report of incorrect behavior.
**Clarify Gate**: No questions required; expected handoff behavior is explicit.
**Plan Gate**: Consolidated with the corrective implementation instruction.
**Task/Analyze Gate**: Consolidated for the narrow production regression;
analysis must show complete requirement coverage before editing behavior.

## Technical Approach

1. Keep provider/application/policy definitions in the public WireGuard
   blueprint.
2. Remove its embedded-outpost mutation so it cannot race the authoritative
   full provider list.
3. Decrypt the existing SOPS Secret only into ignored runtime scratch, append
   the WireGuard provider reference to the private blueprint's existing outpost
   list, consolidate the proxy and icon blueprints under one Secret owner, and
   re-encrypt the tracked manifest.
4. Correct synthetic assertions to accept Authentik's current flow paths and
   explicitly reject wg-easy content before login.
5. Add an Authentik proxy runbook that makes the private blueprint the sole
   embedded-outpost provider-list owner and documents safe addition,
   verification, troubleshooting, and rollback.
6. Validate renders, encryption, blueprint ownership, existing provider
   preservation, and the exact URL.

## Constitution Check

- [x] Git remains the source of durable state.
- [x] Gateway API remains the ingress contract.
- [x] Secret plaintext remains outside Git and command output.
- [x] High-risk evidence and development exception are explicit.
- [x] A dedicated branch, worktree, spec directory, and PR are used.

## Project Structure

```text
kubernetes/infra/authentik/blueprints/wireguard-proxy.yaml
kubernetes/infra/authentik/secret.yaml
kubernetes/apps/synthetics/smoke/routes.spec.js
tests/smoke/routes.spec.js
docs/runbooks/authentik-proxy-apps.md
specs/wireguard-authentik-outpost/
```

## Validation

- SOPS `filestatus` and no-plaintext scans.
- Authentik blueprint parse/schema validation.
- Render Authentik, VPN, synthetics, and production entrypoint.
- Verify only the private blueprint mutates embedded-outpost providers.
- Verify its provider list preserves the six live assignments and WireGuard.
- Verify one rendered Secret contains both private blueprint keys and is owned
  by the private Authentik blueprint Kustomization.
- Run mirrored smoke checks.
- Review runbook commands and links against the implemented manifests.
- After merge, confirm Flux revision, live outpost membership, proxy log
  ownership, unauthenticated denial, and authenticated wg-easy landing.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Existing providers are removed | Preserve and validate the complete authoritative list |
| One Flux apply removes another blueprint key | Render one Secret from one Kustomization with both keys |
| Decrypted secret material leaks | Use ignored scratch, suppress content output, re-encrypt immediately |
| Blueprint ordering regresses | Give one blueprint sole ownership of the outpost list |
| Smoke passes on Authentik 404 | Assert both auth handling and successful authenticated wg-easy content |
