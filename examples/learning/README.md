# Learning Adapter

Example adapter for learning and skill development.

## Overview

This adapter models a learner developing skills or knowledge. It demonstrates:

- **Identity types** based on learning style
- **Journey stages** based on skill acquisition
- **Pattern detection** for learning pace and struggles
- **Nudges** for practice reminders and breakthroughs

## Usage

```python
from sxth_mind import Mind
from examples.learning import LearningAdapter

mind = Mind(adapter=LearningAdapter())

# Starting to learn
response = await mind.chat("user_1", "I want to learn Python")
# → "Great choice! What draws you to Python?"

# During practice
response = await mind.chat("user_1", "I don't understand list comprehensions")
# → "Let me explain with a simple example..."

# After progress
response = await mind.chat("user_1", "I built my first project!")
# → "That's a huge milestone! What did you build?"
```

## Identity Types

| Type | Description |
|------|-------------|
| Conceptual | Needs the big picture, asks "why", theory first |
| Hands-On | Learns by doing, examples first |
| Structured | Prefers step-by-step curriculum |
| Explorer | Curiosity-driven, self-directed |

## Journey Stages

| Stage | When | AI Tone |
|-------|------|---------|
| Exploring | New to the topic | Encouraging |
| Foundations | Learning basics | Patient |
| Practicing | Doing exercises | Supportive |
| Applying | Building projects | Challenging |
| Deepening | Advanced topics | Collaborative |
| Stuck | Frustrated/blocked | Compassionate |

## Patterns Tracked

The adapter tracks:

- **Exercises completed**: Count of completed exercises
- **Projects completed**: Count of finished projects
- **Stuck count**: Consecutive struggle indicators
- **Preferred explanations**: How they like things explained
- **Strong/struggle areas**: Topics of strength or difficulty

## Customization

Extend `LearningAdapter` for specific learning domains:

```python
class CodingLearningAdapter(LearningAdapter):
    @property
    def name(self) -> str:
        return "coding_learning"

    def get_journey_stages(self):
        stages = super().get_journey_stages()
        # Add coding-specific stages
        stages.insert(3, {
            "key": "debugging",
            "label": "Learning to Debug",
            "tone": "analytical",
            "guidance": "Help them develop debugging skills..."
        })
        return stages
```
