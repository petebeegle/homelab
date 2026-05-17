"""Acceptance checks for branch smoke profiles."""

from __future__ import annotations

import json
import shlex
from typing import Sequence

from .config import AppConfig, HttpProbe, Runner, VerificationError
from .kube import kubectl, run_command
from .profiles import load_smoke_profile, render_profile_value


def assert_smoke_profile(config: AppConfig, profile, *, runner: Runner) -> None:
    name = render_profile_value(profile.namespace, config=config, field="namespace")
    run_command(kubectl(config, "get", "namespace", name), runner=runner, timeout=config.timeout)
    for helm_release in profile.helm_releases:
        resource_name = render_profile_value(helm_release, config=config, field="helmRelease")
        run_command(
            kubectl(
                config,
                "-n",
                name,
                "wait",
                f"helmrelease.helm.toolkit.fluxcd.io/{resource_name}",
                "--for=condition=Ready",
                f"--timeout={config.timeout.raw}",
            ),
            runner=runner,
            timeout=config.timeout,
        )
    wait_for_active_pods_ready(
        config,
        runner=runner,
        namespace=name,
        require_non_terminated=True,
        context=f"namespace {name}",
    )
    for pvc in profile.pvcs:
        resource_name = render_profile_value(pvc.name, config=config, field="pvc")
        assert_pvc_ready(config, namespace=name, pvc_name=resource_name, storage_class=pvc.storage_class, runner=runner)
    for service in profile.services:
        resource_name = render_profile_value(service, config=config, field="service")
        run_command(kubectl(config, "-n", name, "get", "service", resource_name), runner=runner, timeout=config.timeout)
    for http_route in profile.http_routes:
        resource_name = render_profile_value(http_route, config=config, field="httpRoute")
        route = run_command(
            kubectl(config, "-n", name, "get", "httproute", resource_name, "-o", "json"),
            runner=runner,
            timeout=config.timeout,
            capture_output=True,
        )
        assert_httproute_ready(str(getattr(route, "stdout", "")), route_name=resource_name)
    for index, probe in enumerate(profile.http_probes):
        run_command(
            build_http_probe_command(config, namespace=name, probe=probe, probe_index=index, total_probes=len(profile.http_probes)),
            runner=runner,
            timeout=config.timeout,
        )


def assert_whoami(config: AppConfig, *, runner: Runner) -> None:
    assert_smoke_profile(config, load_smoke_profile("whoami"), runner=runner)


def assert_pvc_ready(
    config: AppConfig,
    *,
    namespace: str,
    pvc_name: str,
    storage_class: str | None,
    runner: Runner,
) -> None:
    pvc = run_command(
        kubectl(config, "-n", namespace, "get", "pvc", pvc_name, "-o", "json"),
        runner=runner,
        timeout=config.timeout,
        capture_output=True,
    )
    assert_pvc_bound(str(getattr(pvc, "stdout", "")), pvc_name=pvc_name, storage_class=storage_class)


def assert_pvc_bound(pvc_json: str, *, pvc_name: str, storage_class: str | None) -> None:
    try:
        pvc = json.loads(pvc_json)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"PVC {pvc_name} did not return valid JSON: {exc}") from exc

    phase = pvc.get("status", {}).get("phase")
    if phase != "Bound":
        raise VerificationError(f"PVC {pvc_name} is not Bound; observed phase {phase!r}")
    if storage_class is not None and pvc.get("spec", {}).get("storageClassName") != storage_class:
        observed = pvc.get("spec", {}).get("storageClassName")
        raise VerificationError(f"PVC {pvc_name} storageClassName is {observed!r}, expected {storage_class!r}")


def build_http_probe_command(
    config: AppConfig,
    *,
    namespace: str,
    probe: HttpProbe,
    probe_index: int,
    total_probes: int,
) -> list[str]:
    service = render_profile_value(probe.service, config=config, field="httpProbe.service")
    pod_name_value = f"probe-{config.slug}" if total_probes == 1 else f"p{probe_index}-{config.slug}"
    url = f"http://{service}.{namespace}.svc.cluster.local:{probe.port}{probe.path}"
    script = (
        "for attempt in $(seq 1 60); do "
        f"if body=$(curl -LfsS --max-time 20 {shlex.quote(url)}); then "
        f"printf '%s' \"$body\" | grep -E {shlex.quote(probe.body_regex)} >/dev/null && exit 0; "
        "fi; "
        "sleep 5; "
        "done; "
        "exit 1"
    )
    return kubectl(
        config,
        "-n",
        namespace,
        "run",
        pod_name_value,
        "--image=curlimages/curl:8.16.0",
        "--restart=Never",
        "--rm=true",
        "--overrides",
        probe_pod_overrides(pod_name_value, command=["sh", "-ec"], args=[script]),
        "-i",
        "--quiet",
    )


