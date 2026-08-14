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

Pending.
