# Hybrid AI Harness Implementation Plan

**Goal:** Give the receiving code agent an evidence-based path from private CI verification to a reproducible hybrid local/hosted agent system.
**Architecture:** Deterministic supervisor owns durable jobs, budgets, permissions, and verification. Isolated workers execute tools; a dedicated inference host supplies local reasoning, with bounded hosted API escalation.
**Tech Stack:** Existing Python verification tools, GitHub Actions, Proxmox, Talos/Kubernetes/Flux; proposed Linux, Ansible and containerized inference.
**Spec:** `specs/hybrid-ai-harness-handoff/spec.md`

## Scope of this PR

SDD tier: low. Workflow risk: docs-only. Smoke profile: none (no runtime changes).
Fanout: none; one documentation owner. No tests added for prose.
Constitution check: GitOps, Gateway API, SOPS, NFS defaults and Talos boundaries preserved; no deployed resources changed. Dedicated worktree and matching codex branch used. Review is through PR checks; this PR remains draft and unmerged.
Human gates: user authorized the documentation handoff; future executable work is not performed here.
Checklist/analyze: lightweight source and scope review instead of full generators; no workflow standards changed.

## Observed baseline (2026-11-07; refresh before execution)

Main was `ac54370b4632f39d6b541db34658426a6558ce2e`.

