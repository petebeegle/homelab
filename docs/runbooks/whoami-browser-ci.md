---
status: draft
scope:
  - development-cluster
  - browser-verification
authority: operational
created: 2026-11-06
---

# Development Whoami browser CI

The manually dispatched workflow **Whoami development browser smoke** runs Playwright against an *existing* Whoami branch route. Dispatch it on a trusted repository ref with `branch_slug` matching the deployed branch DNS slug. The workflow constructs `https://whoami-<slug>.dev.lab.petebeegle.com` and rejects malformed slug input.

The workflow targets a dedicated **ephemeral self-hosted runner** with labels `self-hosted`, `linux`, `x64`, and `homelab-dev-browser`. Provision this runner **inside the development network** before dispatch. It must resolve internal development DNS, trust the development Gateway certificate, and reach development HTTP(S) routes. No public service exposure is required. The workflow has no kubeconfig and no deployment rights. Until a correctly isolated runner is registered, jobs will queue and the browser smoke remains **NOT RUN**.

Before dispatch, provision and retain the branch environment using the existing development verifier/runbook. After dispatch, inspect the workflow result and uploaded JUnit/Playwright traces; clean up the branch using the development runbook. This workflow never provisions or cleans up branch resources.

**Security boundary:** use an ephemeral VM/container per job with a clean filesystem and no host socket mounts, no production network reachability, and tightly scoped egress. Register the runner just in time, remove it after the job, and restrict workflow dispatch to trusted repository refs. Do not run arbitrary PR checkout code on a persistent privileged self-hosted runner. This manual workflow is not a required PR status check because most PRs do not have an active development branch deployment.
