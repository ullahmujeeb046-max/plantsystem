# Knowledge Base Structure and Validation

## Current data

The project retains its original JSON knowledge base:

- 100 IF-THEN rules.
- 300 structured assertions.
- 20 diagnosis/disorder profiles.
- Five rule patterns per conclusion in the current dataset.

The data is a curated educational prototype. Its counts and structural validity do not establish independent agricultural or clinical validation.

## Current JSON structure (v1 / legacy)

Top-level fields:

- `project`: project name.
- `scope`: domain description.
- `rules`: production rules.
- `assertions`: profile facts.

Each rule requires:

| Field | Meaning |
|---|---|
| `id` | Unique rule identifier |
| `name` | Human-readable rule name |
| `if_all_symptoms` | List of symptom facts required together |
| `then_diagnosis` | Profile identifier concluded when all conditions match |
| `weight` | Existing heuristic score between 0 and 1; not a probability |
| `explanation` | Human-readable reason attached to the rule |

Each assertion requires `id`, `subject`, `predicate`, and `value`. A subject groups facts for one diagnosis/disorder profile. The current profiles provide common name, crop/domain, five symptom descriptions, management, prevention, diagnosis type, host, evidence requirement, advisory level, and knowledge-source type.

## Validation

Run from the repository root:

```bash
python -m knowledge_base.validator
python -m unittest discover -s tests -v
```

The validator uses only the Python standard library. It checks required fields, duplicate IDs and profile facts, missing profile predicates, empty rule conditions, unknown symptom references, missing conclusion profiles, invalid weights, and declared-count mismatches.

Errors make the report invalid and the validator exits with status 1. Warnings identify issues needing review, such as duplicate rule signatures or legacy data without a declared schema version.

## Knowledge quality and provenance

The existing `knowledge_source_type` assertion is retained. It currently identifies the content as curated prototype knowledge. This label is not a citation and does not prove that each rule has been reviewed by a plant pathologist. Do not treat the rule weight as disease probability or the management text as a pesticide prescription.

## Safe extension policy

When adding a rule:

1. Assign a unique rule ID.
2. Use symptom strings already represented by profile symptom assertions.
3. Point the conclusion to an existing profile.
4. Provide a non-empty explanation.
5. Keep the numeric weight within 0–1 and document its heuristic meaning.
6. Run the validator and automated tests before using the changed knowledge base.

Do not add unsupported disease claims merely to increase rule counts. A future schema migration can introduce structured rule categories, explicit priorities, action references, test scenarios, and provenance records after those semantics are defined and reviewed.
