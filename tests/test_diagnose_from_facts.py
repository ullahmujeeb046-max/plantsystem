"""Tests for direct diagnosis from confirmed facts."""
import unittest

from expert_system import TomatoExpertSystem


class DiagnoseFromFactsTests(unittest.TestCase):
    def setUp(self):
        self.system = TomatoExpertSystem()

    def test_empty_facts_returns_no_diagnosis(self):
        result = self.system.diagnose_from_facts([])
        self.assertEqual(result["recognized_symptoms"], [])
        self.assertEqual(result["diagnoses"], [])

    def test_confirmed_facts_are_used_directly(self):
        facts = ["dark brown spots", "concentric rings", "yellowing lower leaves"]
        result = self.system.diagnose_from_facts(facts)
        self.assertEqual(result["recognized_symptoms"], sorted(facts))
        self.assertGreaterEqual(result["fired_rule_count"], 0)

    def test_diagnose_text_and_fact_api_agree_on_recognized_symptoms(self):
        text = "The leaves have dark brown spots with concentric rings."
        extracted = self.system.extract_symptoms(text)
        result = self.system.diagnose_from_facts(extracted)
        self.assertEqual(result["recognized_symptoms"], sorted(extracted))


if __name__ == "__main__":
    unittest.main()
