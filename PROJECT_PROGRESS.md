# Project Progress

## Project identity

- **Project:** Tomato Plant Disease Diagnosis Expert System
- **Developer:** Mujeeb Khan
- **Academic program:** BS Artificial Intelligence, 3rd Semester
- **Institution:** City University, Peshawar
- **Repository:** https://github.com/ullahmujeeb046-max/plantsystem
- **Deployment target:** Streamlit Community Cloud
- **Core policy:** Python, Streamlit, JSON knowledge base, free/open-source dependencies; no paid service is required.

## Current development status

| Phase | Scope | Status |
|---|---|---|
| 1 | Repository audit and architecture roadmap | Complete (audit and plan only) |
| 2 | Knowledge base engineering and validation | Complete — validator and full test workflow passed on GitHub Actions |
| 3 | Modular inference engine | In progress — modular forward/backward chaining added and integrated; CI passed |
| 4 | Natural-language processing and evidence handling | Not started |
| 5 | Consultation and response engine | Not started |
| 6 | Professional Streamlit UI | Not started |
| 7 | Knowledge base management | Not started |
| 8 | Testing, explainability, and rule analyzer | Not started |
| 9 | History, reports, and storage | Not started |
| 10 | Final audit, documentation, and deployment readiness | Not started |

A phase is not marked complete until its implementation and required verification are finished. Phase 1 is complete because it is a repository inspection and planning phase; no feature implementation is claimed here.

## Phase 1 — Repository audit

### Repository state

The repository is an existing, partially developed Python project, not an empty repository.

Current tracked implementation:

- `app.py` — Streamlit interface with symptom diagnosis and disease-information lookup.
- `main.py` — command-line interface.
- `expert_system.py` — one class currently combines knowledge-base loading, profile construction, phrase matching, forward chaining, ranking, diagnosis, and disease lookup.
- `knowledge_base/knowledge_base.json` — JSON knowledge base.
- `tests/test_expert_system.py` — six unit tests.
- `requirements.txt` — Streamlit dependency.
- `README.md`, `PROJECT_REPORT.md`, `DEMO_GUIDE.md` — existing project documentation.
- `.devcontainer/devcontainer.json` — development-container configuration.

The repository also contains committed Python bytecode cache directories/files. These are generated artifacts and should be excluded from version control in a later cleanup; they have not been deleted in this phase.

### Existing knowledge base snapshot

The current JSON file declares:

- 100 IF-THEN rules.
- 300 assertions.
- 20 diagnosis profiles (18 diseases and two physiological disorders, according to the project report).
- Five rules per diagnosis conclusion.
- Current rule fields: `id`, `name`, `if_all_symptoms`, `then_diagnosis`, `weight`, and `explanation`.
- Current assertion predicates include common name, crop, domain, five symptom fields, management, prevention, diagnosis type, host, evidence required, advisory level, and knowledge-source type.

These counts are read from the current repository data; they are not a claim that the domain knowledge has been independently validated by agricultural experts.

### Existing capabilities confirmed by source inspection

- Forward-chaining rule evaluation is implemented.
- Text normalization, symptom phrase aliases, and a limited negation check are implemented.
- Matching rules are grouped by diagnosis and ranked with a heuristic evidence score.
- Disease-information lookup is implemented in the expert-system class.
- Streamlit and CLI interfaces both use the same expert-system class.
- Tests cover knowledge-base counts, two diagnosis patterns, and three disease-information lookups.

### Gaps and risks identified

1. No centralized project configuration module exists; project identity and UI branding are currently embedded in separate files.
2. The inference engine and NLP logic are concentrated in `expert_system.py`; there is no clear separation into domain, reasoning, NLP, and application layers.
3. Backward chaining is not implemented.
4. The current rules do not declare categories, priorities, explicit fact references, recommended actions, or scenario metadata as structured fields.
5. The current rule evaluator supports positive symptom antecedents only; it does not provide general positive/negative evidence records, contradiction resolution, or uncertainty states.
6. Negation handling is phrase-based and limited; it is not a complete context-aware NLP pipeline.
7. There is no structured consultation workflow with follow-up questions, confirmation/rejection of candidate evidence, or missing-evidence tracking.
8. There is no detailed inference trace showing all evaluated rules, intermediate conclusions, and conflict-resolution decisions.
9. Knowledge-base editing, import/export validation UI, history, and report generation are not present in the inspected implementation.
10. The current test suite is small and does not cover backward chaining, contradiction handling, rule validation, or broad regression scenarios.
11. `requirements.txt` uses an open-ended Streamlit version constraint; reproducible dependency pinning should be considered after compatibility checks.
12. The repository contains tracked bytecode cache artifacts.
13. Existing documentation describes the current prototype and will need to be updated as features are implemented.

### Architecture roadmap

The implementation will preserve the existing JSON data and working diagnosis behavior while gradually separating responsibilities:

