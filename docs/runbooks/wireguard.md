# WireGuard

Use this runbook to check the `wg-easy` deployment that provides VPN access to the external `192.168.40.x` service plane.

## Client Routing Defaults

Global wg-easy client defaults are managed in `kubernetes/infra/network/vpn/global-config.yaml`.
The desired global `AllowedIPs` default is `192.168.40.0/24`; the desired global DNS defaults are `1.1.1.1` and `2606:4700:4700::1111`.

wg-easy v15 stores these defaults in `/etc/wireguard/wg-easy.db`.
The `wg-easy-defaults` initContainer runs before the main `wireguard` container and reconciles the `user_configs_table` row with `id = "wg0"` without querying or printing client secrets.
The main container also receives `INIT_ENABLED`, `INIT_ALLOWED_IPS`, and `INIT_DNS` so a fresh database bootstraps with the same defaults.

Existing clients keep the per-client values copied when they were created.
If a client has the old route or DNS values, regenerate or edit that client once after the global defaults are corrected.

Verify the stored defaults without selecting secret-bearing columns:

```bash
kubectl -n wireguard exec deploy/wireguard -- sh -ec 'cd /app/server && node -e '"'"'
const { createRequire } = require("node:module");
const { createClient } = createRequire("/app/server/package.json")("@libsql/client");
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
