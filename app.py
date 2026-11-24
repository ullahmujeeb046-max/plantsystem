import streamlit as st
from expert_system import TomatoExpertSystem

st.set_page_config(
    page_title="Tomato Plant Disease Expert",
    page_icon="🌱",
    layout="centered"
)

@st.cache_resource
def load_system():
    return TomatoExpertSystem()

system = load_system()

st.title("🌱 Tomato Plant Disease Diagnosis")
st.caption("A rule-based expert system for educational symptom screening")

st.info(
    "Describe the visible symptoms of your tomato plant in ordinary English. "
    "The system will identify symptom facts and apply its 100 IF-THEN rules."
)

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
            st.session_state["symptom_text"] = example

user_text = st.text_area(
    "Describe your plant's symptoms",
    key="symptom_text",
    height=130,
    placeholder="For example: My tomato plant has yellow leaves and dark brown spots..."
)

if st.button("🔍 Diagnose plant", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("Please enter a description of at least one symptom.")
    else:
        result = system.diagnose(user_text)
        st.session_state["diagnosis_result"] = result

result = st.session_state.get("diagnosis_result")

if result is not None:
    st.divider()
    st.subheader("Diagnosis results")

    if not result["recognized_symptoms"]:
        st.warning(
            "I could not confidently recognize a symptom. Try describing signs "
            "such as spots, yellowing, wilting, mold, curling, or root galls."
        )
    else:
        st.markdown("**Recognized symptoms**")
        for symptom in result["recognized_symptoms"]:
            st.write(f"- {symptom}")

        st.caption(f"Forward chaining: {result['fired_rule_count']} rule(s) fired.")

        if not result["diagnoses"]:
            st.warning(
                "No diagnosis rule was fully matched. Please add more symptom details. "
                "This does not mean the plant is healthy."
            )
        else:
            for rank, diagnosis in enumerate(result["diagnoses"], start=1):
                with st.container(border=True):
                    st.markdown(f"### {rank}. {diagnosis['name']}")
                    st.progress(diagnosis["score"] / 100)
                    st.caption(
                        f"Rule evidence score: {diagnosis['score']}% "
                        "(heuristic score, not a disease probability)"
                    )
                    st.write(diagnosis["explanation"])
                    st.markdown("**Matched rules:** " + ", ".join(diagnosis["matched_rules"]))
                    st.markdown("**General management**")
                    st.write(diagnosis["management"])
                    st.markdown("**Prevention**")
                    st.write(diagnosis["prevention"])

        st.warning(
            "Educational prototype only: symptoms can overlap between diseases. "
            "This is not a confirmed diagnosis. Consult a local agricultural "
            "extension specialist for serious or spreading symptoms."
        )

with st.sidebar:
    st.header("About this system")
    st.write("**Knowledge base**")
    counts = system.validate_knowledge_base()
    st.metric("IF-THEN rules", counts["rule_count"])
    st.metric("Assertions / facts", counts["assertion_count"])
    st.write("**Inference method**")
    st.write("Forward chaining")
    st.write("**Crop covered**")
    st.write("Tomato")
    st.divider()
    st.caption("Student expert-system prototype")

