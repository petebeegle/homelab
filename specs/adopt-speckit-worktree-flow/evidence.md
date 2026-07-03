# Evidence: adopt-speckit-worktree-flow

**Branch**: `codex/adopt-speckit-worktree-flow`
**Risk Tier**: medium
**Started**: 2026-07-03

## Workflow Bootstrap

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_active_implementation.py ...` | PASS | Ran before tracked edits under the old workflow. |
| `python3 tools/codex-harness/validate_implementation_plan.py ...` | PASS | Ran before tracked edits under the old workflow. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner ...` | PASS | Ran before tracked edits under the old workflow. |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence --head "$(git rev-parse HEAD)"` | PASS | Branch-derived SDD validation succeeds after the workflow migration. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 -m pytest tools/codex-harness/tests/test_implementation_workflow_guard.py tools/codex-harness/tests/test_verifier_push_guard.py tools/codex-harness/tests/test_create_implementation_pr.py tools/codex-harness/tests/test_validate_sdd_context.py` | FAIL/SKIP | `pytest` is not installed in this environment. |
| `python3 -m unittest tools.codex-harness.tests.test_implementation_workflow_guard tools.codex-harness.tests.test_verifier_push_guard tools.codex-harness.tests.test_create_implementation_pr tools.codex-harness.tests.test_validate_sdd_context` | PASS | 30 tests passed. |
| `python3 -m unittest discover -s tools/codex-harness/tests` | PASS | 73 tests passed after implementation and after executable-bit restoration. |
| `python3 tools/architecture/render.py --check` | PASS | No output. |
| `pre-commit run --all-files` | FAIL/BLOCKED | All hooks before `agent-memory-lint` passed. `agent-memory-lint` failed because `.codex/memory` does not exist in this worktree. |

## Development Validation

- Profile: none
- Reason: local workflow tooling and documentation only; no cluster-affecting
  manifests or runtime app behavior changed.

## Final State

- Final branch: `codex/adopt-speckit-worktree-flow`
- Final HEAD: reported in final handoff after commit.
- Commit: reported in final handoff after commit.
