"""Local JSON storage and report generation for consultation history.

Only structured observations and screening results are stored. Free-text plant
descriptions are deliberately excluded by default.
"""
from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "consultation_history.json"


class HistoryStore:
    def __init__(self, path=DEFAULT_PATH, max_records=500):
        self.path = Path(path)
        self.max_records = max_records

    def _read(self):
        if not self.path.exists():
            return []
        try:
            records = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot read consultation history: {exc}") from exc
        if not isinstance(records, list) or any(not isinstance(x, dict) for x in records):
            raise ValueError("Consultation history file has an invalid structure.")
        return records

    def list_records(self):
        return sorted(self._read(), key=lambda row: row.get("updated_at", ""), reverse=True)

    def get(self, record_id):
        for record in self._read():
            if record.get("id") == record_id:
                return record
        raise KeyError(f"History record not found: {record_id}")

    def save_turn(self, turn, record_id=None):
        if not isinstance(turn, dict) or not isinstance(turn.get("evidence"), dict):
            raise ValueError("A valid consultation result is required.")
        evidence = turn["evidence"]
        diagnosis = turn.get("diagnosis", {})
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "id": record_id or str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            "status": "complete" if turn.get("complete") else "in_progress",
            "evidence": {
                key: sorted(set(evidence.get(key, [])))
                for key in ("positive", "negative", "uncertain", "contradictions")
            },
            "diagnoses": [
                {
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "score": item.get("score"),
                    "matched_rules": item.get("matched_rules", []),
                    "explanation": item.get("explanation", ""),
                    "management": item.get("management", ""),
                    "prevention": item.get("prevention", "")
                }
                for item in diagnosis.get("diagnoses", [])
            ],
            "follow_up_question": (turn.get("next_question") or {}).get("text", ""),
            "disclaimer": "Educational screening only; not a confirmed diagnosis."
        }
        records = self._read()
        existing = next((row for row in records if row.get("id") == record["id"]), None)
        if existing:
            record["created_at"] = existing.get("created_at", now)
            records = [row for row in records if row.get("id") != record["id"]]
        records.append(record)
        records = records[-self.max_records:]
        self._write(records)
        return record

    def delete(self, record_id):
        records = self._read()
        updated = [row for row in records if row.get("id") != record_id]
        if len(updated) == len(records):
            raise KeyError(f"History record not found: {record_id}")
        self._write(updated)

    def export_json(self):
        return json.dumps(self.list_records(), indent=2, ensure_ascii=False) + "\n"

    def _write(self, records):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=self.path.parent,
            prefix=self.path.name + ".", suffix=".tmp", delete=False
        )
        try:
            with handle:
                json.dump(records, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            os.replace(handle.name, self.path)
        except Exception:
            try:
                os.unlink(handle.name)
            except OSError:
                pass
            raise


def build_markdown_report(record):
    """Create a portable plain-Markdown report from a saved record."""
    lines = [
        "# Tomato Plant Screening Report",
        "",
        f"- Report ID: {record.get('id', '')}",
        f"- Created (UTC): {record.get('created_at', '')}",
        f"- Status: {record.get('status', '')}",
        "",
        "## Observed evidence",
    ]
    evidence = record.get("evidence", {})
    for key, label in (
        ("positive", "Confirmed observations"),
        ("negative", "Reported absent"),
        ("uncertain", "Uncertain observations"),
        ("contradictions", "Conflicting observations"),
    ):
        lines.append(f"### {label}")
        values = evidence.get(key, [])
        lines.extend([f"- {value}" for value in values] if values else ["- None recorded"])
        lines.append("")
    lines.append("## Possible conditions")
    diagnoses = record.get("diagnoses", [])
    if not diagnoses:
        lines.append("- No complete rule-based match recorded.")
    for item in diagnoses:
        lines.append(f"### {item.get('name', 'Unspecified condition')}")
        if item.get("score") is not None:
            lines.append(f"- Rule evidence score: {item['score']} (not a disease probability)")
        lines.append(f"- Matched rules: {', '.join(item.get('matched_rules', [])) or 'None listed'}")
        if item.get("explanation"):
            lines.append(f"- Explanation: {item['explanation']}")
        if item.get("management"):
            lines.append(f"- General management: {item['management']}")
        if item.get("prevention"):
            lines.append(f"- Prevention: {item['prevention']}")
        lines.append("")
    if record.get("follow_up_question"):
        lines.extend(["## Follow-up question", record["follow_up_question"], ""])
    lines.extend([
        "## Important note",
        record.get("disclaimer", "Educational screening only; not a confirmed diagnosis."),
        "Consult a local agricultural specialist for serious or spreading symptoms.",
        "",
    ])
    return "\n".join(lines)
