# Evidence: access-broker-wgeasy-provisioning

**Branch**: `codex/access-broker-wgeasy-provisioning`
**Date**: 2026-07-17

## Workflow

- Worktree fallback: used `/home/vscode/homelab-worktrees/access-broker-wgeasy-provisioning`
  because `/workspaces/homelab-worktrees` is unavailable.
- homelab-access PR #9 merged at `6c3af6aed110720efa8fe223026dd44326f23238`.
- homelab-access main image workflow `29621599620` passed before the rollout
  annotation update.
- Lightweight SDD exception: clarify/checklist/analyze/converge were skipped for
  this narrow manifest rollout; the required decisions and validation are
  captured in spec, plan, tasks, and this evidence file.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `gh run watch 29621599620 --repo petebeegle/homelab-access --interval 10` | PASS | Main image workflow for merged PR #9 completed successfully. |
| `kubectl kustomize kubernetes/apps/access-broker > /tmp/access-broker-wgeasy-render.yaml && rg -n 'WGEASY_USERNAME\|wgeasy-provisioning-2026-07-17\|kind: Ingress' /tmp/access-broker-wgeasy-render.yaml \|\| true` | PASS | Render includes `WGEASY_USERNAME` and the new rollout annotation; no rendered `Ingress` line appeared. |
| `kubectl kustomize kubernetes/clusters/production > /tmp/production-wgeasy-render.yaml && rg -n 'app-access-broker\|WGEASY_USERNAME\|wgeasy-provisioning-2026-07-17' /tmp/production-wgeasy-render.yaml` | PASS | Production render includes `app-access-broker`; app package content is applied by Flux from its path. |
| `(rg -n 'kind: Ingress\|apiVersion: networking.k8s.io/v1' kubernetes/apps/access-broker kubernetes/clusters/production/apps/access-broker.yaml; test $? -eq 1)` | PASS | No Kubernetes `Ingress` introduced. |
| `(rg -n 'WGEASY_PASSWORD: [^E]\|password-1234\|PrivateKey =\|MTUyMzA0\|GBtIrX\|6Q-TE01sDcEW2T5ual35fzkNFuMomRl8' kubernetes/apps/access-broker specs/access-broker-wgeasy-provisioning; test $? -eq 1)` | PASS | No plaintext wg-easy password, test WireGuard key material, or previously exposed Discord token/client secret fragments in tracked rollout files. |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | Completed with no output. |

## Live Smoke

- Status: blocked until `WGEASY_PASSWORD` is added to
  `kubernetes/apps/access-broker/secret.yaml` as a SOPS-encrypted key.
- Substitute checks: app image CI passed, app package rendered, production Flux
  Kustomization rendered, no Ingress introduced, and plaintext scans passed.

## Final State

- Final branch: `codex/access-broker-wgeasy-provisioning`
- Final HEAD: branch head at PR creation
- Pull request: pending
