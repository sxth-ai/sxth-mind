# Sales Adapter

Example adapter for a Sales/CRM domain.

## Overview

This adapter models a sales rep working deals through a pipeline. It demonstrates:

- **Identity types** based on selling style (Hunter, Farmer, Consultant, Closer)
- **Journey stages** based on deal progression (Prospecting → Closing)
- **Pattern detection** for outreach and follow-up behavior
- **Nudges** for stalled deals and follow-up reminders

## Usage

```python
from sxth_mind import Mind
from examples.sales import SalesAdapter

mind = Mind(adapter=SalesAdapter())

# First interaction
response = await mind.chat("rep_1", "Following up with the enterprise lead")
# → "What's your approach for this follow-up?"

# Later, same topic
response = await mind.chat("rep_1", "Following up with the enterprise lead again")
# → Mind notices the pattern: "Third follow-up with no response.
#    You've tried email twice—want to try a different channel?"
```

## Identity Types

| Type | Description |
|------|-------------|
| Hunter | New logo acquisition, cold outreach |
| Farmer | Account growth, relationship building |
| Consultant | Solution selling, advisory approach |
| Closer | Deal mechanics, negotiation |

## Journey Stages

| Stage | When | AI Tone |
|-------|------|---------|
| Prospecting | Finding new opportunities | Energetic |
| Qualifying | Understanding fit | Curious |
| Presenting | Demos and proposals | Confident |
| Negotiating | Terms and pricing | Strategic |
| Closing | Getting signatures | Decisive |
| Nurturing | Long-term follow-up | Patient |

## Patterns Detected

The adapter tracks:

- **Follow-up frequency**: How often the rep follows up
- **Themes**: Recurring topics (pricing, objections, timeline)
- **Objection patterns**: Common pushback encountered

## Customization

Extend `SalesAdapter` to add your own:

```python
class MySalesAdapter(SalesAdapter):
    def get_journey_stages(self):
        # Add your custom stages
        stages = super().get_journey_stages()
        stages.append({
            "key": "onboarding",
            "label": "Customer Onboarding",
            "tone": "supportive",
            "guidance": "Help with post-sale onboarding..."
        })
        return stages
```
