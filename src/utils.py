import json
import re
from typing import Tuple, Optional, Dict, Any

def parse_llm_json(raw_text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    LLM ke raw output ko safely JSON dictionary mein convert karta hai.
    App crash hone se bachata hai aur error message return karta hai.
    """
    if not raw_text or not raw_text.strip():
        return None, "Empty response received from LLM."
    
    try:
        # Markdown backticks aur accidental labels ko clean karna
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        # JSON extraction agar model ne text ke darmiyan JSON likha ho
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)

        data = json.loads(cleaned)
        return data, None

    except json.JSONDecodeError as err:
        return None, f"JSON Parsing Error: {str(err)}"
    except Exception as err:
        return None, f"Unexpected Parsing Error: {str(err)}"

def get_urgency_color(urgency: str) -> str:
    """
    Urgency level ke mutabiq Streamlit UI color/status helper.
    """
    mapping = {
        "LOW": "green",
        "MEDIUM": "orange",
        "HIGH": "red",
        "EMERGENCY": "red"
    }
    return mapping.get(urgency.upper(), "blue")