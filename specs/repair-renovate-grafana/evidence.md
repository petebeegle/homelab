# Evidence: Repair Renovate Grafana update

## Human gates and workflow

- Intent, spec, plan, and task approval: user's "fix them fan out" followed the
  read-only review establishing stale architecture and controller/CRD skew.
  Approval is carried forward for that concrete repair only.
- Clarify: skipped; desired versions, ownership, and repair are unambiguous.
- Checklist: reviewed version publication/alignment, CRD ownership, generated
  documentation, validation coverage, rollback, and isolation before edits.
- Analyze: requirements map to T002-T006; edits are isolated to this worktree;
  no conflict with parallel PR repairs identified.
- Converge: completed; see final reconciliation below.
- Worktree fallback: `/home/vscode/homelab-worktrees/repair-renovate-grafana`
  because the default `/workspaces/homelab-worktrees` location is unwritable.
- Branch exception: local codex implementation branch will update existing
  Renovate PR #377; no second PR. This lane commits locally and does not push.
- Baseline PR commit: `98d3d4f6f14fe8250eafb9e0f8eda3b704400189`.
- No new automated unit test: the existing architecture check reproduces the
  defect; chart metadata and rendering validate the narrow declarative pin fix.

## Verification results

- `python3 tools/architecture/render.py --check`: reproduced exit 1 before
  edits, showing the stale Grafana CRD URL; passes after `--write`.
- `helm show chart grafana-operator --repo
  https://grafana.github.io/helm-charts --version 5.25.0`: passes; published
  chart version 5.25.0 has appVersion v5.25.0.
- `helm template grafana-operator grafana-operator --repo
  https://grafana.github.io/helm-charts --version 5.25.0 --namespace
  grafana-operator --skip-crds -f .codex/tmp/repair-renovate-grafana/values.yaml`:
  passes with the HelmRelease's values; Deployment image is
  `ghcr.io/grafana/grafana-operator:v5.25.0`.
- `kubectl kustomize` passes for `kubernetes/infra/controllers/grafana-operator`,
  `kubernetes/infra/crds/grafana`, `kubernetes/infra/monitoring/grafana`,
  `kubernetes/clusters/production`, and `kubernetes/clusters/development`.
- OpenAPI validation: extracted each CRD's `openAPIV3Schema` by group/version and
  kind, then ran `jsonschema.Draft7Validator(schema).validate(resource)` for
  each rendered Grafana custom resource. All 32 resources pass against v5.25.0
  schemas. CEL rules and controller reconciliation are not exercised by this
  local check. Used `uv run --no-project --python /usr/bin/python3 --with pyyaml
  --with jsonschema python` because the local interpreter lacks PyYAML and the
  project's Python 3.14.7 is unavailable to the installed uv. Initial attempts
  without `--no-project` failed interpreter selection; the independent check
  succeeded with Python 3.12.3 and temporary dependencies.
- `pre-commit run --all-files`: passes every applicable hook, including
  architecture-doc, yamllint, Kubernetes validation, Terraform formatting/docs,
  and repository policy checks.
- `python3 tools/codex-harness/validate_sdd_context.py --root
  /home/vscode/homelab-worktrees/repair-renovate-grafana --branch
  codex/repair-renovate-grafana --require-plan-artifacts`: passes.
- Spec Kit prerequisite check passes with explicit `SPECIFY_FEATURE_DIRECTORY`
  pointing at this implementation. Its incidental `.specify/feature.json`
  update was restored; no global feature state is included in this repair.

## Development validation and limitations

- Cluster: development, discovered with
  `/home/vscode/.kube/homelab-development.config`; API reachable.
- Read-only discovery: no Grafana or grafana-operator namespace or HelmRelease.
  Thirteen Grafana CRDs exist with stored version v1beta1. The Grafana CRD serves
  and stores v1beta1; existing category is `grafana-operator`, with field managers
  `helm-controller`, `kustomize-controller`, and `kube-apiserver`.
- `kubectl --kubeconfig /home/vscode/.kube/homelab-development.config
  --request-timeout=20s apply --server-side --dry-run=server --force-conflicts
  --field-manager=kustomize-controller -f
  .codex/tmp/repair-renovate-grafana/crds.yaml`: passes for all 13 CRDs.
- Initial dry-run using a separate review manager without `--force-conflicts`
  encountered existing helm-controller/kustomize-controller ownership of
  categories and some version schemas. The forced dry-run proves API admission
  only; it does not prove an unforced apply or Flux reconciliation succeeds.
  No fields were changed in the cluster.
- `smoke_profile: none`: unavailable Grafana development integration exception.
  Parent coordinated and explicitly directed no temporary shared-controller
  installation. A running Grafana instance, credentials, and operator are absent
  in this development topology, so controller reconciliation and the user URL
  cannot be exercised through existing development branch coverage.
- Substitute checks: real development API admission of all proposed CRDs,
  version-aligned chart rendering, 32 repository CR schema checks, focused and
  cluster-root renders, and full pre-commit.
- Deployment state: local rendered desired state only. This lane has not pushed,
  merged, reconciled Flux, installed the controller, or verified Grafana HTTP
  behavior. Runtime compatibility remains unverified; this is not a claim that
  the Grafana upgrade has been deployed successfully.
- Cleanup: no live mutations; scratch manifests remain in ignored `.codex/tmp/`.

## Converge and documentation

- Converge: PASS. Requirements map to verified chart/controller/CRD alignment,
  unchanged Flux CRD ownership, regenerated architecture, and explicit evidence
  of the development coverage boundary. No additional implementation task was
  found; runtime acceptance remains the documented integration exception.
- Updated generated `docs/architecture.md` with its renderer and added this
  implementation's spec, plan, tasks, and evidence.
- Local SDD conformance: artifacts preceded implementation; existing approval
  carried forward, clarify skip recorded, checklist/analyze performed, and
  results reconciled into this evidence. No SDD tooling or standards changed.
