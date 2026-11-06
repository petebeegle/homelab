# Browser CI contract

Provide a manually dispatchable, read-only browser smoke workflow that can verify an existing development Whoami branch route from a runner with development DNS/network access. It must not imply that PR CI has tested a live route.

Acceptance: explicit branch slug input, safe URL construction, no deployment or cluster credentials, fail-closed browser navigation, JUnit and trace artifacts on failure, and a documented runner trust boundary. Existing unit tests remain on ordinary GitHub-hosted CI.
