import streamlit as st
import time

from src.config import (
    OPENAI_API_KEY,
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

# Page configuration
st.set_page_config(
    page_title="MediGuide AI",
    page_icon="🩺",
    layout="wide"
)

# High-Specificity Custom CSS for Modern Streamlit
st.markdown("""
<style>
    /* 1. Main Background and Container Width */
    .stApp {
        background-color: #0d1117 !important;
    }
    .main .block-container {
        max-width: 1050px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
    }

    /* 2. Top Title Gradient Look */
    h1 {
        background: linear-gradient(90deg, #60a5fa, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 2.3rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* 3. Form Card Container with Glowing Border */
    div[data-testid="stForm"] {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 14px !important;
        padding: 28px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
    }

    /* 4. Inputs & Textareas Styling */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div,
    textarea {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #f0f6fc !important;
    }
    div[data-baseweb="input"] > div:focus-within,
    textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 1px #38bdf8 !important;
    }

    /* 5. Blue Gradient Submit Button */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
    }

    /* 6. Sidebar Polish */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d !important;
    }

    /* 7. Metric Card Styling (Results) */
    div[data-testid="stMetric"] {
        background-color: #21262d !important;
        border: 1px solid #30363d !important;
        padding: 16px 20px !important;
        border-radius: 10px !important;
    }
    div[data-testid="stMetricValue"] {
        color: #58a6ff !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("🩺 MediGuide AI")
    st.caption("AI-Powered Medical Symptom Assessment Assistant")
    
    st.divider()
    st.subheader("⚙️ Configuration")
    
    # Model info display
    st.text_input("Active Model", value=DEFAULT_MODEL, disabled=True)
    
    # Caching Selector
    cache_selection = st.radio(
        "LLM Cache Type",
        options=["InMemoryCache", "SQLiteCache"],
        help="InMemoryCache RAM me rehta hai; SQLiteCache disk file me persist hota hai."
    )
    cache_status_msg = configure_cache(cache_type=cache_selection)
    st.info(cache_status_msg)
    
    # Language Selection
    selected_language = st.selectbox("Response Language", options=LANGUAGE_OPTIONS, index=0)
    
    st.divider()
    # Medical Safety Disclaimer
    st.warning(f"⚠️ **MEDICAL DISCLAIMER**\n\n{DISCLAIMER_TEXT}")

# ----------------- MAIN SCREEN -----------------
st.title("Patient Symptom Assessment")
st.write(
    "Yeh application sirf educational purpose ke liye hai. Yeh koi confirmed medical diagnosis ya "
    "professional medical treatment ka badal nahi hai."
)

# API Key Validation
if not OPENAI_API_KEY:
    st.error("OpenAI API key missing hai! Barah-e-karam apni .env file me OPENAI_API_KEY set karein.")
    st.stop()

# Input Form
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
    all_symptoms = list(selected_symptoms)
    if custom_symptoms.strip():
        all_symptoms.append(custom_symptoms.strip())
    
    if not all_symptoms:
        st.error("⚠️ Barah-e-karam kam az kam ek symptom zaroor muntakhab ya enter karein.")
        st.stop()
        
    if not age_input.strip():
        st.error("⚠️ Barah-e-karam patient ki age enter karein.")
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
        st.write_stream(stream_narrative(payload))

    st.divider()

    # Step 2: Structured Assessment Dashboard
    st.subheader("📊 Structured Assessment Dashboard")
    
    with st.spinner("Structured assessment analyze ho rahi hai..."):
        start_time = time.time()
        raw_output = run_assessment_chain(payload)
        elapsed_time = round(time.time() - start_time, 2)
        
        parsed_data, parse_error = parse_llm_json(raw_output)

    if parse_error or not parsed_data:
        st.error(f"Structured response parse karne me issue aaya: {parse_error}")
        with st.expander("Raw Model Output"):
            st.code(raw_output)
    else:
        st.caption(f"⚡ Response time: {elapsed_time}s (Dobara submit karne par cache speed check karein)")
        
        urgency = parsed_data.get("urgency_level", "LOW").upper()

        if urgency in ["HIGH", "EMERGENCY"]:
            st.error(f"🚨 URGENCY LEVEL: {urgency} - Fauran doctor ya emergency service se rabta karein!")
        elif urgency == "MEDIUM":
            st.warning(f"⚠️ URGENCY LEVEL: {urgency} - Healthcare professional se mashwara lene ki sifarish ki jati hai.")
        else:
            st.success(f"✅ URGENCY LEVEL: {urgency} - Gharelu dekhbhal aur aam nigrani kafi ho sakti hai.")

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
                st.write("Koi specific condition identify nahi hui.")

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

# ----------------- SECTION 7: DEMO DIRECT MESSAGES -----------------
with st.expander("🛠️ LangChain Direct Messages Demo (System / Human / AI Message)"):
    st.write("Section 7 ke mutabiq direct message classes ki working testing:")
    if st.button("Run Message Demo"):
        demo_res = demo_direct_messages(
            system_text="You are a medical chatbot explaining triage rules in 1 line.",
            human_text="What does high fever with stiff neck mean?"
        )
        st.write("**System:**", demo_res["system"])
        st.write("**Human:**", demo_res["human"])
        st.write("**AI Message:**", demo_res["ai"])