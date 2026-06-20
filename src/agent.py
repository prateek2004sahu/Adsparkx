from src.persona import detect_persona
from src.retriever import VectorStore, load_documents
from src.generator import generate_response, generate_handoff_summary
from src.escalation import check_escalation, extract_attempted_steps
from typing import Dict, List


class SupportAgent:
    def __init__(self):
        self.vector_store = VectorStore()
        self._ingested = False

    def ingest_knowledge_base(self):
        """Load and index all knowledge base documents."""
        if self._ingested:
            return
        docs = load_documents()
        if not docs:
            print("[Agent] WARNING: No documents found in /data directory.")
        self.vector_store.build(docs)
        self._ingested = True

    def process(
        self,
        user_message: str,
        conversation_history: List[Dict] = None,
        top_k: int = 3,
        confidence_threshold: float = 0.35,
        agent_state: Dict = None
    ) -> Dict:
        """
        Full pipeline:
        1. Detect persona
        2. Retrieve relevant chunks
        3. Check escalation
        4. Generate response (or handoff summary)
        Returns structured result dict.
        """
        if agent_state is None:
            agent_state = {}
        if conversation_history is None:
            conversation_history = []

        # Step 1: Persona Detection
        persona_result = detect_persona(user_message, conversation_history)
        persona = persona_result.get("persona", "Technical Expert")

        # Step 2: Retrieval
        retrieved = self.vector_store.retrieve(user_message, top_k=top_k)
        sources = list({chunk["source"] for chunk, _ in retrieved}) if retrieved else []

        # Step 3: Escalation check
        should_escalate, escalation_reason = check_escalation(
            user_message, retrieved, persona, agent_state, confidence_threshold
        )

        # Update agent state
        agent_state["last_issue"] = user_message
        repeat_count = agent_state.get("repeat_count", 0)
        last_issue = agent_state.get("prev_issue", "")
        curr_words = set(user_message.lower().split())
        prev_words = set(last_issue.lower().split()) if last_issue else set()
        if prev_words and len(curr_words & prev_words) / max(len(curr_words), 1) > 0.5:
            agent_state["repeat_count"] = repeat_count + 1
        else:
            agent_state["repeat_count"] = 0
            agent_state["prev_issue"] = user_message

        result = {
            "persona": persona,
            "persona_confidence": persona_result.get("confidence", 0.5),
            "sources": sources,
            "escalated": should_escalate,
            "agent_state": agent_state,
        }

        if should_escalate:
            attempted_steps = extract_attempted_steps(conversation_history)
            handoff = generate_handoff_summary(
                persona=persona,
                user_message=user_message,
                conversation_history=conversation_history,
                retrieved_chunks=retrieved,
                attempted_steps=attempted_steps
            )
            result["handoff_summary"] = handoff
            result["response"] = (
                f"I understand your concern and I want to make sure you get the best help possible. "
                f"I'm escalating your case to a human support specialist who will follow up with you shortly.\n\n"
                f"**Reason for escalation:** {escalation_reason}\n\n"
                f"Your case reference has been created with a full summary of our conversation."
            )
        else:
            # Step 4: Generate adaptive response
            response = generate_response(
                user_message=user_message,
                persona=persona,
                retrieved_chunks=retrieved,
                conversation_history=conversation_history
            )
            result["response"] = response

        return result
