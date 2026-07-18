# Implementation Plan: access-broker-wgeasy-password

**Branch**: `codex/access-broker-wgeasy-password`
**Date**: 2026-07-18
**Spec**: `specs/access-broker-wgeasy-password/spec.md`

## Summary

Commit the already-created SOPS-encrypted `WGEASY_PASSWORD` key and validate the
access-broker render path before opening a PR.

## Technical Context

**SDD tier**: medium
**Workflow risk tier**: medium
**Smoke strategy**: render and secret validation before PR; live `/access approve`
smoke after Flux applies the merged secret.
**Fanout targets**: render validation and plaintext scans are independent.
**Workflow exception**: using the main checkout after branching because the
operator-created encrypted secret edit was already unstaged there; moving it to
a new worktree would increase secret-handling risk.

## Validation

- `sops filestatus kubernetes/apps/access-broker/secret.yaml`
- `kubectl kustomize kubernetes/apps/access-broker`
- `kubectl kustomize kubernetes/clusters/production`
- plaintext secret scans
- SDD context validation