```text
config.py
  └── centralized project identity and application settings

knowledge_base/
  ├── knowledge_base.json
  └── loader.py / validator.py

core/
  ├── models.py          facts, evidence, rules, conclusions
  ├── inference.py       forward/backward chaining and conflict resolution
  ├── reasoning_trace.py explainable execution records
  └── consultation.py   evidence confirmation and follow-up workflow

nlp/
  ├── normalizer.py
  ├── phrase_matcher.py
  └── evidence_extractor.py

services/
  ├── response_builder.py
  ├── history.py
  └── report_service.py

ui/
  ├── pages / navigation
  └── reusable components

tests/
  ├── unit tests
  ├── knowledge-base validation tests
  └── consultation and regression tests

app.py                  Streamlit entry point
main.py                 optional CLI entry point
```

The exact module boundaries may be adjusted when each phase is implemented. This is a target design, not a claim that these modules already exist.

## Verification record

- Repository tree and key source files were inspected through the connected GitHub repository.
- Knowledge-base structure and declared counts were inspected.
- Automated tests were **not executed** during Phase 1 because this audit session did not provide a repository runtime for running the test suite.
- Streamlit deployment was **not tested**.
- No existing implementation files were replaced or deleted during Phase 1.

## Next phase

**Phase 2 — Knowledge Base Engineering**

Planned work:

1. Define a formal schema for facts, rules, conclusions, categories, priorities, and evidence.
2. Add a validator that reports malformed, duplicate, missing, or inconsistent references.
3. Review the existing 100 rules and 300 assertions without discarding useful data.
4. Preserve provenance/knowledge-source metadata and clearly label information that needs expert verification.
5. Add validation tests and only then migrate the knowledge base to the validated structure.


## Phase 2 — Knowledge Base Engineering (implementation in progress)

### Repository changes committed

- `knowledge_base/validator.py`: standard-library JSON loader and structural/reference validator.
- `tests/test_knowledge_base.py`: seven automated test cases for the current data and deliberately invalid knowledge-base examples.
- `knowledge_base/README.md`: current data model, field definitions, validation commands, provenance caveats, and safe extension guidance.

### Validation design

The validator checks required top-level, rule, assertion, and profile fields; duplicate rule/assertion IDs; duplicate subject/predicate facts; empty or repeated rule antecedents; unknown symptom references; missing conclusion profiles; invalid weights; and declared count mismatches. It reports errors separately from review warnings and does not mutate the JSON source.

The existing JSON knowledge base has been preserved without adding invented disease facts or changing the current 100 rules and 300 assertions. The validator explicitly treats the current data as a legacy v1 structure and warns that a schema version is not yet declared. Rule category/priority/action-reference/test-scenario semantics are deferred until they can be defined without assigning unsupported agricultural meaning.

### Static data inspection

A separate inspection of the current JSON structure found 100 rules, 300 assertions, 20 profiles, unique rule IDs, unique assertion IDs, and no missing profile predicates or rule-to-symptom/conclusion references. This was a structural inspection of repository data, not execution of the Python validator.

### Verification still required

- The Python validator and seven new unit tests have **not yet been executed** in a Python runtime.
- Existing regression tests have not been executed.
- Therefore Phase 2 remains **in progress**, not complete. Next verification should run:
  `python -m knowledge_base.validator`
  and
  `python -m unittest discover -s tests -v`.


## Phase 2 — Verification completed

A GitHub Actions workflow was added at `.github/workflows/tests.yml`. On the current repository commit, the workflow completed successfully:

- Knowledge-base validator step: success.
- Full unittest discovery step: success.
- Workflow run: https://github.com/ullahmujeeb046-max/plantsystem/actions/runs/45428309399

Phase 2 is now marked complete based on this executed CI result.

## Phase 3 — Core Inference Engine (implementation in progress)

### Implemented

- `core/inference.py`: a separate symbolic inference engine that accepts the existing IF-THEN rules and observed facts.
- Forward chaining: evaluates each rule against the supplied facts, fires only rules whose complete antecedents are present, and records per-rule matched/missing conditions.
- Backward chaining: starts from a requested diagnosis goal and inspects only rules that can conclude that goal. It reports whether observed facts prove the goal and lists missing symptom evidence instead of assuming it.
- Conflict resolution: when multiple matched rules support one conclusion, selects the highest-weight rule as the primary explanation while retaining all supporting rules. Legacy `weight` is used as the fallback priority until explicit priority metadata is designed.
- `expert_system.py` now delegates forward chaining to the modular engine while preserving its existing return format for the current diagnosis UI. A public `backward_chain(goal, observed)` method is also available.
- `tests/test_inference_engine.py`: tests for forward chaining, multiple conclusions, missing evidence traces, backward proof, unknown goals, and conflict resolution.

### Verification

GitHub Actions run https://github.com/ullahmujeeb046-max/plantsystem/actions/runs/45428309399 completed successfully. Both the knowledge-base validator and the full unittest discovery command passed after the inference engine was integrated into the existing expert system.

### Remaining Phase 3 work

- Add explicit structured rule categories and priorities after defining a compatible knowledge-base schema.
- Add more complete inference trace records and validation of inference inputs.
- Add regression scenarios using actual tomato knowledge-base cases, including ambiguous and competing diagnoses.
- Review tie-breaking and heuristic-weight semantics with the academic project requirements.

Phase 3 remains in progress until these remaining design and test tasks are addressed.
