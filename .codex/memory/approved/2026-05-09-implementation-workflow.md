---
status: approved
created: 2026-05-09
last_verified: 2026-05-10
review_after: 2026-05-17
source: user-preference
kind: workflow-preference
scope:
  - implementation-workflow
  - codex-harness
authority: binding
supersedes: []
superseded_by:
---

# Mandatory Implementation Workflow

All repository code changes must use the implementation workflow. Agents must not ask whether to use it and must not make direct code changes outside it, except for the bootstrap change that installs the workflow guard.

Break work into named implementations before editing. Each implementation maps to one pull request and may contain multiple conventional commits. A single implementation owner or integrator owns each implementation's tracked-file edits, commits, active implementation marker, PR summary, and final branch state.

Implementation agents must work in full sibling clones under `/workspaces/homelab-ideas/<implementation>`, not in the planner checkout. Create each implementation branch from `origin/main`.

Branches must follow the format `codex/<implementation>`.

Before cloning, the planner must stage any needed local-only secret/config files into `.codex/tmp/implementation-secrets/<implementation>/` in the master checkout. The staged tree must preserve the same repo-relative paths used by the master checkout, so implementation and verifier agents can copy those files into identical locations inside their sibling clones.

Only ignored local files, such as `terraform.tfvars`, other `*.tfvars`, kubeconfig files, or talosconfig files, may be staged this way. Never stage tracked files, SOPS-encrypted manifests, or secret contents in logs.

The active implementation clone must record `.codex/tmp/active-implementation` with `implementation`, `branch`, `base`, `role`, `clone_path`, `owner_role`, and `owner_agent` before tracked files are changed. The marker must validate with `tools/codex-harness/validate_active_implementation.py`: use `branch=codex/<implementation>`, `role=implementation`, `owner_role=implementation-agent`, and `clone_path=/workspaces/homelab-ideas/<implementation>`. `owner_agent` must identify the implementation owner and must not be planner-like.

Multiple helper agents may contribute to one implementation clone when useful. Use the single integrator model: helper agents may research, inspect, test, verify, or prepare focused patch recommendations, but the implementation owner applies tracked-file edits and creates commits in the shared clone.

As implementation agents finish, create separate verifier agents to review the result. The planner coordinates implementation breakdown, delegates implementation and verification, and summarizes status.

Implementation and verifier agents must install the staged secret/config files into their sibling clone before running commands that need them, preserving the repo-relative paths from the staged tree.

Conventional commits are enforced locally and by origin.

Do not push to origin until verifier approval is recorded for the exact `HEAD` commit.

Every implementation must consider whether documentation is stale or incomplete after the change. Update relevant docs, generated docs, decision records, runbooks, or agent guidance when behavior changes. If no documentation changes are needed, record that decision and the reason in the PR summary.

`docs/architecture.md` is generated from Kubernetes and Terraform source files. Do not edit it by hand. If `python3 tools/architecture/render.py --check` fails after Kubernetes or Terraform source changes, run `python3 tools/architecture/render.py --write` and commit the generated result in the same implementation.

Before PR creation, the planner or implementation agent should record plan-derived PR text in `.codex/tmp/pr-summary.md`. Keep this file concise and include the implementation summary, the important changes from the plan, and a documentation impact note listing docs updated or explaining why none were needed. The automatic PR helper includes this text in the PR body and falls back to generated branch, file, commit, and verification details if the file is absent.

After verifier approval is recorded, create the pull request without additional intervention. Push the current `codex/<implementation>` branch to origin, run `gh pr create --base main --head codex/<implementation>`, and delete the sibling clone only after the pull request is created successfully.
