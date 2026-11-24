import streamlit as st

from expert_system import TomatoExpertSystem
from core.consultation import ConsultationEngine
from services.response_builder import build_consultation_response

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
    ["Interactive consultation", "Quick symptom check", "Ask about a disease"]
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


with st.sidebar:
    st.divider()
    st.subheader("Knowledge base")
    counts = system.validate_knowledge_base()
    st.metric("IF-THEN rules", counts["rule_count"])
    st.metric("Assertions / facts", counts["assertion_count"])
    st.caption("Crop covered: Tomato")
    st.caption("Student expert-system prototype")
