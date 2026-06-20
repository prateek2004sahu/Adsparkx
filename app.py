import streamlit as st
import json
import time
from src.agent import SupportAgent

st.set_page_config(
    page_title="Adsparkx AI Support Agent",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    .persona-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .persona-technical { background: #dbeafe; color: #1e40af; }
    .persona-frustrated { background: #fee2e2; color: #991b1b; }
    .persona-executive { background: #d1fae5; color: #065f46; }
    .escalated { background: #fef3c7; color: #92400e; border: 1px solid #fbbf24; padding: 10px; border-radius: 8px; }
    .source-chip {
        display: inline-block;
        background: #f3f4f6;
        color: #374151;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        margin: 2px;
    }
    .chat-meta { font-size: 12px; color: #6b7280; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# Initialize agent
@st.cache_resource
def load_agent():
    agent = SupportAgent()
    agent.ingest_knowledge_base()
    return agent

def persona_color(persona: str) -> str:
    mapping = {
        "Technical Expert": "persona-technical",
        "Frustrated User": "persona-frustrated",
        "Business Executive": "persona-executive",
    }
    return mapping.get(persona, "persona-technical")

def main():
    st.title("🤖 Persona-Adaptive Customer Support Agent")
    st.caption("Powered by Claude + RAG · Detects your persona and adapts responses accordingly")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        top_k = st.slider("Retrieved Chunks (top-k)", 1, 8, 3)
        confidence_threshold = st.slider("Escalation Confidence Threshold", 0.0, 1.0, 0.35, 0.05)
        st.divider()
        st.header("📊 Session Info")
        if "messages" in st.session_state:
            st.metric("Messages", len(st.session_state.messages))
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.session_state.agent_state = {}
            st.rerun()
        st.divider()
        st.markdown("**Persona Guide:**")
        st.markdown("🔵 **Technical Expert** — uses API/log terminology")
        st.markdown("🔴 **Frustrated User** — emotional, urgent language")
        st.markdown("🟢 **Business Executive** — outcome-focused, concise")

    # Init state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_state" not in st.session_state:
        st.session_state.agent_state = {}

    agent = load_agent()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                if msg.get("persona"):
                    css = persona_color(msg["persona"])
                    st.markdown(f'<span class="persona-badge {css}">👤 {msg["persona"]}</span>', unsafe_allow_html=True)
                st.markdown(msg["content"])
                if msg.get("sources"):
                    st.markdown('<div class="chat-meta">📚 Sources: ' +
                        "".join(f'<span class="source-chip">{s}</span>' for s in msg["sources"]) +
                        "</div>", unsafe_allow_html=True)
                if msg.get("escalated"):
                    st.markdown('<div class="escalated">⚠️ <b>Escalated to Human Agent</b></div>', unsafe_allow_html=True)
                    if msg.get("handoff_summary"):
                        with st.expander("📋 View Handoff Summary"):
                            st.json(msg["handoff_summary"])
            else:
                st.markdown(msg["content"])

    # Chat input
    if user_input := st.chat_input("Type your support query..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing your query..."):
                result = agent.process(
                    user_input,
                    conversation_history=st.session_state.messages[:-1],
                    top_k=top_k,
                    confidence_threshold=confidence_threshold,
                    agent_state=st.session_state.agent_state
                )

            st.session_state.agent_state = result.get("agent_state", {})

            persona = result.get("persona", "Unknown")
            css = persona_color(persona)
            st.markdown(f'<span class="persona-badge {css}">👤 {persona}</span>', unsafe_allow_html=True)
            st.markdown(result["response"])

            sources = result.get("sources", [])
            if sources:
                st.markdown('<div class="chat-meta">📚 Sources: ' +
                    "".join(f'<span class="source-chip">{s}</span>' for s in sources) +
                    "</div>", unsafe_allow_html=True)

            if result.get("escalated"):
                st.markdown('<div class="escalated">⚠️ <b>Escalated to Human Agent</b></div>', unsafe_allow_html=True)
                if result.get("handoff_summary"):
                    with st.expander("📋 View Handoff Summary"):
                        st.json(result["handoff_summary"])

        assistant_msg = {
            "role": "assistant",
            "content": result["response"],
            "persona": persona,
            "sources": sources,
            "escalated": result.get("escalated", False),
            "handoff_summary": result.get("handoff_summary"),
        }
        st.session_state.messages.append(assistant_msg)

if __name__ == "__main__":
    main()
