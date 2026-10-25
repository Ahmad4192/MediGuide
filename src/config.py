# Model Configuration
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.2

# Form Options
GENDER_OPTIONS = ["Male", "Female", "Other", "Prefer not to say"]

COMMON_SYMPTOMS = [
    "Fever",
    "Cough",
    "Sore throat",
    "Headache",
    "Runny nose",
    "Shortness of breath",
    "Chest pain",
    "Fatigue",
    "Body aches",
    "Nausea",
    "Diarrhea",
    "Dizziness"
]

DURATION_OPTIONS = [
    "Less than 24 hours",
    "1 - 3 days",
    "4 - 7 days",
    "1 - 2 weeks",
    "More than 2 weeks"
]

LANGUAGE_OPTIONS = [
    "English",
    "Urdu",
    "Spanish",
    "French",
    "Arabic"
]

# Medical Disclaimer
DISCLAIMER_TEXT = (
    "IMPORTANT NOTICE: MediGuide AI is an educational AI prototype only. "
    "It is NOT a replacement for a licensed doctor, professional diagnosis, "
    "or emergency treatment. In case of a serious emergency, please contact "
    "your local emergency services immediately."
)