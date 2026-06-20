import re
from typing import List, Tuple, Dict

# Keywords that always trigger escalation
ESCALATION_KEYWORDS = [
    "billing", "refund", "lawsuit", "legal", "account deletion",
    "fraud", "chargeback", "cancel subscription", "data breach",
    "account locked", "security breach", "lawyer", "gdpr", "dispute",
    "compensation", "regulatory", "compliance violation"
]

# Frustration escalation patterns
FRUSTRATION_PATTERNS = [
    r"this is (unacceptable|ridiculous|terrible|awful|horrible)",
    r"(worst|terrible) (service|support|experience)",
    r"i('ve| have) (been waiting|tried everything|given up)",
    r"(escalate|supervisor|manager|human)",
    r"i want (to speak|a refund|my money back)",
    r"still (not|broken|doesn't|failing)",
]


def check_escalation(
    user_message: str,
    retrieved_chunks: List[Tuple],
    persona: str,
    agent_state: Dict,
    confidence_threshold: float = 0.35
) -> Tuple[bool, str]:
    """
    Returns (should_escalate: bool, reason: str)
    """
    msg_lower = user_message.lower()

    # 1. Billing / legal keyword trigger
    for kw in ESCALATION_KEYWORDS:
        if kw in msg_lower:
            return True, f"Sensitive topic detected: '{kw}'"

    # 2. Low retrieval confidence
    if not retrieved_chunks:
        return True, "No relevant documentation found in knowledge base"
    
    top_score = retrieved_chunks[0][1] if retrieved_chunks else 0.0
    if top_score < confidence_threshold:
        return True, f"Low retrieval confidence ({top_score:.2f} < {confidence_threshold})"

    # 3. Repeated frustration / explicit escalation request
    for pattern in FRUSTRATION_PATTERNS:
        if re.search(pattern, msg_lower):
            return True, "User is expressing high frustration or requesting human agent"

    # 4. User repeated same issue more than twice
    repeat_count = agent_state.get("repeat_count", 0)
    last_issue = agent_state.get("last_issue", "")
    # Simple similarity: check if key words overlap >50%
    curr_words = set(msg_lower.split())
    prev_words = set(last_issue.lower().split()) if last_issue else set()
    if prev_words and len(curr_words & prev_words) / max(len(curr_words), 1) > 0.5:
        repeat_count += 1
    else:
        repeat_count = 0

    if repeat_count >= 2:
        return True, "User has repeated the same issue multiple times without resolution"

    return False, ""


def extract_attempted_steps(conversation_history: List[Dict]) -> List[str]:
    """Extract steps already mentioned or tried from conversation history."""
    steps = []
    step_patterns = [
        r"tried (to )?([\w\s]+)",
        r"already ([\w\s]+)",
        r"(restart|reset|clear cache|reinstall|update|upgrade|reboot|logout|login|sign out)",
        r"(followed|completed|did) (the )?([\w\s]+) steps",
    ]
    
    for msg in conversation_history:
        if msg["role"] == "user":
            text = msg["content"].lower()
            for pattern in step_patterns:
                matches = re.findall(pattern, text)
                for m in matches:
                    step = " ".join(m).strip() if isinstance(m, tuple) else m.strip()
                    if step and len(step) > 3:
                        steps.append(step.capitalize())
    
    return list(dict.fromkeys(steps))[:6]  # Deduplicate, max 6
