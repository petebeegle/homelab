#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_OTEL_ENDPOINT = "https://otel.lab.petebeegle.com/v1/metrics"
DEFAULT_TIMEOUT_SECONDS = 1.0
DEFAULT_FAILURE_COOLDOWN_SECONDS = 60.0
NANOSECONDS_PER_SECOND = 1_000_000_000


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = sys.stdin.buffer.read()
    root = repo_root()
    labels = safe_labels(
        payload=payload,
        root=root,
        phase=args.phase,
        hook=args.hook,
    )

    session_start = time.time()
    if args.session_start:
        record_session_start(root=root, labels=labels, started_at=session_start)

    started = time.time()
    started_ns = time.time_ns()
    status = "success"
    return_code = 0
    try:
        completed = subprocess.run(args.command, input=payload, check=False)
        return_code = completed.returncode
        if return_code != 0:
            status = "failure"
    except FileNotFoundError as exc:
        status = "failure"
        return_code = 127
        print(f"Codex observability: command not found: {exc.filename}", file=sys.stderr)

    ended = time.time()
    ended_ns = time.time_ns()
    duration = max(0.0, ended - started)
    labels["status"] = status

    metrics = hook_metrics(root=root, labels=labels, duration=duration, started_ns=started_ns, ended_ns=ended_ns)
    if args.session_end:
        metrics.extend(session_metrics(root=root, labels=labels, ended_at=ended, ended_ns=ended_ns))

    emit_metrics(root=root, labels=labels, metrics=metrics)
    return return_code


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wrap a Codex hook and emit best-effort workflow telemetry.")
    parser.add_argument("--phase", required=True)
    parser.add_argument("--hook", required=True)
    parser.add_argument("--session-start", action="store_true")
    parser.add_argument("--session-end", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("a wrapped command is required after --")
    return args


def repo_root() -> Path:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        return Path(completed.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def safe_labels(*, payload: bytes, root: Path, phase: str, hook: str) -> dict[str, str]:
    branch = git_output(root, ["git", "branch", "--show-current"]) or "unknown"
    return {
        "repo": root.name or "unknown",
        "branch": sanitize_label(branch),
        "implementation": sanitize_label(implementation_name(root=root, branch=branch)),
        "phase": sanitize_label(phase),
        "hook": sanitize_label(hook),
        "tool_name": sanitize_label(tool_name_from_payload(payload)),
    }


def implementation_name(*, root: Path, branch: str) -> str:
    if branch.startswith("codex/"):
        return branch.split("/", 1)[1]
    return "unknown"


def tool_name_from_payload(payload: bytes) -> str:
    try:
        data = json.loads(payload.decode("utf-8")) if payload.strip() else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "unknown"
    if not isinstance(data, dict):
        return "unknown"
    for key in ("tool_name", "tool", "name"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    tool_input = data.get("tool_input")
    if isinstance(tool_input, dict):
        value = tool_input.get("name")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown"


def sanitize_label(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in "._/-" else "_" for char in value.strip())
    return cleaned[:120] or "unknown"


def git_output(root: Path, command: list[str]) -> str:
    try:
        completed = subprocess.run(command, cwd=root, check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    return completed.stdout.strip()


def hook_metrics(
    *,
    root: Path,
    labels: dict[str, str],
    duration: float,
    started_ns: int,
    ended_ns: int,
) -> list[dict[str, Any]]:
    return [
        gauge_metric("codex_workflow_hook_duration_seconds", duration, labels, ended_ns),
        counter_metric(root, "codex_workflow_hook_runs_total", 1, labels, started_ns, ended_ns),
    ]


def session_metrics(*, root: Path, labels: dict[str, str], ended_at: float, ended_ns: int) -> list[dict[str, Any]]:
    started_at = read_session_started_at(root)
    if started_at is None:
        return []
    duration = max(0.0, ended_at - started_at)
    session_labels = {key: labels[key] for key in ("repo", "branch", "implementation", "status")}
    return [
        gauge_metric("codex_workflow_session_duration_seconds", duration, session_labels, ended_ns),
        counter_metric(
            root,
            "codex_workflow_session_runs_total",
            1,
            session_labels,
            int(started_at * NANOSECONDS_PER_SECOND),
            ended_ns,
        ),
    ]


def record_session_start(*, root: Path, labels: dict[str, str], started_at: float) -> None:
    try:
        observability_dir(root).mkdir(parents=True, exist_ok=True)
        state = {
            "started_at": started_at,
            "repo": labels["repo"],
            "branch": labels["branch"],
            "implementation": labels["implementation"],
        }
        (observability_dir(root) / "session-start.json").write_text(
            json.dumps(state, sort_keys=True),
            encoding="utf-8",
        )
    except OSError:
        return


def read_session_started_at(root: Path) -> float | None:
    path = observability_dir(root) / "session-start.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    value = data.get("started_at")
    return float(value) if isinstance(value, (float, int)) else None


def emit_metrics(*, root: Path, labels: dict[str, str], metrics: list[dict[str, Any]]) -> None:
    if os.environ.get("CODEX_OBSERVABILITY_DISABLED") == "1":
        return

    metrics = [*prior_delivery_failure_metrics(root=root, labels=labels), *metrics]
    if not metrics:
        return

    if telemetry_in_cooldown(root):
        spool_event(root=root, labels=labels, reason="delivery cooldown active")
        return

    endpoint = os.environ.get("CODEX_OTEL_ENDPOINT", DEFAULT_OTEL_ENDPOINT)
    timeout = env_float("CODEX_OTEL_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
    body = json.dumps(otlp_payload(metrics)).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout):
            pass
        clear_delivery_cooldown(root)
        clear_delivery_failures(root)
    except (OSError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        record_delivery_cooldown(root)
        spool_event(root=root, labels=labels, reason=str(exc))


def prior_delivery_failure_metrics(*, root: Path, labels: dict[str, str]) -> list[dict[str, Any]]:
    failure_labels = {key: labels[key] for key in ("repo", "branch", "implementation")}
    failure_labels["status"] = "failure"
    stored = stored_counter_metric(root, "codex_workflow_telemetry_delivery_failures_total", failure_labels)
    return [stored] if stored else []


def clear_delivery_failures(root: Path) -> None:
    try:
        spool_path(root).unlink()
    except FileNotFoundError:
        return
    except OSError:
        return


def telemetry_in_cooldown(root: Path) -> bool:
    try:
        data = json.loads(cooldown_path(root).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    next_attempt_at = data.get("next_attempt_at")
    return isinstance(next_attempt_at, (float, int)) and time.time() < float(next_attempt_at)


def record_delivery_cooldown(root: Path) -> None:
    cooldown = env_float("CODEX_OTEL_FAILURE_COOLDOWN_SECONDS", DEFAULT_FAILURE_COOLDOWN_SECONDS)
    try:
        observability_dir(root).mkdir(parents=True, exist_ok=True)
        cooldown_path(root).write_text(
            json.dumps({"next_attempt_at": time.time() + max(0.0, cooldown)}, sort_keys=True),
            encoding="utf-8",
        )
    except OSError:
        return


def clear_delivery_cooldown(root: Path) -> None:
    try:
        cooldown_path(root).unlink()
    except FileNotFoundError:
        return
    except OSError:
        return


def spool_event(*, root: Path, labels: dict[str, str], reason: str) -> None:
    failure_labels = {key: labels[key] for key in ("repo", "branch", "implementation")}
    failure_labels["status"] = "failure"
    increment_counter_state(
        root,
        "codex_workflow_telemetry_delivery_failures_total",
        failure_labels,
        1,
        time.time_ns(),
    )
    try:
        path = spool_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "labels": labels,
            "reason": reason[:240],
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True))
            handle.write("\n")
    except OSError:
        return


def observability_dir(root: Path) -> Path:
    return root / ".codex" / "tmp" / "observability"


def spool_path(root: Path) -> Path:
    return observability_dir(root) / "events.jsonl"


def counters_path(root: Path) -> Path:
    return observability_dir(root) / "counters.json"


def cooldown_path(root: Path) -> Path:
    return observability_dir(root) / "otel-cooldown.json"


def env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, ""))
    except ValueError:
        return default


def otlp_payload(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "resourceMetrics": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "codex-workflow"}},
                    ],
                },
                "scopeMetrics": [
                    {
                        "scope": {"name": "homelab.codex.workflow", "version": "1.0.0"},
                        "metrics": metrics,
                    }
                ],
            }
        ]
    }


