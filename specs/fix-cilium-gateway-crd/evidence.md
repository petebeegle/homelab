# Evidence: Fix Cilium Gateway CRD

**Branch**: `codex/fix-cilium-gateway-crd`
**Risk Tier**: high
**Started**: 2026-08-03

## Spec Kit Initialization

- Command: Repo-local Spec Kit skills and scripts
- Outcome: PASS; specification, plan, checklist, tasks, and analysis completed
- Spec Kit version: `0.12.5.dev0` from `.specify/init-options.json`
- Integration: `codex`
- Fallback: Preferred `/workspaces/homelab-worktrees/` was not writable; used
  the allowed `.codex/tmp/worktrees/fix-cilium-gateway-crd` worktree. The
  upstream optional agent-context update script is not present in this repo.

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent brief | PASS | User requested investigation, reviewed the diagnosed cause and proposed repair, then instructed "fix". |
| Spec approval | PASS | The follow-up instruction approves the previously proposed bounded repair. |
| Clarify | SKIP | Root cause, scope, non-goals, and acceptance were unambiguous from live evidence. |
| Plan approval | PASS | The plan matches the previously presented CRD, reconcile, operator restart, and layered verification sequence. |
| Checklist | PASS | `checklists/requirements.md` passed 16/16; `checklists/recovery.md` passed 15/15. |
| Tasks/analyze approval | PASS | 7/7 functional requirements and 5/5 buildable success criteria mapped to tasks; no critical/high findings or constitution conflicts. |
| Converge | PASS | No implementation gaps found across 7 functional requirements, 5 success criteria/acceptance outcomes, planned touchpoints, and 7 constitution principles. Existing post-merge tasks cover production outcomes. |

## Baseline Failure Evidence

- Production Cilium HelmRelease upgraded to `1.20.0` at
  `2026-08-01T18:45:42Z`.
- Cilium Operator logged that required CRD
  `backendtlspolicies.gateway.networking.k8s.io` was not found.
- Production `cilium-secrets` contained zero Secrets and Envoy returned
  `{"certificates": []}`.
- All 11 production synthetic HTTPS tests failed with
  `net::ERR_CONNECTION_RESET`.
- `whoami.lab.petebeegle.com`, `monitoring.lab.petebeegle.com`, and
  `otel.lab.petebeegle.com` accepted TCP/443 and reset during TLS negotiation.
- Proxmox metric series stopped after the upgrade window; three active Proxmox
  alerts were missing-data consequences while all five Kubernetes nodes remained
  Ready.
- Development cluster was reachable but did not contain the required CRD.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | Branch and required SDD artifacts satisfy the workflow guard. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| Gateway API v1.5.1 BackendTLSPolicy URL HEAD request | PASS | Upstream raw manifest returned HTTP 200 before the source edit. |
| Pre-change exact CRD render count | FAIL (expected) | The shared CRD render contained zero BackendTLSPolicy CRDs. |
| Initial post-change cluster assertion | FAIL (test design) | Cluster entrypoints activate Flux paths rather than embedding shared CRDs; acceptance and checks were corrected before continuing. |
| Initial `python3 tools/architecture/render.py --check` | FAIL (expected discovery) | Generated architecture inventories remote CRD resources and required regeneration. |
| `kubectl kustomize kubernetes/infra/crds` plus exact count | PASS | Rendered one BackendTLSPolicy CRD. |
| Development and production cluster renders plus exact activation count | PASS | Each rendered one Flux activation of `./kubernetes/infra/crds`. |
| `kubectl --kubeconfig /home/vscode/.kube/homelab-development.config apply --server-side --dry-run=server -k kubernetes/infra/crds -o name` | PASS | Development API server accepted the complete shared CRD set, including BackendTLSPolicy. |
| `python3 tools/architecture/render.py --check` after regeneration | PASS | Generated architecture is current. |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | Branch and required SDD artifacts satisfy the workflow guard. |
| `pre-commit run --all-files` | PASS | All 13 configured hooks passed, including YAML, Kubernetes, Terraform, architecture, retrieval, and synthetic mirror checks. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| `https://whoami.dev.lab.petebeegle.com` | Development verifier plus targeted shared-base recovery | PASS | The committed CRD reconciled from the branch, Cilium 1.20 started its Gateway controllers after an operator restart, the route reported `Accepted=True` and `ResolvedRefs=True`, and curl returned the whoami response with `X-Forwarded-Proto: https`. |
| `https://whoami.lab.petebeegle.com` | Direct HTTPS probe and synthetic smoke | PENDING | |
| `https://otel.lab.petebeegle.com` | Direct TLS/HTTP probe plus Mimir sample freshness | PENDING | |

