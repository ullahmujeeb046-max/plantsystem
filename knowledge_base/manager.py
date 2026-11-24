"""Safe editing and import/export helpers for the JSON knowledge base."""
from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path

from knowledge_base.validator import load_knowledge_base, validate_knowledge_base


DEFAULT_PATH = Path(__file__).with_name("knowledge_base.json")


class KnowledgeBaseManager:
    """Validate every proposed change before replacing the active JSON file."""

    def __init__(self, path=DEFAULT_PATH):
        self.path = Path(path)

    def load(self):
        return load_knowledge_base(self.path)

    def validate(self, data):
        return validate_knowledge_base(data)

    def _commit(self, data):
        report = self.validate(data)
        if not report["valid"]:
            raise ValueError("Knowledge base was not saved: " + "; ".join(report["errors"][:8]))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=self.path.parent,
            prefix=self.path.name + ".", suffix=".tmp", delete=False
        )
        try:
            with handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            os.replace(handle.name, self.path)
        except Exception:
            try:
                os.unlink(handle.name)
            except OSError:
                pass
            raise
        return report

    def add_rule(self, rule):
        data = self.load()
        if any(item["id"] == rule.get("id") for item in data["rules"]):
            raise ValueError("A rule with this ID already exists.")
        data["rules"].append(copy.deepcopy(rule))
        return self._commit(data)

    def update_rule(self, rule_id, replacement):
        data = self.load()
        for index, rule in enumerate(data["rules"]):
            if rule["id"] == rule_id:
                if replacement.get("id") != rule_id:
                    raise ValueError("Rule IDs cannot be changed during editing.")
                data["rules"][index] = copy.deepcopy(replacement)
                return self._commit(data)
        raise KeyError(f"Rule not found: {rule_id}")

    def delete_rule(self, rule_id):
        data = self.load()
        updated = [rule for rule in data["rules"] if rule["id"] != rule_id]
        if len(updated) == len(data["rules"]):
            raise KeyError(f"Rule not found: {rule_id}")
        data["rules"] = updated
        return self._commit(data)

    def update_assertion(self, assertion_id, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Assertion value cannot be empty.")
        data = self.load()
        for fact in data["assertions"]:
            if fact["id"] == assertion_id:
                fact["value"] = value.strip()
                return self._commit(data)
        raise KeyError(f"Assertion not found: {assertion_id}")

    def import_json(self, raw_text):
        try:
            candidate = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON: {exc.msg} (line {exc.lineno}).") from exc
        if not isinstance(candidate, dict):
            raise ValueError("Imported knowledge base must be a JSON object.")
        return self._commit(candidate)

    def export_json(self):
        return json.dumps(self.load(), indent=2, ensure_ascii=False) + "\n"
