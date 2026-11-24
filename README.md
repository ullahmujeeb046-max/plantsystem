# Tomato Plant Disease Diagnosis Expert System

A Python and Streamlit rule-based expert system prototype for screening possible tomato plant diseases and selected physiological disorders from natural-language symptom descriptions.

**Academic project:** BS Artificial Intelligence, 3rd Semester  
**Institution:** City University, Peshawar  
**Knowledge base:** 100 IF-THEN rules, 300 structured assertions, 20 diagnosis/disorder profiles

> This is an educational screening prototype, not a confirmed agricultural diagnosis. The knowledge base has not been independently validated by agricultural experts. Similar symptoms can have different causes; consult a local agricultural specialist for serious or spreading problems.

## Features

- **Interactive consultation:** collect observations and answer follow-up questions with Yes, No, or Unsure.
- **Quick symptom check:** submit an English description and review possible rule matches.
- **Disease information:** view symptoms, general management, and prevention information stored in the knowledge base.
- **Explainable inference:** inspect supporting rules, matched observations, and missing evidence.
- **Knowledge-base management:** add/edit/delete rules, edit existing profile facts, and validate JSON imports before saving.
- **History and reports:** explicitly save structured consultation results, review/delete records, download Markdown reports, and export JSON backups.
- **Command-line interface:** run a basic symptom-screening session without Streamlit.

## Requirements

- Python 3.9 or newer (CI is tested on Python 3.11).
- Dependencies listed in `requirements.txt`.
- No paid API, cloud AI model, or external database is required.

## Run locally

From the repository root:

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies and start Streamlit:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local address printed in the terminal (normally `http://localhost:8501`).

To run the command-line version:

```bash
python main.py
```

## Example input

```text
The lower leaves have yellowing and dark brown spots with concentric rings.
```

The system maps recognized phrases to canonical symptom facts, evaluates IF-THEN rules, and lists possible matching conditions. A rule-evidence score is a heuristic score, not a disease probability.

## Project structure

```text
plantsystem/
├── .github/workflows/tests.yml
├── .streamlit/config.toml
├── core/
│   ├── consultation.py
│   └── inference.py
├── knowledge_base/
│   ├── knowledge_base.json
│   ├── manager.py
│   └── validator.py
├── nlp/
│   ├── evidence_extractor.py
│   └── normalizer.py
├── services/
│   ├── explainability.py
│   ├── history_store.py
│   └── response_builder.py
├── tests/
├── app.py
├── expert_system.py
├── main.py
├── requirements.txt
└── README.md
```

## Knowledge base validation

Run from the repository root:

```bash
python -m knowledge_base.validator
```

The validator checks required fields, duplicate identifiers, profile facts, rule antecedents, conclusion references, and heuristic weight ranges. It reports structural validity; it does not verify agricultural correctness.

To inspect the knowledge-base format and safe editing guidance, see [knowledge_base/README.md](knowledge_base/README.md).

## Automated tests

```bash
python -m unittest discover -s tests -v
```

The GitHub Actions workflow installs the application requirements, validates the knowledge base, compiles the Python modules, and runs the unit tests including a Streamlit startup smoke test.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub and ensure the default branch contains the latest passing CI run.
2. Sign in to Streamlit Community Cloud and create a new app from this repository.
3. Select the repository, branch (normally `main`), and main file path `app.py`.
4. Deploy. The platform installs packages from the root `requirements.txt`.
5. Open the deployed app and manually check all five services: consultation, quick check, disease information, knowledge-base management, and history/reports.
6. If you change the knowledge base or application code, rerun the tests and review the deployed app again.

No secrets are required for the current feature set. Never commit passwords, API keys, private credentials, or `.streamlit/secrets.toml`.

### Important hosting limitation

Consultation history and knowledge-base edits are written to local JSON files. Streamlit hosting filesystems may be reset or replaced during redeployment, and this project does not currently use persistent database storage. Download JSON backups before redeploying if you need to preserve changes. The current history store is a single-user prototype, not a secure multi-user records system.

## Safety, accuracy, and limitations

- Phrase-based English NLP recognizes only known phrases and limited negation/uncertainty patterns; it is not general language understanding.
- Backward chaining is limited to direct rule goals; the main diagnosis flow uses forward chaining.
- Rule weights and displayed evidence scores are heuristic values, not calibrated probabilities.
- A matched rule is not proof that a plant has a disease.
- Agricultural management text is general educational information. Follow local agricultural guidance and product labels; the app does not prescribe pesticide dosages.
- No independent field/laboratory dataset or expert-reviewed benchmark is currently included, so no diagnostic accuracy percentage is claimed.
- Browser-based testing on the deployed hosting platform remains a manual deployment check.

## Development status

See [PROJECT_PROGRESS.md](PROJECT_PROGRESS.md) for the phase-by-phase implementation and verification record.
