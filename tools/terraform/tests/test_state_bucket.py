from __future__ import annotations

import io
import sys
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "terraform"))

import state_bucket  # noqa: E402

ENABLED = b'<VersioningConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Status>Enabled</Status></VersioningConfiguration>'


class FakeS3(BaseHTTPRequestHandler):
    """Records requests; answers the way S3 does for bucket creation and versioning."""

    requests: list[tuple[str, str, str]] = []
    bucket_exists = False
    versioning = b""

    def log_message(self, *args: object) -> None:
        pass

    def _reply(self, code: int, body: bytes = b"") -> None:
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _record(self) -> bytes:
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        type(self).requests.append((self.command, self.path, self.headers.get("Authorization", "")))
        return body

    def do_PUT(self) -> None:
        body = self._record()
        if self.path.endswith("?versioning="):
            type(self).versioning = body
            self._reply(200)
        elif type(self).bucket_exists:
            self._reply(409, b"<Error><Code>BucketAlreadyOwnedByYou</Code></Error>")
        else:
            type(self).bucket_exists = True
            self._reply(200)

    def do_GET(self) -> None:
        self._record()
        self._reply(200, type(self).versioning or b"<VersioningConfiguration/>")


class StateBucketTest(unittest.TestCase):
    def setUp(self) -> None:
        FakeS3.requests = []
        FakeS3.bucket_exists = False
        FakeS3.versioning = b""
        self.server = HTTPServer(("127.0.0.1", 0), FakeS3)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.endpoint = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self) -> None:
        self.server.shutdown()

    def ensure(self) -> str:
        out = io.StringIO()
        with redirect_stdout(out):
            state_bucket.ensure(self.endpoint, "terraform-state", "AKEXAMPLE", "secret-do-not-print")
        return out.getvalue()

    def test_creates_the_bucket_then_turns_versioning_on(self) -> None:
        self.ensure()
        calls = [(method, path) for method, path, _ in FakeS3.requests]
        self.assertEqual(calls[:2], [("PUT", "/terraform-state"), ("PUT", "/terraform-state?versioning=")])
        self.assertIn(b"<Status>Enabled</Status>", FakeS3.versioning)

    def test_an_existing_bucket_is_fine(self) -> None:
        FakeS3.bucket_exists = True
        self.ensure()
        self.assertIn(b"<Status>Enabled</Status>", FakeS3.versioning)

    def test_every_request_is_signed_and_the_secret_is_never_printed(self) -> None:
        output = self.ensure()
        for _, _, auth in FakeS3.requests:
            self.assertRegex(auth, r"^AWS4-HMAC-SHA256 Credential=AKEXAMPLE/\d{8}/us-east-1/s3/aws4_request, ")
            self.assertNotIn("secret-do-not-print", auth)
        self.assertNotIn("secret-do-not-print", output)

    def test_fails_when_versioning_does_not_read_back_enabled(self) -> None:
        original = FakeS3.do_PUT

        def ignore_versioning(handler: FakeS3) -> None:
            if handler.path.endswith("?versioning="):
                handler._record()
                handler._reply(200)
                return
            original(handler)

        FakeS3.do_PUT = ignore_versioning  # type: ignore[method-assign]
        try:
            with self.assertRaisesRegex(state_bucket.BucketError, "versioning"):
                self.ensure()
        finally:
            FakeS3.do_PUT = original  # type: ignore[method-assign]


if __name__ == "__main__":
    unittest.main()
