"""
Phase 6.1: Frontend Application
Groww AI shell for the Mutual Fund FAQ Assistant.
"""

import html
import re
from datetime import datetime
from uuid import uuid4

import requests
import streamlit as st
from dotenv import load_dotenv

from ui_theme import STYLES

load_dotenv()

API_BASE = "http://localhost:8000"
REQUEST_TIMEOUT = 120

# Label -> the question actually sent to the assistant
POPULAR_QUESTIONS = {
    "Fund Manager": "Who is the fund manager of HDFC Mid Cap Fund?",
    "Expense Ratio": "What is the expense ratio of HDFC Mid Cap Fund?",
    "Exit Load": "What is the exit load of HDFC Focused Fund?",
    "Tax Saving (ELSS)": "What is the ELSS lock-in period of HDFC ELSS Tax Saver Fund?",
    "Minimum SIP": "What is the minimum SIP amount for HDFC ELSS Tax Saver Fund?",
}

FOLLOW_UP_TEMPLATES = [
    "What is the expense ratio of {scheme}?",
    "What is the exit load of {scheme}?",
    "What is the minimum SIP amount for {scheme}?",
    "What is the benchmark index of {scheme}?",
    "Who is the fund manager of {scheme}?",
    "What is the riskometer classification of {scheme}?",
]

GENERIC_FOLLOW_UPS = [
    "What is the expense ratio of HDFC Large Cap Fund?",
    "What is the exit load of HDFC Mid Cap Fund?",
    "What is the ELSS lock-in period of HDFC ELSS Tax Saver Fund?",
    "How do I download my capital gains statement?",
]

LINK_ICON = (
    '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#00875f" '
    'stroke-width="2" stroke-linecap="round"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.5 1.5"/>'
    '<path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7L12 19"/></svg>'
)

NAV_ITEMS = [
    ("Documents Indexed", "▤"),
    ("Saved Answers", "☆"),
    ("Alerts & Updates", "◇"),
    ("Settings", "⚙"),
    ("About Groww AI", "ⓘ"),
]

# Emitted immediately before a widget block so CSS can style it, since
# Streamlit widgets cannot carry class names of their own.
MARKER = '<div class="gw-mark gw-mark-{name}"></div>'

