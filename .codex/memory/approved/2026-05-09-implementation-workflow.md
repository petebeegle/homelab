---
status: approved
created: 2026-05-09
source: user-preference
kind: workflow-preference
---

# Mandatory Implementation Workflow

All repository code changes must use the implementation workflow. Agents must not ask whether to use it and must not make direct code changes outside it, except for the bootstrap change that installs the workflow guard.

Break work into named implementations before editing. Each implementation maps to one pull request and may contain multiple conventional commits. A separate implementation agent owns each implementation's work.

Implementation agents must work in full sibling clones under `/workspaces/homelab-ideas/<implementation>`, not in the planner checkout. Create each implementation branch from `origin/main`.

Branches must follow the format `codex/<implementation>`.

Before cloning, the planner must stage any needed local-only secret/config files into `.codex/tmp/implementation-secrets/<implementation>/` in the master checkout. The staged tree must preserve the same repo-relative paths used by the master checkout, so implementation and verifier agents can copy those files into identical locations inside their sibling clones.

Only ignored local files, such as `terraform.tfvars`, other `*.tfvars`, kubeconfig files, or talosconfig files, may be staged this way. Never stage tracked files, SOPS-encrypted manifests, or secret contents in logs.

The active implementation clone must record `.codex/tmp/active-implementation` with the implementation name, branch, base, role, and clone path before tracked files are changed.

As implementation agents finish, create separate verifier agents to review the result. The planner coordinates implementation breakdown, delegates implementation and verification, and summarizes status.

Implementation and verifier agents must install the staged secret/config files into their sibling clone before running commands that need them, preserving the repo-relative paths from the staged tree.

Conventional commits are enforced locally and by origin.

Do not push to origin until verifier approval is recorded for the exact `HEAD` commit.

After verifier approval is recorded, create the pull request without additional intervention. Push the current `codex/<implementation>` branch to origin, run `gh pr create --base main --head codex/<implementation>`, and delete the sibling clone only after the pull request is created successfully.
