# Process-layer audit

Task 12 of `docs/superpowers/plans/2026-11-15-pr-smoke-gate.md`. Read-only: nothing is deleted here.
Every deletion below is a separate PR, after the owner decides.

**Why this exists.** The repo's agent harness (hooks, Spec Kit, validators, memory tooling) has
grown to roughly 12,000 lines across ten areas. The PR smoke gate (`dev-smoke`) now does the job
most of it was written to do: prove a change works in the development cluster before it merges.
This table says, per area, what it is, who actually calls it, and what I recommend.

Recommendations are mine. "Decide" means the answer depends on a choice only the owner can make.

> **Decided 2026-11-16.** The owner chose to end the per-PR Spec Kit requirement. The decision is
> recorded in `docs/decisions/pr-gated-change-workflow.md` (ADR-0016), which supersedes ADR-0007,
> ADR-0012 and ADR-0013. A second review of this audit found the corrections listed in
> "Corrections after review" below; where they conflict with the tables, the corrections win.

## Summary

| Area | Lines | Recommendation |
|---|---:|---|
| `.codex/hooks/sops_guard.sh` | 45 | **Keep** (named in the plan) |
| `.codex/hooks/terraform_plan.sh` | 124 | **Keep** |
| `.codex/hooks/flux_reminder.sh` | 21 | Delete (reminder text only) |
| `.codex/hooks/pre_commit_check.sh` | 24 | Delete (already unwired on purpose) |
| `.codex/hooks/stop_self_verify.sh` | 80 | Delete (runs unit tests every turn; CI does that) |
| `.codex/hooks/user_prompt_submit.sh` | 94 | Delete with Spec Kit |
| `.codex/hooks/implementation_workflow_guard.sh` | 394 | **Decide** (Spec Kit) |
| `.codex/hooks/verifier_push_guard.sh` | 72 | **Decide** (Spec Kit) |
| `.agents/` (10 Spec Kit skills) | 2,408 | **Decide** (Spec Kit) |
| `.specify/` | 2,116 | **Decide** (Spec Kit) |
| `tools/codex-harness` | 2,878 | **Decide**; split, see below |
| `tools/context-pack` | 395 | Delete (no consumer) |
| `tools/agent-memory` | 1,208 | Delete (nothing to compact) |
| `tools/foundry_bluegreen_pkg` | 741 | **Keep** unless you have retired the blue/green flow |
| `tools/nexus` | 515 | **Keep** (active, operational) |
| `tools/vpn` | 86 | **Decide**: wire into CI or delete |
| `tools/onepassword` | 775 | **Keep** (active, CI-enforced) |

If you end the per-PR Spec Kit requirement, the "Spec Kit" rows plus the unconditional deletes
remove about 9,000 lines. If you keep it, only the unconditional deletes (about 1,700 lines) go.

## The one decision that unlocks most of this

**Do you still want every PR to carry `specs/<implementation>/` artifacts (spec, plan, tasks,
evidence) before it can be pushed?**

- The AGENTS.md rules, the Spec Kit skills, `.specify/`, the workflow guard, the push guard, and
  the SDD validators in `tools/codex-harness` all exist to enforce that one requirement.
- `specs/` already holds 63 directories and 325 files; the whole `kubernetes/` tree has 393.
- With `dev-smoke` required (Task 9), the evidence a reviewer needs is the check itself, not a
  hand-written `evidence.md`.
- Binding decision records say otherwise today (`docs/decisions/codex-implementation-workflow.md`,
  `docs/decisions/tdd-and-development-smoke-evidence.md`), and AGENTS.md says binding decisions
  live there. So ending the requirement needs a new decision record that supersedes those two,
  written first, then the deletions.

I recommend ending it. The other choice is to keep Spec Kit for large changes only and drop it for
routine ones; the hooks and guard would then need a size or path exemption, which is more code,
not less.

## Details

Evidence columns: **Called by** is what references the area from outside it (CI, pre-commit, hook
config, other tools, docs). Activity is the date of the last commit touching the area and the number
of commits in the last 90 days.

Activity measures edits, not use. The hooks and skills run on every Codex session even when nobody
has edited them for months, so "0 commits" does not mean "unused".

### `.codex/hooks/` (8 scripts, wired in `.codex/config.toml`)

These run only when the Codex agent is used. The Claude Code side has its own, much smaller set in
`.claude/hooks/` (5 scripts) and is not part of this audit.