def probe_pod_overrides(
    pod_name_value: str,
    image: str = "curlimages/curl:8.16.0",
    command: Sequence[str] | None = None,
    args: Sequence[str] | None = None,
) -> str:
    container: dict[str, object] = {
        "name": pod_name_value,
        "image": image,
        "securityContext": {
            "allowPrivilegeEscalation": False,
            "capabilities": {"drop": ["ALL"]},
            "runAsNonRoot": True,
            "runAsUser": 1000,
        },
    }
    if command is not None:
        container["command"] = list(command)
    if args is not None:
        container["args"] = list(args)

    return json.dumps(
        {
            "spec": {
                "securityContext": {
                    "runAsNonRoot": True,
                    "runAsUser": 1000,
                    "seccompProfile": {"type": "RuntimeDefault"},
                },
                "containers": [
                    container
                ],
            }
        },
        separators=(",", ":"),
    )


def wait_for_active_pods_ready(
    config: AppConfig,
    *,
    runner: Runner,
    namespace: str | None,
    require_non_terminated: bool,
    context: str,
) -> None:
    if namespace is None:
        pod_list = run_command(
            kubectl(config, "get", "pods", "--all-namespaces", "-o", "json"),
            runner=runner,
            timeout=config.timeout,
            capture_output=True,
        )
    else:
        pod_list = run_command(
            kubectl(config, "-n", namespace, "get", "pods", "-o", "json"),
            runner=runner,
            timeout=config.timeout,
            capture_output=True,
        )

    pods = parse_pods(str(getattr(pod_list, "stdout", "")), context=context)
    non_terminated = [pod for pod in pods if not is_pod_deleting(pod) and pod_phase(pod) not in {"Succeeded", "Failed"}]
    if require_non_terminated and not non_terminated:
        raise VerificationError(f"{context} has no non-terminated pods")

    for pod in pods:
        if is_pod_deleting(pod) or pod_phase(pod) == "Succeeded":
            continue
        name = pod_name(pod)
        namespace_name = pod_namespace_name(pod, default=namespace)
        if namespace_name is None:
            raise VerificationError(f"{context} pod {name} did not include a namespace")
        run_command(
            kubectl(config, "-n", namespace_name, "wait", f"pod/{name}", "--for=condition=Ready", f"--timeout={config.timeout.raw}"),
            runner=runner,
            timeout=config.timeout,
        )


def parse_pods(pods_json: str, *, context: str) -> list[dict[str, object]]:
    try:
        pod_list = json.loads(pods_json)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"{context} pods did not return valid JSON: {exc}") from exc

    items = pod_list.get("items")
    if not isinstance(items, list):
        raise VerificationError(f"{context} pods JSON did not contain an items list")
    return [pod for pod in items if isinstance(pod, dict)]


def is_pod_deleting(pod: dict[str, object]) -> bool:
    metadata = pod.get("metadata", {})
    return isinstance(metadata, dict) and bool(metadata.get("deletionTimestamp"))


def pod_phase(pod: dict[str, object]) -> str:
    status = pod.get("status", {})
    if not isinstance(status, dict):
        return ""
    phase = status.get("phase")
    return str(phase) if phase is not None else ""


def pod_name(pod: dict[str, object]) -> str:
    metadata = pod.get("metadata", {})
    if not isinstance(metadata, dict):
        raise VerificationError("pod did not include metadata")
    name = metadata.get("name")
    if not name:
        raise VerificationError("pod did not include metadata.name")
    return str(name)


def pod_namespace_name(pod: dict[str, object], *, default: str | None) -> str | None:
    metadata = pod.get("metadata", {})
    if not isinstance(metadata, dict):
        return default
    namespace = metadata.get("namespace")
    return str(namespace) if namespace else default


def assert_httproute_ready(route_json: str, *, route_name: str) -> None:
    try:
        route = json.loads(route_json)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"HTTPRoute {route_name} did not return valid JSON: {exc}") from exc

    parents = route.get("status", {}).get("parents", [])
    for parent in parents:
        conditions = parent.get("conditions", [])
        if all(
            any(condition.get("type") == condition_type and condition.get("status") == "True" for condition in conditions)
            for condition_type in ("Accepted", "ResolvedRefs")
        ):
            return
    raise VerificationError(f"HTTPRoute {route_name} has no parent with Accepted and ResolvedRefs conditions")
