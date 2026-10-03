# Plan

SDD tier: medium. Workflow risk tier: medium. App: synthetics.
Smoke strategy: manual, automated disposable development browser Job using the
updated source and image; check the development whoami user URL where available.
No production mutation. Coordinate temporary namespace/Job with parent first.

1. Reproduce the existing mirror policy failure and verify image availability.
2. Copy the updated cluster lockfile to tests/smoke; update only the dependency
   version in the local manifest; align CronJob image to v1.63.0-noble.
3. Run mirror policy, npm installation/listing/unit tests, YAML/render checks,
   architecture renderer, and browser smoke; consolidate evidence and commit.

Fanout: this lane owns only Playwright repair; sibling agents own other PRs.
No further child agents. [P] parent independently reviews/publishes results.

Exceptions: worktree is /home/vscode/homelab-worktrees/repair-renovate-playwright
because /workspaces sibling creation was denied. Existing Renovate PR repair
uses a local codex/repair-renovate-playwright branch and matching artifacts;
parent coordinates push to the existing remote PR branch. No push from this lane.
Record any unavailable development layer and substitute checks explicitly.
