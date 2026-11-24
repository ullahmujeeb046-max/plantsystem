# Tomato Plant Disease Diagnosis Expert System

A Python rule-based expert system prototype for diagnosing possible tomato plant diseases and selected physiological disorders from natural-language symptom descriptions.

## Assignment requirement mapping

| Requirement | Included implementation |
|---|---|
| Knowledge Base: 100 rules | `knowledge_base/knowledge_base.json` contains exactly 100 IF-THEN rules |
| Knowledge Base: 300 assertions | The same file contains exactly 300 structured assertions |
| Inference Engine | `expert_system.py` implements forward chaining |
| Natural-language interface | `main.py` accepts ordinary English descriptions and maps symptom phrases to facts |
| Expert System Shell | Python implementation with rule matching, fact storage, and explanation output |

## Requirements

- Python 3.9 or newer
- No third-party packages required

## Run

1. Extract the ZIP file.
2. Open a terminal in the extracted `plant_disease_expert_system` folder.
3. Run:

   ```bash
   python3 main.py
   ```

## Example input

```text
The lower leaves have yellowing and dark brown spots with concentric rings.
```

The system extracts known symptoms, runs the rules through forward chaining, and prints possible diagnoses with matched rule IDs, evidence scores, management suggestions, and prevention suggestions.

## Verify the knowledge base counts

Run:

```bash
python3 -c "from expert_system import TomatoExpertSystem; print(TomatoExpertSystem().validate_knowledge_base())"
```

Expected counts:
- `rule_count`: 100
- `assertion_count`: 300
- `unique_rule_ids`: 100
- `unique_assertion_ids`: 300

## Project structure

```text
plant_disease_expert_system/
├── main.py
├── expert_system.py
├── knowledge_base/
│   └── knowledge_base.json
├── tests/
│   └── test_expert_system.py
└── README.md
```

## Important limitations

- This is a teaching prototype, not a validated agricultural diagnostic product.
- The evidence score is a rule-match score, not a statistically calibrated disease probability.
- Several diseases can produce similar symptoms. A laboratory test or local agricultural expert may be needed for confirmation.
- Management advice is general. Follow local agricultural guidance and product labels; this prototype does not prescribe pesticide dosages.


## Optional Streamlit web interface

The project also includes `app.py`, a browser-based interface built with Streamlit.

Install Streamlit:

```bash
python3 -m pip install -r requirements.txt
```

Run the web app from the project folder:

```bash
streamlit run app.py
```

Streamlit opens the interface in your browser (usually at `http://localhost:8501`). The web interface imports and uses the same `TomatoExpertSystem` class and knowledge base; it does not duplicate the rules or inference engine.


## Explainability and evidence trace

The inference engine records the conditions checked for every IF-THEN rule. In the Streamlit interface, expand **Why did the system suggest this?** under a possible condition to review:
- Which rules fully matched the confirmed symptoms.
- Which observed facts supported those rules.
- Which symptom facts are still missing from related incomplete rules.
- How many rules were evaluated and fully matched.

The explanation is a trace of the system's own rule logic. It is not an independent scientific validation of the diagnosis, and a rule-match score is not a disease probability.

## Knowledge base management

The Streamlit **Manage knowledge base** service supports validated rule editing, rule creation/deletion, existing profile fact editing, and JSON import/export. Each change is validated before the active JSON file is replaced. Back up the knowledge-base JSON before making major changes. On hosting platforms with ephemeral storage, local edits may not survive a redeployment.


## Consultation history and reports

The Streamlit **History & reports** service lets users save a consultation or quick symptom check, review saved evidence and possible conditions, download an individual Markdown report, and export all saved records as JSON. Users can also delete an individual saved record.

History is stored locally in `data/consultation_history.json`. The application stores structured symptom evidence and screening results, but does not store the original free-text description. The store retains up to 500 records by default. This local-file approach is suitable for a single-user prototype; it is not multi-user database storage. On Streamlit hosting or other platforms with ephemeral storage, history may be lost when the app restarts or is redeployed. Use the JSON export to keep a separate backup.
