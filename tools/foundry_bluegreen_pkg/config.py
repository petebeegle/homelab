"""Configuration constants for the Foundry blue/green workflow."""

from __future__ import annotations

from pathlib import Path


DESCRIPTION = "Safe, dev-gated blue/green workflow for Foundry VTT upgrades."

ROOT = Path(__file__).resolve().parents[2]
APP_DIR = Path("kubernetes/apps/foundryvtt")
FIXTURE_DIR = Path("kubernetes/apps/foundry-bluegreen-fixture")
EVIDENCE_PATH = Path(".codex/tmp/foundry-bluegreen-dev-rehearse.json")
DEV_KUBECONFIG = Path.home() / ".kube/homelab-development.config"
PRODUCTION_COMMANDS = {"prepare", "promote", "rollback", "retire"}
CONFIG_VERSION_GLOBS = [
    "tools/foundry_bluegreen.py",
    "tools/foundry_bluegreen_pkg/*.py",
    "kubernetes/infra/controllers/nfs-csi/*.yaml",
    "kubernetes/apps/foundry-bluegreen-fixture/*.yaml",
    "kubernetes/clusters/development/apps/foundry-bluegreen-fixture.yaml",
]
