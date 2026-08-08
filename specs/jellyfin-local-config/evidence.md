# Evidence: jellyfin-local-config

**Branch**: `codex/jellyfin-local-config`
**Risk Tier**: medium
**Started**: 2026-08-08

## Spec Kit Initialization

- Command: Repo-local Spec Kit templates and workflow guidance reviewed through
  the connected GitHub repository.
- Outcome: PASS for artifact creation; no Spec Kit scaffolding changes.
- Spec Kit version: Existing repository version; not changed by this
  implementation.
- Integration: `codex`
- Fallback: The execution environment had no mounted repository checkout,
  kubeconfig, authenticated `gh`, `kubectl`, or `kustomize`. Connector-backed
  branch and commit operations were used. Repository-local and cluster checks
  remain explicit draft-PR gates rather than being represented as passed.

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent brief | PASS | User reported severe ingest degradation and approved moving config I/O off NFS. |
| Spec approval | PASS | User reviewed the proposed artifacts and added critical authentication and memory constraints. |
| Clarify | PASS | Authentication preservation, native fallback, migration ordering, rollback, and low-memory behavior were clarified in conversation. |
| Plan approval | PASS | User instructed "Ok let's open the PR" after reviewing the bounded plan. |
| Checklist | PASS | Requirements and authentication checklists completed; live cutover items remain intentionally unchecked. |
| Tasks/analyze approval | PASS | All functional requirements map to implementation or explicit acceptance tasks; no unresolved critical conflict. |
| Converge | PASS | ADR, runbook, spec, plan, tasks, tests, and manifests agree on node affinity, stale rollback source, authentication, and memory gates. |

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence` | PENDING | Requires a repository checkout; draft PR CI/local owner check must run it. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 -m unittest tools/development/tests/test_jellyfin_config_migration.py` | PASS (isolated) | The exact proposed shell script and test were executed in a reconstructed repository path; 3 tests passed for copy/integrity, completed restart, and missing SSO fail-closed behavior. Repository-environment rerun is pending. |
| PyYAML parse of proposed `pvc.yaml`, `values.yaml`, `kustomization.yaml`, and production Flux Kustomization | PASS | All proposed YAML documents parsed successfully. |
| `pre-commit run yamllint ...` | PENDING | No mounted checkout/pre-commit environment. |
| `pre-commit run k8svalidate ...` | PENDING | No mounted checkout/pre-commit environment. |
| `kubectl kustomize kubernetes/apps/jellyfin` | PENDING | `kubectl`/`kustomize` unavailable in the connector execution environment. |
| `python3 tools/policy/check_decision_metadata.py` | REVIEWED/PENDING | ADR metadata follows the required schema and uses the next unused ID `ADR-0015`; repository execution pending. |
| `python3 tools/architecture/render.py --check` | PENDING | Generated architecture must not be edited manually; repository execution pending. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| Jellyfin development branch environment | Existing `jellyfin` smoke profile | PENDING | Requires development kubeconfig. The fixture proves routed startup but not production-equivalent existing-user OIDC. |
| `https://jellyfin.${cluster_domain}/sso/OID/start/authentik` | Controlled cutover request | PENDING | Must redirect to Authentik without provider errors. |
| Existing SSO user/admin and native administrator | Interactive acceptance | PENDING | Release-blocking; pod readiness alone is insufficient. |

## Deployment State

- Source fetched SHA: Pending merge.
- Target applied SHA: Pending merge.
- Live resource spec checked: Pending.
- Gateway/listener/DNS/certificate checked: Existing route is unchanged; live
  callback behavior pending.
- Exact user-facing URL result: Pending.

## Development Validation

- Profile: existing `jellyfin` profile plus manual storage/init inspection
- Branch slug: Pending
- HEAD: Pending PR head
- Report path: Pending
- Cleanup: Pending
- Result or exception: Not run because this connector session has no development
  kubeconfig. This is an unavailable-infrastructure exception for opening the
  draft PR only, not approval to merge.

## Documentation Impact

- Updated:
  `docs/runbooks/jellyfin-authentik-sso.md`
- Added:
  `docs/decisions/jellyfin-local-config-storage.md`
- Generated docs:
  `docs/architecture.md` check pending; no manual edit made.
- No-docs rationale: N/A.

## SDD Conformance

- Local sources checked: `AGENTS.md`, SDD and implementation runbooks, storage
  ADR, TDD/development evidence ADR, templates, existing Jellyfin SSO runbook.
- Upstream Spec Kit sources checked: N/A; no Spec Kit behavior changed.
- Human-gated Spec Kit alignment: Intent, spec, plan, and task/analyze approvals
  are recorded from the conversation.
- Artifact updates after implementation: Node affinity, stale rollback source,
  memory preflight, and non-representative development OIDC fixture were
  reconciled into all artifacts.

## Exceptions And Follow-Ups

- Repository-local validators and development smoke are pending because the
  connector environment has no checkout or kubeconfig.
- Production authentication acceptance is intentionally pending and
  release-blocking.
- The local PVC needs an explicit long-term backup/recovery follow-up after
  successful cutover.
- The retained NFS PVC is immediate rollback state, not a continuously updated
  backup.

## Final State

- Final branch: `codex/jellyfin-local-config`
- Implementation commit: `59726adf68f23d5cd7b70c2767acb8db575690fc`
- Final HEAD: Use the draft PR head; it is intentionally not embedded because an
  evidence update itself creates a new HEAD.
- Commit: `feat(jellyfin): move config to local storage`
