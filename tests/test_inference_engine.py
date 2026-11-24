"""Tests for symbolic inference engine behavior."""
import unittest

from core.inference import InferenceEngine
from knowledge_base.validator import load_knowledge_base


class InferenceEngineTests(unittest.TestCase):
    def setUp(self):
        self.rules = [
            {
                "id": "R1", "if_all_symptoms": ["spots", "rings"],
                "then_diagnosis": "early_blight", "weight": 0.8,
                "explanation": "Spots with rings."
            },
            {
                "id": "R2", "if_all_symptoms": ["spots", "yellowing"],
                "then_diagnosis": "early_blight", "weight": 0.9,
                "explanation": "Spots with yellowing."
            },
            {
                "id": "R3", "if_all_symptoms": ["white_coating"],
                "then_diagnosis": "powdery_mildew", "weight": 0.7,
                "explanation": "White coating."
            },
        ]
        self.engine = InferenceEngine(self.rules)

    def test_forward_chaining_fires_only_complete_rules(self):
        result = self.engine.forward_chain({"spots", "rings"})
        self.assertEqual([rule["id"] for rule in result["fired_rules"]], ["R1"])
        self.assertIn("early_blight", result["conclusions"])

    def test_forward_chaining_can_produce_multiple_conclusions(self):
        result = self.engine.forward_chain({"spots", "rings", "white_coating"})
        self.assertEqual(set(result["conclusions"]), {"early_blight", "powdery_mildew"})

    def test_unmatched_rule_trace_lists_missing_evidence(self):
        result = self.engine.forward_chain({"spots"})
        row = next(item for item in result["trace"] if item["rule_id"] == "R1")
        self.assertFalse(row["matched"])
        self.assertEqual(row["missing_conditions"], ["rings"])

    def test_backward_chaining_proves_goal_from_complete_evidence(self):
        result = self.engine.backward_chain("early_blight", {"spots", "rings"})
        self.assertTrue(result["proved"])
        self.assertEqual(result["supporting_rule_ids"], ["R1"])

    def test_backward_chaining_reports_missing_evidence(self):
        result = self.engine.backward_chain("early_blight", {"spots"})
        self.assertFalse(result["proved"])
        self.assertIn("rings", result["missing_evidence"])
        self.assertIn("yellowing", result["missing_evidence"])

    def test_backward_chaining_unknown_goal_is_not_invented(self):
        result = self.engine.backward_chain("unknown_disease", {"spots"})
        self.assertFalse(result["proved"])
        self.assertEqual(result["candidate_rule_count"], 0)

    def test_conflict_resolution_selects_highest_weight_support(self):
        result = self.engine.forward_chain({"spots", "rings", "yellowing"})
        self.assertEqual(result["selected_rules"]["early_blight"]["id"], "R2")
        self.assertEqual(len(result["conclusions"]["early_blight"]), 2)

    def test_trace_includes_category_priority_and_explanation(self):
        result = self.engine.forward_chain({"spots"})
        row = next(item for item in result["trace"] if item["rule_id"] == "R1")
        self.assertEqual(row["category"], "uncategorized")
        self.assertEqual(row["priority"], 0.8)
        self.assertEqual(row["explanation"], "Spots with rings.")
        self.assertEqual(result["evaluated_rule_count"], 3)

    def test_invalid_fact_input_is_rejected(self):
        with self.assertRaises(TypeError):
            self.engine.forward_chain("spots")
        with self.assertRaises(ValueError):
            self.engine.forward_chain({"spots", ""})

    def test_empty_backward_goal_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.backward_chain(" ", {"spots"})

    def test_explicit_priority_overrides_legacy_weight(self):
        rules = [
            {"id": "A", "if_all_symptoms": ["spots"], "then_diagnosis": "x",
             "weight": 0.99, "priority": 0.2},
            {"id": "B", "if_all_symptoms": ["spots"], "then_diagnosis": "x",
             "weight": 0.4, "priority": 0.8},
        ]
        result = InferenceEngine(rules).forward_chain({"spots"})
        self.assertEqual(result["selected_rules"]["x"]["id"], "B")

    def test_real_knowledge_base_early_blight_regression(self):
        kb = load_knowledge_base()
        engine = InferenceEngine(kb["rules"])
        result = engine.forward_chain({"dark brown spots", "concentric rings"})
        self.assertIn("early_blight", result["conclusions"])
        self.assertTrue(result["selected_rules"]["early_blight"]["id"].startswith("R"))

    def test_all_production_rules_have_category_and_priority(self):
        kb = load_knowledge_base()
        self.assertTrue(all(rule.get("category") == "symptom_pattern" for rule in kb["rules"]))
        self.assertTrue(all(isinstance(rule.get("priority"), (int, float))
                            for rule in kb["rules"]))


if __name__ == "__main__":
    unittest.main()