| PR | Observed state | What it provides |
| --- | --- | --- |
| [#444](https://github.com/petebeegle/homelab/pull/444) | Merged; commit 963ce97fc4f5fd4244545a321723931056b0822b | Whoami Playwright golden-path foundation |
| [#445](https://github.com/petebeegle/homelab/pull/445) | Merged; commit a436c722f552f244df6002c20c87a2d00de40bad | Shared local/CI verification contract |
| [#446](https://github.com/petebeegle/homelab/pull/446) | Merged; commit ac54370b4632f39d6b541db34658426a6558ce2e | Moves expensive post-tool pre-commit validation to CI; preserves safety guards |
| [#447](https://github.com/petebeegle/homelab/pull/447) | Open draft; base main; head 3234b56c81bf88e23a586558371b50568d9fe306 | Manually dispatched Whoami browser workflow |
| [#448](https://github.com/petebeegle/homelab/pull/448) | Open draft; base codex/browser-ci-contract; head e89e4c94d86013418c9003837ebb3174c662ce57 | Disposable runner bootstrap, one-shot execution, Proxmox lifecycle and mocked cleanup tests |

Successful PR-triggered workflow runs at these heads:

- #447: [CI 42291209700](https://github.com/petebeegle/homelab/actions/runs/42291209700), [Verification contract 42291209831](https://github.com/petebeegle/homelab/actions/runs/42291209831).
- #448: [CI 42291900581](https://github.com/petebeegle/homelab/actions/runs/42291900581), [Verification contract 42291900759](https://github.com/petebeegle/homelab/actions/runs/42291900759).

These are CI results, not live browser/Proxmox proof or confirmation of branch protection. Workflow retrieval covers PR-triggered runs only. No direct cluster, runner inventory, ACL, DNS, certificate, or GPU inspection was performed for this handoff.

### Known discrepancies to reconcile

#447's body describes a GitHub-hosted/public-route limitation, but the stacked runner documentation says the workflow targets self-hosted labels. Read the current workflow before relying on the PR body.
#448's initial boundary/evidence/tasks say provisioning and token delivery are unimplemented or CI pending, but `tools/development/runner/lifecycle.py` now includes clone/start/token acquisition/cleanup and CI is successful. Update those records to distinguish implemented code from unverified deployment.
The example pve04 host, template 900, VM 901, and guest name are explicitly examples, not discovered resources.

## Global constraints

- Do not merge this PR or existing PRs as part of this handoff.
- Keep private development services private; hosted reasoning does not require public cluster endpoints.
- Keep runner guest, management credentials, and inference service separate trust boundaries.
- Never let the local model's confidence or prose alone certify success.
- Preserve safety hooks while moving reproducible validation into shared CI commands.
- No production-first changes; use development evidence and precise unverified-layer reporting.
- Persist secrets only through approved encrypted references; redact logs and hosted escalation payloads.

## Proposed implementation sequence

### 1. Finish the private verification foundation before adding a model

Reuse #447/#448, `tools/development/runner/`, `tests/browser/`, `tools/verification/verify.py`, and `tools/development/verify_branch_deploy.py`.
Inspect existing Terraform patterns before choosing paths for image/template/ACL provisioning. Define a separate named implementation for infrastructure; do not duplicate the runner scripts.

From a management environment with LAN access, inventory real Proxmox hosts, free VM IDs, templates, network segmentation, scoped credentials and development DNS. Reconcile docs with current branch code. Address lifecycle gaps: total deadline, job cancellation, partial clone failure, management process death, VM ownership tags, concurrent leases, pinned guest identity, token expiry and stale GitHub registrations. A Python finally block cannot guarantee cleanup after host loss or process termination; add independently scheduled stale-resource cleanup.

Build the trusted disposable image and network ACLs as code. No sudo or management credentials inside PR execution guests. Browser OS dependencies belong in the image. Do not enable untrusted fork execution.

Acceptance: real private Whoami URL passes Playwright; artifacts identify source revision, workflow run, runner/VM, target URL, results and cleanup. Verify production access is denied. Force job failure, timeout and supervisor interruption; prove eventual teardown and stale-registration cleanup. A queued job is not a pass.
Respect stacked PR order; after any later authorized integration of #447, retarget/rebase #448 and rerun checks. No merge is authorized here.

### 2. Establish the smallest durable supervisor

First inspect existing harness code; add a narrowly scoped `tools/supervisor/` implementation only if no equivalent exists. Run on a trusted reachable management host initially; Kubernetes hosting is not a prerequisite.
Persist job ID, repository/ref SHA, goal, allowed tools, deadline, attempt and cost budgets, lease owner, state, evidence references and escalation history.
Use explicit states queued/running/verifying/succeeded/failed/blocked/cancelled. Deterministic scheduling and checks handle routine polling; no LLM needed for polling.
Serialize shared development deployment/cleanup operations. Recover after restart without executing the same mutation twice. Unavailable credentials/network produce an actionable blocked state, not an endless retry.

Acceptance: submit one Whoami verification job, restart supervisor during execution, resume or safely reconcile once, collect evidence, and clean up. Test duplicate delivery, expired lease, cancellation, stale SHA and failed checks. No success transition without matching evidence.

### 3. Provision the inference appliance reproducibly

Proposed host: GMKtec EVO-X2 / Ryzen AI Max+ 395 / 128 GB / 2 TB; verify actual hardware first.
Prefer bare-metal Linux managed by Ansible and a pinned inference container over making Proxmox passthrough or Talos GPU support prerequisites. Record the selected approach in an ADR before provisioning.
Suggested new implementation-owned paths: `ansible/inference/` (inventory schema, roles, playbook), `config/inference/` (runtime/model declarations), and `docs/runbooks/local-inference.md`; adapt after inspecting existing conventions.
Select and pin supported OS/kernel/GPU stack/runtime after checking current vendor documentation and testing the actual box. Do not assume advertised unified memory is all usable for model weights; account for OS, context/KV cache, concurrent requests and runtime overhead. Use GPU inference as the initial target; do not assume NPU compatibility.
Code owns install/bootstrap, container service, model download checksums, private authenticated endpoint, restart behavior, health probes, logs and metrics. BIOS/initial boot may remain a documented manual step.
Keep model cache on the appliance SSD; this does not change the Kubernetes PVC storage default. Back up durable supervisor state/config separately; record model redownload requirements.

Acceptance: repeat apply without drift; reboot recovers service; real request confirms GPU execution; authenticate from the intended client network; reject unauthorized callers; prove exact model/runtime identity and a tested rollback. Blank-disk recovery requires explicit bootstrap/access prerequisites.

### 4. Add local and hosted reasoning behind the same harness

Suggested new paths: `tools/supervisor/providers/`, `config/agent-routing.yaml`, `tests/agent-evals/` after confirming no existing equivalent.
Begin with local log classification and bounded edits; use a hosted model for ambiguous failures and architectural reasoning.
Both providers receive the same job contract and tool authorization. Harness enforces tool schemas, permission checks, deadlines, maximum attempts and API budget outside model prompts.
Escalate on invalid tool calls, unsupported operations, repeated verification failure, or deadline/budget thresholds; do not rely solely on the model admitting uncertainty.
Escalation includes sanitized goal, exact revisions, observations, attempted actions, and failed checks. Hosted credentials stay on the trusted management side. Provider response is a proposal executed and verified through the same controls.
Provider unavailable or budget exhausted yields blocked/failed, never silent unlimited fallback.

Acceptance: one bounded local task succeeds; a deliberately difficult/failed task escalates to a configured hosted API, resumes, passes independent checks and records cost and provenance. Test malformed calls, prompt injection in logs, network failure, redaction and exhaustion.

### 5. Gate model changes on task outcomes and recovery evidence

Candidate model/runtime stays separate from the serving version. Pin dependencies and model artifacts; evaluate before switching the endpoint.
Maintain representative repository tasks with independent assertions plus held-out cases. Measure completion rate, retries, latency, hosted cost, intervention rate and cleanup reliability. Establish an initial baseline before setting numeric promotion thresholds.
Prevent the worker from weakening the checks used to approve its own task. Security/network isolation checks are mandatory regardless of benchmark score.
Promote only after the fixed acceptance suite passes and declared performance thresholds are met; retain the previous model/config for rollback. Test reboot, bad candidate, interrupted downloads, missing model files and unavailable hosted fallback.
Treat recovery improvements as reviewed code/runbook/test changes, not unrestricted self-modification.

## Review focus

1. Cancellation or process death leaves a privileged runner: independent cleanup and ownership reconciliation in phase 1.
2. Stale evidence or duplicate jobs certify the wrong revision: SHA binding and leases in phase 2.
3. GPU/runtime incompatibility silently falls back to slow CPU: actual device-use checks in phase 3.
4. Untrusted logs or tool calls cross credential boundaries: enforced permissions and redaction tests in phase 4.
5. Candidate optimizes the test or erases prior working service: independent held-out checks and rollback in phase 5.

## Open PR inventory

All 32 open PRs returned by the repository query on 2026-11-07, before creating this handoff PR. Only #447/#448 were inspected in depth for this work. Other states/checks/dependencies require fresh inspection; do not bundle their changes into this plan. In particular, #437/#438/#440 may overlap infrastructure/tooling versions but are not established prerequisites; #237 may relate to DNS but is not proven necessary.

| PR | Title |
| --- | --- |
| [#448](https://github.com/petebeegle/homelab/pull/448) | feat(runner): bootstrap single-job isolated development browser runner |
| [#447](https://github.com/petebeegle/homelab/pull/447) | feat(browser): add manually dispatched development Whoami smoke in CI |
| [#443](https://github.com/petebeegle/homelab/pull/443) | chore(deps): update terraform nexus to v3 |
| [#441](https://github.com/petebeegle/homelab/pull/441) | chore(deps): update ghcr.io/gethomepage/homepage docker tag to v2 |
| [#440](https://github.com/petebeegle/homelab/pull/440) | chore(deps): update actions/checkout action to v7 |
| [#439](https://github.com/petebeegle/homelab/pull/439) | chore(deps): update traefik/whoami docker tag to v1.12.0 |
| [#438](https://github.com/petebeegle/homelab/pull/438) | chore(deps): update terraform talos to v0.12.0 |
| [#437](https://github.com/petebeegle/homelab/pull/437) | chore(deps): update terraform proxmox to v0.120.0 |
| [#436](https://github.com/petebeegle/homelab/pull/436) | chore(deps): update terraform kubernetes to v3.5.0 |
| [#435](https://github.com/petebeegle/homelab/pull/435) | chore(deps): update terraform helm to v3.3.0 |
| [#434](https://github.com/petebeegle/homelab/pull/434) | chore(deps): update terraform grafana to v4.53.0 |
| [#433](https://github.com/petebeegle/homelab/pull/433) | chore(deps): update mikefarah/yq docker tag to v4.54.2 |
| [#432](https://github.com/petebeegle/homelab/pull/432) | chore(deps): update helm release pihole to v2.38.0 |
| [#431](https://github.com/petebeegle/homelab/pull/431) | chore(deps): update helm release opentelemetry-collector to v0.178.2 |
| [#430](https://github.com/petebeegle/homelab/pull/430) | chore(deps): update helm release metrics-server to v3.14.0 |
| [#429](https://github.com/petebeegle/homelab/pull/429) | chore(deps): update helm release intel-device-plugins-operator to v0.37.1 |
| [#428](https://github.com/petebeegle/homelab/pull/428) | chore(deps): update helm release intel-device-plugins-gpu to v0.37.1 |
| [#427](https://github.com/petebeegle/homelab/pull/427) | chore(deps): update helm release cloudnative-pg to v0.29.1 |
| [#426](https://github.com/petebeegle/homelab/pull/426) | chore(deps): update helm release cert-manager to v1.21.3 |
| [#425](https://github.com/petebeegle/homelab/pull/425) | chore(deps): update helm release authentik to v2026.8.5 |
| [#424](https://github.com/petebeegle/homelab/pull/424) | chore(deps): update registry.k8s.io/coredns/coredns docker tag to v1.15.0 |
| [#423](https://github.com/petebeegle/homelab/pull/423) | chore(deps): update python docker tag |
| [#422](https://github.com/petebeegle/homelab/pull/422) | chore(deps): update pre-commit hook agilicus/pre-commit-hook-k8svalidate to v0.2.1 |
| [#421](https://github.com/petebeegle/homelab/pull/421) | chore(deps): pin dependencies |
| [#410](https://github.com/petebeegle/homelab/pull/410) | chore(deps): update terraform random to v3.9.1 |
| [#409](https://github.com/petebeegle/homelab/pull/409) | chore(deps): update terraform local to v2.9.1 |
| [#403](https://github.com/petebeegle/homelab/pull/403) | feat: cut over Grafana credentials to 1Password |
| [#378](https://github.com/petebeegle/homelab/pull/378) | chore(deps): update dependency kubernetes-sigs/gateway-api to v1.6.2 |
| [#315](https://github.com/petebeegle/homelab/pull/315) | [codex] Fix Jellyfin Authentik SSO |
| [#295](https://github.com/petebeegle/homelab/pull/295) | Align Jellyfin OAuth provider secret source |
| [#237](https://github.com/petebeegle/homelab/pull/237) | feat(terraform): manage unifi dns records |
| [#163](https://github.com/petebeegle/homelab/pull/163) | chore(deps): update ghcr.io/devcontainers/features/terraform docker tag to v1.5.0 |

## Validation for this documentation PR

Run the existing SDD context validator and git whitespace check. Review source links, SHA accuracy, dependency order, no-merge constraint, and observation/proposal separation. No architecture regeneration, live smoke or deployment is needed because only these planning artifacts change.
