import os
import html
from datetime import datetime

import streamlit as st
from textblob import TextBlob
import google.generativeai as genai

st.set_page_config(page_title="Aurora Skies Assistant", page_icon="💬", layout="wide")

API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.warning(
        "Gemini API key is missing. The assistant may not work properly."
    )
    st.stop()

genai.configure(api_key=API_KEY)
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
model = genai.GenerativeModel(MODEL_NAME)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"
theme = st.session_state.theme

if "conversation" not in st.session_state:
    st.session_state.conversation = []  

def correct_text(text: str) -> str:
    try:
        return str(TextBlob(text).correct())
    except Exception:
        return text

def build_prompt(user_text: str) -> str:
    conversation_text = "\n".join(
        [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.conversation]
    )
    system = (
        "You are Aurora Skies Airways' support assistant. "
        "Be helpful, professional, accurate, and concise. "
        "Only answer within typical airline-support scope (flights, baggage, "
        "cancellations, changes, fees, timelines, itineraries). "
        "When unsure, ask a short follow-up question."
    )
    return f"{system}\n\n{conversation_text}\nUSER: {user_text}\nASSISTANT:"

def get_gemini_reply(user_text: str) -> str:
    prompt = build_prompt(user_text)
    try:
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip()
        return text if text else "I'm here—could you please rephrase that?"
    except Exception as e:
        return f"Sorry, I ran into an issue reaching the service: {e}"

def now_hm() -> str:
    return datetime.now().strftime("%H:%M")

css_dark = """
<style>
:root {
  --bg1:#0b1220; --bg2:#0f1a2f;
  --text:#e5e7eb; --muted:#94a3b8; --border:#1f2a44;
  --u1:#2563eb; --u2:#3b82f6; --ai1:#0f172a; --ai2:#1f2937;
}
* { box-sizing: border-box; }
[data-testid="stAppViewContainer"] {
  background: radial-gradient(1000px 600px at 10% 10%, var(--bg1), var(--bg2));
  color: var(--text);
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}
.topbar{position:sticky;top:0;z-index:5;display:flex;justify-content:center;padding:18px 16px 8px;background:linear-gradient(180deg,rgba(11,18,32,.95),rgba(11,18,32,.55),transparent);backdrop-filter:blur(6px);}
.brand{display:inline-flex;gap:10px;align-items:center;padding:10px 14px;border-radius:14px;background:linear-gradient(135deg,rgba(96,165,250,.18),rgba(34,211,238,.14));border:1px solid rgba(99,102,241,.25);box-shadow:0 6px 24px rgba(2,132,199,.15),inset 0 0 30px rgba(96,165,250,.08);}
.brand .title{font-weight:700;letter-spacing:.2px;}
.app-wrap{max-width:1050px;margin:0 auto;padding:10px 16px 120px;}
.chat-card{border-radius:18px;padding:10px 8px;background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.02));border:1px solid var(--border);box-shadow:0 12px 40px rgba(0,0,0,.35),inset 0 0 60px rgba(255,255,255,.02);}
.chat-scroll{height:calc(100vh - 250px);min-height:440px;overflow-y:auto;padding:14px 12px 12px;}
/* ---- FIX START: robust flex layout ---- */
.msg-row{display:flex;gap:10px;margin:12px 4px;align-items:flex-end;}
.msg-row.user{flex-direction:row-reverse;}
.msg-row .avatar{flex:0 0 38px;height:38px;width:38px;border-radius:50%;display:grid;place-items:center;font-weight:700;color:#fff;font-size:.95rem;box-shadow:0 6px 16px rgba(0,0,0,.4);}
.avatar.user{background:linear-gradient(135deg,var(--u1),var(--u2));border:1px solid rgba(59,130,246,.5);}
.avatar.ai{background:linear-gradient(135deg,#14b8a6,#06b6d4);border:1px solid rgba(34,211,238,.5);}
.msg-row .content{flex:1 1 auto;min-width:0;max-width:calc(100% - 58px);display:flex;flex-direction:column;align-items:flex-start;}
.msg-row.user .content{align-items:flex-end;}
.bubble{display:inline-block;max-width:min(80%,820px);padding:12px 14px;border-radius:16px;line-height:1.45;white-space:pre-wrap;/* preserve newlines */
overflow-wrap:anywhere;word-break:normal;border:1px solid rgba(255,255,255,.08);backdrop-filter:blur(8px);}
.user .bubble{color:#eaf2ff;background:linear-gradient(135deg,rgba(37,99,235,.95),rgba(59,130,246,.9));box-shadow:0 8px 24px rgba(37,99,235,.35);}
.ai .bubble{color:#e5e7eb;background:linear-gradient(135deg,rgba(15,23,42,.85),rgba(31,41,55,.75));box-shadow:0 8px 24px rgba(2,132,199,.18);}
.meta{margin-top:6px;font-size:.75rem;color:var(--muted);}
/* ---- FIX END ---- */
.sep{display:flex;align-items:center;gap:10px;margin:14px 0;color:var(--muted);font-size:.8rem;}
.sep::before,.sep::after{content:"";height:1px;flex:1;background:linear-gradient(90deg,transparent,rgba(148,163,184,.35),transparent);}
.input-hint{color:var(--muted);font-size:.85rem;margin-top:6px;text-align:center;}
</style>
"""

