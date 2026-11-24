"""Tests for human-readable inference explanations."""
import unittest

from core.inference import InferenceEngine
from services.explainability import build_explanation_report
from knowledge_base.validator import load_knowledge_base


class ExplainabilityTests(unittest.TestCase):
    def test_report_separates_supporting_rules_and_missing_evidence(self):
        rules = [
            {"id": "R1", "if_all_symptoms": ["spots", "rings"],
             "then_diagnosis": "early_blight", "priority": 0.8,
             "explanation": "Spots with rings."},
            {"id": "R2", "if_all_symptoms": ["spots", "yellowing"],
             "then_diagnosis": "early_blight", "priority": 0.7,
             "explanation": "Spots with yellowing."},
        ]
        inference = InferenceEngine(rules).forward_chain({"spots", "rings"})
        report = build_explanation_report(inference, ["early_blight"])
        item = report["diagnoses"][0]
        self.assertTrue(item["supported"])
        self.assertEqual(item["supporting_rules"][0]["rule_id"], "R1")
        self.assertEqual(item["missing_evidence"], ["yellowing"])
        self.assertEqual(report["fired_rule_count"], 1)
        self.assertEqual(report["unmatched_rule_count"], 1)

    def test_report_does_not_claim_unsupported_diagnosis(self):
        rules = [{"id": "R1", "if_all_symptoms": ["spots", "rings"],
                  "then_diagnosis": "early_blight", "priority": 0.8}]
        inference = InferenceEngine(rules).forward_chain({"spots"})
        report = build_explanation_report(inference, ["early_blight"])
        self.assertFalse(report["diagnoses"][0]["supported"])
        self.assertEqual(report["diagnoses"][0]["missing_evidence"], ["rings"])

    def test_report_with_real_knowledge_base(self):
        kb = load_knowledge_base()
        result = InferenceEngine(kb["rules"]).forward_chain(
            {"dark brown spots", "concentric rings"}
        )
        report = build_explanation_report(result)
        self.assertGreater(report["evaluated_rule_count"], 0)
        self.assertGreaterEqual(report["fired_rule_count"], 1)
        self.assertTrue(report["diagnoses"])


if __name__ == "__main__":
    unittest.main()
