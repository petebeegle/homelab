# Evidence: Nexus Hosted Docker Registry

**Branch**: `codex/nexus-hosted-registry`
**Risk Tier**: high
**Started**: 2026-10-03

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent brief | PASS | User: “lets add all of that then,” referring to the hosted repository, push permissions, and HTTPS endpoint managed through the repo. |
| Spec approval | PASS | User approved the linked spec on 2026-10-03: “yep go for it.” |
| Clarify | SKIP | Approved spec assumptions resolve the original intent. A new implementation prerequisite about consumer credentials was surfaced during planning through an asynchronous question. |
| Plan approval | PASS | User approved the linked plan with “go” on 2026-10-03; task generation and analysis follow. |
| Checklist | PASS | `checklists/requirements.md` records the specification quality review; implementation checklist follows during planning. |
| Tasks/analyze approval | PENDING | 25 tasks generated; cross-artifact review covers all 17 FR/SC items. Known production credential/state prerequisite remains explicit. |
| Converge | PENDING | Not yet reached. |

## Discovery

- Existing Terraform defines `docker-proxy` and `docker-group` only; the group uses HTTP connector 8082 and includes only the proxy.
- Prior authenticated live inventory in this conversation also returned zero hosted Docker repositories.
- Synology's existing `docker-registry.petebeegle.com` reverse proxy targets connector 8082.
- The tracked Nexus Compose configuration publishes only UI 8081 and group 8082, so adding a repository alone will not establish a new reachable connector.
- The existing Docker account is scoped to group privileges; a separate publisher avoids granting write access to existing cluster consumers.
- The group endpoint certificate was renewed in the prior operational task. Its continued availability is a regression requirement, not a new certificate task in this implementation.
- New ingress must follow Gateway API decisions; proposed `docker-push.lab.petebeegle.com` fits the existing `${cluster_domain}` wildcard listener and certificate model.

## Workspace And Baseline

- Main checkout contained unrelated changes on `codex/upgrade-talos-oom-fix`; it was left untouched.
- `git fetch origin`: PASS.
- Preferred worktree creation at `/workspaces/homelab-worktrees/nexus-hosted-registry`: FAILED because the parent location was not writable. Git created the branch before that failure.
- Reused that branch in `/home/vscode/homelab-worktrees/nexus-hosted-registry`: PASS. This writable sibling location is the documented worktree fallback.
- Base revision: `d914946` (`origin/main` at creation).
- New worktree started clean. Nexus definitions and Compose match the inspected main checkout; Synology provider versions differ between branches, so planning must use this branch's pinned versions.
- No ignored credentials or Terraform state were required or copied for the specification draft. Stage and install them through the prescribed main-checkout secret staging directory before authenticated commands in the worktree.

## Local Checks

- Specification reviewed against `checklists/requirements.md`.
- `git diff --check`: PASS. A direct scan of all draft Markdown files also passed, covering the untracked artifacts.
- Required-section, non-empty-artifact, and unresolved-clarification-marker checks: PASS.
- Runtime tests, Terraform initialization, plans, and deployment smoke have not run: no implementation changes exist yet.

## Deployment State

No Nexus, Synology, DNS, or cluster configuration was changed by this specification task. The proposed push endpoint is not provisioned.

## SDD Conformance

- Applied `speckit-specify` using the repository's spec template and constitution.
- Implementation naming follows the binding branch/directory convention rather than upstream numeric prefixes.
- No `.specify/extensions.yml` hooks were present.
- `.specify/feature.json` in the unrelated checkout is preserved. The worktree pointer was updated by the required setup-plan script using the explicit feature directory.
- The brainstorming skill's generic artifact location is superseded by the repository's `specs/nexus-hosted-registry/` location.
- Spec, plan, and task/analysis human gates are not waived by authorization to add the feature.

## Exceptions And Follow-Ups

- Worktree location fallback is recorded above.
- Separate clarification interview was skipped with the rationale above. Planning checklist is complete; tasks, analysis, and converge remain future stages.
- Determine development validation availability and any external-service exception in `plan.md` before implementation.

## Planning Research And Checks

- Used `writing-plans`, `speckit-plan`, and `speckit-checklist`; generated plan, research, model, contract, quickstart, and a 14-item plan quality checklist.
- `SPECIFY_FEATURE_DIRECTORY=specs/nexus-hosted-registry SPECIFY_FEATURE=codex/nexus-hosted-registry .specify/scripts/bash/setup-plan.sh --json`: PASS; correct worktree paths returned.
- Read-only explorer `registry_dev_research` confirmed branch profile discovery, naming/cleanup constraints, mandatory development Terraform plan, probe limitations, and Retain-PV cleanup implications. Findings are incorporated in research and plan.
- Development node Ready at `192.168.30.170`; internal Gateway Programmed at `192.168.30.225`. Production and development candidate DNS names resolved to their expected LAN Gateways.
- NAS TCP 8083 refused connections; allocation still requires Container Manager inspection before use.
- Nexus provider 2.8.0 hosted schema, role schema, security realm import and random provider 3.9.0 import behavior checked against pinned upstream sources linked in research.
- Nexus local state and backend metadata are absent; production consumer credentials in both tfvars and saved Talos machine configuration returned HTTP 401. Live `docker` account/role and DockerToken realm exist. No credentials were printed, rotated or copied into tracked artifacts.
- The user was asked for the current secret-store location or a coordinated reset preference. No reset is authorized by the original approved spec. Production apply is gated on resolution.
- `update-agent-context.sh` is absent from this repository's bundled scripts; skipped rather than modifying AGENTS.md or introducing unrelated tooling.
- All planning work is repository documentation plus read-only live checks. No registry, NAS or cluster configuration was changed.

- Planning artifact completeness, required-section, and Markdown whitespace checks: PASS. Spec Kit prerequisite discovery found the research/model/contracts/quickstart in the correct feature directory. Production credential recovery is explicitly an unresolved runtime prerequisite, not a completed check.

## Task Generation

- Applied `speckit-tasks` using `setup-tasks.sh --json` with the explicit feature directory; the expected repository template and all design artifacts were found.
- Generated 25 unchecked tasks, grouped into setup/foundation, US1 hosted publication, US2 cache compatibility, US3 operation/recovery, and review/rollout. No implementation task is claimed complete.
- Production credential recovery (T018) explicitly does not block independent development work, but does block production apply and final completion.
- Source changes and runtime mutations have not started. No extension hooks are configured.

## Task/Analysis Handoff

- Task generation format validation identified missing user-story labels; corrected the generated list without changing scope or task substance.
- Read-only semantic review: all 12 functional requirements and 5 success criteria have coverage; no constitution conflicts or critical design issues.
- Operational finding R1: missing Nexus state and rejected consumer credentials remain a high-severity production rollout prerequisite, addressed by T018/T020/T023 gating. Independent development work remains available after the task gate.
- Full SDD context validator (including non-empty spec, plan, tasks, evidence): PASS. Whitespace and final task-label checks are run at handoff.
- No production changes or implementation source edits were made during task generation/analysis.
