# Harness golden path — specification

## Intent
Establish an independently executable, fail-closed browser verification step for the existing Whoami development branch smoke profile. Preserve all existing workflow and production safety controls.

## Acceptance
- A browser smoke checks the exact HTTPS user-facing route for Whoami, not a pod/service proxy.
- A non-2xx response, TLS failure, browser navigation failure, or unexpected response content fails.
- Test output is machine-readable and includes a Playwright trace on failure.
- A local unit test validates URL restrictions and test configuration without requiring a cluster.
- No tests run against production, no GitOps manifests change, and no cluster resources are mutated by the new verifier.
- Unavailable development DNS/browser dependencies are reported as unverified, never passed.

## Non-goals
Authentik, new cluster deployment, replacing Spec Kit, supervisor dispatch, or modifying CI gates in this increment.
