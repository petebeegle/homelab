from __future__ import annotations

import http.server
import importlib.util
import json
import os
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[3] / ".codex" / "scripts" / "codex_observe.py"
SPEC = importlib.util.spec_from_file_location("codex_observe", MODULE_PATH)
assert SPEC is not None
observer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = observer
SPEC.loader.exec_module(observer)


class Receiver(http.server.BaseHTTPRequestHandler):
    requests: list[dict[str, object]] = []

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        self.__class__.requests.append(
            {
                "path": self.path,
                "content_type": self.headers.get("Content-Type"),
                "body": body,
            }
        )
        self.send_response(200)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


class ThreadedTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class CodexObserveTest(unittest.TestCase):
    def setUp(self) -> None:
        Receiver.requests = []
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_observer(
        self,
        *command: str,
        endpoint: str | None = None,
        disabled: bool = False,
        payload: bytes = b'{"tool_name":"Bash","command":"do not record this"}',
    ) -> subprocess.CompletedProcess[bytes]:
        env = os.environ.copy()
        env["CODEX_OTEL_TIMEOUT_SECONDS"] = "0.2"
        if endpoint is not None:
            env["CODEX_OTEL_ENDPOINT"] = endpoint
        if disabled:
            env["CODEX_OBSERVABILITY_DISABLED"] = "1"
        return subprocess.run(
            [
                sys.executable,
                str(MODULE_PATH),
                "--phase",
                "post_tool",
                "--hook",
                "unit_test_hook",
                "--",
                *command,
            ],
            cwd=self.root,
            input=payload,
            env=env,
            check=False,
            capture_output=True,
        )

    def test_successful_command_records_otlp_metrics(self) -> None:
        with ThreadedTCPServer(("127.0.0.1", 0), Receiver) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            result = self.run_observer(
                sys.executable,
                "-c",
                "print('ok')",
                endpoint=f"http://127.0.0.1:{server.server_address[1]}/v1/metrics",
            )
            server.shutdown()
            thread.join(timeout=2)

        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(len(Receiver.requests), 1)
        request = Receiver.requests[0]
        self.assertEqual(request["path"], "/v1/metrics")
        self.assertEqual(request["content_type"], "application/json")
        body = json.loads(request["body"])
        metrics = body["resourceMetrics"][0]["scopeMetrics"][0]["metrics"]
        metric_names = {metric["name"] for metric in metrics}
        self.assertIn("codex_workflow_hook_duration_seconds", metric_names)
        self.assertIn("codex_workflow_hook_runs_total", metric_names)

    def test_failed_command_preserves_exit_code(self) -> None:
        result = self.run_observer(
            sys.executable,
            "-c",
            "raise SystemExit(42)",
            disabled=True,
        )

        self.assertEqual(result.returncode, 42)

    def test_otlp_failure_spools_event_without_failing_command(self) -> None:
        result = self.run_observer(
            sys.executable,
            "-c",
            "raise SystemExit(0)",
            endpoint="http://127.0.0.1:9/v1/metrics",
        )

        self.assertEqual(result.returncode, 0, result.stderr.decode())
        spool = self.root / ".codex" / "tmp" / "observability" / "events.jsonl"
        self.assertTrue(spool.exists())
        self.assertTrue((self.root / ".codex" / "tmp" / "observability" / "otel-cooldown.json").exists())
        event = json.loads(spool.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["labels"]["hook"], "unit_test_hook")
        self.assertEqual(event["labels"]["status"], "success")

    def test_payload_parsing_keeps_only_safe_labels(self) -> None:
        labels = observer.safe_labels(
            payload=b'{"tool_name":"Bash","command":"sops -d secret.yaml","tool_input":{"cmd":"cat private"}}',
            root=self.root,
            phase="pre_tool",
            hook="sops_guard",
        )

        self.assertEqual(
            set(labels),
            {"repo", "branch", "implementation", "phase", "hook", "tool_name"},
        )
        self.assertEqual(labels["tool_name"], "Bash")
        rendered = json.dumps(labels)
        self.assertNotIn("secret", rendered)
        self.assertNotIn("private", rendered)
        self.assertNotIn("sops -d", rendered)


if __name__ == "__main__":
    unittest.main()
