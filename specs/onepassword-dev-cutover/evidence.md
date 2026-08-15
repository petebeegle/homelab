# Evidence: onepassword-dev-cutover

## Prior Gate

- Phase 3 merge: `0986a461d21e02d4adc973729648bae98c1d56eb`.
- Production `onepassword-items` Ready at exact revision.
- 17 `OnePasswordItem` resources Ready=True.
- Canonical no-output parity: 17/17 PASS.
- The production gate is temporarily degraded by the account-wide rate-limit incident. PR #396 merged as `8d703908d785d7ab21c35321c1d531d5058261c1`; production now polls hourly and development uses explicit refresh. Live cutover remains blocked until the provider resets and production returns 17/17 Ready.

## Discovery

- Development base is Ready at phase-3 main revision and operator Deployment is 1/1.
- Cert-manager currently reconciles the shared SOPS Secret; both ClusterIssuers reference `cloudflare-api-token`.
- Immich branch currently includes both base SOPS Secrets and references their legacy names in Helm values and CloudNativePG bootstrap.
- Required development items: cert-manager token, Immich configuration, and Immich basic-auth database user.
- The original 300-second outage wait is obsolete after the user's manual-refresh decision. The validator will explicitly trigger one failed reconcile under deny-egress and one successful reconcile after cleanup.

## Validation

- T004 inventory/resolver: 3 exact development items, strict output-path allowlist, and ID-only renderer covered by unit tests.
- T007 parity/certificate: dynamic namespace override, no-value parity comparison, and disposable staging Certificate cleanup covered by unit tests.
- T008 outage retention: Cilium deny-egress isolation with only the `kube-apiserver` entity allowed, explicit operator restart/recovery, Secret byte-digest continuity, Pod identity/readiness, and guaranteed policy/consumer cleanup covered by unit tests.
- `python3 -m unittest discover -s tools/onepassword/tests -p 'test_*.py'`: 13 passed.
- `python3 -m unittest discover -s tools/development/tests -p 'test_verify_onepassword*.py'`: 12 passed.
- `git diff --check`: passed.

## Live Gate Check — 2026-08-14T21:02:31Z

- Development and production Flux `onepassword-operator` Kustomizations are Ready at `main@sha1:8d703908d785d7ab21c35321c1d531d5058261c1`.
- Both HelmReleases are Ready on chart `connect@2.4.1`; both operator Deployments are 1/1 on operator `1.12.0`.
- Production remains 0/17 `OnePasswordItem` Ready. Current operator logs at 20:59–21:00 UTC explicitly report `1Password rate limit hit` and a 15-minute requeue for all 17 items.
- A metadata-only development vault lookup at 21:05:06 UTC, using the development cluster's read-only service-account token via process environment, was also rejected with `Too many requests`; no item data was emitted.
- No development item was created, rendered, applied, or used for cutover while this prerequisite was unhealthy.

## Provider Recovery — 2026-08-15T02:21:21Z

- Production recovered to 17/17 `OnePasswordItem` resources Ready=True.
- A metadata-only lookup through the development read-only service account succeeded, confirming the provider quota recovered.
- The lookup found 0/3 required development item titles, so ID rendering and live cutover remain gated on creating those three items in `cluster development`.

## Development Items and Local Validation

- Development read-only service-account validation: 3/3 exact item schemas passed.
- Development renderer: 3 ID-only `OnePasswordItem` resources generated at the strict allowlisted paths.
- Development cert-manager and certs paths are isolated overlays; production paths and consumers remain unchanged.
- Immich branch Helm and CloudNativePG references use the generated Secret names; the SOPS base Secrets remain present for rollback.
- OnePassword tooling tests: 13 passed.
- Development 1Password verifier tests: 12 passed.
- Codex harness: 81 passed.
- Production, development, and Immich branch Kustomize renders: 134 resources total.
- Kubeconform 0.7.0: 50 valid, 84 missing-schema skips, 0 invalid, 0 errors.
- Direct-auth chart policy and production-foundation policy: passed.
- Architecture generator write/check: passed.
- Full pre-commit: passed.

## Live Iteration

- First branch-base reconciliation failed before applying the cert-manager overlay because Flux's Kustomize builder rejected a child overlay that referenced its parent as a cycle.
- The verifier's guaranteed restoration returned `flux-system` to `main@sha1:9d2d762bc7d49605d00764494b800a6e31e52b67`; no development consumer changed during the failed attempt.
- Both development overlays were moved to sibling directories (`cert-manager-development` and `certs-development`). Direct overlay renders, architecture regeneration, focused tests, and full pre-commit passed after the correction.
- Immich branch reconciliation, Helm readiness, workload readiness, storage/service/route checks, and the exact `/api/server/ping` probe passed at the PR revision.
- Development has no Authentik deployment. The migrated configuration preserves the rendered legacy development URLs for byte parity; OIDC is explicitly unavailable and was not claimed as an acceptance path for this phase.
- No-output Secret comparison passed 3/3 after replacing Flux's `${cluster_domain}` placeholders with the rendered development domain in the 1Password item.
- Disposable Let's Encrypt staging Certificate issuance passed and its temporary namespace was removed.
- The first outage attempt showed that a blanket egress deny also prevents the operator from observing Kubernetes API events. Cleanup and recovery succeeded.
- A follow-up IP allowlist proved insufficient because Cilium evaluates kube-apiserver traffic after Service translation. Operator logs recorded lost Kubernetes watch streams, so the final validator uses a temporary `CiliumNetworkPolicy` allowing only the native `kube-apiserver` entity and denying vault egress.
- Because development polling is intentionally disabled and metadata-only annotations do not enqueue reconciliation, the validator restarts the stateless operator pod to force startup reconciliation under the outage. The pod became present but NotReady while the generated Secret stayed byte-identical and the consumer stayed ready with the same Pod UID.

## Final Development Acceptance — 2026-08-15

- Exact tested revision: `codex/onepassword-dev-cutover@sha1:12072c0c59fd13a388364291a6a31891263b4ae6`.
- Cert-manager and certs reconciled from the branch revision; no-output parity passed 3/3.
- Disposable Let's Encrypt staging Certificate became Ready and its namespace was removed.
- During simulated vault outage, the operator was unavailable while the generated Secret and ready consumer were retained unchanged.
- After egress restoration, the operator became Ready and the `OnePasswordItem` recovered; the temporary consumer and Cilium policy were removed.
- The shared development Flux source and root Kustomization were restored to `main@sha1:9d2d762bc7d49605d00764494b800a6e31e52b67`.
- The retained `branch-immich-onepassword-dev-cutover` Kustomization, GitRepository, and namespace were deleted normally. The older, unrelated `onepassword-dev-seed` branch environment was left untouched.
- Development Immich OIDC remains untested and unavailable because development has no Authentik deployment; the exact API smoke, route, workloads, database, and storage checks passed.