| Script | Purpose | Called by | Activity | Recommendation |
|---|---|---|---|---|
| `sops_guard.sh` | Blocks writing unencrypted Kubernetes Secret manifests | `config.toml` PreToolUse and PostToolUse; named in `docs/runbooks/verification-contract.md` as a guard to keep | 2026-07-04, 0 | **Keep.** CI's `Secrets` job also checks for a `sops:` block, so this is the early local warning, not the only line of defence. |
| `terraform_plan.sh` | When an agent runs `terraform apply`, requires an initialised directory and runs a plan first | `config.toml` PreToolUse (Bash) | 2026-07-04, 0 | **Keep.** A real safety guard on infrastructure changes. |
| `flux_reminder.sh` | Prints a checklist before pushing (Flux deps, SOPS, Gateway refs, StorageClass) | `config.toml` PostToolUse only | 2026-07-04, 0 | **Delete.** It only prints text. The dev smoke now checks the live outcome. |
| `pre_commit_check.sh` | Runs pre-commit | Nothing in `config.toml`. `tools/verification/tests/test_hook_migration.py` asserts it stays unwired. | 2026-07-04, 0 | **Delete.** Already migrated away from on purpose; it is an orphan. |
| `stop_self_verify.sh` | On every agent stop: syntax-checks hooks, runs the `codex-harness` and `context-pack` unit tests, validates the TOML | `config.toml` Stop | 2026-07-04, 0 | **Delete.** CI runs the same tests on the PR. Running them at the end of every agent turn is cost with no extra safety. |
| `user_prompt_submit.sh` | Detects "repo change" prompts and injects the Spec Kit workflow reminder | `config.toml` UserPromptSubmit | 2026-07-04, 0 | **Delete** with the Spec Kit decision. |
| `implementation_workflow_guard.sh` | Refuses edits outside a `codex/<name>` branch with non-empty `specs/<name>/` artifacts (394 lines, five `config.toml` entries) | `config.toml` (Pre/PostToolUse), `tools/codex-harness/tests`, `tools/verification/tests`. `docs/runbooks/verification-contract.md` says to keep "implementation-workflow branch guards". | 2026-07-04, 0 | **Decide.** This is the Spec Kit enforcement. If Spec Kit goes, so does this, and that runbook line must be updated. |
| `verifier_push_guard.sh` | Pre-push check that refuses pushing to `origin` without Spec Kit evidence | `.pre-commit-config.yaml` (`spec-kit-push-guard`, `stages: [pre-push]`) | 2026-07-04, 0 | **Decide**, same as above. Note: in this checkout only the `pre-commit` git hook is installed, so the pre-push guard is currently inert here. It would block the new pipeline anywhere it is installed. |

### `.agents/` and `.specify/` (Spec Kit)

| Area | Purpose | Called by | Activity | Recommendation |
|---|---|---|---|---|
| `.agents/skills/speckit-*` (10 skills) | Codex slash-skills for each Spec Kit phase: specify, clarify, plan, checklist, tasks, analyze, implement, converge, constitution, taskstoissues | Only `.specify/` manifests and the workflow files reference them | 2026-07-03, 0 | **Decide** (Spec Kit). The superpowers skills in this session cover the same phases without a repo-local copy. |
| `.specify/` (templates, bash scripts, constitution, workflow registry, `feature.json`) | Spec Kit scaffolding that produces `specs/<name>/` | The ten skills above, `docs/runbooks/spec-driven-development.md` | 2026-10-03, 3 | **Decide** (Spec Kit). `.specify/feature.json` is rewritten by whichever session is active, so it shows up as a modified file in unrelated work. |

### `tools/`

| Area | Purpose | Called by | Activity | Recommendation |
|---|---|---|---|---|
| `tools/codex-harness` | SDD validators (`validate_active_implementation`, `_implementation_plan`, `_sdd_context`, `_workflow_attestations`) plus tests for the hooks and for two secret-bootstrap helper scripts | `ci.yml` ("Run Codex harness tests"), `stop_self_verify.sh`, `verifier_push_guard.sh`, `create_implementation_pr.sh`, docs | 2026-08-09, 0 | **Decide, and split.** The SDD validators and their tests go with the Spec Kit decision. The tests for `flux_bootstrap_secrets` and `prepare_development_smoke_secrets` cover operational scripts, not process, and should move out (for example to `tools/development/tests`) before this directory is deleted, with the CI step updated. |
| `tools/context-pack` | Renders an agent context pack from `.codex/retrieval.yaml` | Only `stop_self_verify.sh`, which runs its tests. `.codex/retrieval.yaml` is checked by a pre-commit hook and read only by this tool. | 2026-05-17, 0 | **Delete**, with `.codex/retrieval.yaml`, `tools/policy/check_retrieval_manifest.py` and its pre-commit hook. |
| `tools/agent-memory` | CLI that extracts, consolidates and compacts agent memory | `ci.yml` (runs its tests via `uv`), `PLANS.md`, `docs/decisions/agent-memory-compaction.md` | 2026-10-03, 1 | **Delete.** `.codex/memory/` is empty, so there is nothing to compact. Also remove its CI step and the two `.codex/agents/memory_*.toml` files. Needs a superseding decision record. |
| `tools/foundry_bluegreen_pkg` | Blue/green switch tooling for the foundryvtt app, with a shim, 244 lines of tests and a runbook | `tools/foundry_bluegreen.py`, `docs/runbooks/foundry-bluegreen.md`. Not in CI. | 2026-05-17, 0 | **Keep** unless you have retired that flow. It is operational tooling, not agent process. |
| `tools/nexus` | Acceptance check for the hosted Nexus registry | `scripts/NEXUS.md` | 2026-10-03, 3 | **Keep.** Active, operational. |
| `tools/vpn` | Test of the wg-easy defaults reconcile script embedded in `kubernetes/infra/network/vpn/global-config.yaml` | Nothing. Not in CI, not in the harness profile, not in any doc. It needs the wg-easy image or a local libsql to run. | 2026-10-03, 1 | **Decide.** Either run it somewhere that fails a PR, or delete it. As it stands it is a test nothing runs. |
| `tools/onepassword` | Renders and validates 1Password item manifests; checks secret parity | `ci.yml`, two pre-commit hooks, `docs/runbooks/onepassword-operator.md` | 2026-08-29, 1 | **Keep.** Active and enforced; the dev secrets cutover just used it. |

