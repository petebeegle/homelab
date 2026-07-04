from __future__ import annotations

import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
POLICY_ROOT = REPO_ROOT / "tools" / "policy"
if str(POLICY_ROOT) not in sys.path:
    sys.path.insert(0, str(POLICY_ROOT))

import check_synthetic_smoke_mirroring


class SyntheticSmokeMirroringTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="synthetic-smoke-mirror-")
        self.root = Path(self.temp_dir.name)
        self.local_routes = self.root / "tests" / "smoke" / "routes.spec.js"
        self.cluster_routes = self.root / "kubernetes" / "apps" / "synthetics" / "smoke" / "routes.spec.js"
        self.local_lock = self.root / "tests" / "smoke" / "package-lock.json"
        self.cluster_lock = self.root / "kubernetes" / "apps" / "synthetics" / "smoke" / "package-lock.json"
        self._write_pair(self.local_routes, self.cluster_routes, "route-content\n")
        self._write_pair(self.local_lock, self.cluster_lock, '{"lockfileVersion":3}\n')

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_allows_required_mirrors_to_match(self) -> None:
        result = check_synthetic_smoke_mirroring.check_mirrors(self.root)

        self.assertTrue(result.ok, result.issues)

    def test_reports_route_spec_drift(self) -> None:
        self.local_routes.write_text("local-only\n", encoding="utf-8")

        result = check_synthetic_smoke_mirroring.check_mirrors(self.root)

        self.assertFalse(result.ok)
        self.assertTrue(any("routes.spec.js must exactly match" in issue for issue in result.issues))

    def test_reports_lockfile_drift(self) -> None:
        self.cluster_lock.write_text('{"lockfileVersion":2}\n', encoding="utf-8")

        result = check_synthetic_smoke_mirroring.check_mirrors(self.root)

        self.assertFalse(result.ok)
        self.assertTrue(any("package-lock.json must exactly match" in issue for issue in result.issues))

    def test_ignores_intentionally_different_cluster_only_files(self) -> None:
        local_package = self.root / "tests" / "smoke" / "package.json"
        cluster_package = self.root / "kubernetes" / "apps" / "synthetics" / "smoke" / "package.json"
        self._write_pair(local_package, cluster_package, "local\n", cluster_content="cluster\n")

        result = check_synthetic_smoke_mirroring.check_mirrors(self.root)

        self.assertTrue(result.ok, result.issues)

    def test_main_prints_failing_pair(self) -> None:
        self.local_routes.write_text("local-only\n", encoding="utf-8")
        stream = StringIO()

        with redirect_stderr(stream):
            exit_code = check_synthetic_smoke_mirroring.main(["--root", str(self.root)])

        self.assertEqual(exit_code, 1)
        self.assertIn("Synthetic smoke mirror check failed", stream.getvalue())
        self.assertIn("tests/smoke/routes.spec.js", stream.getvalue())

    def _write_pair(
        self,
        local_path: Path,
        cluster_path: Path,
        content: str,
        *,
        cluster_content: str | None = None,
    ) -> None:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        cluster_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(content, encoding="utf-8")
        cluster_path.write_text(cluster_content if cluster_content is not None else content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
