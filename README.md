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
