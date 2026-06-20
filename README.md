# 🤖 Adsparkx AI — Persona-Adaptive Customer Support Agent

A full-stack AI support agent that detects customer personas, retrieves relevant knowledge base content via RAG, generates persona-adapted responses, and escalates to human agents when necessary.

---

## Project Overview

This system automatically identifies which type of customer is interacting, retrieves relevant documentation, and tailors its response style to match:
- **Technical Expert** — detailed, precise, includes code/configs
- **Frustrated User** — empathetic, simple language, action-oriented
- **Business Executive** — concise, impact-focused, no jargon

---

## Tech Stack

| Component         | Technology                        | Version  |
|-------------------|-----------------------------------|----------|
| Language          | Python                            | 3.11+    |
| LLM               | Anthropic Claude (claude-sonnet-4-6) | Latest |
| RAG / Retrieval   | Custom TF-IDF Vector Store        | —        |
| UI                | Streamlit                         | 1.38+    |
| CLI               | Python built-in                   | —        |
| PDF Generation    | fpdf2                             | 2.7+     |
| HTTP Client       | anthropic SDK                     | 0.34+    |

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────┐
│     Persona Detection       │  ← Claude classifies user type
│  (Technical / Frustrated /  │    with confidence score
│   Business Executive)       │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    Knowledge Base Retrieval │  ← TF-IDF vector search
│    (RAG Pipeline)           │    over 11 support documents
│  top-k chunks + scores      │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    Escalation Check         │  ← Rules + confidence threshold
│  - Low confidence?          │    - Billing/legal keywords
│  - Sensitive topic?         │    - Repeated frustration
│  - Repeated issue?          │    - No relevant docs found
└─────────────┬───────────────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
┌──────────┐  ┌──────────────────────┐
│ Generate │  │  Human Handoff       │
│ Adaptive │  │  Summary (JSON)      │
│ Response │  │  + Escalation Msg    │
└──────────┘  └──────────────────────┘
```

---

## Persona Detection Strategy

**Method**: LLM-based zero-shot classification via Claude

**Approach**: The incoming message (plus last 2 conversation turns for context) is sent to Claude with a strict classification prompt. The model returns JSON with:
- `persona`: one of the three types
- `confidence`: float 0.0–1.0
- `reasoning`: one-sentence explanation

**Rules used**:
- Technical Expert: technical terminology, API/log/config references, error codes
- Frustrated User: emotional language, urgency signals, repeated complaints
- Business Executive: outcome-focused, timeline/impact language, brevity preference

---

## RAG Pipeline Design

**Chunking Strategy**: Sliding window — 400 words per chunk, 80-word overlap — preserves cross-sentence context while keeping chunks small enough for relevant retrieval.

**Embedding Model**: Custom TF-IDF sparse vectors (no external embedding API needed). This makes the project zero-cost beyond the Anthropic API key and zero-latency for indexing.

**Vector Store**: In-memory Python dict with cosine similarity scoring. Simple, fast, and sufficient for a knowledge base of this size (<20 documents).

**Retrieval Strategy**: Query is tokenized and TF-IDF scored against all chunk vectors. Top-k chunks (configurable, default 3) are returned with similarity scores. Scores below the configurable threshold trigger escalation.

**Metadata per chunk**: source filename, section heading (auto-detected from markdown headers), word count.

---

## Escalation Logic

The system escalates when ANY of these conditions are met:

| Trigger | Condition |
|---------|-----------|
| No documents found | Zero chunks retrieved |
| Low confidence | Top chunk score < threshold (default 0.35) |
| Sensitive keywords | Billing, legal, fraud, account deletion, GDPR, etc. |
| Frustration patterns | "unacceptable", "escalate", "supervisor", regex-matched |
| Repeated issue | Same query topic detected 3+ times without resolution |

All thresholds are configurable via the Streamlit UI sidebar or CLI parameters.

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/adsparkx-support-agent.git
cd adsparkx-support-agent
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 5. Run the app

**Streamlit UI (recommended):**
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser.

**CLI mode:**
```bash
python cli.py
```

---

## Environment Variables

| Variable            | Required | Description                        |
|---------------------|----------|------------------------------------|
| `ANTHROPIC_API_KEY` | ✅ Yes   | Your Anthropic API key from console.anthropic.com |

---

## Example Queries

### Technical Expert
```
Can you explain the OAuth 2.0 token refresh flow and how to handle 401 errors in production?
```
```
My webhook is not receiving events. I checked the endpoint is accessible. What could cause this?
```

### Frustrated User
```
I've tried everything and my account is still locked! This is ridiculous, I can't log in at all!
```
```
Nothing is working! I keep getting errors and your support is useless!
```

### Business Executive
```
How does a platform outage affect our campaign delivery and what's the resolution timeline?
```
```
We're spending $50K/month. What SLA guarantees do we have and what credits do we get if you miss them?
```

### Escalation Trigger
```
I want a refund and I'm considering legal action if this isn't resolved.
```
```
I need to speak to a manager immediately about this billing dispute.
```

---

## Knowledge Base Documents

| File | Content |
|------|---------|
| `api_authentication_guide.md` | OAuth 2.0, API keys, rate limits, error codes |
| `password_reset_guide.md` | Password reset, account lockout, 2FA issues |
| `billing_policy.md` | Plans, pricing, refunds, cancellation |
| `campaign_setup_guide.md` | Campaign creation, ad formats, approval process |
| `data_privacy_policy.md` | GDPR, CCPA, data retention, security |
| `technical_troubleshooting.md` | Dashboard issues, API errors, webhook debugging |
| `sla_uptime_policy.md` | Uptime SLAs, credits, support response times |
| `onboarding_faq.md` | Getting started, team setup, common questions |
| `integrations_guide.md` | Shopify, HubSpot, GA4, Zapier integration |
| `ad_policy_compliance.md` | Prohibited content, appeal process |
| `performance_optimization.md` | Campaign optimization, metrics, scaling |
| `enterprise_support_contract.pdf` | Enterprise SLA, dedicated support, escalation paths |

---

## Known Limitations

1. **TF-IDF retrieval**: Keyword-based retrieval won't understand semantic similarity. Replacing with OpenAI/Cohere embeddings + ChromaDB would significantly improve retrieval quality.
2. **No persistent memory**: Conversation history is session-only; refreshing loses context. Adding SQLite/Redis storage would enable multi-session continuity.
3. **Single language**: The agent responds in English only. Adding multilingual support would require prompt engineering and translated knowledge base documents.
4. **PDF content**: The PDF document (`enterprise_support_contract.pdf`) is loaded but not extracted — adding pypdf2 or pdfminer would enable PDF text retrieval.

## Future Improvements
- Swap TF-IDF for dense embeddings (OpenAI/Sentence Transformers + ChromaDB)
- Add LangGraph workflow for multi-step agentic resolution
- Implement sentiment analysis for real-time frustration scoring
- Add confidence dashboard and analytics
- Human approval workflow for escalated cases
- Multi-language support
#   A d s p a r k x  
 # Adsparkx
