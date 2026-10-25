from typing import Generator, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Naye aur classic dono LangChain versions ke liye safe LLMChain import
try:
    from langchain.chains import LLMChain
except ImportError:
    try:
        from langchain_classic.chains import LLMChain
    except ImportError:
        LLMChain = None

from src.config import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from src.prompts import (
    ASSESSMENT_CHAT_TEMPLATE,
    RAW_PROMPT_TEMPLATE,
    NARRATIVE_CHAT_TEMPLATE
)

def get_llm(temperature: float = DEFAULT_TEMPERATURE, streaming: bool = False) -> ChatOpenAI:
    """
    OpenAI ChatOpenAI client instantiate karta hai.
    """
    return ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=temperature,
        api_key=OPENAI_API_KEY,
        streaming=streaming
    )

def run_assessment_chain(inputs: Dict[str, Any]) -> str:
    """
    LLMChain ya Modern LCEL pipeline ke zariye structured JSON assessment run karta hai.
    """
    llm = get_llm(temperature=0.1)
    
    # Agar legacy LLMChain available hai to use karein (Assignment Task 5 ke mutabiq)
    if LLMChain is not None:
        chain = LLMChain(llm=llm, prompt=ASSESSMENT_CHAT_TEMPLATE)
        return chain.run(inputs)
    else:
        # Fallback to modern LangChain LCEL syntax
        chain = ASSESSMENT_CHAT_TEMPLATE | llm
        response = chain.invoke(inputs)
        return str(response.content)

def stream_narrative(inputs: Dict[str, Any]) -> Generator[str, None, None]:
    """
    NARRATIVE_CHAT_TEMPLATE ke zariye live output chunks yield karta hai st.write_stream ke liye.
    """
    llm = get_llm(temperature=0.3, streaming=True)
    messages = NARRATIVE_CHAT_TEMPLATE.format_messages(**inputs)
    
    for chunk in llm.stream(messages):
        if chunk.content:
            yield chunk.content

def demo_direct_messages(system_text: str, human_text: str) -> Dict[str, str]:
    """
    Section 7 requirement: Direct SystemMessage, HumanMessage aur AIMessage flow demonstrate karta hai.
    """
    llm = get_llm()
    messages = [
        SystemMessage(content=system_text),
        HumanMessage(content=human_text)
    ]
    ai_response: AIMessage = llm.invoke(messages)
    
    return {
        "system": system_text,
        "human": human_text,
        "ai": str(ai_response.content)
    }