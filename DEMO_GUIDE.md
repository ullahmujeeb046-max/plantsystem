# Live Demonstration Guide

## Start the application

Install dependencies and start Streamlit from the repository root:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed in the terminal.

## Suggested presentation sequence

### 1. Interactive consultation
- Choose **Interactive consultation**.
- Enter: `The lower leaves have dark brown spots with concentric rings and yellowing.`
- Start the consultation.
- Show the recognized evidence and possible conditions.
- If a follow-up question appears, select Yes, No, or Unsure and submit.
- Open **Why did the system suggest this?** to show the supporting rule and missing evidence.
- Save the consultation to history.

### 2. Quick symptom check
- Choose **Quick symptom check**.
- Try one of the built-in examples or enter a new symptom description.
- Show recognized, absent, uncertain, or conflicting evidence where available.
- Explain that the evidence score is a heuristic, not a disease probability.
- Save the screening result if appropriate.

### 3. Disease information
- Choose **Ask about a disease**.
- Enter a condition name from the knowledge base.
- Show its stored symptoms, general management, and prevention information.

### 4. Knowledge-base management
- Choose **Manage knowledge base**.
- Show the rule count, assertion count, and profile count.
- Open a rule to inspect its conditions and explanation.
- Do not change production knowledge during a graded demonstration unless you have a backup.
- Explain that imports and edits are validated before saving.

### 5. History and reports
- Choose **History & reports**.
- Open the saved consultation.
- Download its Markdown report.
- Show the JSON export option.
- Explain that local files may not persist after a hosted redeployment.

## Suggested CLI demonstration

```bash
python main.py
```

Try the same example text, then type `help` or `quit`.

## Run checks before presenting

```bash
python -m knowledge_base.validator
python -m compileall -q app.py expert_system.py core nlp services
python -m unittest discover -s tests -v
```

## Key points to explain to the teacher

- The project is a **rule-based expert system**, not a trained machine-learning model.
- The knowledge base contains 100 IF-THEN rules, 300 assertions, and 20 diagnosis/disorder profiles.
- Forward chaining compares confirmed symptom facts with rule conditions.
- The interface can ask follow-up questions to collect additional evidence.
- The explanation panel shows which rules matched and which observations are missing.
- The score is a heuristic rule-evidence score, not a disease probability.
- The application is an educational screening prototype. A local agricultural specialist should confirm serious or spreading cases.

## Before a public deployment

- Confirm the latest GitHub Actions workflow passes.
- Select `app.py` as the Streamlit app entry point.
- Test all five services in the deployed browser.
- Download backups of knowledge-base edits and consultation history.
- Do not upload secrets or private user data to the repository.
