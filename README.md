# Customer-Support-Chatbot (Aurora Skies Assistant) 

A simple airline customer support chatbot built with **Streamlit** and **Google Gemini API**.  
It corrects user input using **TextBlob**, answers questions conversationally, and can optionally retrieve answers from an FAQ dataset.

---

## #️Features
- Conversational replies 
- Spell correction (TextBlob)
- Optional FAQ retrieval (Sentence-Transformers + FAISS)
- Modern chat UI with dark/light themes

---

##  Prerequisites
- Python 3.10+
- A Google Gemini API key

---

##  Installation
```bash
git clone <your-repo-url>
cd <your-repo>
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
