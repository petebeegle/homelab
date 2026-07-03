# Evidence: sdd-speckit-foundation

**Branch**: `codex/sdd-speckit-foundation`
**Risk Tier**: low
**Workflow Tier**: docs-only
**Started**: 2026-07-03
**Owner**: implementation-agent-sdd-speckit-foundation

## Spec Kit Initialization

| Command | Result | Notes |
| ------- | ------ | ----- |
| `uvx --from git+https://github.com/github/spec-kit.git specify init --here --integration codex` | ABORTED | The CLI prompted because the current directory was not empty; no tracked changes were made before the prompt aborted. |
| `uvx --from git+https://github.com/github/spec-kit.git specify init --help` | PASS | Help output listed `--integration codex` and `--force`. |
| `uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --integration codex` | PASS | Spec Kit initialized successfully with selected coding agent integration `codex`. |

Spec Kit metadata:

- Version: `0.12.5.dev0` from `.specify/init-options.json`
- Integration: `codex`
- Fallback: Not used; `codex` integration was available

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Ran before tracked edits. |
| `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Ran before tracked edits. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Ran before tracked edits. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `pre-commit run --all-files` | PASS | All hooks passed: yamllint, merge conflict check, trailing whitespace, large files, end of files, k8svalidate, Terraform fmt/docs, architecture check, Synology OAuth redirect check, Codex retrieval manifest, decision metadata, MCP config consistency, and Codex memory docs lint. |
| `python3 tools/architecture/render.py --check` | PASS | No output; generated architecture is current. |
| `python3 -m unittest discover -s tools/codex-harness/tests` | PASS | 58 tests passed. |
| `python3 -m unittest discover -s tools/development/tests` | PASS | 26 tests passed. |
| `python3 -m unittest discover -s tools/context-pack/tests` | PASS | 2 tests passed. |
| `uv run --project tools/agent-memory pytest tools/agent-memory/tests` | PASS | 16 tests passed. |
| `npm ci && npm test` in `tests/smoke` | PASS | `npm ci` added 3 packages with 0 vulnerabilities; Playwright ran 6 routed-service smoke tests and all passed. |

## Verifier Follow-Up

The verifier did not approve exact HEAD
`90311d5b8db6261d1167aca2d6067ee7a5e491ee` because
`pre-commit run --all-files` modified tracked files for trailing whitespace and
end-of-file normalization.

The implementation owner inspected the verifier-generated tracked diff and kept
it because `git diff --ignore-space-at-eol --ignore-blank-lines` produced no
output for the modified files. The retained modifications were limited to
whitespace and final-newline normalization in Spec Kit-generated files.

Follow-up checks:

| Command | Result | Notes |
| ------- | ------ | ----- |
| `git diff --ignore-space-at-eol --ignore-blank-lines -- <normalized files>` | PASS | No output; verifier changes were whitespace-only. |
| `git diff --check` | PASS | No whitespace errors after normalization. |
| `pre-commit run --all-files` | PASS | Clean rerun after keeping the normalization changes. |

## PR #317 CI Fix Follow-Up

GitHub Actions Agnix CI failed for existing PR #317 at head
`053ebce8da16110ef37bbcd576175de65b77170f` because generated Spec Kit skill
markdown tripped two Agnix hard-error heuristics:

- Repeated shell-quoting examples used `I'm` plus backslash-heavy escaping,
  which Agnix reported as Windows path separators in eight generated skill
  files.
- `.agents/skills/speckit-specify/SKILL.md` used the placeholder
  `<resolved feature dir>` in a JSON example, which Agnix reported as an
  unclosed XML tag.

Fix:

- Reworded the repeated shell-quoting guidance to avoid contractions and
  backslash-heavy example text while preserving the instruction to prefer
  double quotes or shell-safe single-quote escaping.
- Replaced the JSON placeholder with `RESOLVED_FEATURE_DIR` and updated the
  adjacent sentence so the example no longer resembles an XML tag.
- Left the non-failing Agnix `Use when...` description warnings unchanged to
  keep the CI repair focused on hard errors.

Follow-up checks:

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Recreated and validated before tracked edits for the existing PR fix. |
| `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Recreated and validated before tracked edits for the existing PR fix. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Recreated and validated before tracked edits for the existing PR fix. |
| `rg -n "I'm\|I'\\\\''m\|\"<resolved feature dir>\"" .agents/skills/speckit-*/SKILL.md \|\| true` | PASS | No remaining matches for the reported Agnix error patterns. |
| `npx -y agnix@0.25.0 .` | PASS | Found 0 errors and 14 warnings; warnings are the known non-failing description/AGENTS guidance warnings. |
| `pre-commit run --all-files` | PASS | All configured hooks passed. |

## Development Validation

- Profile: none
- Branch slug: N/A
- HEAD: Recorded in implementation owner handoff after commit.
- Report path: N/A
- Cleanup: N/A
- Result or exception: No development-cluster smoke is required because this PR
  changes documentation, agent guidance, and Spec Kit scaffolding only. It does
  not change Kubernetes desired state, Terraform, Flux wiring, Gateway routes,
  storage, secret references, branch overlays, or app behavior.

## Documentation Impact

- Updated: `AGENTS.md`, `.specify/memory/constitution.md`,
  `.specify/templates/spec-template.md`, `.specify/templates/plan-template.md`,
  `.specify/templates/tasks-template.md`,
  `.specify/templates/evidence-template.md`,
  `docs/runbooks/spec-driven-development.md`, and
  `specs/sdd-speckit-foundation/`.
- Generated docs: `docs/architecture.md` was not regenerated because no
  Kubernetes or Terraform source changed.
- No-docs rationale: N/A; documentation is the implementation output.

## Exceptions And Follow-Ups

- No development-cluster smoke for docs-only scaffolding; substitute local checks
  are recorded above.
- Verifier found that the original exact HEAD required pre-commit whitespace/EOF
  normalization; this was fixed and pre-commit now reruns cleanly.
- PR #317 Agnix CI then failed on generated Spec Kit skill markdown; this
  follow-up fixes only the hard errors and intentionally leaves non-failing
  warnings for a separate cleanup if desired.

## Final State

- Final branch: `codex/sdd-speckit-foundation`
- Final HEAD: Recorded in implementation owner handoff after commit.
- Commit: Conventional commit created; exact final `HEAD` is recorded in the
  implementation owner handoff because it cannot be embedded in its own commit
  without changing the SHA.
- Verifier approval: not created by implementation owner
