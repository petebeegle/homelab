# Evidence: sdd-dev-smoke-matrix

**Branch**: `codex/sdd-dev-smoke-matrix`
**Risk Tier**: medium
**Started**: 2026-07-03
**Owner**: implementation-agent-sdd-dev-smoke-matrix

## Spec Kit Initialization

- Command: Not rerun; repository Spec Kit scaffolding already present on
  `origin/main`.
- Outcome: Used existing `.specify/` templates and constitution.
- Spec Kit version: Not changed by this implementation.
- Integration: Existing repository integration.
- Fallback: None.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked edits. |
| `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked edits. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked edits. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 -m unittest discover -s tools/development/tests` | FAIL then PASS | Red phase failed with missing `SmokeProfile.kustomizations`, missing `assert_tlsroute_ready`, and missing profile-driven Kustomization wait. Final run: 31 tests passed. |
| `python3 -m unittest discover -s tools/codex-harness/tests` | PASS | 75 tests passed. |
| `python3 -m unittest discover -s tools/context-pack/tests` | PASS | 2 tests passed. |
| `pre-commit run --all-files` | PASS | All hooks passed, including generated architecture check. |
| `python3 tools/architecture/render.py --check` | PASS | No generated architecture changes required. |
| `npx -y agnix@0.25.0 .` | PASS with warnings | Initial parallel run saw `tests/smoke/node_modules`; removed generated dependency directory and reran with 0 errors, 14 existing warnings, 1 info. |
| `npm ci && npm test` in `tests/smoke` | PASS | 6 Playwright smoke tests passed against default production smoke domain; generated `node_modules` and `test-results` were removed. |
| `uv run --project tools/agent-memory pytest tools/agent-memory/tests` | SKIP | Environment limitation: uv could not find required Python 3.14.6. |
| `python3 tools/development/verify_branch_deploy.py --app whoami --branch codex/sdd-dev-smoke-matrix --slug sdd-dev-smoke-matrix --print-route-urls` | PASS | Rendered `https://whoami-sdd-dev-smoke-matrix.dev.lab.petebeegle.com` without cluster access. |
| `kubectl --kubeconfig ~/.kube/homelab-development.config get namespace flux-system --request-timeout=10s` | PASS | Read-only credential check succeeded; live smoke attempt is deferred until after the branch has a committed HEAD to push. |

## Development Validation

- Profile: `whoami`
- Branch slug: `sdd-dev-smoke-matrix`
- HEAD: Final committed branch HEAD is reported in handoff; live `--push` smoke must run against committed content.
- Report path: None yet.
- Cleanup: None yet.
- Result or exception: Development kubeconfig exists and read-only access works. The mutating `--push` smoke command is intentionally attempted after the conventional commit so Flux fetches a real implementation branch HEAD instead of the pre-commit base.

## Documentation Impact

- Updated: `docs/runbooks/development-cluster.md` and
  `tools/development/README.md`.
- Generated docs: `docs/architecture.md` unchanged; `render.py --check` passed.
- No-docs rationale: N/A.

## App Coverage And Gaps

- Preserved coverage: `whoami`, `jellyfin`, and `home-assistant` profiles still load and now include branch Flux Kustomization checks plus route URL handoff.
- New coverage: No new app branch overlays were added. `pihole` and
  `foundryvtt` were investigated and documented as gaps because current
  production manifests rely on encrypted secrets and app-specific live
  dependencies that are unsafe to synthesize in this slice.
- Gaps: `authentik` and `monitoring` are infra stacks, not current app branch
  overlays, and require encrypted secrets/cross-stack dependencies. Generic
  branch Playwright execution is documented as a handoff path through
  `routeUrls` and `--print-route-urls`; failure screenshots/traces are not yet
  automated by the dev verifier.
- Synthetic smoke audit: `tests/smoke` and `kubernetes/apps/synthetics/smoke`
  are not exact mirrors. The cluster copy includes runner/reporter files and a
  Home Assistant route case that the local copy lacks; this slice documents the
  gap instead of enforcing generation.

## Exceptions And Follow-Ups

- `uv run --project tools/agent-memory pytest tools/agent-memory/tests` could
  not run because Python 3.14.6 is unavailable in this environment.
- Exact live branch smoke evidence is attempted after commit because
  `verify_branch_deploy.py --push` pushes `HEAD` to origin for Flux to fetch.

## Final State

- Final branch: `codex/sdd-dev-smoke-matrix`
- Final commit SHA: reported in final handoff after commit.
- Commit: Conventional commit pending at evidence write time.
- Verifier approval: not created by implementation owner
