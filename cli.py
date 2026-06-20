#!/usr/bin/env python3
"""
Command-Line Interface for the Persona-Adaptive Support Agent
Usage: python cli.py
"""

import json
import sys
import os

# Ensure src is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent import SupportAgent

PERSONA_COLORS = {
    "Technical Expert": "\033[94m",   # Blue
    "Frustrated User": "\033[91m",    # Red
    "Business Executive": "\033[92m", # Green
}
RESET = "\033[0m"
BOLD = "\033[1m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GRAY = "\033[90m"


def print_banner():
    print(f"\n{BOLD}{'='*60}")
    print("  🤖 Adsparkx AI — Persona-Adaptive Support Agent")
    print(f"{'='*60}{RESET}")
    print(f"{GRAY}Type 'exit' or 'quit' to end the session.{RESET}\n")


def print_response(result: dict):
    persona = result.get("persona", "Unknown")
    color = PERSONA_COLORS.get(persona, "\033[97m")

    print(f"\n{color}{BOLD}👤 Detected Persona: {persona}{RESET}")
    print(f"{GRAY}Confidence: {result.get('persona_confidence', 0):.0%}{RESET}")

    if result.get("sources"):
        sources_str = ", ".join(result["sources"])
        print(f"{CYAN}📚 Sources: {sources_str}{RESET}")

    print(f"\n{BOLD}Agent:{RESET}")
    print(result["response"])

    if result.get("escalated"):
        print(f"\n{YELLOW}{BOLD}⚠️  ESCALATED TO HUMAN AGENT{RESET}")
        if result.get("handoff_summary"):
            print(f"\n{YELLOW}📋 Handoff Summary:{RESET}")
            print(json.dumps(result["handoff_summary"], indent=2))

    print(f"\n{GRAY}{'-'*60}{RESET}")


def main():
    print_banner()
    
    print("⏳ Loading knowledge base... ", end="", flush=True)
    agent = SupportAgent()
    agent.ingest_knowledge_base()
    print("✅ Ready!\n")

    conversation_history = []
    agent_state = {}

    while True:
        try:
            user_input = input(f"{BOLD}You: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{GRAY}Goodbye!{RESET}")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "bye"):
            print(f"{GRAY}Thank you for using Adsparkx Support. Goodbye!{RESET}")
            break

        conversation_history.append({"role": "user", "content": user_input})

        result = agent.process(
            user_message=user_input,
            conversation_history=conversation_history[:-1],
            top_k=3,
            confidence_threshold=0.35,
            agent_state=agent_state
        )

        agent_state = result.get("agent_state", {})
        conversation_history.append({"role": "assistant", "content": result["response"]})

        print_response(result)


if __name__ == "__main__":
    main()
