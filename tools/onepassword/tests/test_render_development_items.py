from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools/onepassword/render_development_items.py"
INVENTORY_PATH = REPO_ROOT / "tools/onepassword/development_items.json"


class RenderDevelopmentItemsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("render_development_items", MODULE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load development resolver")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_inventory_has_three_exact_development_items(self) -> None:
        inventory = self.module.load_development_inventory(INVENTORY_PATH)
        identities = {
            (item["namespace"], item["legacy_name"])
            for item in inventory["items"]
        }
        self.assertEqual(
            {
                ("cert-manager", "cloudflare-api-token"),
                ("immich", "immich-postgres-user"),
                ("immich", "immich-secrets"),
            },
            identities,
        )

    def test_writer_places_only_id_resources_at_allowlisted_paths(self) -> None:
        inventory = self.module.load_development_inventory(INVENTORY_PATH)
        resolved = [(item, chr(ord("b") + index) * 26) for index, item in enumerate(inventory["items"])]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.module.write_development_manifests(root, "a" * 26, resolved)
            rendered = [
                (root / item["output_path"]).read_text(encoding="utf-8")
                for item in inventory["items"]
            ]
        self.assertEqual(3, len(rendered))
        self.assertTrue(all("vaults/" + "a" * 26 + "/items/" in text for text in rendered))
        self.assertTrue(all("item_title" not in text for text in rendered))

    def test_writer_rejects_path_outside_allowlisted_overlays(self) -> None:
        item = {
            "namespace": "immich",
            "legacy_name": "immich-secrets",
            "generated_name": "immich-secrets-onepassword",
            "item_title": "k8s--immich--immich-secrets",
            "type": "Opaque",
            "keys": ["immich-config.yaml"],
            "output_path": "kubernetes/clusters/production/unsafe.yaml",
        }
        with tempfile.TemporaryDirectory() as temp_dir, self.assertRaisesRegex(
            ValueError, "output path"
        ):
            self.module.write_development_manifests(
                Path(temp_dir), "a" * 26, [(item, "b" * 26)]
            )


if __name__ == "__main__":
    unittest.main()
