import streamlit as st

from expert_system import TomatoExpertSystem
from core.consultation import ConsultationEngine
from services.response_builder import build_consultation_response
from knowledge_base.manager import KnowledgeBaseManager

st.set_page_config(
    page_title="Tomato Plant Disease Expert",
    page_icon="🌱",
    layout="wide"
)


@st.cache_resource
def load_system():
    return TomatoExpertSystem()


system = load_system()
consultation = ConsultationEngine(system)

st.title("🌱 Tomato Plant Disease Expert System")
st.caption("An educational, rule-based tool for tomato symptom screening and disease information.")

mode = st.sidebar.radio(
    "Choose a service",
    ["Interactive consultation", "Quick symptom check", "Ask about a disease", "Manage knowledge base"]
)


def show_diagnoses(diagnosis):
    items = diagnosis.get("diagnoses", [])
    if not items:
        st.info("No complete diagnosis rule matches the confirmed symptoms yet. More observations may help.")
        return
    st.subheader("Possible conditions")
    for rank, item in enumerate(items, start=1):
        with st.container(border=True):
            st.markdown(f"**{rank}. {item['name']}**")
            if "score" in item:
                st.progress(item["score"] / 100)
                st.caption(f"Rule evidence score: {item['score']}% (heuristic, not a disease probability)")
            st.write(item.get("explanation", ""))
            st.write("**Matched rules:** " + ", ".join(item.get("matched_rules", [])))
            if item.get("management"):
                st.write("**General management:** " + item["management"])
            if item.get("prevention"):
                st.write("**Prevention:** " + item["prevention"])


def show_evidence(evidence):
    left, middle, right = st.columns(3)
    left.metric("Confirmed", len(evidence.get("positive", [])))
    middle.metric("Not observed", len(evidence.get("negative", [])))
    right.metric("Uncertain", len(evidence.get("uncertain", [])))
    if evidence.get("positive"):
        st.write("**Confirmed symptoms:** " + ", ".join(evidence["positive"]))
    if evidence.get("negative"):
        st.write("**Symptoms reported absent:** " + ", ".join(evidence["negative"]))
    if evidence.get("uncertain"):
        st.write("**Uncertain symptoms:** " + ", ".join(evidence["uncertain"]))
    if evidence.get("contradictions"):
        st.warning("Conflicting observations: " + ", ".join(evidence["contradictions"]))


if mode == "Interactive consultation":
    st.header("Step-by-step plant consultation")
    st.write("Describe what you can see. The system will identify evidence and ask a relevant follow-up question when possible.")
    with st.form("start_consultation"):
        description = st.text_area(
            "Describe your tomato plant",
            placeholder="Example: The lower leaves have dark brown spots...",
            height=120
        )
        start = st.form_submit_button("Start consultation", type="primary", use_container_width=True)
    if start:
        try:
            st.session_state["consultation_turn"] = consultation.start(description)
        except ValueError as error:
            st.warning(str(error))

    turn = st.session_state.get("consultation_turn")
    if turn:
        st.divider()
        st.subheader("Evidence collected")
        show_evidence(turn["evidence"])
        response = build_consultation_response(turn)
        st.info(response["summary"])
        show_diagnoses(turn["diagnosis"])

        if turn.get("next_question"):
            question = turn["next_question"]
            st.subheader("Follow-up question")
            st.write(question["text"])
            with st.form("answer_follow_up"):
                answer = st.radio("Choose your answer", ["Yes", "No", "Unsure"], horizontal=True)
                submitted = st.form_submit_button("Submit answer", type="primary")
            if submitted:
                st.session_state["consultation_turn"] = consultation.answer(
                    turn["session"], question["fact"], answer.lower()
                )
                st.rerun()
        else:
            st.success("No further rule-based follow-up question is available.")
        st.caption(response["disclaimer"])
        if st.button("Start a new consultation"):
            st.session_state.pop("consultation_turn", None)
            st.rerun()


