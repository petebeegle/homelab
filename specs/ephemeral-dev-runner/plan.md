# Plan

Add minimal fail-closed VM bootstrap and one-shot registration scripts. Pin/checksum runner release, avoid committed secrets, and document lifecycle/ACL boundaries. Proxmox lifecycle orchestration is implemented in lifecycle.py (hardened in specs/runner-hardening) and mock-tested only. Template build, live run, network ACL enforcement and a stale-VM sweeper remain; no production mutation or live runner claim. User requested implementation; no human approval for these bounded repository-only changes.
