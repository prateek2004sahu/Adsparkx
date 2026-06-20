import anthropic
from typing import List, Dict

PERSONA_PROMPTS = {
    "Technical Expert": """You are a senior technical support engineer.
The user is a Technical Expert. Respond with:
- Detailed technical accuracy
- Root cause analysis when relevant
- Step-by-step troubleshooting with exact commands/configs
- Error codes, log snippets, and API references where applicable
- No over-explanation of basics
Use technical terminology freely. Be precise and comprehensive.""",

    "Frustrated User": """You are an empathetic customer support specialist.
The user is Frustrated. Respond with:
- Acknowledge their frustration sincerely in the first sentence
- Use simple, clear language (no jargon)
- Be warm, reassuring, and patient
- Provide clear, numbered action steps
- End with a positive and encouraging note
- Keep it concise and focused on immediate relief""",

    "Business Executive": """You are a senior customer success manager.
The user is a Business Executive. Respond with:
- Lead with business impact and resolution timeline
- Be concise (under 150 words unless detail is critical)
- Avoid technical jargon
- Use bullet points for key actions/outcomes
- Focus on what matters: timeline, impact, who owns the fix
- Professional and confident tone"""
}

def generate_response(
    user_message: str,
    persona: str,
    retrieved_chunks: list,
    conversation_history: list = None
) -> str:
    """Generate a persona-adapted response grounded in retrieved context."""
    client = anthropic.Anthropic()
    
    # Build context from retrieved chunks
    if retrieved_chunks:
        context_parts = []
        for chunk, score in retrieved_chunks:
            context_parts.append(
                f"[Source: {chunk['source']} | Section: {chunk['section']}]\n{chunk['text']}"
            )
        knowledge_context = "\n\n---\n\n".join(context_parts)
    else:
        knowledge_context = "No relevant documentation found."
    
    system_prompt = PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["Technical Expert"])
    system_prompt += f"""

KNOWLEDGE BASE CONTEXT (use ONLY this to answer):
{knowledge_context}

RULES:
- Answer ONLY based on the provided knowledge base context
- If the context does not contain the answer, say so honestly and recommend escalation
- Do NOT hallucinate or invent information
- Cite the source document name naturally in your response when relevant"""

    # Build message history
    messages = []
    if conversation_history:
        for msg in conversation_history[-6:]:  # Last 3 turns
            if msg["role"] in ("user", "assistant"):
                messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_message})
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=system_prompt,
        messages=messages
    )
    
    return response.content[0].text.strip()


def generate_handoff_summary(
    persona: str,
    user_message: str,
    conversation_history: list,
    retrieved_chunks: list,
    attempted_steps: list
) -> dict:
    """Generate a structured human handoff summary."""
    client = anthropic.Anthropic()
    
    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in conversation_history[-10:]
    )
    
    docs_used = list({c["source"] for c, _ in retrieved_chunks}) if retrieved_chunks else []
    
    prompt = f"""Generate a structured escalation summary for a human support agent.

Detected Persona: {persona}
Latest User Message: {user_message}
Conversation History:
{history_text}
Documents Referenced: {', '.join(docs_used) if docs_used else 'None'}
Steps Already Attempted: {', '.join(attempted_steps) if attempted_steps else 'None identified'}

Return ONLY a JSON object with these exact keys:
{{
  "persona": "...",
  "issue": "one sentence summary of the user's problem",
  "documents_used": ["list", "of", "docs"],
  "attempted_steps": ["list", "of", "steps"],
  "recommendation": "what the human agent should do next",
  "urgency": "Low | Medium | High | Critical"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    
    import json, re
    text = response.content[0].text.strip()
    # Extract JSON
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    
    return {
        "persona": persona,
        "issue": user_message[:200],
        "documents_used": docs_used,
        "attempted_steps": attempted_steps,
        "recommendation": "Manual review required",
        "urgency": "Medium"
    }