elif mode == "Quick symptom check":
    st.header("Quick symptom check")
    examples = [
        "The lower leaves have dark brown spots with concentric rings and yellowing.",
        "There is a white powdery coating on the leaves and the leaves are curling.",
        "The plant suddenly wilts although the soil is moist and the roots have galls.",
        "The bottom of the tomato fruit has a dark sunken patch and soil moisture is irregular.",
        "The leaves have a mosaic pattern with light and dark green areas and distorted new growth."
    ]
    with st.expander("Try an example"):
        for i, example in enumerate(examples):
            if st.button(example, key=f"example_{i}", use_container_width=True):
                st.session_state["quick_text"] = example
    user_text = st.text_area(
        "Describe the symptoms",
        key="quick_text",
        height=130,
        placeholder="For example: My tomato plant has yellow leaves and dark brown spots..."
    )
    if st.button("Diagnose plant", type="primary", use_container_width=True):
        if not user_text.strip():
            st.warning("Please enter a description of at least one symptom.")
        else:
            try:
                st.session_state["quick_result"] = system.diagnose(user_text)
                st.session_state["quick_evidence"] = system.extract_evidence(user_text)
            except Exception as error:
                st.error(f"Could not complete screening: {error}")
    result = st.session_state.get("quick_result")
    if result:
        st.divider()
        st.subheader("Recognized symptoms")
        if result["recognized_symptoms"]:
            st.write(", ".join(result["recognized_symptoms"]))
        else:
            st.warning("No known symptom phrase was confidently recognized.")
        evidence = st.session_state.get("quick_evidence", {})
        if evidence.get("negative_facts"):
            st.write("**Reported absent:** " + ", ".join(evidence["negative_facts"]))
        if evidence.get("uncertain_facts"):
            st.write("**Uncertain:** " + ", ".join(evidence["uncertain_facts"]))
        if evidence.get("contradictions"):
            st.warning("Conflicting observations: " + ", ".join(evidence["contradictions"]))
        show_diagnoses(result)
        st.warning("Educational screening only. This is not a confirmed diagnosis. Consult an agricultural specialist for serious or spreading symptoms.")


else:
    st.header("Disease information")
    st.write("Ask about a condition included in the current knowledge base.")
    question = st.text_input(
        "Enter a disease name or question",
        placeholder="What are the symptoms of Early blight?"
    )
    if st.button("Get disease information", type="primary"):
        if not question.strip():
            st.warning("Please enter a disease name or question.")
        else:
            st.session_state["disease_information"] = system.get_disease_information(question)
    info = st.session_state.get("disease_information")
    if info:
        st.divider()
        if not info["found"]:
            st.warning("I could not find that condition in the current knowledge base.")
            st.write("**Available conditions:**")
            for name in info["available_diseases"]:
                st.write("- " + name)
        else:
            st.subheader(info["name"])
            st.write("**Common symptoms**")
            for symptom in info["symptoms"]:
                st.write("- " + symptom)
            st.write("**General management**")
            st.write(info["management"])
            st.write("**Prevention**")
            st.write(info["prevention"])
            st.warning("This is general educational information, not a confirmed diagnosis. Ask a local agricultural specialist before applying treatments.")