## Deployment State

- Development source fetched SHA: `d02f2cf41b1127b65c64268b8ba50ef726bcc0b7`
- Development target CRD SHA: the `crds` Kustomization successfully applied the
  branch SHA before verifier cleanup restored the source to `main`
- Development live resource: BackendTLSPolicy CRD present; temporarily applied
  outside Flux inventory and annotated
  `codex.openai.com/temporary-development-validation=fix-cilium-gateway-crd`
  until the reviewed change merges
- Development Gateway/listener/route: all Flux Kustomizations restored Ready;
  whoami parents reported `Accepted=True` and `ResolvedRefs=True`
- Development exact user-facing URL: PASS; HTTPS returned whoami and
  `X-Forwarded-Proto: https`
- Production source, target, and user path: PENDING reviewed merge

## Development Validation

- Profile: whoami with `--include-cluster-base`
- Branch slug: `fix-cilium-gateway-crd`
- Validated implementation SHA: `d02f2cf41b1127b65c64268b8ba50ef726bcc0b7`
- Report path: N/A; the verifier emits command output and performs cleanup rather
  than writing a report artifact
- Cleanup: PASS; branch-scoped Flux objects and namespace were deleted, the
  shared GitRepository was restored to `main`, and every development Flux
  Kustomization was restored Ready
- Result: PASS with a documented verifier limitation. The first run reconciled
  the shared base from `main`, so its branch-scoped route lacked an accepted
  parent. After the CRD was applied and the Cilium Operator restarted, the exact
  development HTTPS path passed. A second run proved the branch `crds`
  Kustomization applied `d02f2cf`, but the root Kustomization then restored the
  shared source to `main`; dependent Kustomizations correctly rejected the mixed
  revision. The redundant wait was interrupted and cleanup completed.
- Substitute checks: server-side apply of the exact committed Gateway API v1.5.1
  CRD to development, operator rollout, required-GVK discovery log, Gateway
  reconciliation, route conditions, exact HTTPS curl, and final all-Ready Flux
  audit
- Restart behavior: REQUIRED. Cilium discovers the required Gateway API set at
  operator startup; restarting only `deployment/cilium-operator` enabled the
  Gateway controllers.
- Terraform preflight: init and validate passed with existing provider
  deprecation warnings. Plan reported 12 creates because development Terraform
  state was unavailable to this checkout; no Terraform apply was requested or
  performed.

## Documentation Impact

- Updated: SDD artifacts under `specs/fix-cilium-gateway-crd/`
- Generated docs: `docs/architecture.md` regenerated to include the new remote
  CRD resource; runtime topology is unchanged
- No-docs rationale: Binding Gateway API and GitOps decisions already describe
  the intended architecture; this is a compatibility repair, not a new operating
  model.

## SDD Conformance

- Local sources checked: `AGENTS.md`, Spec-Driven Development runbook,
  Implementation Workflow runbook, development validation ADR/runbook, GitOps
  ADR, and Cilium Gateway API ADR
- Upstream Spec Kit sources checked: N/A; no Spec Kit behavior changes
- Human-gated Spec Kit alignment: Intent, spec, plan, checklist, and task/analyze
  approvals are recorded above
- Artifact updates after implementation: PASS; converge found no unrepresented
  implementation work and left `tasks.md` unchanged

## Exceptions And Follow-Ups

- The worktree location fallback and missing optional agent-context update script
  are recorded above.
- The development verifier cannot keep the shared GitRepository on a branch
  revision while reconciling root-managed Flux objects; the exact limitation and
  substitute validation are recorded above. This did not relax the exact routed
  HTTPS acceptance criterion.
- Production recovery remains gated on reviewed PR merge per the approved plan.

## Final State

- Final branch: `codex/fix-cilium-gateway-crd`
- Final HEAD: supplied from the current branch by the PR workflow guard
- Implementation commit: `d02f2cf41b1127b65c64268b8ba50ef726bcc0b7`
- Evidence/handoff commit: this final pre-merge evidence update
- Draft PR: `https://github.com/petebeegle/homelab/pull/374`
- Merge status: PENDING human review; production remains unchanged by this branch
