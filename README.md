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
pip install sxth-mind              # Core only
pip install sxth-mind[openai]      # With OpenAI provider
pip install sxth-mind[api]         # With HTTP API server
pip install sxth-mind[sqlite]      # With SQLite storage
pip install sxth-mind[all]         # Everything
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
print(state["user_mind"])    # UserMind data as dict
print(state["project_mind"]) # ProjectMind data as dict
```

### 3. Get a Human-Readable Summary

```python
summary = await mind.explain_state(user_id="user_123")
print(summary)
# "User has logged 15 sales interactions over 4 weeks.
#  Pattern: enterprise deals require 4+ touches before response.
#  Current stage: active_pipeline (tone: strategic)"
```

### 4. Check for Nudges

```python
# Get proactive suggestions based on state
nudges = await mind.get_pending_nudges(user_id="user_123")
for nudge in nudges:
    print(f"{nudge.title}: {nudge.message}")
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
│ - stages      │   │ - OpenAI      │   │ - Memory      │
│ - identity    │   │ - Custom      │   │ - SQLite      │
│ - nudges      │   │               │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
```

**Key insight:** Adapters are skins. The Mind is the engine.

---

## Core Concepts

### Mind

The central abstraction. Holds cognitive state, routes to adapters, coordinates persistence.

```python
from sxth_mind import Mind
from sxth_mind.storage import SQLiteStorage
from sxth_mind.providers.openai import OpenAIProvider
from examples.sales import SalesAdapter

mind = Mind(
    adapter=SalesAdapter(),                     # Domain configuration
    provider=OpenAIProvider(),                  # LLM calls (optional)
    storage=SQLiteStorage("mind.db"),           # Persistence (optional)
)
```

### UserMind

User-level understanding that persists across all projects/contexts.

```python
class UserMind:
    user_id: str

    # What we've learned about them
    identity_type: str | None       # "hunter", "farmer", etc.
    identity_data: dict             # Adapter-specific identity info
    patterns: dict                  # Detected behavioral patterns
    preferences: dict               # User preferences

    # Interaction history
    total_interactions: int
    trust_score: float              # 0.0 to 1.0
```

### ProjectMind

Context-specific state (a deal, a habit, a learning topic).

```python
class ProjectMind:
    project_id: str
    user_mind_id: str

    # Journey progress
    journey_stage: str | None       # "prospecting", "qualifying", etc.
    momentum_score: float           # 0.0 to 1.0

    # Context-specific data
    context_data: dict              # Adapter-defined structure
    progress_data: dict             # Adapter-defined metrics
    days_since_activity: int
```

### Adapters

Domain-specific configuration. Adapters define:
- **Identity types**: What user archetypes exist in this domain
- **Journey stages**: What progression looks like
- **Stage detection**: How to determine current stage from state
- **Nudge templates**: Proactive messages for re-engagement

```python
from sxth_mind import BaseAdapter

class SalesAdapter(BaseAdapter):
    def get_journey_stages(self):
        return [
            {"key": "prospecting", "tone": "proactive"},
            {"key": "qualifying", "tone": "analytical"},
            {"key": "negotiating", "tone": "strategic"},
            {"key": "stalled", "tone": "supportive"},
        ]

    def detect_journey_stage(self, project_mind):
        if project_mind.interaction_count < 3:
            return "prospecting"
        if project_mind.days_since_activity > 14:
            return "stalled"
        if project_mind.momentum_score > 0.7:
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

**Identity types:** hunter, farmer, consultant, closer
**Stages:** prospecting → qualifying → proposing → negotiating → closing (+ nurturing, stalled)
**Tracks:** outreach patterns, response rates, deal velocity

### Habits

Habit building with streak tracking and recovery.

```python
from examples.habits import HabitCoachAdapter

mind = Mind(adapter=HabitCoachAdapter())
```

**Identity types:** all_or_nothing, slow_builder, accountability_seeker, self_motivated
**Stages:** starting → struggling → building → consistent (+ recovering)
**Tracks:** streaks, blockers, time-of-day patterns

### Learning

Skill development with progress tracking.

```python
from examples.learning import LearningAdapter

mind = Mind(adapter=LearningAdapter())
```

**Identity types:** conceptual, hands_on, structured, explorer
**Stages:** exploring → foundations → practicing → applying → deepening (+ stuck)
**Tracks:** exercises completed, projects completed, stuck indicators

---

## Pluggable Providers

sxth-mind is **framework-agnostic**. Bring your own LLM provider.

### OpenAI

```python
from sxth_mind.providers.openai import OpenAIProvider

mind = Mind(
    adapter=SalesAdapter(),
    provider=OpenAIProvider(
        api_key="sk-...",           # Or set OPENAI_API_KEY env var
        default_model="gpt-4o-mini",
    ),
)
```

### Custom Provider

```python
from sxth_mind.providers import BaseLLMProvider, LLMResponse, Message

class MyProvider(BaseLLMProvider):
    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        # Your implementation
        ...

    async def chat_stream(self, messages, **kwargs):
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

### Custom Storage

```python
from sxth_mind.storage import BaseStorage
from sxth_mind import UserMind, ProjectMind

