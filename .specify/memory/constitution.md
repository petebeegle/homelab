# Homelab Constitution

## Core Principles

### I. GitOps Is The Source Of Truth

All durable cluster state is expressed in Git and reconciled by Flux. Manual
cluster changes are temporary break-glass or diagnostic actions and must be
backfilled into the repository when they should persist. Production changes are
never made first in the live cluster.

Binding source: `docs/decisions/flux-gitops-source-of-truth.md`.

### II. Gateway API Is The Ingress Contract

Cilium Gateway API is the ingress standard. New exposure uses `HTTPRoute` for
Gateway-terminated HTTP(S) or Cloudflare Tunnel HTTP routing, and `TLSRoute` for
passthrough services that terminate TLS themselves. Traditional Kubernetes
`Ingress` resources are not added.

Binding source: `docs/decisions/cilium-gateway-api-ingress.md`.

### III. Secrets Stay Encrypted

Committed Kubernetes secrets are SOPS-encrypted with Age recipients. Plaintext
secret manifests, local kubeconfigs, Talos configs, Terraform variable files, and
runtime credentials stay out of commits. Secret manifests use names matched by
`.sops.yaml`.

Binding source: `docs/decisions/sops-age-secrets.md`.

### IV. Storage Defaults To Synology NFS

Persistent app storage uses the Synology-backed NFS CSI default
`nfs-csi-storage` unless a binding decision record requires a different class.
Media or download payloads may opt into the dedicated media StorageClass when the
decision record allows it. NFS-backed workloads depend on healthy `nfs-csi`.

Binding source: `docs/decisions/synology-nfs-storage.md`.

### V. Talos Boundaries Are Respected

Talos nodes are managed through the Talos API with `talosctl`. SSH-based node
administration is outside the operating model. Diagnostics prefer direct control
plane node endpoints and follow the Talos-first order from the runbook and ADR.

Binding source: `docs/decisions/talos-management-boundaries.md`.

### VI. Evidence Scales With Risk

Every implementation declares a risk tier and records TDD, local checks, and
development validation evidence appropriate to that tier. Covered
cluster-affecting changes require development-cluster validation before
production-oriented PR completion, or a documented unavailable-infrastructure
exception with substitute checks.

Binding sources:

- `docs/decisions/tdd-and-development-smoke-evidence.md`
- `docs/runbooks/development-cluster.md`
- `docs/runbooks/implementation-workflow.md`

### VII. Branch-Scoped Spec Kit Work

Each implementation uses one `codex/<implementation>` branch, one
`specs/<implementation>/` directory, and one PR. Tracked changes default to a
dedicated worktree under `/workspaces/homelab-worktrees/<implementation>` so
multiple efforts can run concurrently. Runtime scratch files under `.codex/tmp/`
are local and non-durable; GitHub PR review and status checks provide review
gating.

Binding source: `docs/decisions/codex-implementation-workflow.md`.

## SDD Artifacts

Each implementation keeps durable planning artifacts in
`specs/<implementation>/`:

- `spec.md` states the user-visible outcome, requirements, acceptance scenarios,
  assumptions, and binding source links.
- `plan.md` records risk tier, technical approach, constitution check,
  development validation expectations, documentation impact, and test strategy.
- `tasks.md` lists implementation tasks in executable order with traceability to
  requirements and evidence.
- `evidence.md` records commands, outcomes, smoke evidence, exceptions, and final
  branch state.

`.codex/tmp/` remains local runtime scratch for prompt intent, temporary command
state, and PR summary drafts. Anything needed by future readers belongs in
`specs/<implementation>/` or a canonical doc/runbook.

## Tiered Workflow

Use these tiers when writing `plan.md`, `tasks.md`, and `evidence.md`:

- `tiny`: comment, typo, link, or wording-only change with no behavior change.
- `low`: narrow local code, tooling, generated-doc, or manifest-adjacent change
  with little operational blast radius.
- `medium`: app behavior, Kubernetes manifests, Flux wiring, Terraform logic,
  Gateway routes, storage, secret references, or branch overlays.
- `high`: cluster-scoped controllers, CRDs, networking, storage classes,
  authentication, production traffic paths, secret handling, or multi-app impact.

`docs-only` from `docs/runbooks/implementation-workflow.md` maps to `tiny` or
`low` SDD work depending on review risk.

## Governance

This constitution summarizes binding decisions and routes agents to durable
artifacts. It does not supersede ADRs, runbooks, AGENTS.md, or harness
validators. When conflict appears, follow the binding decision record or
validator and update this constitution in the same implementation.

Amendments require:

1. A named implementation on branch `codex/<implementation>`.
2. Updated SDD artifacts under `specs/<implementation>/`.
3. Links to new or changed ADRs/runbooks when authority changes.
4. Evidence that relevant local checks passed or documented exceptions explain
   why they did not run.

**Version**: 1.0.0 | **Ratified**: 2026-07-03 | **Last Amended**: 2026-07-03
