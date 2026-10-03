# Fix WireGuard endpoint

Branch: `codex/fix-wireguard-endpoint`
SDD tier: medium. Workflow risk: high (VPN production traffic configuration).

## Intent and acceptance
The user requested “update the config to fix this as well” after diagnosis of
the stale public endpoint. Persist the verified current address and ensure
wg-easy profile downloads use it after GitOps rollout. Existing installed
profiles require a one-time endpoint edit; peer keys must remain unchanged.

Requirements:
- FR-001: Replace the stale endpoint with the public IPv4 independently observed
  from the cluster through ipify and Cloudflare: 69.180.24.212.
- FR-002: Reconcile the existing wg0 profile host without changing peers, keys,
  listener port 30000, or per-client routes.
- FR-003: Keep the Secret encrypted with SOPS and preserve all other values.
- FR-004: Validate reconciliation and report deployment/user-path limits.

Non-goals: dynamic DNS, router changes, key rotation, secret-provider migration.

Binding sources: AGENTS.md; .specify/memory/constitution.md;
docs/runbooks/implementation-workflow.md; docs/runbooks/wireguard.md;
docs/decisions/flux-gitops-source-of-truth.md;
docs/decisions/sops-age-secrets.md.

Human gate: user's explicit follow-up authorizes this bounded correction.
Clarification is unnecessary: destination and port are established by diagnosis.
