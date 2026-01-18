# Habit Coach Adapter

Example adapter for habit tracking and building.

## Overview

This adapter models a user building and maintaining habits. It demonstrates:

- **Identity types** based on habit-building style
- **Journey stages** based on habit formation
- **Pattern detection** for consistency and struggles
- **Nudges** for streak maintenance and recovery

## Usage

```python
from sxth_mind import Mind
from examples.habits import HabitCoachAdapter

mind = Mind(adapter=HabitCoachAdapter())

# Starting a habit
response = await mind.chat("user_1", "I want to start exercising")
# → "Great! Let's start small. What's a tiny version of exercise you could do?"

# After building consistency
response = await mind.chat("user_1", "Done! That's day 7")
# → "A full week! You're building real momentum. How are you feeling?"

# After a setback
response = await mind.chat("user_1", "I missed the last 3 days")
# → "That happens. One break doesn't erase your progress. Ready to restart today?"
```

## Identity Types

| Type | Description |
|------|-------------|
| All-or-Nothing | Goes hard but struggles with setbacks |
| Slow Builder | Prefers gradual, sustainable progress |
| Accountability Seeker | Thrives with external support |
| Self-Motivated | Independent, internally driven |

## Journey Stages

| Stage | When | AI Tone |
|-------|------|---------|
| Starting | New habit, first few days | Encouraging |
| Struggling | Inconsistent, low momentum | Supportive |
| Building | Growing consistency | Motivating |
| Consistent | Solid streak (14+ days) | Reinforcing |
| Recovering | After breaking a streak | Compassionate |

## Patterns Tracked

The adapter tracks:

- **Current streak**: Days in a row
- **Longest streak**: Personal best
- **Common blockers**: What typically gets in the way
- **Completions**: Total times completed

## Customization

Extend `HabitCoachAdapter` for specific habit domains:

```python
class FitnessHabitAdapter(HabitCoachAdapter):
    @property
    def name(self) -> str:
        return "fitness_habits"

    def get_journey_stages(self):
        stages = super().get_journey_stages()
        # Add fitness-specific stages
        stages.append({
            "key": "leveling_up",
            "label": "Leveling Up",
            "tone": "challenging",
            "guidance": "User is ready for more intensity..."
        })
        return stages
```
