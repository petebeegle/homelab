from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools/onepassword/render_production_items.py"
INVENTORY_PATH = REPO_ROOT / "tools/onepassword/production_items.json"


class RenderProductionItemsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("render_production_items", MODULE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load resolver")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_production_inventory_has_all_seventeen_unique_pairs(self) -> None:
        inventory = self.module.load_inventory(INVENTORY_PATH)
        self.assertEqual(17, len(inventory["items"]))
        pairs = {(item["namespace"], item["legacy_name"]) for item in inventory["items"]}
        self.assertEqual(17, len(pairs))

    def test_render_contains_ids_and_never_values_or_titles_in_item_path(self) -> None:
        sentinel = "resolver-secret-sentinel"
        item = {
            "namespace": "example",
            "legacy_name": "legacy",
            "generated_name": "legacy-onepassword",
            "item_title": "k8s--example--legacy",
            "type": "Opaque",
            "keys": ["password"],
        }
        rendered = self.module.render_item(
            item,
            vault_id="a" * 26,
            item_id="b" * 26,
        )
        self.assertIn("vaults/" + "a" * 26 + "/items/" + "b" * 26, rendered)
        self.assertNotIn(item["item_title"], rendered)
        self.assertNotIn(sentinel, rendered)

    def test_item_validation_rejects_extra_nonempty_field_without_printing_value(self) -> None:
        sentinel = "extra-field-secret-sentinel"
        item_json = {
            "id": "b" * 26,
            "fields": [
                {"id": "password", "label": "password", "value": "expected"},
                {"id": "extra", "label": "extra-key", "value": sentinel},
            ],
        }
        with self.assertRaisesRegex(ValueError, "field set mismatch") as raised:
            self.module.validate_item_metadata(
                "k8s--example--legacy", item_json, {"password"}
            )
        self.assertNotIn(sentinel, str(raised.exception))
        self.assertNotIn("extra-key", str(raised.exception))

    def test_writer_emits_only_id_only_resources_and_kustomization(self) -> None:
        item = {
            "namespace": "example",
            "legacy_name": "legacy",
            "generated_name": "legacy-onepassword",
            "item_title": "k8s--example--legacy",
            "type": "Opaque",
            "keys": ["password"],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            self.module.write_manifests(output, "a" * 26, [(item, "b" * 26)])
            manifest = (output / "example--legacy-onepassword.yaml").read_text(
                encoding="utf-8"
            )
            kustomization = (output / "kustomization.yaml").read_text(
                encoding="utf-8"
            )
        self.assertIn('itemPath: "vaults/' + "a" * 26 + "/items/" + "b" * 26 + '"', manifest)
        self.assertNotIn(item["item_title"], manifest)
        self.assertIn("example--legacy-onepassword.yaml", kustomization)

    def test_failed_item_lookup_reports_title_without_captured_output(self) -> None:
        sentinel = "op-error-secret-sentinel"
        completed = subprocess.CompletedProcess(
            args=["op", "item", "get"],
            returncode=1,
            stdout="",
            stderr=sentinel,
        )
        with patch.object(self.module.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(
                RuntimeError,
                "item lookup failed for k8s--example--legacy",
            ) as raised:
                self.module.run_json(
                    ["op", "item", "get", "k8s--example--legacy"],
                    failure_context="item lookup failed for k8s--example--legacy",
                )
        self.assertNotIn(sentinel, str(raised.exception))


if __name__ == "__main__":
    unittest.main()
