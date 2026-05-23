# WireGuard

Use this runbook to check the `wg-easy` deployment that provides VPN access to the external `192.168.40.x` service plane.

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
