import streamlit as st
import time

from src.config import (
    GENDER_OPTIONS,
    COMMON_SYMPTOMS,
    DURATION_OPTIONS,
    LANGUAGE_OPTIONS,
    DISCLAIMER_TEXT,
    DEFAULT_MODEL
)
from src.cache_manager import configure_cache
from src.chains import run_assessment_chain, stream_narrative, demo_direct_messages
from src.utils import parse_llm_json

st.set_page_config(
    page_title="MediGuide AI",
    page_icon="🩺",
    layout="wide"
)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("🩺 MediGuide AI")
    st.caption("AI-Powered Medical Symptom Assessment Assistant")
    
    st.divider()
    st.subheader("🔑 OpenAI API Key")
    # Kono pre-filled key thakbe na, user nijer key enter korbe
    user_api_key = st.text_input(
        "Enter your OpenAI API Key",
        type="password",
        placeholder="sk-proj-...",
        help="App use korar jonno obosshoi valid OpenAI API key lagbe."
    )
    
    if not user_api_key:
        st.warning("⚠️ Proceed korte apnar API key enter korun.")
    else:
        st.success("API Key prottashito hoyeche!")

    st.subheader("⚙️ Configuration")
    st.text_input("Active Model", value=DEFAULT_MODEL, disabled=True)
    
    cache_selection = st.radio(
        "LLM Cache Type",
        options=["InMemoryCache", "SQLiteCache"]
    )
    cache_status_msg = configure_cache(cache_type=cache_selection)
    st.info(cache_status_msg)
    
    selected_language = st.selectbox("Response Language", options=LANGUAGE_OPTIONS, index=0)
    
    st.divider()
    st.warning(f"⚠️ **MEDICAL DISCLAIMER**\n\n{DISCLAIMER_TEXT}")

    st.divider()
    with st.expander("🛠️ LangChain Direct Messages Demo"):
        st.caption("Testing System / Human / AI Message classes")
        if st.button("Run Message Demo"):
            if not user_api_key.strip():
                st.error("Prothome sidebar-e valid API key enter korun.")
            else:
                demo_res = demo_direct_messages(
                    system_text="You are a medical chatbot explaining triage rules in 1 line.",
                    human_text="What does high fever with stiff neck mean?",
                    api_key=user_api_key.strip()
                )
                st.write("**System:**", demo_res["system"])
                st.write("**Human:**", demo_res["human"])
                st.write("**AI:**", demo_res["ai"])

# ----------------- MAIN SCREEN -----------------
st.title("Patient Symptom Assessment")
st.write(
    "Ei application-ti shudhu shikkhamulok uddeshe toiri. Eta kono daktar ba medical diagnosis-er bikolpo noy."
)

with st.form("patient_assessment_form"):
    st.subheader("📋 Patient Details & Symptoms")
    
    col1, col2 = st.columns(2)
    with col1:
        age_input = st.text_input("Patient Age", placeholder="e.g. 28")
        gender_input = st.selectbox("Gender", options=GENDER_OPTIONS)
        duration_input = st.selectbox("Duration of Symptoms", options=DURATION_OPTIONS)
    
    with col2:
        selected_symptoms = st.multiselect("Select Primary Symptoms", options=COMMON_SYMPTOMS)
        custom_symptoms = st.text_input("Other Symptoms (optional free-text)", placeholder="e.g. slight chills, sneezing")
        severity_val = st.slider("Severity Level (1 = Very Mild, 10 = Severe/Unbearable)", min_value=1, max_value=10, value=3)

    st.subheader("📝 Medical Context")
    existing_cond = st.text_area("Existing Medical Conditions", placeholder="e.g. Asthma, Diabetes, Hypertension, None")
    medications = st.text_area("Current Medications", placeholder="e.g. Inhaler, Metformin, None")
    notes = st.text_area("Additional Notes / Context", placeholder="e.g. Recent travel, family history, etc.")

    submit_button = st.form_submit_button("Assess Symptoms", use_container_width=True)

