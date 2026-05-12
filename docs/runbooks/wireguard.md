# WireGuard

Use this runbook to check the `wg-easy` deployment that provides VPN access to the external `192.168.40.x` service plane.

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

After Flux reconciles a fix or after a pod restart, verify:

```bash
kubectl -n wireguard rollout status deploy/wireguard
kubectl -n wireguard exec deploy/wireguard -- wg show wg0 dump
```
