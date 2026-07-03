# Evidence: sdd-skill-doc-cleanup

**Branch**: `codex/sdd-skill-doc-cleanup`
**Risk Tier**: low
**Started**: 2026-07-03
**Owner**: implementation-agent-sdd-skill-doc-cleanup

## Spec Kit Initialization

- Command: Not run during this cleanup; existing Spec Kit scaffolding on
  `origin/main` was used.
- Outcome: Existing `.specify/` templates and generated skills were present.
- Spec Kit version: Not changed by this implementation.
- Integration: Existing Codex integration.
- Fallback: None.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked SDD bootstrap. |
| `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked SDD bootstrap. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Completed before tracked SDD bootstrap. |

## Audit Decisions

| Area | Decision | Notes |
| ---- | -------- | ----- |
| `.agents/skills/` | Keep tracked files unchanged. | `git ls-files .agents/skills` shows only generated Spec Kit skills; legacy homelab skills are not tracked on this branch. |
| `.codex/agents/*.toml` | Update stale schema keys. | Replaced `instructions` with `developer_instructions`; added SDD context reminders to migration worker and verifier agents. |
| `.codex/memory/approved/*.md` | Reverify useful entries. | Refreshed expired `last_verified` values to 2026-07-03 and `review_after` values to 2026-10-03; updated harness validation commands to current repo usage. |
| `.codex/retrieval.yaml` | Remove historical plans from default binding context. | Dropped `PLANS.md` from the binding-agent-context include list. |
| `AGENTS.md` and runbooks | Keep unchanged. | Current start-here guidance already points to SDD and implementation workflow runbooks. |
| `PLANS.md` | Keep as historical reference. | Added note that current implementation planning lives in `specs/<implementation>/` and the file is no longer default binding context. |
| `docs/decisions/agent-memory-compaction.md` | Update stale resume context. | Replaced `PLANS.md` resume guidance with SDD and implementation workflow runbooks, and refreshed `last_verified`. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | SDD artifacts are present and non-empty. |
| `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence --head "$(git rev-parse HEAD)"` | PASS | Re-run after evidence edits; evidence contains no stale explicit `HEAD:` record. |
| `python3 -m unittest discover -s tools/codex-harness/tests` | PASS | Ran 75 tests. |
| `pre-commit run --all-files` | PASS | Ran twice; yamllint, merge-conflict check, whitespace checks, k8svalidate, Terraform fmt/docs, generated architecture, Synology OAuth redirect, retrieval manifest, decision metadata, MCP config, and memory lint all passed. |
| `python3 tools/architecture/render.py --check` | PASS | No generated architecture changes needed. |
| `python3 -m unittest discover -s tools/development/tests` | PASS | Ran 28 tests. |
| `python3 -m unittest discover -s tools/context-pack/tests` | PASS | Ran 2 tests. |
| `uv run --project tools/agent-memory pytest tools/agent-memory/tests` | FAIL | Environment issue: `uv` reported no interpreter found for Python 3.14.6 in managed installations or search path. Branch does not change agent-memory code. |
| `npx -y agnix@0.25.0 .` | PASS | Exit 0 with 14 warnings: generated Spec Kit skill descriptions, existing AGENTS placeholder paths, one negative-instruction warning, and `.agnix.toml` version-pinning info. |
| `(cd tests/smoke && npm ci && npm test)` | PASS | Optional Playwright smoke suite ran 6 tests; all passed. Generated `node_modules` was removed afterward. |
| `git diff --check` | PASS | No whitespace errors. |

## Development Validation

- Profile: none
- Branch slug: N/A
- HEAD: N/A for development smoke
- Report path: N/A
- Cleanup: N/A
- Result or exception: Docs-only/local agent configuration cleanup. No
  Kubernetes, Terraform, Flux, Gateway, storage, secret, or app behavior changes
  are in scope, so development-cluster smoke is not required.

## Documentation Impact

- Updated: `.codex/agents/*.toml`, `.codex/memory/approved/*.md`,
  `.codex/retrieval.yaml`, `PLANS.md`,
  `docs/decisions/agent-memory-compaction.md`, and
  `specs/sdd-skill-doc-cleanup/`.
- Generated docs: `docs/architecture.md` not expected to change.
- No-docs rationale: N/A; documentation and agent guidance are the primary
  implementation surface.

## Exceptions And Follow-Ups

- `uv run --project tools/agent-memory pytest tools/agent-memory/tests` could
  not start because this environment does not provide Python 3.14.6 to `uv`.
- Optional `tests/smoke` Playwright live-route smoke was run because the package
  had a normal lockfile path; all 6 tests passed.
- Exact post-commit handoff SHA is recorded in `.codex/tmp/pr-summary.md` after
  commit so tracked evidence does not contain a stale self-referential `HEAD:`
  record.

## Final State

- Final branch: `codex/sdd-skill-doc-cleanup`
- Final commit SHA: Recorded after commit in `.codex/tmp/pr-summary.md` and
  final handoff response.
- Commit: Conventional commit created after this evidence update; exact SHA is
  recorded in `.codex/tmp/pr-summary.md` and the handoff response.
- Verifier approval: not created by implementation owner
