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


def get_disease_information(system, user_text):
    """
    Compatibility-safe disease lookup.
    Uses the class method when available; otherwise reads the loaded profiles.
    """
    lookup = getattr(system, "get_disease_information", None)
    if callable(lookup):
        return lookup(user_text)

    import re

    normalize = lambda value: re.sub(
        r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", str(value).lower().replace("-", " "))
    ).strip()
    text = normalize(user_text)

    for pid, profile in system.profiles.items():
        common_name = profile.get("has_common_name", "")
        profile_id = normalize(pid.replace("_", " "))
        name = normalize(common_name)
        if (name and name in text) or (profile_id and profile_id in text):
            return {
                "found": True,
                "id": pid,
                "name": common_name or pid.replace("_", " ").title(),
                "symptoms": [
                    profile.get(f"symptom_{i}")
                    for i in range(1, 6)
                    if profile.get(f"symptom_{i}")
                ],
                "management": profile.get(
                    "management", "No management advice is available in the knowledge base."
                ),
                "prevention": profile.get(
                    "prevention", "No prevention advice is available in the knowledge base."
                ),
            }

    available = sorted(
        profile.get("has_common_name", pid.replace("_", " ").title())
        for pid, profile in system.profiles.items()
    )
    return {"found": False, "requested": user_text, "available_diseases": available}


system = load_system()

st.title("🌱 Tomato Plant Disease Expert System")
st.caption("A rule-based educational tool for tomato disease information and symptom screening")

mode = st.radio(
    "Choose what you want to do",
    ["Diagnose from symptoms", "Ask about a disease"],
    horizontal=True
)

if mode == "Diagnose from symptoms":
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
            try:
                st.session_state["diagnosis_result"] = system.diagnose(user_text)
            except Exception as error:
                st.error(f"Could not complete diagnosis: {error}")

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

            st.caption(f"Matched rules: {result['fired_rule_count']}")

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

else:
    st.info(
        "Ask about a disease already included in the knowledge base. "
        "For example: What is Early blight? or How can I prevent Powdery mildew?"
    )
    question = st.text_input(
        "Enter your disease question",
        placeholder="What are the symptoms of Early blight?"
    )

    if st.button("📘 Get disease information", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a disease name or question.")
        else:
            try:
                st.session_state["disease_information"] = get_disease_information(
                    system, question
                )
            except Exception as error:
                st.error(f"Could not load disease information: {error}")

    info = st.session_state.get("disease_information")
    if info is not None:
        st.divider()
        if not info["found"]:
            st.warning("I could not find that disease in the current knowledge base.")
            st.markdown("**Conditions currently available:**")
            for name in info["available_diseases"]:
                st.write(f"- {name}")
        else:
            st.subheader(info["name"])
            st.markdown("**Common symptoms**")
            for symptom in info["symptoms"]:
                st.write(f"- {symptom}")
            st.markdown("**General management**")
            st.write(info["management"])
            st.markdown("**Prevention**")
            st.write(info["prevention"])
            st.warning(
                "This information comes from the project's knowledge base. "
                "It is general educational guidance, not a confirmed diagnosis. "
                "Ask a local agricultural specialist before applying treatments."
            )

with st.sidebar:
    st.header("About this system")
    counts = system.validate_knowledge_base()
    st.metric("IF-THEN rules", counts["rule_count"])
    st.metric("Assertions / facts", counts["assertion_count"])
    st.write("**Methods**")
    st.write("Rule-based symptom matching")
    st.write("Disease information lookup")
    st.write("**Crop covered**")
    st.write("Tomato")
    st.divider()
    st.caption("Student expert-system prototype")
