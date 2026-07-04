# Evidence: home-assistant-region

**Branch**: `codex/home-assistant-region`
**Risk Tier**: high
**Started**: 2026-07-03
**Owner**: implementation-agent-home-assistant-region

## Spec Kit Initialization

- Command: Not run; repository already contains Spec Kit scaffolding.
- Outcome: Reused existing `.specify/` templates.
- Spec Kit version: Not changed.
- Integration: Existing repository integration.
- Fallback: N/A.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_active_implementation.py ...` | PASS | Completed before tracked edits. |
| `python3 tools/codex-harness/validate_implementation_plan.py ...` | PASS | Completed before tracked edits. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner ...` | PASS | Completed before tracked edits. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `sops -d kubernetes/apps/home-assistant/secret.yaml` | PASS | Decryption succeeded; output was discarded to avoid logging secret contents. |
| `kubectl kustomize kubernetes/apps/home-assistant` | PASS | Render includes `home-assistant-secrets`, `/config/secrets.yaml`, and US/Eastern regional settings. |
| `kubectl kustomize kubernetes/apps/home-assistant/branch` | PASS | Render includes non-sensitive branch regional defaults. |
| `python3 tools/architecture/render.py --check` | PASS | Initially reported stale generated docs; passed after `python3 tools/architecture/render.py --write`. |
| `git grep -n -E 'home_latitude:|home_longitude:|home_elevation:' -- . ':!kubernetes/apps/home-assistant/secret.yaml' ':!specs/home-assistant-region/evidence.md'` | PASS | No coordinate secret keys outside the encrypted Secret file and this evidence record. |
| `rg -n 'home_latitude:|home_longitude:|home_elevation:' kubernetes/apps/home-assistant/secret.yaml` | PASS | Encrypted Secret does not expose inner secret keys. |
| `PYTHONPATH=tools/agent-memory/src python3 -m agent_memory.cli lint` | PASS | Added `.codex/memory/.gitkeep` after PR CI reported `missing-root`. |

## Development Validation

- Profile: manual/home-assistant
- Branch slug: home-assistant-region
- HEAD: validation attempted against pre-evidence-amend commit `36f7988`
- Report path: N/A
- Cleanup: No development cluster resources were created before failure.
- Result or exception: `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-region --slug home-assistant-region --push --timeout 600` failed during `terraform -chdir=terraform/development plan -detailed-exitcode -input=false -no-color` because required local development variables were unavailable: `pm_api_url`, `pm_api_token_id`, `pm_api_token_secret`, `github_token`, `github_user`, `docker_user`, `docker_password`, and `talos_version`. Substitute checks were SOPS decryption, production render, branch render, generated architecture check, and secret-safety scans.

## Documentation Impact

- Updated: `docs/runbooks/home-assistant.md`
- Generated docs: `docs/architecture.md`
- No-docs rationale: N/A

## Exceptions And Follow-Ups

- Delegated implementation ownership is unavailable in this runtime because the
  available sub-agent tool requires explicit user authorization for spawning.
  The user explicitly requested implementation by the current agent, and no
  verifier approval is created by the implementation owner.
- Development validation could not complete because required local development
  Terraform variables/secrets were unavailable in this environment.
- PR CI initially failed `agent-memory-lint` because GitHub `main` no longer
  had a tracked `.codex/memory` root after `.gitkeep` cleanup. This branch adds
  `.codex/memory/.gitkeep` so the lint root exists without restoring old memory
  documents.

## Final State

- Final branch: `codex/home-assistant-region`
- Final HEAD: current branch HEAD at verifier handoff, checked with `validate_sdd_context.py --head`.
- Commit: `fix: configure home assistant region`
- Verifier approval: not created by implementation owner
