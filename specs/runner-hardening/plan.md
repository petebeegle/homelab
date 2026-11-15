# Runner hardening — plan

SDD tier: low. Workflow risk: low (repository code/docs only; no cluster, Proxmox, or GitHub mutations).
Smoke strategy: mocked unit tests in the shared harness profile (`python3 tools/verification/verify.py --profile harness`); live smoke not applicable. Honest limit: no live Proxmox/ssh/process-death proof.
Fanout: findings came from two parallel read-only reviewers (lifecycle gaps; written-record drift). Implementation was a single owner.
Exceptions: stacked on #448's head (branch `codex/runner-hardening`, base `codex/ephemeral-dev-runner`) rather than editing #447/#448 branches. `prepare-vm.sh` needs root on a disposable VM and was only syntax-checked.
Human gate: user approved this work ("A then B", manage branches and merge as needed). Spec/plan/task checkpoints combined under the low-risk exception; merging still goes through PR checks.
