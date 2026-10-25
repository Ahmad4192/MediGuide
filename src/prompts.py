from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# 1. System Prompt with strict Medical Safety Rules & JSON Schema instructions
SYSTEM_PROMPT = """You are MediGuide AI, an intelligent, empathetic educational medical symptom assessment prototype.

MANDATORY SAFETY AND OPERATIONAL CONSTRAINTS:
1. You are NOT a licensed doctor and you CANNOT provide a confirmed medical diagnosis.
2. Every guidance output is preliminary and purely for educational purposes.
3. You must urge the patient to consult a qualified healthcare professional.
4. If urgency is 'EMERGENCY' or symptoms indicate critical distress, instruct immediate contact with emergency medical services.
5. Provide response strictly in the requested language: {language}.
6. You MUST return ONLY valid JSON matching the exact schema below. Do not wrap in markdown tags like ```json or include conversational pleasantries outside the JSON.

REQUIRED JSON OUTPUT SCHEMA:
{{
  "summary": "Concise overview of reported symptoms and patient profile",
  "possible_conditions": [
    {{
      "name": "Condition name",
      "reason": "Educational explanation of why these symptoms could align with this condition"
    }}
  ],
  "urgency_level": "LOW",
  "recommended_next_steps": [
    "Step 1",
    "Step 2"
  ],
  "questions_for_doctor": [
    "Question 1",
    "Question 2"
  ],
  "warning_signs": [
    "Warning sign 1",
    "Warning sign 2"
  ]
}}
Note: 'urgency_level' must be strictly one of: LOW, MEDIUM, HIGH, EMERGENCY.
"""

# 2. Human Prompt containing patient data
HUMAN_PROMPT = """Patient Profile & Assessment Inputs:
- Age: {age}
- Gender: {gender}
- Primary Symptoms: {symptoms}
- Symptom Duration: {duration}
- Severity Score (1-10): {severity}
- Existing Medical Conditions: {conditions}
- Current Medications: {medications}
- Additional Notes: {notes}

Analyze these symptoms responsibly and return the preliminary guidance in the exact JSON format."""

# 3. ChatPromptTemplate for structured assessment
ASSESSMENT_CHAT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT)
])

# 4. PromptTemplate (single string template as required by section 7)
RAW_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=[
        "age", "gender", "symptoms", "duration", 
        "severity", "conditions", "medications", "notes", "language"
    ],
    template=SYSTEM_PROMPT + "\n\n" + HUMAN_PROMPT
)

# 5. Narrative Chat Template for streaming (live narrative stream)
NARRATIVE_CHAT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", (
        "You are MediGuide AI. In a natural, empathetic tone, stream a helpful educational "
        "summary narrative of the patient's symptoms and initial next steps. "
        "Remind them this is educational guidance, not a diagnosis. Language: {language}."
    )),
    ("human", HUMAN_PROMPT)
])