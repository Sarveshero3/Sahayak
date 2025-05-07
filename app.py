# app.py
import uuid
import streamlit as st
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from config import DEFAULT_CHAT_MODEL, DEFAULT_EMBED_MODEL
from vector_store import get_vectordb

# ---------- Streamlit page ----------
st.set_page_config(
    page_title="🧘 Sahayak",
    page_icon="🧘‍♂️",
    layout="wide",
)

# ---------- Dark theme + hide sidebar ----------
st.markdown(
    """
    <style>
    /* ---- remove Streamlit's sidebar entirely ---- */
    [data-testid="stSidebar"],             /* the sidebar */
    [data-testid="stSidebarNav"],          /* menu in older versions */
    [data-testid="baseButton-sidebarCollapse"] {display:none !important;}

    /* ---- dark surfaced UI ---- */
    .stApp            {background:#0f1117;   color:#e4e4e4;}
    h1,h2,h3,h4,h5,h6 {color:#fdfdfd;}       /* bright headings */

    /* chat bubbles */
    div[data-testid="stChatMessage"]{
        background:#1e222a;
        border-radius:10px;
        padding:12px 16px;
        margin-bottom:8px;
    }

    /* primary buttons */
    button[kind="primary"]{
        border-radius:999px;
        font-weight:600;
        padding:0.4rem 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Fixed models (no user input) ----------
chat_model  = DEFAULT_CHAT_MODEL
embed_model = DEFAULT_EMBED_MODEL

# ---------- Bootstrap (first run or code-level model change) ----------
if (
    "qa_chain" not in st.session_state
    or st.session_state.get("models") != (chat_model, embed_model)
):
    with st.spinner("Bootstrapping models & vector store…"):
        vectordb  = get_vectordb(embed_model)
        chat_llm  = Ollama(model=chat_model, temperature=0.7)

        st.session_state.chat_llm = chat_llm
        st.session_state.qa_chain = RetrievalQA.from_chain_type(
            llm=chat_llm,
            chain_type="stuff",
            retriever=vectordb.as_retriever(),
        )
        st.session_state.models  = (chat_model, embed_model)
        st.session_state.helpful = {}

# ---------- Header & disclaimer ----------
st.title("🧘 Sahayak")
st.markdown(
    "**Disclaimer 🔔** I’m not a medical professional. If you feel unsafe or in crisis, "
    "please reach out to a qualified expert or local helpline."
)

# ---------- Conversation history ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(
        msg["role"],
        avatar="🧘" if msg["role"] == "assistant" else "💬",
    ):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ---------- User prompt ----------
STRESS_KWS = {"stress", "anxiety", "anxious", "nervous", "overwhelmed", "panic"}
prompt = st.chat_input("How can I help you relax today? …")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "id": str(uuid.uuid4())}
    )

    with st.chat_message("assistant", avatar="🧘"):
        # choose the chain
        if any(k in prompt.lower() for k in STRESS_KWS):
            answer = st.session_state.qa_chain.run(prompt)
        else:
            answer = st.session_state.chat_llm(prompt)

        # light formatting (Exercise/Duration)
        formatted_lines = []
        for ln in str(answer).split("\n"):
            low = ln.lower()
            if low.startswith("exercise:"):
                formatted_lines.append(f"### 🟢 {ln.split(':',1)[1].strip()}")
            elif low.startswith("duration:"):
                formatted_lines.append(
                    f"**⏱️ Duration:** {ln.split(':',1)[1].strip()}"
                )
            else:
                formatted_lines.append(ln)

        html = "\n".join(formatted_lines)
        st.markdown(html, unsafe_allow_html=True)

        aid = str(uuid.uuid4())
        st.session_state.messages.append(
            {"role": "assistant", "content": html, "id": aid}
        )

        # feedback button
        if st.button("👍 This helped", key=aid):
            st.session_state.helpful[aid] = True
            st.success("Glad it helped! 🙂")

# ---------- Feedback stats ----------
with st.expander("📊 Your feedback stats"):
    total = len(
        [m for m in st.session_state.messages if m["role"] == "assistant"]
    )
    good = len(st.session_state.helpful)
    st.write(f"You marked **{good}/{total}** suggestions as helpful.")
    st.write("Use Streamlit’s ‘R’ icon ↻ to reset anytime.")
