# Evidence: onepassword-dual-publish

## Prior Gate

- Production Flux/operator revision: `main@sha1:6844af5ccc5bbd0d06b2120140915dabf0ecb0db`, Ready.
- Production rotation: Secret resourceVersion `116799548 -> 116801968`; pod UID `982d500a-39e6-4980-858c-ed4940b953b9 -> 407f0ea8-1043-4c1b-b603-1eb4890a676f`; namespace removed.
- Operator alert: deployed healthy expression `0`; missing-Deployment expression `1`.
- Item alert: isolated invalid item reached Ready=False and query `1`; disposable namespace removed before ten minutes.

## Inventory Discovery

- Encrypted files: 16.
- Kubernetes Secret documents: 17; Immich contains two.
- Live schemas/types: 17/17 read successfully without value output.
- `kubernetes/infra/monitoring/grafana/secret.yaml`: committed SOPS MAC mismatch confirmed; live Secret is the recovery authority.

## Implementation Validation

- Authenticated item validation: `Production 1Password items validated: 17 ID-only resources`.
- Authenticated manifest generation: `Production 1Password items rendered: 17 ID-only resources`.
- ID-only safety scan: 17/17 resources contain only valid 26-character vault/item IDs; no `ENC[` payload appears.
- Direct item Kustomization render: 17 `OnePasswordItem` resources.
- Production and development cluster entrypoints: render PASS; the production root alone references `onepassword-items.yaml`.
- Resolver/parity unit tests: 8 PASS.
- Codex harness: 81 PASS.
- Architecture generator: write/check PASS.
- Direct-auth operator chart policy and production-foundation policy: PASS.
- Full pre-commit: PASS, including YAML, Kubernetes validation, generated architecture, production policy, and migration safety tooling.
- SOPS/consumer diff assertion: zero encrypted Secret/Grafana environment manifests and zero consumer paths changed.
- Pinned kubeconform 0.7.0 over production, development, and direct item renders: 139 resources, 44 valid, 0 invalid, 0 errors, 95 missing-schema skips.
- Rebased onto prerequisite merge `cdc8927b98deeb932dcf6edd05c35d116d6cadac`; the active Spec Kit pointer remains `onepassword-dual-publish`, and generated architecture contains both the Jellyfin SOPS correction and production item activation.

## Discovered Prerequisite

- Before correction, the live decoded `jellyfin/jellyfin-secrets` value began with SOPS ciphertext because `app-jellyfin` lacked a Flux `decryption` block.
- A no-output comparison confirmed the committed Jellyfin and Authentik SOPS fields decrypt to identical plaintext.
- The Jellyfin 1Password item therefore uses the decoded live `authentik/authentik-secrets` field as the correct shared OAuth credential, never the live Jellyfin ciphertext.
- Prerequisite PR #390 merged as `cdc8927b98deeb932dcf6edd05c35d116d6cadac`.
- Production Flux source and `app-jellyfin` applied that exact revision; the live resource uses `sops`/`sops-age`.
- No-output live comparison passed: Jellyfin and Authentik OAuth bytes are equal and the Jellyfin value is not an SOPS envelope.
- Jellyfin HelmRelease remained Ready and Deployment rollout status was complete.

## PR State

- Branch: `codex/onepassword-dual-publish`
- Commit subject: `feat: publish 1password secret mirrors`
- Draft PR: #393
- Post-merge Ready/parity acceptance remains pending by design.
