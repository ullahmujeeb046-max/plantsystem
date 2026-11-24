"""Tests for local consultation history and report export."""
import tempfile
import unittest
from pathlib import Path

from services.history_store import HistoryStore, build_markdown_report


class HistoryStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = HistoryStore(Path(self.temp_dir.name) / "history.json", max_records=3)
        self.turn = {
            "complete": False,
            "evidence": {
                "positive": ["dark spots"],
                "negative": ["wilting"],
                "uncertain": ["yellowing"],
                "contradictions": []
            },
            "diagnosis": {
                "diagnoses": [{
                    "id": "early_blight", "name": "Early blight",
                    "score": 75, "matched_rules": ["R1"],
                    "explanation": "Spots and rings matched.",
                    "management": "Remove affected leaves.",
                    "prevention": "Avoid overhead watering."
                }]
            },
            "next_question": {"text": "Have you noticed concentric rings?"}
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_reload_record(self):
        saved = self.store.save_turn(self.turn)
        loaded = self.store.get(saved["id"])
        self.assertEqual(loaded["evidence"]["positive"], ["dark spots"])
        self.assertEqual(len(self.store.list_records()), 1)

    def test_update_same_record_instead_of_duplicate(self):
        saved = self.store.save_turn(self.turn, record_id="session-1")
        changed = dict(self.turn, complete=True)
        updated = self.store.save_turn(changed, record_id="session-1")
        self.assertEqual(updated["id"], saved["id"])
        self.assertEqual(len(self.store.list_records()), 1)
        self.assertEqual(self.store.get("session-1")["status"], "complete")

    def test_free_text_description_is_not_saved(self):
        turn = dict(self.turn, original_description="Private text should not be stored")
        saved = self.store.save_turn(turn)
        self.assertNotIn("original_description", saved)

    def test_delete_record(self):
        saved = self.store.save_turn(self.turn)
        self.store.delete(saved["id"])
        self.assertEqual(self.store.list_records(), [])

    def test_history_limit(self):
        for index in range(4):
            self.store.save_turn(self.turn, record_id=f"record-{index}")
        self.assertEqual(len(self.store.list_records()), 3)

    def test_markdown_report_contains_evidence_and_warning(self):
        saved = self.store.save_turn(self.turn)
        report = build_markdown_report(saved)
        self.assertIn("Early blight", report)
        self.assertIn("dark spots", report)
        self.assertIn("not a disease probability", report)
        self.assertIn("not a confirmed diagnosis", report)

    def test_missing_record_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.store.get("missing")


if __name__ == "__main__":
    unittest.main()
