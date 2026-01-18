# sxth-mind

**The understanding layer for adaptive AI products.**

```python
from sxth_mind import Mind
from examples.sales import SalesAdapter

mind = Mind(adapter=SalesAdapter())

# First conversation
await mind.chat("user_1", "Following up with the enterprise lead")
# → "What's your approach for this follow-up?"

# Two weeks later
await mind.chat("user_1", "Following up with the enterprise lead again")
# → "Third follow-up with no response. You've tried email twice—want to try a different channel or contact?"
```

The Mind accumulates state, detects patterns, and adapts over time.

> **Read the motivation:** [Why This Exists](https://sxth.ai/blog/understanding-layer) — the architectural problem this solves.

---

## Why sxth-mind?

### The Problem

Every AI application hits the same wall: **conversations don't accumulate understanding**.

```python
# Week 1
User: "Following up with the enterprise lead"
Bot:  "What's your approach for this follow-up?"

# Week 2
User: "Following up with the enterprise lead"
Bot:  "What's your approach for this follow-up?"  # ← Same response

# Week 3
User: "Following up with the enterprise lead"
Bot:  "What's your approach for this follow-up?"  # ← Still no learning
```

You can stuff chat history into context. But that's not understanding—it's retrieval.

### The Solution

sxth-mind maintains **derived state** that evolves with each interaction:

| Interaction | What User Says | What Mind Learns |
|-------------|----------------|------------------|
| 1 | "Following up with the enterprise lead" | `themes: ["outreach"]` |
| 3 | "Still no response, sent another email" | `patterns: {outreach: "email-only"}` |
| 5 | "They finally replied but went dark again" | `identity: {style: "persistent"}` |
| 7 | "Got a meeting scheduled" | `patterns: {conversion: "requires 4+ touches"}` |
| 10 | "Following up with a new lead" | Full context available |

By interaction 10, the response becomes:

> "Based on your pattern, enterprise leads usually need 4+ touches. Want to plan a multi-channel sequence upfront?"

**That's derived understanding—not retrieval.**

---

## The Key Distinction

> **sxth-mind performs state-based reasoning (interpreting what is true over time), not action-based reasoning (deciding what to do next).**

| sxth-mind reasons about | sxth-mind does NOT reason about |
|-------------------------|--------------------------------|
| Patterns | Plans |
| Frequency | Tool sequences |
| Trends | Multi-step strategies |
| Identity signals | "What should I do next?" |
| Journey stage | Action selection |

sxth-mind is **cognitive infrastructure**—not an agent framework.

You bring the intelligence. We maintain the understanding.

---

## Installation

```bash
pip install sxth-mind[agno]  # With Agno provider (recommended)
pip install sxth-mind        # Core only, bring your own LLM provider
```

---

## Quick Start

### 1. Basic Usage

```python
from sxth_mind import Mind
from examples.sales import SalesAdapter

# Create a Mind with the sales adapter
mind = Mind(adapter=SalesAdapter())

# Chat (state is managed automatically)
response = await mind.chat(
    user_id="user_123",
    message="Need to follow up with the enterprise lead"
)
print(response)
```

### 2. Inspect the State

sxth-mind exposes everything—no black boxes.

```python
# See what the Mind knows
state = await mind.get_state(user_id="user_123")
print(state.themes)       # ["outreach", "enterprise"]
print(state.patterns)     # {}
print(state.identity)     # {}

# After more interactions...
state = await mind.get_state(user_id="user_123")
print(state.themes)       # ["outreach", "enterprise", "follow_ups"]
print(state.patterns)     # {"outreach": {"preferred_channel": "email", "avg_touches": 4}}
print(state.identity)     # {"style": "persistent", "strength": "relationship_building"}
```

### 3. Get a Human-Readable Summary

```python
summary = await mind.explain_state(user_id="user_123")
print(summary)
# "User has logged 15 sales interactions over 4 weeks.
#  Pattern: enterprise deals require 4+ touches before response.
#  Preferred channel: email, but LinkedIn warming up.
#  Current stage: active_pipeline (tone: strategic)"
```

### 4. Preview Updates (Dry Run)

```python
delta = await mind.preview_update(
    user_id="user_123",
    message="The enterprise lead finally responded"
)
print(delta)
# {"themes_added": ["responses"],
#  "patterns_updated": {"outreach": "conversion after 5 touches"}}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Mind                                   │
│                                                                  │
│   The core abstraction. Accumulates understanding over time.    │
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │  UserMind   │  │ ProjectMind │  │   Memory    │            │
│   │  (identity) │  │  (context)  │  │  (history)  │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│    Adapter    │   │   Provider    │   │    Storage    │
│               │   │               │   │               │
│ Defines the   │   │ Handles LLM   │   │ Persists the  │
│ domain:       │   │ calls:        │   │ mind:         │
│ - stages      │   │ - Agno        │   │ - Memory      │
│ - identity    │   │ - LangChain   │   │ - SQLite      │
│ - nudges      │   │ - Direct API  │   │ - Postgres    │
└───────────────┘   └───────────────┘   └───────────────┘
```

**Key insight:** Adapters are skins. The Mind is the engine.

---

## Core Concepts

### Mind

The central abstraction. Holds cognitive state, routes to adapters, coordinates persistence.

```python
mind = Mind(
    adapter=SalesAdapter(),              # Domain configuration
    provider=AgnoProvider(),             # LLM calls (optional, has default)
    storage=SQLiteStorage("mind.db"),    # Persistence (optional, defaults to memory)
)
```

### UserMind

User-level understanding that persists across all projects/contexts.

```python
class UserMind:
    user_id: str

    # What we've learned about them
    identity: dict          # {"style": "persistent", "strength": "relationship_building"}
    patterns: dict          # {"outreach": {"avg_touches": 4, "preferred_channel": "email"}}
    themes: list[str]       # ["enterprise", "outreach", "follow_ups"]

    # Interaction history
    interaction_count: int
    last_interaction: datetime
```

### ProjectMind

Context-specific state (a deal, a pipeline, a campaign).

```python
class ProjectMind:
    project_id: str
    user_mind_id: str

    # Journey progress
    stage: str              # "prospecting", "qualifying", "negotiating", etc.
    momentum: float         # 0.0 to 1.0

    # Context-specific data
    context: dict           # Adapter-defined structure
    progress: dict          # Adapter-defined metrics
```

### Adapters

Domain-specific configuration. Adapters define:
- **Identity types**: What user archetypes exist in this domain
- **Journey stages**: What progression looks like
- **Stage detection**: How to determine current stage from state
- **Nudge templates**: Proactive messages for re-engagement

```python
class SalesAdapter(BaseAdapter):
    def get_journey_stages(self):
        return [
            {"key": "prospecting", "tone": "proactive"},
            {"key": "qualifying", "tone": "analytical"},
            {"key": "negotiating", "tone": "strategic"},
            {"key": "stalled", "tone": "supportive"},
        ]

    def detect_stage(self, project_mind):
        if project_mind.interaction_count < 3:
            return "prospecting"
        if project_mind.days_since_activity > 14:
            return "stalled"
        if project_mind.momentum > 0.7:
            return "negotiating"
        return "qualifying"
```

---

## Example Adapters

sxth-mind ships with three example adapters to demonstrate the pattern:

### Sales

Pipeline tracking and outreach pattern detection.

```python
from examples.sales import SalesAdapter

mind = Mind(adapter=SalesAdapter())
```

**Stages:** prospecting → qualifying → negotiating → stalled
**Identity types:** relationship_builder, closer, hunter, farmer
**Tracks:** outreach patterns, response rates, deal velocity

### Habits

Habit building with streak tracking and recovery.

```python
from sxth_mind.examples import HabitCoachAdapter

mind = Mind(adapter=HabitCoachAdapter())
```

**Stages:** starting → struggling → building → consistent → recovering
**Identity types:** all_or_nothing, slow_builder, accountability_seeker, self_motivated
**Tracks:** streaks, skip patterns, time-of-day preferences

### Learning

Skill development with progress tracking.

```python
from sxth_mind.examples import LearningAdapter

mind = Mind(adapter=LearningAdapter())
```

**Stages:** exploring → practicing → applying → mastering
**Identity types:** conceptual_learner, hands_on, structured, explorer
**Tracks:** topics covered, struggle points, learning velocity

---

## Pluggable Providers

sxth-mind is **framework-agnostic**. Bring your own LLM provider.

### Agno (Default)

```python
from sxth_mind.providers import AgnoProvider

mind = Mind(
    adapter=SalesAdapter(),
    provider=AgnoProvider(model="gpt-4o"),
)
```

### Direct OpenAI

```python
from sxth_mind.providers import OpenAIDirectProvider

mind = Mind(
    adapter=SalesAdapter(),
    provider=OpenAIDirectProvider(api_key="sk-..."),
)
```

### Custom Provider

```python
from sxth_mind.providers import BaseLLMProvider

class MyProvider(BaseLLMProvider):
    async def chat(self, messages, tools=None, model=None):
        # Your implementation
        ...

    async def chat_stream(self, messages, tools=None, model=None):
        # Your streaming implementation
        ...

mind = Mind(adapter=SalesAdapter(), provider=MyProvider())
```

---

## Pluggable Storage

### In-Memory (Default)

```python
mind = Mind(adapter=SalesAdapter())  # Memory storage by default
```

### SQLite

```python
from sxth_mind.storage import SQLiteStorage

mind = Mind(
    adapter=SalesAdapter(),
    storage=SQLiteStorage("mind.db"),
)
```

### PostgreSQL

```python
from sxth_mind.storage import PostgresStorage

mind = Mind(
    adapter=SalesAdapter(),
    storage=PostgresStorage("postgresql://localhost/mydb"),
)
```

### Custom Storage

```python
from sxth_mind.storage import BaseStorage

class MyStorage(BaseStorage):
    async def get_user_mind(self, user_id: str) -> UserMind | None:
        ...

    async def save_user_mind(self, user_mind: UserMind) -> None:
        ...

    # ... other methods

mind = Mind(adapter=SalesAdapter(), storage=MyStorage())
```

---

## Nudges (Proactive Outreach)

sxth-mind can generate proactive messages based on state.

```python
# Check for pending nudges
nudges = await mind.get_pending_nudges(user_id="user_123")

for nudge in nudges:
    print(nudge.title)    # "Deal going cold?"
    print(nudge.message)  # "No activity on the enterprise deal in 7 days. Time to re-engage?"
    print(nudge.priority) # 5
```

Nudges are **adapter-defined** and **rule-based**:

```python
class SalesAdapter(BaseAdapter):
    def get_nudge_templates(self):
        return {
            "stalled": {
                "title": "Deal going cold?",
                "template": "No activity on {deal} in {days} days. Time to re-engage?",
                "min_days": 7,
                "priority": 5,
            },
            "momentum": {
                "title": "Hot lead!",
                "template": "{deal} is moving fast. Consider accelerating the timeline.",
                "priority": 3,
            },
        }
```

---

## HTTP API

Run sxth-mind as a service:

```bash
sxth-mind serve --adapter sales --port 8000
```

### Endpoints

```
POST /chat              # Send a message
GET  /state/{user_id}   # Get user state
GET  /explain/{user_id} # Get human-readable summary
GET  /nudges/{user_id}  # Get pending nudges
```

### Example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Following up with the enterprise lead"}'
```

---

## CLI

```bash
# Run interactive chat with an adapter
sxth-mind chat --adapter sales

# Start HTTP server
sxth-mind serve --adapter sales --port 8000

# Inspect state
sxth-mind state user_123 --adapter sales

# List available adapters
sxth-mind adapters
```

---

## Building Your Own Adapter

```python
from sxth_mind import BaseAdapter

class MyAppAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "my_app"

    def get_identity_types(self):
        """What user archetypes exist in your domain?"""
        return [
            {"key": "power_user", "traits": ["fast", "keyboard-driven"]},
            {"key": "casual", "traits": ["occasional", "mouse-driven"]},
        ]

    def get_journey_stages(self):
        """What does progression look like?"""
        return [
            {"key": "onboarding", "tone": "helpful"},
            {"key": "learning", "tone": "educational"},
            {"key": "proficient", "tone": "efficient"},
            {"key": "churning", "tone": "supportive"},
        ]

    def detect_stage(self, project_mind):
        """How do you determine current stage?"""
        if project_mind.interaction_count < 5:
            return "onboarding"
        if project_mind.days_since_activity > 30:
            return "churning"
        if project_mind.context.get("completed_tutorial"):
            return "proficient"
        return "learning"

    def get_nudge_templates(self):
        """What proactive messages should we send?"""
        return {
            "churning": {
                "title": "We miss you!",
                "template": "It's been {days} days. Here's what's new...",
                "min_days": 30,
            },
        }

# Use it
mind = Mind(adapter=MyAppAdapter())
```

---

## What sxth-mind is NOT

sxth-mind is **cognitive infrastructure**. It is not:

- **An agent framework** — We don't plan or execute actions
- **A vector database** — We don't do similarity search
- **A chat history store** — We store understanding, not transcripts
- **A prompt template library** — We manage state, not prompts

If you need those things, use them alongside sxth-mind. We complement, not compete.

---

## When to Use sxth-mind

**Good fit:**
- Sales assistants / CRM copilots
- Customer success tools
- Learning applications
- Habit tracking with AI
- Any app where users return over days/weeks/months

**Not a fit:**
- One-shot Q&A
- Stateless APIs
- Real-time agents that need planning

---

## License

MIT

---

## What's NOT Included

sxth-mind provides the **cognitive substrate**. For production applications that need to **improve over time**, check out **Brain Engine Cloud** which adds:

- Learning from user feedback (accepted/rejected advice)
- Cross-user pattern detection
- Intelligent nudge timing optimization
- Trust calibration
- Enterprise support & SLAs

[Learn more about Brain Engine Cloud →](https://sxth.ai/cloud)

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Especially welcome:
- New example adapters
- Storage backend implementations
- Provider implementations
- Documentation improvements

---

## Links

- [Why This Exists](https://sxth.ai/blog/understanding-layer) — The problem this solves
- [Documentation](https://sxth-mind.readthedocs.io)
- [GitHub](https://github.com/sxth/sxth-mind)
- [PyPI](https://pypi.org/project/sxth-mind)
- [Discord](https://discord.gg/sxth)
