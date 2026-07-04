# Evidence: home-assistant-automation-yaml-writable

**Branch**: `codex/home-assistant-automation-yaml-writable`
**Risk Tier**: medium
**Started**: 2026-07-04
**Owner**: implementation-agent-home-assistant-automation-yaml-writable

## Spec Kit Initialization

- Command: Manual artifact creation from repo templates and user-provided implementation slug.
- Outcome: PASS
- Spec Kit version: 0.12.5.dev0 from `.specify/init-options.json`
- Integration: codex
- Fallback: Not needed.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_active_implementation.py` | PASS | `.codex/tmp/active-implementation` matches implementation, branch, owner, and clone path. |
| `python3 tools/codex-harness/validate_implementation_plan.py --branch "$(git branch --show-current)"` | PASS | `.codex/tmp/implementation-plan.yaml` matches the active implementation marker and current branch. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner` | PASS | Owner attestation and delegation token validate for `implementation-agent-home-assistant-automation-yaml-writable`. |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence` | PASS | Required SDD artifacts are present and non-empty. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `kubectl kustomize kubernetes/apps/home-assistant > .codex/tmp/home-assistant.render.yaml` | PASS | Base Home Assistant manifests rendered successfully. |
| `kubectl kustomize kubernetes/apps/home-assistant/branch > .codex/tmp/home-assistant-branch.render.yaml` | PASS | Branch Home Assistant manifests rendered successfully. |
| Python/PyYAML render parser assertion | FAIL | PyYAML is not installed in this environment (`No module named 'yaml'`); replaced with source/render `rg` assertions below. |
| `rg -n "automations\\.yaml=config/automations\\.yaml|mountPath: /config/automations\\.yaml" kubernetes/apps/home-assistant kubernetes/apps/home-assistant/branch || true` | PASS | No source ConfigMap generator entry or `/config/automations.yaml` volumeMount remains. |
| `rg -n "^  automations\\.yaml:|mountPath: /config/automations\\.yaml" .codex/tmp/home-assistant.render.yaml .codex/tmp/home-assistant-branch.render.yaml || true` | PASS | No rendered ConfigMap data key named `automations.yaml` and no rendered `/config/automations.yaml` mount. |
| `rg -n "\\[ -f /config/automations\\.yaml \\] \\|\\| printf '\\[\\]\\\\\\\\n' > /config/automations\\.yaml|automation: !include automations\\.yaml" ...` | PASS | Base and branch source plus renders contain the conditional seed and preserved automation include. |
| `python3 tools/architecture/render.py --check` | PASS | Generated architecture document remains current; no generated architecture update required. |
| `git diff --check` | PASS | No whitespace errors before commit. |
| Commit hooks for `git commit -m "fix(home-assistant): keep automation yaml writable"` | PASS | `yamllint`, merge conflict check, whitespace, large-file, EOF, `k8svalidate`, architecture check, and other configured hooks passed. |
| `git restore --source origin/main -- .specify/feature.json` | PASS | Removed the accidental global Spec Kit feature pointer change from this PR payload before verifier. |
| Post-cleanup `kubectl kustomize kubernetes/apps/home-assistant > .codex/tmp/home-assistant.render.yaml` | PASS | Base render still passes after `.specify/feature.json` cleanup. |
| Post-cleanup `kubectl kustomize kubernetes/apps/home-assistant/branch > .codex/tmp/home-assistant-branch.render.yaml` | PASS | Branch render still passes after `.specify/feature.json` cleanup. |
| Post-cleanup source/render assertions for automations mount, ConfigMap key, seed, and include | PASS | Forbidden source/render mount and ConfigMap key remain absent; conditional seed and `automation: !include automations.yaml` remain present. |
| Post-cleanup `python3 tools/architecture/render.py --check` | PASS | Generated architecture document remains current. |
| Post-cleanup `git diff --check` | PASS | No whitespace errors after `.specify/feature.json` cleanup and evidence update. |
| Verifier cleanup `rg -n '\`config/automations\\.yaml\`|code-owned automations|automations in Git|packages or automations|scripts, scenes, or automations' docs/runbooks/home-assistant.md || true` | PASS | No stale repo-path `config/automations.yaml` Git-owned destination remains; runbook now points UI-managed automations to the PVC and Git-owned controls to packages/scripts/scenes unless intentionally moving an automation back to Git. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| `home-assistant-automation-yaml-writable` | Development Home Assistant branch profile with `--push` | PASS | Flux fetched and applied `codex/home-assistant-automation-yaml-writable@sha1:77e91a17196f44eeda5c87c5c3673d1d60e2df6a`; namespace became Active, pod became Ready, PVC/Service/HTTPRoute checks ran, in-cluster HTTP probe matched `Home Assistant|Sign in|Login`, and cleanup deleted the Kustomization/GitRepository and waited for namespace removal. |

## Deployment State

- Source fetched SHA: Development Flux GitRepository fetched `77e91a17196f44eeda5c87c5c3673d1d60e2df6a`.
- Target applied SHA: Development Flux Kustomization applied `77e91a17196f44eeda5c87c5c3673d1d60e2df6a`.
- Live resource spec checked: Development profile checked namespace, pod readiness, PVC storage class, Service, and HTTPRoute.
- Gateway/listener/DNS/certificate checked: Development profile checked HTTPRoute resource; it did not perform an external browser TLS check.
- Exact user-facing URL result: In-cluster Service HTTP probe passed; authenticated Home Assistant UI save path was not exercised.

## Development Validation

- Profile: home-assistant
- Branch slug: home-assistant-automation-yaml-writable
- HEAD: smoke-tested commit `77e91a17196f44eeda5c87c5c3673d1d60e2df6a`
- Smoke-tested SHA: `77e91a17196f44eeda5c87c5c3673d1d60e2df6a`
- Report path: N/A; command emitted inline workflow output.
- Cleanup: PASS; branch Kustomization and GitRepository deleted, namespace deletion completed.
- Result or exception: PASS. Command: `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-automation-yaml-writable --slug home-assistant-automation-yaml-writable --kubeconfig ~/.kube/homelab-development.config --push --timeout 20m`.

## Documentation Impact

- Updated: `docs/runbooks/home-assistant.md`
- Generated docs: No generated architecture update expected because app topology, routes, Services, PVCs, and Terraform source are unchanged.
- No-docs rationale: N/A

## SDD Conformance

- Local sources checked: `AGENTS.md`, `docs/runbooks/spec-driven-development.md`, `docs/runbooks/implementation-workflow.md`, `.specify/memory/constitution.md`
- Upstream Spec Kit sources checked: Local Spec Kit templates and workflow guidance in `.specify/`
- Spec -> Plan -> Tasks -> Implement alignment: Spec defines writable automation behavior, plan records technical approach and medium validation, tasks enumerate implementation and verification steps.
- Artifact updates after implementation: `tasks.md` and `evidence.md` reconciled after local validation and development smoke.
- Verifier cleanup: `.specify/feature.json` restored to `origin/main`; no Home Assistant payload files changed during cleanup.
- Verifier doc cleanup: Removed stale runbook references that presented `config/automations.yaml` as a normal Git-owned automation destination. The runbook now keeps UI-managed automations on the PVC and routes Git-owned controls to packages/scripts/scenes unless an implementation intentionally changes automation ownership.

## Exceptions And Follow-Ups

- PyYAML was unavailable for the first render parser attempt; source/render assertions with `rg` were used instead.
- The development smoke proved render, push, Flux fetch/apply, pod/PVC/Service/HTTPRoute readiness, and an in-cluster Home Assistant HTTP response. It did not authenticate to Home Assistant or click Save in the UI.

## Final State

- Final branch: `codex/home-assistant-automation-yaml-writable`
- Final HEAD: Reported in final response after evidence commit/amend.
- Commit: `fix(home-assistant): keep automation yaml writable`