def gauge_metric(name: str, value: float, labels: dict[str, str], time_unix_nano: int) -> dict[str, Any]:
    return {
        "name": name,
        "gauge": {
            "dataPoints": [
                {
                    "attributes": attributes(labels),
                    "timeUnixNano": str(time_unix_nano),
                    "asDouble": value,
                }
            ]
        },
    }


def counter_metric(
    root: Path,
    name: str,
    value: int,
    labels: dict[str, str],
    start_time_unix_nano: int,
    time_unix_nano: int,
) -> dict[str, Any]:
    state = increment_counter_state(root, name, labels, value, start_time_unix_nano)
    return counter_metric_data(
        name,
        state["value"],
        labels,
        state["start_time_unix_nano"],
        time_unix_nano,
    )


def stored_counter_metric(root: Path, name: str, labels: dict[str, str]) -> dict[str, Any] | None:
    counters = load_counters(root)
    state = counters.get(counter_key(name, labels))
    if not isinstance(state, dict):
        return None
    value = state.get("value")
    start_time = state.get("start_time_unix_nano")
    if not isinstance(value, int) or not isinstance(start_time, int):
        return None
    return counter_metric_data(name, value, labels, start_time, time.time_ns())


def counter_metric_data(
    name: str,
    value: int,
    labels: dict[str, str],
    start_time_unix_nano: int,
    time_unix_nano: int,
) -> dict[str, Any]:
    return {
        "name": name,
        "sum": {
            "aggregationTemporality": 2,
            "isMonotonic": True,
            "dataPoints": [
                {
                    "attributes": attributes(labels),
                    "startTimeUnixNano": str(start_time_unix_nano),
                    "timeUnixNano": str(time_unix_nano),
                    "asInt": str(value),
                }
            ],
        },
    }