st.set_page_config(
    page_title="Groww AI - Mutual Fund Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(STYLES, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------

def new_chat() -> str:
    """Start an empty conversation and make it active."""
    chat_id = uuid4().hex
    st.session_state.chats[chat_id] = {"title": "New chat", "messages": []}
    st.session_state.active_chat = chat_id
    return chat_id


def init_state():
    st.session_state.setdefault("chats", {})
    st.session_state.setdefault("saved", [])
    st.session_state.setdefault("feedback", {})
    st.session_state.setdefault("pending", None)
    if not st.session_state.chats:
        new_chat()


def active_messages():
    return st.session_state.chats[st.session_state.active_chat]["messages"]


def ask(question: str):
    """Record the question and queue it for the backend."""
    question = (question or "").strip()
    if not question:
        return
    chat = st.session_state.chats[st.session_state.active_chat]
    if not chat["messages"]:
        chat["title"] = question if len(question) <= 46 else question[:43] + "..."
    chat["messages"].append(
        {
            "role": "user",
            "text": question,
            "time": datetime.now().strftime("%I:%M %p").lstrip("0"),
        }
    )
    st.session_state.pending = question
    st.rerun()


init_state()


# --------------------------------------------------------------------------
# Backend
# --------------------------------------------------------------------------

@st.cache_data(ttl=60, show_spinner=False)
def fetch_stats():
    try:
        response = requests.get(f"{API_BASE}/stats", timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return {"indexed_chunks": 0, "schemes": 0}


def fetch_answer(question: str) -> dict:
    try:
        response = requests.post(
            f"{API_BASE}/query", json={"query": question}, timeout=REQUEST_TIMEOUT
        )
        if response.status_code != 200:
            return {"error": f"The assistant returned status {response.status_code}."}
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Could not reach the assistant API on http://localhost:8000."}
    except requests.exceptions.Timeout:
        return {"error": "The request timed out before the assistant replied."}
    except requests.RequestException as exc:
        return {"error": f"Request failed: {exc}"}


# --------------------------------------------------------------------------
# Rendering helpers
# --------------------------------------------------------------------------

def linkify(escaped: str) -> str:
    return re.sub(
        r"(https?://[^\s<]+)",
        r'<a href="\1" target="_blank">\1</a>',
        escaped,
    )


def answer_html(answer: str) -> str:
    """Render the answer text, highlighting question headings and source lines."""
    blocks = []
    for line in answer.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        escaped = html.escape(stripped)
        if re.match(r"^\d+\.\s", stripped):
            blocks.append(f'<div class="gw-qhead">{escaped}</div>')
        elif stripped.lower().startswith("source:"):
            blocks.append(f'<div class="gw-src">{linkify(escaped)}</div>')
        else:
            blocks.append(f"<div>{linkify(escaped)}</div>")
    return "".join(blocks)


def sources_html(sources: list) -> str:
    rows = []
    for source in sources:
        rows.append(
            f'<div class="gw-source">'
            f'<div class="gw-source-icon">{LINK_ICON}</div>'
            f'<div class="gw-source-text">'
            f'<div class="gw-source-title">{html.escape(source["title"])}</div>'
            f'<div class="gw-source-sub">{html.escape(source["subtitle"])}</div>'
            f"</div>"
            f'<a class="gw-source-view" href="{html.escape(source["url"])}" '
            f'target="_blank">View</a>'
            f"</div>"
        )
    return (
        f'<div class="gw-sources">'
        f'<div class="gw-sources-head">Sources ({len(sources)})<span>Official pages</span></div>'
        f'{"".join(rows)}</div>'
    )


def follow_up_questions(message: dict) -> list:
    """Suggest related factual questions about the scheme just discussed."""
    schemes = [
        source["title"]
        for source in message.get("sources", [])
        if source.get("subtitle") == "Groww scheme page"
    ]
    if not schemes:
        return GENERIC_FOLLOW_UPS[:4]

    # One message can hold several questions, so match on containment
    asked = " ".join(
        msg["text"].lower() for msg in active_messages() if msg["role"] == "user"
    )
    suggestions = [
        question
        for question in (t.format(scheme=schemes[0]) for t in FOLLOW_UP_TEMPLATES)
        if question.lower() not in asked
    ]
    return suggestions[:4] or GENERIC_FOLLOW_UPS[:4]


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div class="gw-brand"><div class="gw-brand-mark"></div>'
        '<div class="gw-brand-name">Groww <span>AI</span></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(MARKER.format(name="newchat"), unsafe_allow_html=True)
    if st.button("＋  New Chat", key="new_chat"):
        new_chat()
        st.rerun()

    st.markdown('<div class="gw-side-label">Recent Chats</div>', unsafe_allow_html=True)
    for chat_id, chat in reversed(list(st.session_state.chats.items())):
        if chat_id == st.session_state.active_chat:
            st.markdown(MARKER.format(name="active"), unsafe_allow_html=True)
        if st.button(chat["title"], key=f"chat_{chat_id}"):
            st.session_state.active_chat = chat_id
            st.rerun()

    stats = fetch_stats()
    badges = {
        "Documents Indexed": f"{stats['indexed_chunks']:,}",
        "Saved Answers": str(len(st.session_state.saved)) if st.session_state.saved else "",
    }
    nav_rows = "".join(
        f'<div class="gw-nav"><span class="gw-nav-icon">{icon}</span>'
        f'<span style="flex:1;">{label}</span>'
        f'<span class="gw-nav-badge">{badges.get(label, "")}</span></div>'
        for label, icon in NAV_ITEMS
    )
    st.markdown(f'<div class="gw-side-rule"></div>{nav_rows}', unsafe_allow_html=True)

    st.markdown(
        '<div class="gw-facts-card"><b>🛡 Facts Only</b>'
        "<p>This assistant provides factual information from official documents.</p>"
        '<div class="gw-strong">Not investment advice.</div></div>'
        '<div class="gw-user"><div class="gw-avatar">GU</div>'
        '<div class="gw-user-name">Guest User</div></div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------

st.markdown(
    '<div class="gw-header"><div class="gw-bot">🤖</div><div>'
    '<div class="gw-title">Mutual Fund Assistant ✨</div>'
    '<div class="gw-subtitle">Ask factual questions about mutual funds and get '
    "instant answers.</div>"
    '<div class="gw-pills"><div class="gw-pill">🛡 Facts Only</div>'
    '<div class="gw-pill">🔒 No Investment Advice</div>'
    '<div class="gw-pill">✓ SEBI Compliant</div></div></div></div>',
    unsafe_allow_html=True,
)

with st.form("ask_form", clear_on_submit=True):
    bar, send = st.columns([12, 1.6])
    with bar:
        typed = st.text_input(
            "Question",
            placeholder="Ask anything about mutual funds...",
            label_visibility="collapsed",
        )
    with send:
        sent = st.form_submit_button("Ask ➤")

if sent:
    ask(typed)

st.markdown('<div class="gw-group-label">Popular Questions</div>', unsafe_allow_html=True)
st.markdown(MARKER.format(name="chips"), unsafe_allow_html=True)
# Trailing spacer keeps the chips compact instead of stretched across the row
chip_columns = st.columns([1.15, 1.15, 1, 1.45, 1.1, 3.2])
for column, (label, question) in zip(chip_columns, POPULAR_QUESTIONS.items()):
    with column:
        if st.button(label, key=f"chip_{label}"):
            ask(question)


# --------------------------------------------------------------------------
# Conversation
# --------------------------------------------------------------------------

messages = active_messages()

if not messages:
    st.markdown(
        '<div class="gw-empty">Ask about expense ratios, exit loads, minimum SIP '
        "amounts, ELSS lock-in, riskometer, benchmarks, fund managers or how to "
        "download statements.<br>You can ask several questions at once.</div>",
        unsafe_allow_html=True,
    )

for index, message in enumerate(messages):
    if message["role"] == "user":
        st.markdown(
            f'<div class="gw-user-row"><div class="gw-bubble">'
            f'{html.escape(message["text"])}'
            f'<span class="gw-time">{message["time"]} ✓✓</span></div>'
            f'<div class="gw-avatar">GU</div></div>',
            unsafe_allow_html=True,
        )
        continue

    st.markdown(
        f'<div class="gw-answer-row"><div class="gw-bot">🤖</div>'
        f'<div class="gw-card">{answer_html(message["text"])}'
        f'<div class="gw-note">ⓘ Fund details can change. Please verify against the '
        f"latest scheme documents before acting on them.</div></div></div>",
        unsafe_allow_html=True,
    )

    if message.get("sources"):
        st.markdown(sources_html(message["sources"]), unsafe_allow_html=True)

    # Feedback row
    feedback_key = f"{st.session_state.active_chat}:{index}"
    given = st.session_state.feedback.get(feedback_key)
    st.markdown(MARKER.format(name="feedback"), unsafe_allow_html=True)
    label, helpful, unhelpful, copy, save, _ = st.columns([2.5, 1.15, 1.4, 0.95, 0.95, 3])
    with label:
        st.markdown(
            '<div class="gw-feedback-label">Was this answer helpful?</div>',
            unsafe_allow_html=True,
        )
    with helpful:
        if st.button("👍 Helpful", key=f"up_{index}"):
            st.session_state.feedback[feedback_key] = "helpful"
            st.rerun()
    with unhelpful:
        if st.button("👎 Not Helpful", key=f"down_{index}"):
            st.session_state.feedback[feedback_key] = "not helpful"
            st.rerun()
    with copy:
        copied = st.button("⧉ Copy", key=f"copy_{index}")
    with save:
        if st.button("🔖 Save", key=f"save_{index}"):
            if message["text"] not in st.session_state.saved:
                st.session_state.saved.append(message["text"])
            st.rerun()

    if given:
        st.caption(f"Thanks - recorded as {given}.")
    if copied:
        st.code(message["text"], language=None)

    # Follow-up suggestions, only under the latest answer
    if index == len(messages) - 1:
        suggestions = follow_up_questions(message)
        st.markdown(
            '<div class="gw-group-label">You may also ask</div>', unsafe_allow_html=True
        )
        st.markdown(MARKER.format(name="follow"), unsafe_allow_html=True)
        for column, suggestion in zip(st.columns(len(suggestions)), suggestions):
            with column:
                if st.button(suggestion, key=f"next_{index}_{suggestion}"):
                    ask(suggestion)


# --------------------------------------------------------------------------
# Pending request
# --------------------------------------------------------------------------

if st.session_state.pending:
    with st.spinner("Checking the indexed documents..."):
        data = fetch_answer(st.session_state.pending)

    if data.get("error") and not data.get("answer"):
        messages.append({"role": "assistant", "text": data["error"], "sources": []})
    else:
        messages.append(
            {
                "role": "assistant",
                "text": data.get("answer", ""),
                "sources": data.get("sources", []),
            }
        )
    st.session_state.pending = None
    st.rerun()


st.markdown(
    '<div class="gw-foot">Groww AI can make mistakes. Please verify important '
    "information from official documents.</div>",
    unsafe_allow_html=True,
)
