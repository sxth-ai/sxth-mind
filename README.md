# sxth-mind

**The understanding layer for adaptive AI products.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/sxth-mind.svg)](https://pypi.org/project/sxth-mind/)

[Documentation](https://docs.sxth.ai) · [Examples](examples/) · [Contributing](CONTRIBUTING.md)

---

## What is sxth-mind?

sxth-mind is a **cognitive state layer** for AI applications. It accumulates understanding about users over time—detecting patterns, tracking journey stages, and adapting responses based on derived insights.

Use it to personalize **any** LLM-powered experience:

- **Chat assistants** that remember user patterns across sessions
- **Personalized dashboards** that adapt to user behavior
- **Content recommendations** informed by journey stage
- **Proactive nudges** triggered by inactivity or momentum drops
- **Any AI feature** where understanding should evolve over time

```python
from sxth_mind import Mind
from examples.sales import SalesAdapter

mind = Mind(adapter=SalesAdapter())

# Get user state to personalize any LLM call
state = await mind.get_state("user_1")
# → Use state["user_mind"]["patterns"] to customize prompts, UI, recommendations

# Or use the built-in chat with automatic state management
await mind.chat("user_1", "Following up with the enterprise lead")
```

Unlike chat history retrieval, sxth-mind maintains **derived understanding** that evolves with each interaction.

---

## Why sxth-mind?

| | |
|---|---|
| **Derived understanding** | Not just retrieval—patterns, identity, and journey stage evolve with each interaction |
| **Pluggable everything** | Bring your own LLM provider, storage backend, and domain adapter |
| **Framework-agnostic** | Works with OpenAI, Anthropic, or any LLM. Not an agent framework—complements them |

---

## Installation

```bash
pip install sxth-mind[openai]      # With OpenAI provider
pip install sxth-mind[api]         # With HTTP API server
pip install sxth-mind[sqlite]      # With SQLite storage
pip install sxth-mind[all]         # Everything
```

---

## Quick Start

```python
import asyncio
from sxth_mind import Mind
from examples.sales import SalesAdapter

async def main():
    mind = Mind(adapter=SalesAdapter())

    # Chat - state accumulates automatically
    response = await mind.chat("user_1", "Working on the Acme deal")
    print(response)

    # Inspect what the Mind knows
    state = await mind.get_state("user_1")
    print(state["user_mind"]["patterns"])

    # Human-readable summary
    print(await mind.explain_state("user_1"))

asyncio.run(main())
```

---

## Features

### Core
- **Mind** — Central abstraction coordinating state, LLM calls, and persistence
- **UserMind** — User-level identity, patterns, and preferences
- **ProjectMind** — Context-specific state (deals, habits, learning topics)
- **ConversationMemory** — Sliding window of recent messages

### Adapters
- **Domain-specific behavior** — Define identity types, journey stages, and nudge templates
- **Three examples included** — Sales, Habits, Learning
- **Build your own** — Simple interface, full control

### Proactive Intelligence
- **Nudge engine** — Generate suggestions based on inactivity, momentum drops, patterns
- **Journey detection** — Automatically track progression through stages
- **Pattern recognition** — Detect recurring themes and behaviors

### Infrastructure
- **Pluggable LLM providers** — OpenAI included, bring your own
- **Pluggable storage** — Memory (default), SQLite, or custom
- **HTTP API** — FastAPI server for service deployment
- **CLI** — Demo mode and server commands

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Mind                                   │
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
│  (domain)     │   │  (LLM)        │   │  (persist)    │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## Example Adapters

### Sales
```python
from examples.sales import SalesAdapter
mind = Mind(adapter=SalesAdapter())
```
**Tracks:** outreach patterns, deal stages, follow-up frequency

### Habits
```python
from examples.habits import HabitCoachAdapter
mind = Mind(adapter=HabitCoachAdapter())
```
**Tracks:** streaks, blockers, recovery patterns

### Learning
```python
from examples.learning import LearningAdapter
mind = Mind(adapter=LearningAdapter())
```
**Tracks:** progress, stuck indicators, learning style

---

## Build Your Own Adapter

```python
from sxth_mind import BaseAdapter
from sxth_mind.schemas import ProjectMind

class MyAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "my_app"

    def get_identity_types(self):
        return [
            {"key": "power_user", "traits": ["fast", "keyboard-driven"]},
            {"key": "casual", "traits": ["occasional", "exploratory"]},
        ]

    def get_journey_stages(self):
        return [
            {"key": "onboarding", "tone": "helpful"},
            {"key": "proficient", "tone": "efficient"},
        ]

    def detect_journey_stage(self, project_mind: ProjectMind) -> str:
        if project_mind.interaction_count < 5:
            return "onboarding"
        return "proficient"

    def get_nudge_templates(self):
        return {}
```

See [docs/adapters.md](docs/adapters.md) for the full guide.

---

## HTTP API

```bash
sxth-mind serve --adapter sales --port 8000
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send a message |
| GET | `/state/{user_id}` | Get cognitive state |
| GET | `/explain/{user_id}` | Human-readable summary |
| GET | `/nudges/{user_id}` | Pending nudges |

---

## What sxth-mind is NOT

- **Not an agent framework** — We don't plan or execute actions
- **Not a vector database** — We don't do similarity search
- **Not chat history** — We store derived understanding, not transcripts

sxth-mind is **cognitive infrastructure**. You bring the intelligence; we maintain the understanding.

---

## Security

sxth-mind is a library you integrate into your application. Authentication, rate limiting, and network security are your responsibility. See [SECURITY.md](SECURITY.md).

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Links

- [Documentation](docs/getting-started.md)
- [PyPI](https://pypi.org/project/sxth-mind)
- [Changelog](CHANGELOG.md)
- [License](LICENSE) (MIT)
