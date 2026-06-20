import anthropic
import json

PERSONA_SYSTEM_PROMPT = """You are a customer persona classifier for a support system.
Classify the user message into exactly ONE of these personas:
- Technical Expert: Uses technical terms, asks about APIs, logs, configs, error codes, root causes
- Frustrated User: Shows emotional distress, urgency, repeated complaints, uses words like "nothing works", "terrible", "I can't believe"
- Business Executive: Outcome-focused, asks about business impact, timelines, ROI, prefers brevity

Respond ONLY with valid JSON:
{"persona": "<one of the three>", "confidence": <0.0-1.0>, "reasoning": "<one sentence>"}
"""

def detect_persona(message: str, history: list = None) -> dict:
    """Classify the user's persona using Claude."""
    client = anthropic.Anthropic()
    
    context = ""
    if history:
        last_msgs = history[-4:]  # Last 2 turns
        for m in last_msgs:
            if m["role"] == "user":
                context += f"Previous user message: {m['content']}\n"
    
    full_input = f"{context}Current message: {message}" if context else message
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        system=PERSONA_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": full_input}]
    )
    
    try:
        text = response.content[0].text.strip()
        result = json.loads(text)
        return result
    except Exception:
        return {"persona": "Technical Expert", "confidence": 0.5, "reasoning": "Could not classify"}
