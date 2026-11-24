"""Automated tests for knowledge-base schema and reference integrity."""
import copy
import unittest

from knowledge_base.validator import load_knowledge_base, validate_knowledge_base


class KnowledgeBaseValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = load_knowledge_base()

    def test_current_knowledge_base_is_structurally_valid(self):
        report = validate_knowledge_base(self.data)
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["summary"]["rule_count"], 100)
        self.assertEqual(report["summary"]["assertion_count"], 300)
        self.assertEqual(report["summary"]["profile_count"], 20)

    def test_duplicate_rule_id_is_reported(self):
        data = copy.deepcopy(self.data)
        data["rules"][1]["id"] = data["rules"][0]["id"]
        report = validate_knowledge_base(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("Duplicate rule ID" in item for item in report["errors"]))

    def test_unknown_symptom_reference_is_reported(self):
        data = copy.deepcopy(self.data)
        data["rules"][0]["if_all_symptoms"].append("purple glowing leaves")
        report = validate_knowledge_base(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("unknown symptom fact" in item for item in report["errors"]))

    def test_unknown_conclusion_profile_is_reported(self):
        data = copy.deepcopy(self.data)
        data["rules"][0]["then_diagnosis"] = "unknown_condition"
        report = validate_knowledge_base(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("has no assertion profile" in item for item in report["errors"]))

    def test_invalid_weight_is_reported(self):
        data = copy.deepcopy(self.data)
        data["rules"][0]["weight"] = 1.5
        report = validate_knowledge_base(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("weight must be between 0 and 1" in item for item in report["errors"]))

    def test_missing_profile_predicate_is_reported(self):
        data = copy.deepcopy(self.data)
        data["assertions"] = [
            fact for fact in data["assertions"]
            if not (fact["subject"] == "early_blight" and fact["predicate"] == "prevention")
        ]
        report = validate_knowledge_base(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("Profile 'early_blight' is missing predicates" in item
                            for item in report["errors"]))

    def test_duplicate_assertion_id_is_reported(self):
        data = copy.deepcopy(self.data)
        data["assertions"][1]["id"] = data["assertions"][0]["id"]
        report = validate_knowledge_base(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("Duplicate assertion ID" in item for item in report["errors"]))


if __name__ == "__main__":
    unittest.main()
