from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent_memory.compaction import compact_transcript


class CompactionTests(unittest.TestCase):
    def test_compaction_writes_checkpoint_and_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text = """
            General conversation.
            Remember: user prefers concise final summaries.
            Decision: keep memory storage local and file-based.
            """

            checkpoint = compact_transcript(text, root=root, source="unit-test")

            checkpoint_path = root / "checkpoints" / f"{checkpoint.checkpoint_id}.json"
            pending_path = root / "candidates" / "pending.jsonl"

            self.assertTrue(checkpoint_path.exists())
            self.assertTrue(pending_path.exists())
            self.assertEqual(len(checkpoint.candidate_ids), 2)

            checkpoint_record = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            pending_records = [json.loads(line) for line in pending_path.read_text(encoding="utf-8").splitlines()]

            self.assertEqual(checkpoint_record["source"], "unit-test")
            self.assertEqual([record["candidate_id"] for record in pending_records], list(checkpoint.candidate_ids))
            self.assertTrue(
                all((root / name / ".gitkeep").exists() for name in ["checkpoints", "candidates", "approved", "rejected", "reports"])
            )
