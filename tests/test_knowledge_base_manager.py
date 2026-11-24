"""Tests for safe knowledge-base editing operations."""
import json
import tempfile
import unittest
from pathlib import Path

from knowledge_base.manager import KnowledgeBaseManager


class KnowledgeBaseManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        source = Path(__file__).parents[1] / "knowledge_base" / "knowledge_base.json"
        self.path = Path(self.temp_dir.name) / "knowledge_base.json"
        self.path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        self.manager = KnowledgeBaseManager(self.path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_delete_rule(self):
        original = len(self.manager.load()["rules"])
        new_rule = {
            "id": "TEST001", "name": "Test rule",
            "if_all_symptoms": ["dark brown spots", "concentric rings"],
            "then_diagnosis": "early_blight", "weight": 0.5,
            "explanation": "Test-only rule.", "category": "symptom_pattern",
            "priority": 0.5
        }
        self.manager.add_rule(new_rule)
        self.assertEqual(len(self.manager.load()["rules"]), original + 1)
        self.manager.delete_rule("TEST001")
        self.assertEqual(len(self.manager.load()["rules"]), original)

    def test_invalid_rule_is_not_saved(self):
        before = self.path.read_text(encoding="utf-8")
        with self.assertRaises(ValueError):
            self.manager.add_rule({"id": "BAD"})
        self.assertEqual(self.path.read_text(encoding="utf-8"), before)

    def test_update_rule_keeps_id_stable(self):
        rule = self.manager.load()["rules"][0]
        changed = dict(rule, explanation="Updated test explanation.")
        self.manager.update_rule(rule["id"], changed)
        self.assertEqual(self.manager.load()["rules"][0]["explanation"], "Updated test explanation.")
        with self.assertRaises(ValueError):
            self.manager.update_rule(rule["id"], dict(changed, id="OTHER"))

    def test_update_assertion(self):
        fact = self.manager.load()["assertions"][0]
        self.manager.update_assertion(fact["id"], "Updated test value")
        found = next(x for x in self.manager.load()["assertions"] if x["id"] == fact["id"])
        self.assertEqual(found["value"], "Updated test value")

    def test_invalid_import_does_not_replace_data(self):
        before = self.manager.export_json()
        with self.assertRaises(ValueError):
            self.manager.import_json(json.dumps({"rules": []}))
        self.assertEqual(self.manager.export_json(), before)

    def test_export_can_be_imported(self):
        exported = self.manager.export_json()
        report = self.manager.import_json(exported)
        self.assertTrue(report["valid"])


if __name__ == "__main__":
    unittest.main()