else:
    st.header("Knowledge base management")
    st.write("Review and maintain IF-THEN rules and profile facts. Every change is validated before it is saved.")
    manager = KnowledgeBaseManager()
    data = manager.load()
    counts = st.columns(3)
    counts[0].metric("Rules", len(data["rules"]))
    counts[1].metric("Assertions", len(data["assertions"]))
    counts[2].metric("Profiles", len({fact["subject"] for fact in data["assertions"]}))

    tab_rules, tab_facts, tab_transfer = st.tabs(["Manage rules", "Edit profile facts", "Import / export"])

    with tab_rules:
        st.subheader("Existing rules")
        rule_ids = [rule["id"] for rule in data["rules"]]
        selected_id = st.selectbox("Select a rule", rule_ids)
        selected_rule = next(rule for rule in data["rules"] if rule["id"] == selected_id)
        with st.form("edit_rule_form"):
            edit_name = st.text_input("Rule name", selected_rule["name"])
            edit_conditions = st.text_area("Required symptoms (one per line)", "\\n".join(selected_rule["if_all_symptoms"]))
            edit_conclusion = st.selectbox(
                "Diagnosis profile", sorted({fact["subject"] for fact in data["assertions"]}),
                index=sorted({fact["subject"] for fact in data["assertions"]}).index(selected_rule["then_diagnosis"])
            )
            edit_weight = st.number_input("Heuristic weight (0–1)", 0.0, 1.0, float(selected_rule["weight"]), 0.01)
            edit_priority = st.number_input("Priority (0–1)", 0.0, 1.0, float(selected_rule.get("priority", selected_rule["weight"])), 0.01)
            edit_explanation = st.text_area("Explanation", selected_rule["explanation"])
            save_rule = st.form_submit_button("Save rule changes", type="primary")
        if save_rule:
            updated = dict(selected_rule)
            updated.update({
                "name": edit_name.strip(),
                "if_all_symptoms": [line.strip() for line in edit_conditions.splitlines() if line.strip()],
                "then_diagnosis": edit_conclusion,
                "weight": edit_weight,
                "priority": edit_priority,
                "explanation": edit_explanation.strip()
            })
            try:
                manager.update_rule(selected_id, updated)
                st.success("Rule saved. The knowledge base passed validation.")
                st.cache_resource.clear()
                st.rerun()
            except (ValueError, KeyError) as error:
                st.error(str(error))

        with st.expander("Add a new rule"):
            with st.form("add_rule_form"):
                new_id = st.text_input("New rule ID (example: R101)")
                new_name = st.text_input("New rule name")
                new_conditions = st.text_area("Required symptoms (one per line)")
                profile_ids = sorted({fact["subject"] for fact in data["assertions"]})
                new_conclusion = st.selectbox("Conclusion profile", profile_ids, key="new_rule_profile")
                new_weight = st.number_input("Heuristic weight", 0.0, 1.0, 0.7, 0.01, key="new_rule_weight")
                new_priority = st.number_input("Priority", 0.0, 1.0, 0.7, 0.01, key="new_rule_priority")
                new_explanation = st.text_area("Explanation", key="new_rule_explanation")
                add_rule = st.form_submit_button("Add rule")
            if add_rule:
                new_rule = {
                    "id": new_id.strip(), "name": new_name.strip(),
                    "if_all_symptoms": [line.strip() for line in new_conditions.splitlines() if line.strip()],
                    "then_diagnosis": new_conclusion, "weight": new_weight,
                    "priority": new_priority, "category": "symptom_pattern",
                    "explanation": new_explanation.strip()
                }
                try:
                    manager.add_rule(new_rule)
                    st.success("New rule added and validated.")
                    st.cache_resource.clear()
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

        with st.expander("Delete selected rule"):
            st.warning("Deleting a rule changes which symptom patterns the system can recognize.")
            confirm_delete = st.checkbox("I understand and want to delete " + selected_id, key="confirm_delete_rule")
            if st.button("Delete rule", disabled=not confirm_delete):
                try:
                    manager.delete_rule(selected_id)
                    st.success("Rule deleted. Remaining knowledge base is valid.")
                    st.cache_resource.clear()
                    st.rerun()
                except (ValueError, KeyError) as error:
                    st.error(str(error))

    with tab_facts:
        st.subheader("Edit disease / disorder profile facts")
        subjects = sorted({fact["subject"] for fact in data["assertions"]})
        selected_subject = st.selectbox("Select a profile", subjects)
        profile_facts = [fact for fact in data["assertions"] if fact["subject"] == selected_subject]
        selected_fact_id = st.selectbox(
            "Select a profile field",
            [fact["id"] for fact in profile_facts],
            format_func=lambda fact_id: next(
                fact["predicate"] for fact in profile_facts if fact["id"] == fact_id
            )
        )
        selected_fact = next(fact for fact in profile_facts if fact["id"] == selected_fact_id)
        st.caption("Subject: " + selected_fact["subject"] + " · Field: " + selected_fact["predicate"])
        with st.form("edit_profile_fact"):
            fact_value = st.text_area("Value", str(selected_fact["value"]))
            save_fact = st.form_submit_button("Save profile field", type="primary")
        if save_fact:
            try:
                manager.update_assertion(selected_fact_id, fact_value)
                st.success("Profile field updated and knowledge base validated.")
                st.cache_resource.clear()
                st.rerun()
            except (ValueError, KeyError) as error:
                st.error(str(error))

    with tab_transfer:
        st.subheader("Export knowledge base")
        st.download_button(
            "Download knowledge_base.json",
            data=manager.export_json(),
            file_name="knowledge_base.json",
            mime="application/json"
        )
        st.divider()
        st.subheader("Import a knowledge base")
        st.caption("Only a complete JSON file that passes all structural and reference checks can replace the current data.")
        uploaded = st.file_uploader("Choose a JSON knowledge-base file", type=["json"])
        if uploaded is not None:
            if st.button("Validate and import JSON", type="primary"):
                try:
                    raw = uploaded.getvalue().decode("utf-8")
                    report = manager.import_json(raw)
                    st.success("Import successful. The new knowledge base passed validation.")
                    st.json(report["summary"])
                    st.cache_resource.clear()
                    st.rerun()
                except (UnicodeDecodeError, ValueError) as error:
                    st.error(str(error))
        current_report = manager.validate(data)
        if current_report["warnings"]:
            st.warning("Review warnings: " + " ".join(current_report["warnings"][:5]))


with st.sidebar:
    st.divider()
    st.subheader("Knowledge base")
    counts = system.validate_knowledge_base()
    st.metric("IF-THEN rules", counts["rule_count"])
    st.metric("Assertions / facts", counts["assertion_count"])
    st.caption("Crop covered: Tomato")
    st.caption("Student expert-system prototype")