## Also found, outside the list

Not audited in depth, but they belong to the same decision:

- `.codex/scripts/`: `create_implementation_pr.sh`, `stage_implementation_secrets.sh`,
  `install_implementation_secrets.sh` (all exist to move secrets between worktrees for Spec Kit
  runs), `codex_observe.py` (a wrapper that logs every hook call), `prepare_development_smoke_secrets.sh`,
  `run_grafana_mcp.sh` (keep: it starts the Grafana MCP server).
- `.codex/agents/*.toml` (four sub-agent definitions) and `PLANS.md`.
- Four runbooks and one decision record about the Codex/Spec Kit workflow:
  `spec-driven-development.md`, `implementation-workflow.md`, `codex-workflow-protocol.md`,
  `harness-golden-path.md`, `docs/decisions/codex-implementation-workflow.md`.
- `specs/` (63 directories, 325 files): history. Archive or delete after the decision; nothing
  executable depends on it except the validators above.

## Corrections after review

A second pass over this audit, checking its claims against the repository, found these.

1. **ADR-0013 forbade the hard gate.** It said the harness "must not add hard gates for TDD or
   smoke testing until the practice proves stable". Making `dev-smoke` required is such a gate, so
   the superseding record was needed before that step, not only before the deletions. ADR-0016 now
   covers it.
2. **The repository was already outside ADR-0012.** PRs #454 to #476 merged without
   `specs/<implementation>/` artifacts, on the owner's direction. ADR-0016 makes the written rule
   match.
3. **"`dev-smoke` is the evidence" was overstated.** It is true only for apps with a smoke profile
   (whoami and homepage). Everything else reports "not smoke-tested" and passes. ADR-0016 rule 4
   therefore keeps a development-validation requirement for those changes, stated in the PR
   description.
4. **Missed: a production Grafana dashboard depends on the hooks.**
   `kubernetes/infra/monitoring/grafana/dashboards/codex-operations-dashboard.json` charts
   telemetry that `.codex/scripts/codex_observe.py` emits around every hook call. Removing hooks
   empties the matching panels. Keep `codex_observe.py` wrapping the hooks that stay, and treat
   removing or trimming the dashboard as its own production change.
5. **Missed: a required test asserts the workflow guard is wired.**
   `tools/verification/tests/test_hook_migration.py` checks that
   `implementation_workflow_guard.sh` is in the hook config. The removal PR must update it.
6. **Confirmed:** `.codex/memory/` holds only `.gitkeep` and is `tools/agent-memory`'s default
   root, so that tool is unused (its ADR-0007 is now superseded). Nothing invokes
   `tools/context-pack` except the stop hook's tests; `README.md` documents `.codex/retrieval.yaml`
   and needs an edit when it goes. `pre_commit_check.sh` is unwired on purpose.

## Suggested order, once you decide

1. Decision record ADR-0016 (done with this correction).
2. Unconditional deletes (flux_reminder, pre_commit_check, stop_self_verify, context-pack and the
   retrieval manifest check, agent-memory): one PR.
3. Move the two operational test files out of `tools/codex-harness`; one PR.
4. Spec Kit removal (hooks, `.agents`, `.specify`, SDD validators, the pre-push guard, the CI step,
   runbooks, AGENTS.md sections, the wiring test): one PR.
5. `specs/`: archive or delete, last, once no in-flight branch still adds to it.
6. Making `dev-smoke` required and the Renovate auto-merge rule: GitHub issue #477.

Task 11 (trimming AGENTS.md) overlaps with step 4 and should be done together with it.
