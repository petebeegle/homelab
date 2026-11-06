# Harness golden path — plan

SDD tier: low. Workflow risk: low for added local test tooling; no cluster mutations.
Smoke strategy: existing development Whoami branch verifier remains the deployment path; new Playwright suite checks the user-facing route after it succeeds.
Fanout: [P] independent review of existing verifier and browser-test contract; no concurrent tracked edits needed.
No production or shared-cluster write operations.

Implementation:
1. Add an opt-in Playwright project with pinned dependency and chromium configuration.
2. Accept a single explicitly supplied development Whoami URL; fail closed if absent or not within the exact development host pattern.
3. Validate HTTPS response and Whoami identity content through a browser.
4. Capture JUnit results and failure traces.
5. Document commands and boundaries, without claiming live execution.
6. Do not modify binding hooks or ADR-0012.

Human approval: user's explicit 'ship it' authorizes this bounded initial golden-path PR. Separate spec/plan/task checkpoints combined under low-risk exception. Review and CI remain required.
