# Verification contract

## Goal
Make the same lightweight, fail-closed verification entrypoint available to agents and GitHub Actions. Independent CI status is authoritative; local hooks remain safety controls.

## Acceptance
- A documented `python3 tools/verification/verify.py --profile harness` command works locally and in CI.
- Browser URL guard tests run and fail the command if they fail.
- The Playwright smoke test is discoverable in CI, but a development-cluster browser test is not falsely reported as executed.
- CI runs the contract as a required *candidate* status; branch protection configuration is a separate administrative step.
- A regression test proves that a failing subprocess fails the contract.
- No production mutations, cluster credentials, or removal of safety hooks.
