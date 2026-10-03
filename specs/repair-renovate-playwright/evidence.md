# Evidence

Original PR head reviewed: 6a7bb8db03a27d751fff795ebf550d26c30652a5.
Failed check: https://github.com/petebeegle/homelab/actions/runs/33934834451/job/101220605388

Before edits, `python3 tools/policy/check_synthetic_smoke_mirroring.py` failed
with the exact CI error: tests/smoke/package-lock.json must exactly match the
cluster package-lock.json. This existing behavioral policy is the red test;
no redundant test added for a version-only configuration correction.

Gate evidence: user's "fix them fan out" approves the previously reported
bounded fixes and their execution. Compact Spec Kit artifacts precede edits;
combined gates are an explicit narrow repair exception, despite medium runtime
risk. Clarify skipped because versions, affected files, and acceptance are
unambiguous. Checklist performed inline: preserve scripts, synchronize locks,
align browser image, no production mutation, verify development runtime.
Analyze performed before implementation: each requirement maps to T002–T004;
no conflicting ownership or broader dependency-policy changes. Converge will
reconcile outcomes below before commit.

Development API read: explicit ~/.kube/homelab-development.config reported
one Ready node (Kubernetes v1.35.0). No ignored repo-relative secret/config files
are needed; the external operator kubeconfig is used directly without logging it.

## Implementation and focused checks

- Both package.json dependency sets and both lockfiles now resolve Playwright
  1.63.0; local/cluster manifest script differences are preserved.
- CronJob image is mcr.microsoft.com/playwright:v1.63.0-noble. Registry manifest
  GET with Docker manifest Accept headers returned HTTP 200 and tags/list
  included that exact tag. A preliminary generic HEAD returned 404; the explicit
  manifest GET and later actual cluster pull are the meaningful evidence.
- `python3 tools/policy/check_synthetic_smoke_mirroring.py`: PASS after repair.
- `npm ci --no-audit --no-fund` in each smoke directory: PASS, three packages.
- `npm run test:unit` in the cluster smoke directory: PASS, five tests.
- `npx playwright test --list` in tests/smoke: PASS, 11 browser route cases.
- `pre-commit run --all-files`: PASS, all hooks including synthetic mirroring.
- `python3 tools/architecture/render.py --check`: PASS; no generated doc change.
- `kubectl kustomize kubernetes/clusters/production` and the development entry:
  both PASS; app-level synthetics render also PASS.
- Local Node v24.18.1 satisfies the upgraded dependency's Node >=20 constraint.
- Both lockfile SHA-256 values:
  `0a538c1683232cfc91b35cda50be0b22576ef3d1c2d59f051922f7d81f99c873`.

Runtime manifests/logs are under `.codex/tmp/repair-renovate-playwright/`.
Parent reserved the disposable development namespace before mutation. The smoke
Job uses the source ConfigMap and pod spec from the changed app render, with
namespace, lifecycle limits, SMOKE_BASE_DOMAIN=dev.lab.petebeegle.com and
SMOKE_PLAYWRIGHT_COMMAND='npm run test -- --grep whoami' as test-only overrides.
No production or shared development desired state was changed.

## Development browser evidence

On 2026-10-03, disposable Job `repair-renovate-playwright/browser-smoke` ran
against **https://whoami.dev.lab.petebeegle.com/** using the explicit development
operator kubeconfig. Pod `browser-smoke-szgrd` ran from 02:11:06Z to 02:11:27Z,
exited 0, and Job Complete=True was reported at 02:11:29Z.

The existing Chromium test `whoami exercises Gateway TLS and routing` passed:
`1 passed (8.0s)`. The actual wrapper/reporter emitted:

```text
SMOKE_RUN_SUMMARY run="browser-smoke" status=success failed_count=0 failed_tests="" duration_seconds=7
```

Image observed in the completed container:
`mcr.microsoft.com/playwright:v1.63.0-noble`, resolved to
`sha256:eff16c30e6f3f4af0a03fa4b706120d5e9b0891c344a27d64559aff5900a4a27`.
All six live ConfigMap source files were compared byte-for-byte with the
worktree smoke source and matched. No implementation source changed afterward.
The runtime source is the original PR plus this commit's dependency/image repair;
only evidence is finalized after the runtime check. Branch/slug:
`codex/repair-renovate-playwright` / `repair-renovate-playwright`.

The fresh image download took approximately four minutes; the 912 MiB compressed
image pulled successfully. Read-only checks found no node pressure, ~153 GB free
ImageFs space, and no pull error. Initial short wait timeouts were observation
windows, not failed Job conditions; the Job's 480-second deadline was not hit.

Verified layers: app/cluster render, live updated image and ConfigMap source,
npm install, Chromium startup, real development DNS/TLS/Gateway/user page shell,
and wrapper summary. This is a temporary development smoke, not a Flux branch
reconcile or production deployment. Remaining production route cases were not
executed because their applications are not represented by this isolated smoke.
No unavailable-infrastructure exception was needed for the exercised path.

Parent performed an independent diff review with no findings. Converge checked
all requirements against T002–T004 evidence: no additional implementation work
identified. Broader Renovate coupling remains outside this bounded PR repair.

Cleanup: deleted the disposable namespace and confirmed a subsequent namespace
lookup with --ignore-not-found returned no resources. No smoke Job, ConfigMap,
PVC, or Flux resources were retained. Publication and remote CI remain the
parent lane's responsibility; this lane commits locally only.
