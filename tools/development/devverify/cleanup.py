"""Cleanup helpers for branch verification resources."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from .config import FLUX_NAMESPACE, AppConfig, Duration, Runner, SmokeProfile, VerificationError
from .kube import kubectl, run_command
from .profiles import render_profile_value


def cleanup_branch_environment(config: AppConfig, profile: SmokeProfile, *, runner: Runner) -> None:
    git_repository = render_profile_value(profile.git_repository, config=config, field="gitRepository")
    run_command(
        kubectl(
            config,
            "-n",
            FLUX_NAMESPACE,
            "delete",
            f"kustomization.kustomize.toolkit.fluxcd.io/{config.kustomization}",
            "--ignore-not-found=true",
            "--wait=true",
            f"--timeout={config.timeout.raw}",
        ),
        runner=runner,
        timeout=config.timeout,
    )
    run_command(
        kubectl(config, "wait", f"namespace/{config.namespace}", "--for=delete", f"--timeout={config.timeout.raw}"),
        runner=runner,
        timeout=config.timeout,
    )
    delete_released_volumes(
        config.kubeconfig, lambda namespace, _pv: namespace == config.namespace, runner=runner, timeout=config.timeout,
        settle_namespace=config.namespace,
    )
    run_command(
        kubectl(
            config,
            "-n",
            FLUX_NAMESPACE,
            "delete",
            f"gitrepository.source.toolkit.fluxcd.io/{git_repository}",
            "--ignore-not-found=true",
            "--wait=true",
            f"--timeout={config.timeout.raw}",
        ),
        runner=runner,
        timeout=config.timeout,
    )


RECLAIM_DELETE = json.dumps({"spec": {"persistentVolumeReclaimPolicy": "Delete"}}, separators=(",", ":"))
VolumeSelector = Callable[[str, dict], bool]


def _claim_namespace(pv: dict) -> str:
    return str(((pv.get("spec") or {}).get("claimRef") or {}).get("namespace") or "")


def _list_volumes(kubeconfig: Path, *, runner: Runner, timeout: Duration) -> list[dict]:
    listing = run_command(
        ["kubectl", "--kubeconfig", str(kubeconfig), "get", "persistentvolumes", "-o", "json"],
        runner=runner, timeout=timeout, capture_output=True,
    )
    try:
        return list(json.loads(str(getattr(listing, "stdout", "")))["items"])
    except (ValueError, KeyError, TypeError) as exc:
        raise VerificationError("could not read PersistentVolumes") from exc


def delete_released_volumes(
    kubeconfig: Path,
    select: VolumeSelector,
    *,
    runner: Runner,
    timeout: Duration,
    settle_namespace: str | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> list[str]:
    """Let Kubernetes delete the volumes a branch environment left behind.

    Development's StorageClasses use reclaimPolicy Retain, so a deleted branch claim
    leaves its PV Released and its directory on the NAS. A Released, Retain volume that
    `select(claim namespace, pv)` accepts is switched to Delete, and csi-driver-nfs then
    removes it. Only Released volumes are touched: their claim is already gone.
    With `settle_namespace`, first wait (up to a minute) for that namespace's volumes to
    leave Bound, since the claims were deleted moments ago.
    """
    for _ in range(12):
        volumes = _list_volumes(kubeconfig, runner=runner, timeout=timeout)
        if settle_namespace is None or not any(
            _claim_namespace(pv) == settle_namespace and (pv.get("status") or {}).get("phase") == "Bound" for pv in volumes
        ):
            break
        sleep(5)
    names = [
        pv["metadata"]["name"]
        for pv in volumes
        if (pv.get("status") or {}).get("phase") == "Released"
        and (pv.get("spec") or {}).get("persistentVolumeReclaimPolicy") == "Retain"
        and select(_claim_namespace(pv), pv)
    ]
    for name in names:
        run_command(
            ["kubectl", "--kubeconfig", str(kubeconfig), "patch", "persistentvolume", name, "--type=merge", "-p", RECLAIM_DELETE],
            runner=runner, timeout=timeout,
        )
    return names