css_light = """
<style>
:root {
  --bg1:#f1f5f9; --bg2:#e2e8f0;
  --text:#0f172a; --muted:#475569; --border:#e5e7eb;
  --u1:#0284c7; --u2:#0ea5e9; --ai1:#ffffff; --ai2:#f8fafc;
}
* { box-sizing: border-box; }
[data-testid="stAppViewContainer"]{background:radial-gradient(1200px 700px at 12% 10%,var(--bg1),var(--bg2));color:var(--text);font-family:'Inter',system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;}
.topbar{position:sticky;top:0;z-index:5;display:flex;justify-content:center;padding:18px 16px 8px;background:linear-gradient(180deg,rgba(255,255,255,.9),rgba(255,255,255,.55),transparent);backdrop-filter:blur(6px);}
.brand{display:inline-flex;gap:10px;align-items:center;padding:10px 14px;border-radius:14px;background:linear-gradient(135deg,rgba(14,165,233,.12),rgba(99,102,241,.12));border:1px solid rgba(99,102,241,.25);box-shadow:0 6px 24px rgba(2,132,199,.08),inset 0 0 30px rgba(99,102,241,.05);}
.brand .title{font-weight:700;letter-spacing:.2px;}
.app-wrap{max-width:1050px;margin:0 auto;padding:10px 16px 120px;}
.chat-card{border-radius:18px;padding:10px 8px;background:#fff;border:1px solid var(--border);box-shadow:0 12px 40px rgba(2,6,23,.08);}
.chat-scroll{height:calc(100vh - 250px);min-height:440px;overflow-y:auto;padding:14px 12px 12px;}
/* ---- FIX START ---- */
.msg-row{display:flex;gap:10px;margin:12px 4px;align-items:flex-end;}
.msg-row.user{flex-direction:row-reverse;}
.msg-row .avatar{flex:0 0 38px;height:38px;width:38px;border-radius:50%;display:grid;place-items:center;font-weight:700;color:#fff;font-size:.95rem;box-shadow:0 6px 16px rgba(15,23,42,.12);}
.avatar.user{background:linear-gradient(135deg,var(--u1),var(--u2));border:1px solid rgba(14,165,233,.35);}
.avatar.ai{background:linear-gradient(135deg,#22c55e,#10b981);border:1px solid rgba(16,185,129,.35);}
.msg-row .content{flex:1 1 auto;min-width:0;max-width:calc(100% - 58px);display:flex;flex-direction:column;align-items:flex-start;}
.msg-row.user .content{align-items:flex-end;}
.bubble{display:inline-block;max-width:min(80%,820px);padding:12px 14px;border-radius:16px;line-height:1.45;white-space:pre-wrap;overflow-wrap:anywhere;word-break:normal;border:1px solid rgba(15,23,42,.06);}
.user .bubble{color:#f0f9ff;background:linear-gradient(135deg,rgba(2,132,199,.95),rgba(14,165,233,.92));box-shadow:0 8px 20px rgba(2,132,199,.25);}
.ai .bubble{color:var(--text);background:linear-gradient(135deg,var(--ai1),var(--ai2));box-shadow:0 8px 20px rgba(2,6,23,.06);}
.meta{margin-top:6px;font-size:.75rem;color:var(--muted);}
/* ---- FIX END ---- */
.sep{display:flex;align-items:center;gap:10px;margin:14px 0;color:var(--muted);font-size:.8rem;}
.sep::before,.sep::after{content:"";height:1px;flex:1;background:linear-gradient(90deg,transparent,rgba(71,85,105,.4),transparent);}
.input-hint{color:var(--muted);font-size:.85rem;margin-top:6px;text-align:center;}
</style>
"""

st.markdown(css_dark if theme == "dark" else css_light, unsafe_allow_html=True)

with st.sidebar:
    st.title("Chat Settings")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.conversation = []
        st.rerun()

    theme_toggle = st.toggle("Dark Mode", value=(theme == "dark"))
    st.session_state.theme = "dark" if theme_toggle else "light"

    st.markdown("---")
    st.markdown("**Aurora Skies AI Assistant**  \nPowered by Gemini • Built with Streamlit")

st.markdown(
    '<div class="topbar"><div class="brand"><span style="font-size:1.2rem">🛫</span><div class="title">Aurora Skies Assistant</div></div></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="app-wrap">', unsafe_allow_html=True)
st.markdown('<div class="chat-card">', unsafe_allow_html=True)
st.markdown('<div class="sep">Welcome! Ask anything about bookings, baggage, or cancellations.</div>', unsafe_allow_html=True)

def render_msg(role: str, content: str, at: str) -> str:
    safe = html.escape(content).replace("\n", "<br/>")
    align = "user" if role == "user" else "ai"
    avatar_cls = "user" if role == "user" else "ai"
    label = "You" if role == "user" else "AI"
    initials = "Y" if role == "user" else "AI"
    return (
        '<div class="msg-row ' + align + '">'
        '<div class="avatar ' + avatar_cls + '">' + initials + '</div>'
        '<div class="content">'
        '<div class="bubble">' + safe + '</div>'
        '<div class="meta">' + label + ' · ' + at + '</div>'
        '</div>'
        '</div>'
    )

chat_html = ['<div class="chat-scroll">']
for msg in st.session_state.conversation:
    chat_html.append(render_msg(msg["role"], msg["content"], msg["time"]))
chat_html.append('</div>')
st.markdown("".join(chat_html), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="input-hint">Tip: Press Enter to send • Shift+Enter for a new line</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

user_input = st.chat_input("Ask me about flights, baggage, or cancellations...")

if user_input:
    corrected = correct_text(user_input)
    st.session_state.conversation.append({"role": "user", "content": corrected, "time": now_hm()})
    reply = get_gemini_reply(corrected)
    st.session_state.conversation.append({"role": "assistant", "content": reply, "time": now_hm()})
    st.rerun()