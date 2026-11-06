# Ephemeral development browser runner

A single-job GitHub Actions runner for private development routes, hosted on a fresh disposable development-only VM. It must register with a short-lived repository registration token, use a verified runner binary, have no production access or privileged mounts, and be destroyed after one job. The existing browser workflow remains manually dispatched and read-only.
