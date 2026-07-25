# WireGuard

Use this runbook to check the `wg-easy` deployment that provides VPN access to the external `192.168.40.x` service plane.

## Administration Authentication

The human administration URL, `https://vpn.<cluster-domain>`, is LAN-only on
`gateway/internal` and is protected by the Authentik embedded proxy outpost.
The Authentik `wireguard-proxy` provider forwards authorized requests to
`http://wireguard-http.wireguard.svc.cluster.local:51821`.
See `docs/runbooks/authentik-proxy-apps.md` before adding or changing proxy
providers; the embedded outpost provider list has a single authoritative owner.

Access is allowed to either of these Authentik groups:

- `WireGuard Admins` for normal delegated administration.
- Built-in `authentik Admins` for break-glass access and initial population of
  `WireGuard Admins`.

Users in neither group must receive an Authentik authorization denial. The
provider does not configure unauthenticated paths or inject the wg-easy
credential. After Authentik authorization, wg-easy's existing login remains as
defense in depth.

The Gateway route fails closed through Authentik. If Authentik or the embedded
outpost is unavailable, do not add a durable direct-to-wg-easy backend as a
workaround. Restore service through Git by fixing Authentik or reverting the
change that introduced the proxy route.

### Machine Access Boundary

Trusted in-cluster automation, including access-broker, continues to use:

```text
http://wireguard-http.wireguard.svc.cluster.local:51821
```

That ClusterIP path uses the existing wg-easy username and SOPS-encrypted
password. It does not traverse browser SSO. Do not expose the ClusterIP
credential through Authentik headers or synthetic-test output.

Authentik protects only the HTTP administration hostname. The WireGuard UDP
Service, peer keys, tunnel routing, VPN DNS, and existing client configurations
are unchanged.

### Verify The Authentication Path

First verify the reconciled resource chain:

```bash
. scripts/kube-aliases.sh
fp get kustomizations authentik vpn app-synthetics
kp -n authentik get helmrelease authentik
kp -n authentik get referencegrant wireguard-routes-to-authentik-server -o yaml
kp -n wireguard get httproute wireguard-ui -o yaml
```

The `wireguard-ui` route must report `Accepted=True` and
`ResolvedRefs=True`, and its only backend must be
`authentik/authentik-server:80`.

Use separate browser contexts for the user-path checks:

1. With no Authentik session, open both `/` and `/api/client` on the `vpn`
   hostname. Both must reach Authentik before exposing wg-easy.
2. With a user in neither authorized group, confirm Authentik denies access.
3. With a `WireGuard Admins` or `authentik Admins` account, confirm Authentik
   permits access and wg-easy presents its existing login/UI.

After the blueprint first reconciles, use an existing `authentik Admins`
account to populate `WireGuard Admins`. Keep at least one tested break-glass
administrator.

Then verify the unchanged non-browser paths:

1. Connect one existing WireGuard peer and reach an already allowed
   `192.168.40.0/24` service-plane destination.
2. Run the existing credentialed access-broker/wg-easy API smoke through the
   ClusterIP Service without logging the password or response secrets.
3. Confirm neither check requires regenerating a peer or changing the wg-easy
   database.

Run the production synthetic suite after the user-path checks:

```bash
kp create job -n synthetics synthetic-smoke-manual-$(date +%Y%m%d%H%M%S) \
  --from=cronjob/synthetic-smoke
kp logs -n synthetics -l app.kubernetes.io/name=synthetic-smoke --tail=200
```

The WireGuard root and API-path tests must pass and the run must emit one
`SMOKE_RUN_SUMMARY` line with `status=success`.

## Client Routing Defaults

Global wg-easy client defaults are managed in `kubernetes/infra/network/vpn/global-config.yaml`.
The desired global `AllowedIPs` default is `192.168.40.0/24`; the desired global DNS default is `192.168.40.250`.
That DNS address is the `vpn-dns` LoadBalancer service on the external service plane.

wg-easy v15 stores these defaults in `/etc/wireguard/wg-easy.db`.
The `wg-easy-defaults` initContainer runs before the main `wireguard` container and reconciles the `user_configs_table` row with `id = "wg0"` without querying or printing client secrets.
The main container also receives `INIT_ENABLED`, `INIT_ALLOWED_IPS`, and `INIT_DNS` so a fresh database bootstraps with the same defaults.

Existing clients keep the per-client values copied when they were created.
If a client has the old route or DNS values, regenerate or edit that client once after the global defaults are corrected.

## VPN DNS

The `vpn-dns` CoreDNS service runs in the `wireguard` namespace and requests external LoadBalancer IP `192.168.40.250` from the Cilium external pool.
It exposes DNS on TCP and UDP port 53 and is selected into that pool with the `homelab.petebeegle.com/exposure: external` service label.

CoreDNS provides split-DNS behavior for VPN clients:

- `dev.lab.petebeegle.com` and `*.dev.lab.petebeegle.com` A queries return the development external Gateway IP `192.168.40.225`.
- `*.lab.petebeegle.com` A queries return `192.168.40.241`.
- All other queries forward to UniFi DNS at `192.168.1.1`.

wg-easy copies the global DNS default into each client when the client is created.
Existing clients that still use the previous DNS values must be edited or regenerated so their WireGuard profile uses `192.168.40.250`.

Verify the stored defaults without selecting secret-bearing columns:

```bash
kubectl -n wireguard exec deploy/wireguard -- sh -ec 'node --input-type=module -e '"'"'
import { createClient } from "/app/server/node_modules/@libsql/client/lib-esm/node.js";
const db = createClient({ url: "file:/etc/wireguard/wg-easy.db" });
(async () => {
  const result = await db.execute({
    sql: "SELECT default_allowed_ips, default_dns FROM user_configs_table WHERE id = ?",
    args: ["wg0"],
  });
  console.log(JSON.stringify(result.rows[0] ?? null, null, 2));
  if (typeof db.close === "function") {
    await db.close();
  }
})().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
'"'"''
```

If the `wg-easy-defaults` initContainer fails with `Cannot find module` for `@libsql/client/lib-cjs/node.js`, confirm the ConfigMap script imports `createClient` from `/app/server/node_modules/@libsql/client/lib-esm/node.js`. The `ghcr.io/wg-easy/wg-easy:15.2.2` image ships that ESM build, but not the CJS build.

## Client API Returns 500

If `https://vpn.<cluster-domain>/api/client` returns HTTP 500, confirm that the WireGuard interface exists inside the pod:

```bash
kubectl -n wireguard exec deploy/wireguard -- wg show wg0 dump
```

If this fails with `Unable to access interface: No such device`, inspect the recent pod logs:

```bash
kubectl -n wireguard logs deploy/wireguard --since=10m --all-containers=true
```

On Talos, `wg-easy` default hooks may fail if they resolve to legacy `iptables` instead of nftables. The desired state provides `/opt/wg-hooks-bin/iptables` and `/opt/wg-hooks-bin/ip6tables` shims and prepends that directory to `PATH`, so the default hooks use `iptables-nft` and `ip6tables-nft`.

Embedded scripts in ConfigMap data must avoid JavaScript template literals because Flux post-build substitution scans that syntax before applying manifests. Use string concatenation in those scripts instead.

After Flux reconciles a fix or after a pod restart, verify:

```bash
kubectl -n wireguard rollout status deploy/wireguard
kubectl -n wireguard exec deploy/wireguard -- wg show wg0 dump
```
