from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "render.py"
SPEC = importlib.util.spec_from_file_location("context_pack_render", MODULE_PATH)
assert SPEC is not None
render = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = render
SPEC.loader.exec_module(render)


class ContextPackRenderTest(unittest.TestCase):
    def test_select_sources_excludes_secret_paths_and_overdue_memory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(root)
            self._write(root / "AGENTS.md", "# Rules\n\nUse GitOps for Kubernetes.")
            self._write(root / "docs/runbooks/add-app.md", "# Add App\n\nUse HTTPRoute and SOPS secret.yaml.")
            self._write(root / "docs/runbooks/secret.yaml", "password: nope")
            self._write(
                root / ".codex/memory/approved/2026-05-09-old.md",
                "---\nstatus: approved\nreview_after: 2026-05-09\nsuperseded_by: []\n---\n\n# Old\n\nAdd app memory.",
            )

            old_root = render.ROOT
            render.ROOT = root
            try:
                manifest = render.parse_manifest(root / ".codex/retrieval.yaml", "binding-agent-context")
                sources = render.select_sources("add app with SOPS secret and HTTPRoute", manifest, limit=8)
                paths = [source.relative_path for source in sources]
            finally:
                render.ROOT = old_root

            self.assertIn("AGENTS.md", paths)
            self.assertIn("docs/runbooks/add-app.md", paths)
            self.assertNotIn("docs/runbooks/secret.yaml", paths)
            self.assertNotIn(".codex/memory/approved/2026-05-09-old.md", paths)

    def test_render_pack_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(root)
            self._write(root / "AGENTS.md", "# Rules\n\nUse Git as truth.")
            self._write(root / "docs/runbooks/add-secret.md", "# Add Secret\n\nEncrypt secret.yaml with SOPS.")

            old_root = render.ROOT
            old_commit_sha = render.commit_sha
            render.ROOT = root
            render.commit_sha = lambda: "abc123"
            try:
                manifest = render.parse_manifest(root / ".codex/retrieval.yaml", "binding-agent-context")
                sources = render.select_sources("add secret with sops", manifest, limit=8)
                first = render.render_pack("add secret with sops", sources)
                second = render.render_pack("add secret with sops", sources)
            finally:
                render.ROOT = old_root
                render.commit_sha = old_commit_sha

            self.assertEqual(first, second)
            self.assertIn("Commit: abc123", first)
            self.assertLess(first.index("### AGENTS.md"), first.index("### docs/runbooks/add-secret.md"))

    def _write_manifest(self, root: Path) -> None:
        self._write(
            root / ".codex/retrieval.yaml",
            "---\nindexes:\n  - name: binding-agent-context\n    include:\n      - AGENTS.md\n      - docs/runbooks/**/*.md\n      - .codex/memory/approved/**/*.md\n    exclude:\n      - '**/secret.yaml'\n    required_metadata:\n      - source_path\n",
        )

    def _write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