# ----------------- SUBMISSION HANDLING -----------------
if submit_button:
    # 1. API key check
    if not user_api_key.strip():
        st.error("❌ OpenAI API Key deoya hoyni! Barah-e-karam sidebar theke apnar nijer OpenAI API key enter korun.")
        st.stop()

    # 2. Symptoms check
    all_symptoms = list(selected_symptoms)
    if custom_symptoms.strip():
        all_symptoms.append(custom_symptoms.strip())
    
    if not all_symptoms:
        st.error("⚠️ Onugroho kore ontoto ek-ti symptom select ba likhe din.")
        st.stop()
        
    if not age_input.strip():
        st.error("⚠️ Onugroho kore patient-er age enter korun.")
        st.stop()

    payload = {
        "age": age_input.strip(),
        "gender": gender_input,
        "symptoms": ", ".join(all_symptoms),
        "duration": duration_input,
        "severity": str(severity_val),
        "conditions": existing_cond.strip() if existing_cond.strip() else "None reported",
        "medications": medications.strip() if medications.strip() else "None reported",
        "notes": notes.strip() if notes.strip() else "None",
        "language": selected_language
    }

    st.divider()

    # Step 1: Live Narrative Streaming
    st.subheader("🗣️ Preliminary Guidance Narrative (Live Stream)")
    with st.chat_message("assistant"):
        st.write_stream(stream_narrative(payload, api_key=user_api_key.strip()))

    st.divider()

    # Step 2: Structured Assessment Dashboard
    st.subheader("📊 Structured Assessment Dashboard")
    
    with st.spinner("Analyzing symptoms..."):
        start_time = time.time()
        raw_output = run_assessment_chain(payload, api_key=user_api_key.strip())
        elapsed_time = round(time.time() - start_time, 2)
        
        parsed_data, parse_error = parse_llm_json(raw_output)

    if parse_error or not parsed_data:
        st.error(f"Response parsing-e shomossha hoyeche: {parse_error}")
        with st.expander("Raw Model Output"):
            st.code(raw_output)
    else:
        st.caption(f"⚡ Response time: {elapsed_time}s")
        
        urgency = parsed_data.get("urgency_level", "LOW").upper()

        if urgency in ["HIGH", "EMERGENCY"]:
            st.error(f"🚨 URGENCY LEVEL: {urgency} - Druto daktar ba emergency service-e jogajog korun!")
        elif urgency == "MEDIUM":
            st.warning(f"⚠️ URGENCY LEVEL: {urgency} - Healthcare professional-er poramorsho neoyar onurodh roilo.")
        else:
            st.success(f"✅ URGENCY LEVEL: {urgency} - Sadharan ghoroa porichorja jotheshto hote pare.")

        st.metric(label="Calculated Urgency Level", value=urgency)
        st.info(f"**Patient Summary:** {parsed_data.get('summary', 'N/A')}")

        tab1, tab2, tab3 = st.tabs(["🩺 Possible Conditions", "📋 Next Steps & Questions", "⚠️ Red Flags / Warning Signs"])

        with tab1:
            st.markdown("##### Possible Conditions (Educational Only)")
            conditions_list = parsed_data.get("possible_conditions", [])
            if conditions_list:
                for item in conditions_list:
                    with st.expander(f"📌 {item.get('name', 'Condition')}"):
                        st.write(item.get("reason", "No details provided."))
            else:
                st.write("Kono specific condition paoya jayni.")

        with tab2:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("##### Recommended Next Steps")
                steps = parsed_data.get("recommended_next_steps", [])
                for s in steps:
                    st.write(f"- {s}")
            with col_b:
                st.markdown("##### Questions to Ask Your Doctor")
                doctor_q = parsed_data.get("questions_for_doctor", [])
                for q in doctor_q:
                    st.write(f"❓ {q}")

        with tab3:
            st.markdown("##### Warning Signs (Seek Immediate Medical Care)")
            warnings = parsed_data.get("warning_signs", [])
            for w in warnings:
                st.error(f"⚠️ {w}")