def attributes(labels: dict[str, str]) -> list[dict[str, Any]]:
    return [{"key": key, "value": {"stringValue": value}} for key, value in sorted(labels.items())]


def increment_counter_state(
    root: Path,
    name: str,
    labels: dict[str, str],
    amount: int,
    start_time_unix_nano: int,
) -> dict[str, int]:
    counters = load_counters(root)
    key = counter_key(name, labels)
    state = counters.get(key)
    if not isinstance(state, dict):
        state = {"value": 0, "start_time_unix_nano": start_time_unix_nano}
    value = state.get("value", 0)
    start_time = state.get("start_time_unix_nano", start_time_unix_nano)
    if not isinstance(value, int):
        value = 0
    if not isinstance(start_time, int):
        start_time = start_time_unix_nano
    next_state = {"value": value + amount, "start_time_unix_nano": start_time}
    counters[key] = next_state
    save_counters(root, counters)
    return next_state


def load_counters(root: Path) -> dict[str, dict[str, int]]:
    try:
        data = json.loads(counters_path(root).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_counters(root: Path, counters: dict[str, dict[str, int]]) -> None:
    try:
        observability_dir(root).mkdir(parents=True, exist_ok=True)
        counters_path(root).write_text(json.dumps(counters, sort_keys=True), encoding="utf-8")
    except OSError:
        return


def counter_key(name: str, labels: dict[str, str]) -> str:
    return json.dumps({"name": name, "labels": labels}, sort_keys=True)


if __name__ == "__main__":
    raise SystemExit(main())
