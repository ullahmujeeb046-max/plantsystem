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
| 3 | Modular inference engine | Complete — chaining, priority/category metadata, input validation, traces, regression tests, and CI passed |
| 4 | Natural-language processing and evidence handling | Complete — phrase extraction, negation, uncertainty, contradiction handling, integration, tests, and CI passed |
| 5 | Consultation and response engine | Complete — interactive evidence collection, follow-up questions, response builder, tests, and CI passed |
| 6 | Professional Streamlit UI | In progress — interactive consultation, quick symptom check, and disease-information pages implemented; CI verification pending |
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


## Phase 3 — Core Inference Engine (completed)

### Additional implementation

- Added explicit `category: "symptom_pattern"` and `priority` metadata to all 100 existing rules. Priority values retain the existing heuristic weight values; this does not reinterpret them as probabilities or expert-validated clinical confidence.
- Extended the knowledge-base validator to validate optional category and priority fields and their allowed value types/ranges.
- Strengthened inference input validation: a single string is not accepted as an iterable of facts; empty/non-string facts and blank backward goals are rejected with clear errors.
- Expanded the forward trace to include rule category, priority, explanation, matched conditions, missing conditions, and total evaluated rule count.
- Expanded backward-chain proof records with category and evaluated-rule count.
- Added regression coverage using the actual repository knowledge base for the Early blight pattern, plus tests for metadata, invalid input, explicit priority behavior, and trace details.

### Verification

GitHub Actions run https://github.com/ullahmujeeb046-max/plantsystem/actions/runs/45428753249 completed successfully:

- Knowledge-base validator: success.
- Full unittest discovery: success.

Phase 3 is marked complete based on the successful CI run.

### Known scope boundary

The current backward-chaining implementation is goal-directed over direct symptom-to-diagnosis rules. It does not yet recursively prove intermediate facts because the existing tomato knowledge base contains direct symptom antecedents and diagnosis conclusions rather than a multi-level fact dependency graph. Contradictory positive/negative evidence is also deferred to the NLP/evidence phases. Conflict resolution selects a primary supporting rule per conclusion; it does not choose one diagnosis over another when separate diagnoses both have matching rules.


## Phase 4 — Natural Language Processing and Evidence Handling (implementation in progress)

### Implemented

- `nlp/normalizer.py`: Unicode normalization, lowercase/punctuation cleanup, whitespace normalization, and tokenization.
- `nlp/evidence_extractor.py`: transparent phrase-dictionary matching with word boundaries and longest-phrase-first matching.
- Evidence is separated into positive, negative, uncertain, and contradictory mentions. Only confirmed positive facts are passed into the existing diagnosis inference path.
- Negation patterns include phrases such as "no", "not", "without", "does not", and common contractions.
- Uncertainty cues such as "maybe", "possibly", "might", and "unsure" prevent a mention from being treated as confirmed.
- Unknown phrases do not create new facts.
- `expert_system.py` delegates symptom extraction to the new NLP module and preserves the existing `extract_symptoms()` set-returning interface for compatibility.
- `tests/test_nlp.py`: tests normalization, tokenization, positive phrase extraction, negation, uncertainty, contradiction detection, unknown input, and integration with the expert-system wrapper.

### Limitations

This is lightweight dictionary-based NLP, not unrestricted natural-language understanding. It recognizes only phrases in the symptom dictionary and a limited set of English negation/uncertainty constructions. Negation scope is local and may misread complex sentences or multiple clauses. It does not yet ask follow-up questions; that belongs to the consultation phase.

### Verification status

GitHub Actions run https://github.com/ullahmujeeb046-max/plantsystem/actions/runs/45429118207 was triggered by the NLP test commit. At the time of this update, the run is still in progress. Phase 4 is therefore not complete until the workflow finishes successfully and any failures are fixed.

### Phase 4 — Verification completed

GitHub Actions run https://github.com/ullahmujeeb046-max/plantsystem/actions/runs/45429118207 completed successfully after the NLP test suite was committed. The workflow's knowledge-base validation and full unittest discovery steps passed. Phase 4 is marked complete based on this CI result.

## Phase 5 — Consultation and Response Engine (implementation in progress)

### Implemented

- `core/consultation.py`: starts a consultation from a symptom description, stores positive/negative/uncertain/contradictory evidence, and selects a follow-up symptom question from partially matched knowledge-base rules.
- Follow-up answers accept yes, no, or unsure. A negative or unsure answer is not treated as confirmed positive evidence.
- Each consultation turn returns current evidence, the current rule-based screening results, the next question, and a completion flag.
- `services/response_builder.py`: creates a plain-language summary, lists evidence states, reports possible conditions, and includes a safety disclaimer.
- `tests/test_consultation.py`: covers starting a consultation, follow-up answers, invalid input, and response summaries.

### Limitations

The consultation currently selects follow-up questions from rules that already have at least one confirmed matching symptom. It does not yet maintain persistent sessions, provide a multi-user web chat, or use a trained language model. If there are no partially matched rules, it stops asking questions and reports that the current evidence is insufficient. The response builder summarizes rule results and does not independently validate agricultural advice.

### Verification status

GitHub Actions run https://github.com/ullahmujeeb046-max/plantsystem/actions/runs/45429920128 was triggered by the consultation tests. Phase 5 remains in progress until the workflow completes successfully.

### Phase 5 — Verification completed

GitHub Actions run https://github.com/ullahmujeeb046-max/plantsystem/actions/runs/45429920128 completed successfully. The knowledge-base validation and full unittest discovery steps passed. Phase 5 is marked complete based on this CI result.

## Phase 6 — Professional Streamlit UI (implementation in progress)

### Implemented

- Reworked `app.py` into a wide, three-service interface:
  1. Interactive consultation with follow-up questions and Yes/No/Unsure answers.
  2. Quick symptom check with example descriptions and evidence-state display.
  3. Disease information lookup from the existing knowledge base.
- Added reusable display helpers for evidence and possible diagnoses.
- Added sidebar knowledge-base counts and clearer educational disclaimers.
- Connected the consultation UI to `ConsultationEngine` and `build_consultation_response`.
- Added `diagnose_from_facts()` to `expert_system.py` so confirmed evidence collected across follow-up turns can be evaluated directly, without reparsing the original description.
- Added `tests/test_diagnose_from_facts.py`.
- Extended GitHub Actions with a Python compile check for the application, core, NLP, and service modules.

### Limitations

The UI has been implemented in source code but has not been manually launched in a browser or visually reviewed in Streamlit Community Cloud. Session state is local to the active Streamlit session; persistent consultation history is not part of this phase. The application remains an educational screening prototype, not a confirmed agricultural diagnosis.

### Verification status

The latest GitHub Actions workflow was triggered by the UI and compile-check changes. Phase 6 remains in progress until the latest workflow completes successfully.
