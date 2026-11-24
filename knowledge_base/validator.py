"""Validation utilities for the tomato expert-system JSON knowledge base.

Uses only the Python standard library. Validation does not modify source data.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_KB_PATH = Path(__file__).with_name("knowledge_base.json")
REQUIRED_TOP_LEVEL = {"project", "scope", "rules", "assertions"}
REQUIRED_RULE_FIELDS = {
    "id", "name", "if_all_symptoms", "then_diagnosis", "weight", "explanation"
}
REQUIRED_ASSERTION_FIELDS = {"id", "subject", "predicate", "value"}
REQUIRED_PROFILE_PREDICATES = {
    "has_common_name", "crop", "domain",
    "symptom_1", "symptom_2", "symptom_3", "symptom_4", "symptom_5",
    "management", "prevention", "diagnosis_type", "host",
    "evidence_required", "advisory_level", "knowledge_source_type",
}


def load_knowledge_base(path: str | Path = DEFAULT_KB_PATH) -> dict[str, Any]:
    """Load JSON data and ensure the root value is an object."""
    source = Path(path)
    try:
        with source.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {source} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(data, dict):
        raise ValueError("Knowledge base root must be a JSON object.")
    return data


def validate_knowledge_base(data: dict[str, Any]) -> dict[str, Any]:
    """Return a detailed, deterministic validation report.

    Errors indicate structural or referential problems. Warnings identify
    legacy metadata or suspicious patterns that need human review.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return {
            "valid": False,
            "errors": ["Knowledge base root must be an object."],
            "warnings": [],
            "summary": {},
        }

    missing_top = sorted(REQUIRED_TOP_LEVEL - set(data))
    for key in missing_top:
        errors.append(f"Missing required top-level field: {key}")

    rules = data.get("rules", [])
    assertions = data.get("assertions", [])
    if not isinstance(rules, list):
        errors.append("'rules' must be a list.")
        rules = []
    if not isinstance(assertions, list):
        errors.append("'assertions' must be a list.")
        assertions = []

    if not data.get("project"):
        errors.append("'project' must contain a non-empty project name.")
    if not data.get("scope"):
        errors.append("'scope' must contain a non-empty domain description.")

    assertion_ids: list[str] = []
    rule_ids: list[str] = []
    profiles: dict[str, dict[str, Any]] = defaultdict(dict)
    assertion_keys: list[tuple[str, str]] = []

    for index, fact in enumerate(assertions):
        label = f"Assertion at index {index}"
        if not isinstance(fact, dict):
            errors.append(f"{label} must be an object.")
            continue
        missing = sorted(REQUIRED_ASSERTION_FIELDS - set(fact))
        if missing:
            errors.append(f"{label} is missing fields: {', '.join(missing)}")
            continue
        fact_id = fact["id"]
        subject = fact["subject"]
        predicate = fact["predicate"]
        value = fact["value"]
        if not all(isinstance(item, str) and item.strip()
                   for item in (fact_id, subject, predicate)):
            errors.append(f"{label} has an empty or non-text id, subject, or predicate.")
            continue
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{label} ({fact_id}) has an empty value.")
        assertion_ids.append(fact_id)
        assertion_keys.append((subject, predicate))
        profiles[subject][predicate] = value

    duplicate_assertion_ids = sorted(
        item for item, count in Counter(assertion_ids).items() if count > 1
    )
    for item in duplicate_assertion_ids:
        errors.append(f"Duplicate assertion ID: {item}")

    duplicate_fact_keys = sorted(
        key for key, count in Counter(assertion_keys).items() if count > 1
    )
    for subject, predicate in duplicate_fact_keys:
        errors.append(
            f"Duplicate assertion for subject '{subject}' and predicate '{predicate}'."
        )

    for subject, profile in sorted(profiles.items()):
        missing = sorted(REQUIRED_PROFILE_PREDICATES - set(profile))
        if missing:
            errors.append(
                f"Profile '{subject}' is missing predicates: {', '.join(missing)}"
            )

    known_symptoms = {
        str(value).strip()
        for profile in profiles.values()
        for key, value in profile.items()
        if key.startswith("symptom_") and isinstance(value, str) and value.strip()
    }
    known_profiles = set(profiles)

    rule_signatures: list[tuple[tuple[str, ...], str]] = []
    conclusions: list[str] = []

    for index, rule in enumerate(rules):
        label = f"Rule at index {index}"
        if not isinstance(rule, dict):
            errors.append(f"{label} must be an object.")
            continue
        missing = sorted(REQUIRED_RULE_FIELDS - set(rule))
        if missing:
            errors.append(f"{label} is missing fields: {', '.join(missing)}")
            continue

        rule_id = rule["id"]
        if not isinstance(rule_id, str) or not rule_id.strip():
            errors.append(f"{label} has an invalid rule ID.")
            continue
        rule_ids.append(rule_id)

        if not isinstance(rule["name"], str) or not rule["name"].strip():
            errors.append(f"Rule {rule_id} has an empty or invalid name.")
        if not isinstance(rule["explanation"], str) or not rule["explanation"].strip():
            errors.append(f"Rule {rule_id} has an empty or invalid explanation.")

        conditions = rule["if_all_symptoms"]
        if not isinstance(conditions, list) or not conditions:
            errors.append(f"Rule {rule_id} must have at least one antecedent symptom.")
            continue
        if any(not isinstance(item, str) or not item.strip() for item in conditions):
            errors.append(f"Rule {rule_id} contains an empty or non-text antecedent.")
            continue
        if len(conditions) != len(set(conditions)):
            errors.append(f"Rule {rule_id} repeats an antecedent symptom.")

        for symptom in conditions:
            if symptom not in known_symptoms:
                errors.append(
                    f"Rule {rule_id} references unknown symptom fact: '{symptom}'."
                )

        conclusion = rule["then_diagnosis"]
        if not isinstance(conclusion, str) or not conclusion.strip():
            errors.append(f"Rule {rule_id} has an empty or invalid conclusion.")
        else:
            conclusions.append(conclusion)
            if conclusion not in known_profiles:
                errors.append(
                    f"Rule {rule_id} conclusion '{conclusion}' has no assertion profile."
                )

        weight = rule["weight"]
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            errors.append(f"Rule {rule_id} weight must be a number from 0 to 1.")
        elif not 0 <= weight <= 1:
            errors.append(f"Rule {rule_id} weight must be between 0 and 1.")

        rule_signatures.append((tuple(sorted(conditions)), str(conclusion)))

    duplicate_rule_ids = sorted(
        item for item, count in Counter(rule_ids).items() if count > 1
    )
    for item in duplicate_rule_ids:
        errors.append(f"Duplicate rule ID: {item}")

    duplicate_signatures = sorted(
        signature for signature, count in Counter(rule_signatures).items()
        if count > 1
    )
    for conditions, conclusion in duplicate_signatures:
        warnings.append(
            "Multiple rules share the same antecedents and conclusion: "
            f"{list(conditions)} -> {conclusion}."
        )

    declared_rules = data.get("ruleCount")
    if declared_rules is not None and declared_rules != len(rules):
        warnings.append(
            f"Declared ruleCount is {declared_rules}, but {len(rules)} rules were loaded."
        )
    declared_assertions = data.get("assertionCount")
    if declared_assertions is not None and declared_assertions != len(assertions):
        warnings.append(
            "Declared assertionCount is "
            f"{declared_assertions}, but {len(assertions)} assertions were loaded."
        )

    if not data.get("schema_version"):
        warnings.append(
            "Legacy knowledge base: schema_version is not declared. "
            "The current v1 structure was validated."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "rule_count": len(rules),
            "assertion_count": len(assertions),
            "profile_count": len(profiles),
            "unique_rule_ids": len(set(rule_ids)),
            "unique_assertion_ids": len(set(assertion_ids)),
            "unique_profile_conclusions": len(set(conclusions)),
            "known_symptom_count": len(known_symptoms),
            "error_count": len(errors),
            "warning_count": len(warnings),
        },
    }


def validate_file(path: str | Path = DEFAULT_KB_PATH) -> dict[str, Any]:
    """Load and validate a knowledge-base file."""
    return validate_knowledge_base(load_knowledge_base(path))


if __name__ == "__main__":
    report = validate_file()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["valid"] else 1)
