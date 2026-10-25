# 🩺 MediGuide AI - Medical Symptom Assessment Assistant

MediGuide AI is an educational prototype built with Streamlit and LangChain for preliminary medical symptom assessment and guidance.

> **CRITICAL MEDICAL DISCLAIMER:**  
> This application is strictly an educational prototype. It is NOT a substitute for licensed medical advice, diagnosis, or treatment. It does not provide confirmed diagnoses. Always consult a qualified healthcare professional.

---

## 🚀 Features
- **LangChain Integration:** Prompt templates, ChatPromptTemplate, and structured JSON parsing.
- **Live Streaming:** Real-time narrative response streaming using `llm.stream()` and `st.write_stream`.
- **Dual Caching System:** Demonstrates both `InMemoryCache` and `SQLiteCache`.
- **Safety-First Dashboard:** Structured urgency indicators (LOW, MEDIUM, HIGH, EMERGENCY).

---

## ⚡ Caching Explanation (InMemoryCache vs SQLiteCache)
| Feature | InMemoryCache | SQLiteCache |
| :--- | :--- | :--- |
| **Storage Location** | System RAM (Memory) | Persistent SQLite database file on disk (`cache.db`) |
| **Speed** | Ultra-fast (microsecond access) | Fast, slightly slower due to disk I/O |
| **Persistence** | Cleared when app/server restarts | Persists across app restarts and multiple sessions |
| **Ideal For** | Short-lived, temporary test sessions | Production environments and identical query optimization |

---

## 🛠️ Local Installation & Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/Ahmad4192/MediGuide.git](https://github.com/Ahmad4192/MediGuide.git)
   cd medical_ai_assistant