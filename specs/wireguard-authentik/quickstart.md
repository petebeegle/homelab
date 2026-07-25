# Quickstart: Validate The WireGuard Authentik Gate

## Prerequisites

- Branch `codex/wireguard-authentik`
- `kubectl`, `flux`, Python 3, Node/npm, and pre-commit
- Production kubeconfig for post-reconcile verification
- One Authentik account in `WireGuard Admins` or built-in `authentik Admins`
- One Authentik account in neither authorized group
- An existing WireGuard peer and the existing credentialed in-cluster API probe
- No credentials printed to terminal logs or committed evidence

## 1. Render Desired State

```bash
export cluster_domain=lab.petebeegle.com
kubectl kustomize kubernetes/infra/authentik | flux envsubst --strict
kubectl kustomize kubernetes/infra/network/vpn | flux envsubst --strict
kubectl kustomize kubernetes/clusters/production | flux envsubst --strict
python3 tools/architecture/render.py --check
```

Expected: all commands exit zero; the rendered WireGuard HTTPRoute backend is
the Authentik Service, and a matching ReferenceGrant is present.

## 2. Validate Mirrored Smoke

```bash
diff -u tests/smoke/routes.spec.js kubernetes/apps/synthetics/smoke/routes.spec.js
python3 tools/policy/check_synthetic_smoke_mirroring.py
npm --prefix tests/smoke test -- --grep "wireguard reaches Authentik"
```

Before the route change reaches production, the focused user-path assertion is
expected to fail against the direct wg-easy response. After Flux applies the
change, it must pass.

## 3. Review Applied State

After merge, use the production-scoped aliases from `scripts/kube-aliases.sh`:

```bash
. scripts/kube-aliases.sh
fp get kustomizations vpn authentik app-synthetics
kp -n wireguard get httproute wireguard-ui -o yaml
kp -n authentik get referencegrant
kp -n authentik get helmrelease authentik
```

Expected: Flux has fetched/applied the merge revision; `wireguard-ui` reports
`Accepted=True` and `ResolvedRefs=True`; Authentik is Ready.

## 4. Exercise The Exact User Paths

Use isolated browser contexts:

1. No session: open `https://vpn.lab.petebeegle.com/`; expect Authentik, not
   wg-easy.
2. No session: request the selected representative API path; expect Authentik
   or its denial, not a wg-easy API response.
3. Session in neither authorized group: expect an Authentik authorization
   denial.
4. `WireGuard Admins` or `authentik Admins` session: expect proxy authorization,
   then the existing wg-easy login/UI.

Do not record session cookies, passwords, tokens, or client configurations.

## 5. Run Synthetic Smoke

```bash
kp create job -n synthetics synthetic-smoke-manual-$(date +%Y%m%d%H%M%S) \
  --from=cronjob/synthetic-smoke
kp get jobs,pods -n synthetics -l app.kubernetes.io/name=synthetic-smoke
kp logs -n synthetics -l app.kubernetes.io/name=synthetic-smoke --tail=200
```

Expected: the WireGuard Authentik test and the full suite pass, with one
`SMOKE_RUN_SUMMARY ... status=success` line.

## 6. Preserve VPN And Automation

- Verify one existing peer can establish its tunnel and reach an already allowed
  service-plane destination.
- Run the existing credentialed in-cluster wg-easy API probe used by the
  access-broker workflow.
- Confirm neither check required peer recreation, database mutation, or a new
  secret.

## 7. Rollback

If authorized users or trusted automation cannot operate, revert the Git commit
and allow Flux to restore the previous desired state. Record which verification
failed. A temporary live diagnostic may be used only under the GitOps runbook;
do not leave a durable direct-to-wg-easy route outside Git.
