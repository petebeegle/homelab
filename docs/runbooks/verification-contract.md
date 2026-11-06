---
status: draft
scope:
  - codex-harness
  - ci
authority: operational
created: 2026-11-06
---

# Shared verification contract

Agents and CI run the same command:

```bash
python3 tools/verification/verify.py --profile harness
```

This initial profile runs the Python verification-contract tests and the existing Node URL-guard tests. It exits nonzero on test failure or missing executable. The GitHub Actions job is named **Verification / harness**.

This is deliberately **not** a full browser or development-cluster check. The existing Playwright workflow only discovers the smoke test; neither job proves a browser reached the development Gateway. Record those separately as NOT RUN until a dedicated, isolated development-capable runner executes them.

## Hook migration

Keep `.codex/hooks/sops_guard.sh`, Terraform safety checks, and implementation-workflow branch guards as immediate agent-side safety protections. Existing `.codex/hooks/pre_commit_check.sh` currently runs changed-file pre-commit after each tool operation; leave it intact until its CI counterpart and failure semantics have been compared. The existing CI pre-commit job already runs `pre-commit run --all-files`.

Next migration: expose more existing validators through named, stable profiles; remove only redundant post-tool validation (not safety guards) once CI equivalence is proven. Require the verification job via repository branch protection after observing a passing run. A successful workflow alone does not configure branch protection.

For live integration verification, provision a restricted, preferably ephemeral runner outside the Talos cluster, with development-only network access and credentials. Do not expose privileged self-hosted runners to arbitrary untrusted PR code. Use serialized branch deployment and cleanup, and publish JUnit/Playwright traces as CI artifacts.
