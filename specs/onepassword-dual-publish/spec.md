# Feature Specification: 1Password Dual Publish

**Feature Branch**: `codex/onepassword-dual-publish`
**Created**: 2026-08-09
**Status**: Approved
**Risk Tier**: high

## Summary

Create production-vault items matching every legacy SOPS-managed Kubernetes Secret object, then publish parallel `OnePasswordItem` resources whose generated Secrets use a `-onepassword` suffix. Require exact type, key-set, and byte parity before any consumer cutover. Existing SOPS resources and consumers remain unchanged.

## Human Gate Status

The user supplied and approved this as phase 3 of the migration. Clarification found one source-count correction: the repository contains 16 encrypted files but 17 `kind: Secret` documents because the Immich file contains two Secrets. All 17 objects are in scope; omitting one would violate the requested complete dual publication.

## In Scope

- Maintain a non-secret inventory of 17 legacy namespace/name/type/key schemas and corresponding 1Password item titles.
- Create the 17 items out of band in `cluster production`, with exact non-empty field labels and values.
- Recover `grafana/grafana-credentials` from the live Kubernetes Secret because its committed SOPS document fails MAC validation.
- Resolve vault/item IDs from authenticated `op` metadata and generate Git-tracked `OnePasswordItem` resources containing IDs only.
- Generate parallel Secrets named `<legacy-name>-onepassword`.
- Reconcile all items only in production after their namespace owners and the operator are Ready.
- Validate `Ready=True`, Secret type, exact key set, and byte-for-byte data parity without printing names of mismatched keys or any values.

## Out of Scope

- Changing a workload, issuer, Flux source, or other consumer to the generated Secret.
- Removing or editing a SOPS Secret, decryption block, Age key, or SOPS tooling.
- Creating development-vault application items; development cutover items belong to phase 4.
- Terraform/provider credentials.

## User Stories

### P1 - Build Exact Item Inventory

As an operator, I can see every required item title and field label without exposing values, including both Immich Secrets and the live-authoritative Grafana credentials.

**Acceptance**: Inventory contains 17 unique namespace/name pairs, unique item titles, valid generated names, exact live key schemas, and Secret types.

### P2 - Publish Parallel Secrets

As an operator, I can resolve authenticated 1Password item IDs into Git-tracked `OnePasswordItem` resources without names or values in item paths.

**Acceptance**: All resources use the production vault/item IDs, a `-onepassword` name, correct namespace/type, and reconcile `Ready=True`; no consumer changes.

### P3 - Prove Parity Without Output

As a reviewer, I can run one validator that proves all legacy/generated pairs have identical types, key sets, and decoded bytes while reporting only pair-level PASS or mismatch class/count.

**Acceptance**: All 17 pairs pass. Captured output contains no fixture or live Secret value, base64 payload, or mismatched key name.

## Requirements

- **FR-001**: The migration inventory MUST cover 16 encrypted files and all 17 Secret documents.
- **FR-002**: Item titles MUST be `k8s--<namespace>--<legacy-name>` and contain exactly the expected non-empty fields, with no populated note, URL, or extra field.
- **FR-003**: Git-tracked item paths MUST use vault and item IDs, never titles.
- **FR-004**: Generated Secret names MUST append `-onepassword` and MUST NOT collide with legacy names.
- **FR-005**: `immich/immich-postgres-user-onepassword` MUST use type `kubernetes.io/basic-auth`; every other generated Secret MUST use `Opaque`.
- **FR-006**: The resolver MUST capture `op` JSON without echoing it, validate IDs/field labels, and write only non-secret manifests.
- **FR-007**: The parity validator MUST compare decoded bytes with constant-time comparison and suppress captured Kubernetes output on success and failure.
- **FR-008**: A missing pair, non-Ready item, type mismatch, key-set mismatch, or any byte mismatch MUST fail acceptance.
- **FR-009**: The production Flux Kustomization MUST depend on the operator and namespace-owning Kustomizations, prune/wait, and change no consumer reference.
- **FR-010**: Deleting a durable `OnePasswordItem` MUST be documented as destructive because it deletes the generated Secret.
- **FR-011**: All existing 17 SOPS decryption blocks and 16 encrypted files MUST remain unchanged.

## Edge Cases

- Duplicate item titles, missing/empty fields, populated default notes, URLs/files, invalid IDs, or extra fields block manifest generation.
- Dotted keys such as `credentials.json`, `secrets.yaml`, and `immich-config.yaml` remain exact; the operator supports Kubernetes-valid `[-._a-zA-Z0-9]+` labels.
- Multiline values and trailing newlines are byte-significant and caught by parity.
- Grafana committed decryption failure does not permit using stale ciphertext; its live Secret is authoritative for value recovery and parity.
- If any namespace dependency is unready, dual publication waits rather than applying a partial set.

## Success Criteria

- **SC-001**: Inventory validation reports 17 unique, complete entries.
- **SC-002**: Both cluster entrypoints render/conform and development receives no production item.
- **SC-003**: All 17 production items report Ready and all 17 generated Secrets exist.
- **SC-004**: No-output parity reports 17/17 PASS.
- **SC-005**: Git diff changes zero SOPS documents, decryption blocks, and consumer Secret references.

## Assumptions

- The authenticated human account can create Secure Note items in `cluster production`; item notes remain empty and all credential data is stored in custom fields whose labels exactly match the inventory.
- The production service account can read every created item.
- Operator 1.12.0 behavior is authoritative: non-empty item fields become Secret data keys, valid dotted/uppercase labels are preserved, empty fields are skipped, and `OnePasswordItem.type` controls Secret type.
