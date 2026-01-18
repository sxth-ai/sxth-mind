"""
Sales Adapter

Example adapter for a Sales/CRM domain. Demonstrates how to build
an adapter for B2B sales workflows.
"""

from typing import Any

from sxth_mind.adapters.base import BaseAdapter
from sxth_mind.schemas import ProjectMind, UserMind


class SalesAdapter(BaseAdapter):
    """
    Sales/CRM adapter example.

    This adapter models a sales rep working deals through a pipeline.
    It demonstrates:
    - Identity types based on selling style
    - Journey stages based on deal progression
    - Pattern detection for outreach and follow-up behavior
    - Nudges for stalled deals and follow-up reminders

    Usage:
        from sxth_mind import Mind
        from examples.sales import SalesAdapter

        mind = Mind(adapter=SalesAdapter())
        response = await mind.chat("rep_1", "Following up with the enterprise lead")
    """

    @property
    def name(self) -> str:
        return "sales"

    @property
    def display_name(self) -> str:
        return "Sales Assistant"

    # ═══════════════════════════════════════════════════════════════
    # Identity Model
    # ═══════════════════════════════════════════════════════════════

    def get_identity_types(self) -> list[dict[str, Any]]:
        """Sales rep styles/archetypes."""
        return [
            {
                "key": "hunter",
                "label": "Hunter",
                "traits": ["aggressive outreach", "cold calling", "new business"],
                "description": "Focused on new logo acquisition and cold outreach",
            },
            {
                "key": "farmer",
                "label": "Farmer",
                "traits": ["relationship building", "account growth", "retention"],
                "description": "Focused on growing existing accounts and relationships",
            },
            {
                "key": "consultant",
                "label": "Consultant",
                "traits": ["solution selling", "discovery", "advisory"],
                "description": "Focused on understanding needs and providing solutions",
            },
            {
                "key": "closer",
                "label": "Closer",
                "traits": ["negotiation", "urgency", "deal mechanics"],
                "description": "Focused on moving deals to close",
            },
        ]

    def get_identity_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "style": {"type": "string", "enum": ["hunter", "farmer", "consultant", "closer"]},
                "avg_deal_size": {"type": "number"},
                "typical_sales_cycle": {"type": "string"},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "areas_to_improve": {"type": "array", "items": {"type": "string"}},
            },
        }

    # ═══════════════════════════════════════════════════════════════
    # Journey Model (Deal Stages)
    # ═══════════════════════════════════════════════════════════════

    def get_journey_stages(self) -> list[dict[str, Any]]:
        """Deal pipeline stages."""
        return [
            {
                "key": "prospecting",
                "label": "Prospecting",
                "tone": "energetic",
                "guidance": """User is in early prospecting phase. Help with:
- Identifying good-fit prospects
- Crafting outreach messages
- Research on target accounts
Be proactive about suggesting outreach strategies.""",
            },
            {
                "key": "qualifying",
                "label": "Qualifying",
                "tone": "curious",
                "guidance": """User is qualifying leads. Help with:
- Discovery questions to ask
- Identifying decision makers
- Understanding budget and timeline
Ask probing questions to help them qualify effectively.""",
            },
            {
                "key": "presenting",
                "label": "Presenting",
                "tone": "confident",
                "guidance": """User is presenting/demoing to prospects. Help with:
- Tailoring presentations to buyer needs
- Handling objections
- Demonstrating value
Focus on connecting features to buyer pain points.""",
            },
            {
                "key": "negotiating",
                "label": "Negotiating",
                "tone": "strategic",
                "guidance": """User is in negotiation phase. Help with:
- Pricing strategies
- Contract terms
- Handling objections and pushback
- Creating urgency without pressure
Be tactical and help them think through leverage points.""",
            },
            {
                "key": "closing",
                "label": "Closing",
                "tone": "decisive",
                "guidance": """User is trying to close deals. Help with:
- Final objection handling
- Getting signatures
- Avoiding last-minute deal killers
Be direct and help them drive to commitment.""",
            },
            {
                "key": "nurturing",
                "label": "Nurturing",
                "tone": "patient",
                "guidance": """User is nurturing longer-term opportunities. Help with:
- Staying top of mind
- Adding value without being pushy
- Timing for re-engagement
Be patient and help them build relationships.""",
            },
        ]

    def detect_journey_stage(self, project_mind: ProjectMind) -> str:
        """Detect stage based on project context."""
        # Check explicit stage in context
        stage = project_mind.get_context_field("deal_stage")
        if stage:
            return stage

        # Infer from interaction patterns
        interactions = project_mind.interaction_count

        if interactions < 3:
            return "prospecting"
        elif interactions < 8:
            return "qualifying"
        elif interactions < 15:
            return "presenting"
        else:
            return "negotiating"

    # ═══════════════════════════════════════════════════════════════
    # Proactive Intelligence
    # ═══════════════════════════════════════════════════════════════

    def get_nudge_templates(self) -> dict[str, dict[str, Any]]:
        return {
            "stalled_deal": {
                "title": "Deal may be stalling",
                "template": "No activity on {deal_name} for {days} days. Time for a follow-up?",
                "priority": 7,
            },
            "follow_up_reminder": {
                "title": "Follow-up due",
                "template": "You mentioned following up with {contact_name}. Ready to reach out?",
                "priority": 6,
            },
            "pattern_detected": {
                "title": "Pattern noticed",
                "template": "{pattern_description}",
                "priority": 5,
            },
            "similar_deal_won": {
                "title": "Similar deal insight",
                "template": "This deal looks similar to {won_deal}. Consider: {suggestion}",
                "priority": 4,
            },
            "momentum_drop": {
                "title": "Momentum dropping",
                "template": "Activity on {deal_name} has slowed. What's blocking progress?",
                "priority": 8,
            },
        }

    def get_insight_types(self) -> list[dict[str, Any]]:
        return [
            {
                "key": "pattern",
                "label": "Behavioral Pattern",
                "severity": "info",
                "description": "Recurring pattern in sales behavior",
            },
            {
                "key": "objection_recurring",
                "label": "Recurring Objection",
                "severity": "warning",
                "description": "Same objection coming up repeatedly",
            },
            {
                "key": "win_factor",
                "label": "Win Factor",
                "severity": "info",
                "description": "Something that contributed to winning deals",
            },
            {
                "key": "risk",
                "label": "Deal Risk",
                "severity": "warning",
                "description": "Potential risk to deal success",
            },
        ]

    # ═══════════════════════════════════════════════════════════════
    # System Prompt
    # ═══════════════════════════════════════════════════════════════

    def get_system_prompt(self, user_mind: UserMind, project_mind: ProjectMind) -> str:
        stage = project_mind.journey_stage or self.detect_journey_stage(project_mind)
        stage_info = next(
            (s for s in self.get_journey_stages() if s["key"] == stage),
            self.get_journey_stages()[0]
        )

        # Build identity context
        identity_context = ""
        if user_mind.identity_type:
            identity_type = next(
                (t for t in self.get_identity_types() if t["key"] == user_mind.identity_type),
                None
            )
            if identity_type:
                identity_context = f"""
Sales Style: {identity_type['label']}
Traits: {', '.join(identity_type['traits'])}
"""

        # Build pattern context
        pattern_context = ""
        if user_mind.patterns:
            patterns = []
            if user_mind.patterns.get("follow_up_frequency"):
                patterns.append(f"Follow-up pattern: {user_mind.patterns['follow_up_frequency']}")
            if user_mind.patterns.get("themes"):
                patterns.append(f"Common themes: {', '.join(user_mind.patterns['themes'][:3])}")
            if patterns:
                pattern_context = "\n".join(patterns)

        return f"""You are a Sales AI assistant helping a sales rep work their deals.

## Your Role
You help with deal strategy, outreach, objection handling, and pipeline management.
You remember context from previous conversations and notice patterns.

{identity_context}

## Current Deal Stage: {stage_info['label']}
Tone: {stage_info['tone']}
{stage_info['guidance']}

## Patterns & History
{pattern_context if pattern_context else "No patterns detected yet."}
Total interactions: {user_mind.total_interactions}
Deal interactions: {project_mind.interaction_count}

## Guidelines
- Be practical and actionable
- Reference past context when relevant
- Notice patterns in their sales behavior
- Suggest next steps proactively
- If you notice recurring themes or issues, mention them
"""

    # ═══════════════════════════════════════════════════════════════
    # State Updates
    # ═══════════════════════════════════════════════════════════════

    def update_after_interaction(
        self,
        user_mind: UserMind,
        project_mind: ProjectMind,
        message: str,
        response: str,
    ) -> None:
        """Update state after interaction with sales-specific logic."""
        # Basic updates
        user_mind.increment_interactions()
        project_mind.increment_interactions()
        project_mind.update_momentum()

        # Update journey stage
        new_stage = self.detect_journey_stage(project_mind)
        if new_stage != project_mind.journey_stage:
            project_mind.journey_stage = new_stage

        # Detect patterns
        self._detect_patterns(user_mind, message)

    def _detect_patterns(self, user_mind: UserMind, message: str) -> None:
        """Simple pattern detection for sales context."""
        message_lower = message.lower()

        # Track themes
        themes = user_mind.patterns.get("themes", [])

        theme_keywords = {
            "follow_up": ["follow up", "following up", "check in", "checking in"],
            "objection": ["objection", "pushback", "concern", "hesitation"],
            "pricing": ["price", "pricing", "cost", "budget", "discount"],
            "timeline": ["timeline", "when", "deadline", "urgency"],
            "competition": ["competitor", "alternative", "other vendor"],
        }

        for theme, keywords in theme_keywords.items():
            if any(kw in message_lower for kw in keywords):
                if theme not in themes:
                    themes.append(theme)

        user_mind.patterns["themes"] = themes[-10:]  # Keep last 10

        # Track follow-up frequency
        if any(kw in message_lower for kw in ["follow up", "following up"]):
            follow_up_count = user_mind.patterns.get("follow_up_count", 0) + 1
            user_mind.patterns["follow_up_count"] = follow_up_count

            if follow_up_count > 5:
                user_mind.patterns["follow_up_frequency"] = "high"
            elif follow_up_count > 2:
                user_mind.patterns["follow_up_frequency"] = "moderate"