class MyStorage(BaseStorage):
    async def get_user_mind(self, user_id: str) -> UserMind | None:
        ...

    async def save_user_mind(self, user_mind: UserMind) -> None:
        ...

    async def get_project_minds(self, user_mind_id: str) -> list[ProjectMind]:
        ...

    async def get_project_mind(self, user_mind_id: str, project_id: str) -> ProjectMind | None:
        ...

    async def save_project_mind(self, project_mind: ProjectMind) -> None:
        ...

mind = Mind(adapter=SalesAdapter(), storage=MyStorage())
```

---

## Nudge Engine

sxth-mind includes a baseline nudge engine for proactive outreach.

```python
from sxth_mind.engine import BaselineNudgeEngine

engine = BaselineNudgeEngine(adapter, storage)

# Check and generate nudges for a user
nudges = await engine.check_and_generate("user_123")

for nudge in nudges:
    print(f"{nudge.title}: {nudge.message}")
    # "Deal going cold?" : "No activity on deal_1 in 8 days. Time to re-engage?"
```

The engine checks for:
- **Inactivity**: User hasn't interacted in X days
- **Momentum drop**: Activity level has decreased
- **Streak risk**: Habits at risk of breaking
- **Milestones**: Progress worth celebrating

Nudge templates are **adapter-defined**:

```python
class SalesAdapter(BaseAdapter):
    def get_nudge_templates(self):
        return {
            "stalled_deal": {
                "title": "Deal going cold?",
                "template": "No activity on {project} in {days} days. Time to re-engage?",
                "priority": 5,
            },
            "momentum_drop": {
                "title": "Momentum slipping",
                "template": "Activity on {project} has dropped. Everything okay?",
                "priority": 4,
            },
        }
```

---

## HTTP API

Run sxth-mind as a service:

```bash
pip install sxth-mind[api]
sxth-mind serve --adapter sales --port 8000
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/chat` | Send a message |
| POST | `/chat/stream` | Stream a response (SSE) |
| GET | `/state/{user_id}` | Get user state |
| GET | `/explain/{user_id}` | Get human-readable summary |
| GET | `/nudges/{user_id}` | Get pending nudges |
| POST | `/nudges/{user_id}/generate` | Generate new nudges |
| POST | `/nudges/{nudge_id}/dismiss` | Dismiss a nudge |
| POST | `/nudges/{nudge_id}/act` | Mark nudge as acted upon |

### Example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "Following up with the enterprise lead"}'
```

---

## CLI

```bash
# Run interactive demo with an adapter
sxth-mind demo                      # Sales adapter (default)
sxth-mind demo --adapter habits     # Habits adapter
sxth-mind demo --adapter learning   # Learning adapter

# Start HTTP server
sxth-mind serve --adapter sales --port 8000
sxth-mind serve --adapter habits --storage sqlite --db-path minds.db

# Show package info
sxth-mind info
```

---

## Building Your Own Adapter

```python
from sxth_mind import BaseAdapter
from sxth_mind.schemas import UserMind, ProjectMind

class MyAppAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "my_app"

    @property
    def display_name(self) -> str:
        return "My App"

    def get_identity_types(self):
        """What user archetypes exist in your domain?"""
        return [
            {"key": "power_user", "traits": ["fast", "keyboard-driven"]},
            {"key": "casual", "traits": ["occasional", "mouse-driven"]},
        ]

    def get_journey_stages(self):
        """What does progression look like?"""
        return [
            {"key": "onboarding", "tone": "helpful", "guidance": "Help them get started..."},
            {"key": "learning", "tone": "educational", "guidance": "Teach key concepts..."},
            {"key": "proficient", "tone": "efficient", "guidance": "Stay out of their way..."},
            {"key": "churning", "tone": "supportive", "guidance": "Re-engage gently..."},
        ]

    def detect_journey_stage(self, project_mind: ProjectMind) -> str:
        """How do you determine current stage?"""
        if project_mind.interaction_count < 5:
            return "onboarding"
        if project_mind.days_since_activity > 30:
            return "churning"
        if project_mind.get_context_field("completed_tutorial"):
            return "proficient"
        return "learning"

    def get_nudge_templates(self):
        """What proactive messages should we send?"""
        return {
            "comeback": {
                "title": "We miss you!",
                "template": "It's been {days} days. Here's what's new...",
                "priority": 5,
            },
        }

    def get_system_prompt(self, user_mind: UserMind, project_mind: ProjectMind) -> str:
        """Generate context-aware system prompt."""
        stage = project_mind.journey_stage or self.detect_journey_stage(project_mind)
        return f"You are a helpful assistant. User is in the {stage} stage."

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

## Contributing

We welcome contributions! Especially:

- New example adapters
- Storage backend implementations
- Provider implementations
- Documentation improvements

---

## Links

- [GitHub](https://github.com/toywobot/sxth-mind)
- [PyPI](https://pypi.org/project/sxth-mind)
