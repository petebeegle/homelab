---
status: current
scope:
  - authentik
  - proxy-providers
  - embedded-outpost
authority: operational
created: 2026-07-25
last_verified: 2026-07-25
---

# Add An Authentik Proxy Application

Use this runbook when an HTTP application cannot implement OAuth or OIDC and
Authentik must authenticate users before proxying requests to the application.
This procedure applies to Authentik proxy-mode providers served by the embedded
outpost.

## Ownership Rule

Exactly one blueprint owns the embedded outpost's `providers` attribute.
Authentik treats that attribute as the complete desired list, not an additive
patch. If two blueprints set it, the last blueprint to apply removes providers
that appear only in the other list.

The authoritative list is `private-app-proxy.yaml` in the SOPS-encrypted
two-key Secret:

```text
homelab-private/kubernetes/infra/authentik/blueprints/private-authentik-blueprint-secret.yaml
```

Public application blueprints may create a proxy provider, application, groups,
and policy bindings. They must not contain an
`authentik_outposts.outpost` entry. Every proxy provider, public or private,
must also be added to the authoritative private list.

That Secret is owned only by the private Authentik blueprint Kustomization and
contains both `private-app-proxy.yaml` and `private-app-icons.yaml`. Never
generate or apply another Secret with the same name from an application
Kustomization; one Flux apply can remove the other owner's data key.

## Before You Start

Confirm the application is suitable for a reverse proxy:

- It uses HTTP or HTTPS; protocol-only TCP/UDP services need a different
  control.
- Authentik may proxy every browser and API path needed by the application.
- The upstream Service is reachable from the `authentik` namespace.
- WebSockets, large uploads, and streaming behavior are identified for smoke
  coverage.
- An authorization group and a tested break-glass administrator are defined.

Use one named implementation and coordinate the public and private repository
changes. Do not apply the Authentik objects manually as the durable fix.

## Add The Provider And Application

Create a blueprint under `kubernetes/infra/authentik/blueprints/` in the public
homelab repository. A proxy-mode provider needs:

- a unique provider name;
- `mode: proxy`;
- the externally routed HTTPS hostname;
- an in-cluster upstream URL;
- authorization and invalidation flows;
- an Authentik application that references the provider;
- explicit application policy bindings.

Use a stable Service DNS name for `internal_host`. Keep application credentials
in the upstream application's SOPS Secret; do not put them in headers or
blueprints unless the integration explicitly requires that behavior.

Register the blueprint ConfigMap in
`kubernetes/infra/authentik/blueprints/kustomization.yaml` and mount it through
`kubernetes/infra/authentik/app.yaml`.

Do not add this block to an application blueprint:

```yaml
- model: authentik_outposts.outpost
  identifiers:
    managed: goauthentik.io/outposts/embedded
  attrs:
    providers: []
```

Even a one-provider list replaces the existing assignments when it applies.

## Add The Provider To The Embedded Outpost

In the private repository, decrypt only the `private-app-proxy.yaml` value into
ignored runtime scratch. Do not print its content:

```bash
mkdir -p .codex/tmp/implementation-secrets/<implementation>
sops --decrypt \
  --extract '["stringData"]["private-app-proxy.yaml"]' \
  kubernetes/infra/authentik/blueprints/private-authentik-blueprint-secret.yaml \
  > .codex/tmp/implementation-secrets/<implementation>/private-app-proxy.yaml
```

Add one `!Find` entry to the existing embedded-outpost `providers` list:

```yaml
- !Find [authentik_providers_proxy.proxyprovider, [name, <provider-name>]]
```

Preserve every existing entry. Re-encrypt the value without sending plaintext
to the terminal:

```bash
jq -Rsa . \
  < .codex/tmp/implementation-secrets/<implementation>/private-app-proxy.yaml |
  sops set --value-stdin \
    kubernetes/infra/authentik/blueprints/private-authentik-blueprint-secret.yaml \
    '["stringData"]["private-app-proxy.yaml"]'
```

Verify `sops filestatus` reports `encrypted: true`, then remove the decrypted
scratch after validation. Never commit the scratch file.

## Route The Hostname

Use Gateway API. For full proxy mode, the application `HTTPRoute` sends the
hostname to `authentik/authentik-server:80`; a cross-namespace backend also
requires a narrowly scoped `ReferenceGrant` in `authentik`.

Keep machine-only ClusterIP access separate when trusted automation must bypass
browser SSO. Do not expose that Service through another human-facing route.

## Validate Before Merge

At minimum:

1. Render the Authentik, application, synthetics, and target cluster
   Kustomizations.
2. Validate the public blueprint against the deployed Authentik version.
3. Confirm no public blueprint writes
   `authentik_outposts.outpost.attrs.providers`.
4. Decrypt only for a non-content-emitting check that the authoritative list
   contains all previous providers plus the new provider exactly once.
5. Confirm the private production render contains exactly one
   `private-authentik-blueprints` Secret with both expected keys.
6. Confirm every changed Secret reports encrypted and scan the diff for
   plaintext.
7. Add unauthenticated UI and API-path smoke tests that identify Authentik and
   explicitly reject upstream application content.
8. Plan an authenticated smoke that proves the original hostname reaches the
   upstream application after authorization.

An unauthenticated Authentik page, a route with `Accepted=True`, and a ready
Kustomization do not prove the proxy handoff.

## Post-Merge Verification

Verify each layer in order:

```bash
. scripts/kube-aliases.sh
fp get gitrepository homelab
fp get kustomizations authentik vpn app-synthetics
kp -n <app-namespace> get httproute <route> -o yaml
```

Then inspect Authentik read-only state. The embedded outpost must contain the new
provider and every previous provider. Requests for the application hostname
must be logged by `authentik.outpost.proxyv2.application` with the new provider
name; requests logged only by `authentik.asgi` are reaching Authentik itself,
not its proxy engine.

Complete three browser checks:

1. No session: UI and sensitive API paths enter Authentik and reveal no upstream
   content.
2. Unauthorized session: Authentik denies the application.
3. Authorized session: the original application hostname serves the upstream
   application and its essential API/WebSocket paths.

## Troubleshooting

### Authentication Ends At Authentik

Query the proxy provider and embedded-outpost assignments. If the provider
exists but is absent from the outpost, compare blueprint `last_applied` times.
A later blueprint with a shorter `providers` list has replaced the assignment.

Fix the authoritative private list and remove all competing outpost entries.
Do not repeatedly restart Authentik; the same blueprints will reproduce the
same state.

If the mounted directory lacks either private blueprint file, inspect the
rendered Secret and Flux ownership. Consolidate both keys under the private
Authentik blueprint Kustomization; do not create a second same-named Secret.

### Existing Proxy Applications Stop Working

Treat this as a provider-list regression. Revert the private-list change or
restore the omitted entries in Git, then allow Flux and the blueprint worker to
reconcile. Verify all previous applications before accepting the repair.

### Provider Cannot Reach The Upstream

Check Service DNS, port, NetworkPolicy, endpoints, and application logs from the
cluster. Do not change the human route to bypass Authentik as a diagnostic
shortcut.

## Rollback

Revert both halves of the implementation:

1. Remove the provider reference from the authoritative private outpost list
   while preserving all other entries.
2. Revert the public route/provider/application resources to their previous
   desired state.

Merge the coordinated rollback and verify Flux, outpost membership, the route,
and the exact user path. A direct application backend is acceptable only when
it restores the previously approved exposure; never introduce a new
unauthenticated exposure as an emergency workaround.
