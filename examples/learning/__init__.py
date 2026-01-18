"""
Learning Adapter

Example adapter for learning and skill development.
Demonstrates journey stages for educational progress.
"""

from typing import Any

from sxth_mind.adapters.base import BaseAdapter
from sxth_mind.schemas import ProjectMind, UserMind


class LearningAdapter(BaseAdapter):
    """
    Learning/Education adapter example.

    This adapter models a learner developing skills or knowledge.
    It demonstrates:
    - Identity types based on learning style
    - Journey stages based on skill acquisition
    - Pattern detection for learning pace and struggles
    - Nudges for practice reminders and breakthroughs

    Usage:
        from sxth_mind import Mind
        from examples.learning import LearningAdapter

        mind = Mind(adapter=LearningAdapter())
        response = await mind.chat("user_1", "I want to learn Python")
    """

    @property
    def name(self) -> str:
        return "learning"

    @property
    def display_name(self) -> str:
        return "Learning Coach"

    # ═══════════════════════════════════════════════════════════════
    # Identity Model
    # ═══════════════════════════════════════════════════════════════

    def get_identity_types(self) -> list[dict[str, Any]]:
        """Learning style types."""
        return [
            {
                "key": "conceptual",
                "label": "Conceptual Learner",
                "traits": ["needs the big picture", "asks 'why'", "theory first"],
                "description": "Learns best by understanding concepts before practice",
            },
            {
                "key": "hands_on",
                "label": "Hands-On Learner",
                "traits": ["learn by doing", "examples first", "trial and error"],
                "description": "Learns best through practice and experimentation",
            },
            {
                "key": "structured",
                "label": "Structured Learner",
                "traits": ["step-by-step", "clear path", "checkpoints"],
                "description": "Prefers organized curriculum with clear progression",
            },
            {
                "key": "explorer",
                "label": "Explorer",
                "traits": ["curiosity-driven", "tangents welcome", "self-directed"],
                "description": "Learns by exploring topics of interest freely",
            },
        ]

    def get_identity_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "style": {
                    "type": "string",
                    "enum": ["conceptual", "hands_on", "structured", "explorer"],
                },
                "preferred_format": {"type": "string"},  # video, text, interactive
                "session_length": {"type": "string"},  # short, medium, long
                "strong_areas": {"type": "array", "items": {"type": "string"}},
                "struggle_areas": {"type": "array", "items": {"type": "string"}},
            },
        }

    # ═══════════════════════════════════════════════════════════════
    # Journey Model (Learning Stages)
    # ═══════════════════════════════════════════════════════════════

    def get_journey_stages(self) -> list[dict[str, Any]]:
        """Learning progression stages."""
        return [
            {
                "key": "exploring",
                "label": "Exploring",
                "tone": "encouraging",
                "guidance": """User is exploring a new topic. Help with:
- Understanding what the topic involves
- Setting realistic expectations
- Identifying starting points
- Building initial interest
Be welcoming and help them find their entry point.""",
            },
            {
                "key": "foundations",
                "label": "Building Foundations",
                "tone": "patient",
                "guidance": """User is learning fundamentals. Help with:
- Core concepts and terminology
- Basic exercises and examples
- Building mental models
- Connecting new ideas to what they know
Be patient. Foundations take time.""",
            },
            {
                "key": "practicing",
                "label": "Practicing",
                "tone": "supportive",
                "guidance": """User is practicing skills. Help with:
- Deliberate practice suggestions
- Debugging and troubleshooting
- Recognizing progress
- Handling frustration
Encourage persistence. Struggle is part of learning.""",
            },
            {
                "key": "applying",
                "label": "Applying",
                "tone": "challenging",
                "guidance": """User is applying skills to real problems. Help with:
- Project ideas at their level
- Connecting concepts to practice
- Code/design review
- Expanding beyond tutorials
Challenge them appropriately. They're ready.""",
            },
            {
                "key": "deepening",
                "label": "Deepening",
                "tone": "collaborative",
                "guidance": """User is deepening expertise. Help with:
- Advanced topics and edge cases
- Best practices and patterns
- Teaching others (solidifies learning)
- Exploring related areas
Treat them as a peer. They have solid foundations.""",
            },
            {
                "key": "stuck",
                "label": "Stuck",
                "tone": "compassionate",
                "guidance": """User is stuck or frustrated. Help with:
- Identifying the specific blocker
- Breaking down the problem
- Alternative explanations
- Encouragement without being dismissive
Be patient. Everyone gets stuck.""",
            },
        ]

    def detect_journey_stage(self, project_mind: ProjectMind) -> str:
        """Detect stage based on learning progress."""
        # Check explicit stage
        stage = project_mind.get_context_field("learning_stage")
        if stage:
            return stage

        # Check for stuck indicators
        stuck_count = project_mind.get_progress_field("stuck_count", 0)
        if stuck_count >= 3:
            return "stuck"

        # Infer from progress
        interactions = project_mind.interaction_count
        exercises_completed = project_mind.get_progress_field("exercises_completed", 0)
        projects_completed = project_mind.get_progress_field("projects_completed", 0)

        if interactions < 5:
            return "exploring"
        elif exercises_completed < 5:
            return "foundations"
        elif projects_completed == 0:
            return "practicing"
        elif projects_completed < 3:
            return "applying"
        else:
            return "deepening"

    # ═══════════════════════════════════════════════════════════════
    # Proactive Intelligence
    # ═══════════════════════════════════════════════════════════════

    def get_nudge_templates(self) -> dict[str, dict[str, Any]]:
        return {
            "practice_reminder": {
                "title": "Time to practice?",
                "template": "It's been {days} days since you practiced {topic}. Ready to continue?",
                "priority": 5,
            },
            "stuck_help": {
                "title": "Need help?",
                "template": "Looks like you've been stuck on {topic}. Want to try a different approach?",
                "priority": 7,
            },
            "milestone": {
                "title": "Nice progress!",
                "template": "You've completed {count} exercises in {topic}. You're building momentum!",
                "priority": 4,
            },
            "new_topic": {
                "title": "Ready for more?",
                "template": "You've got solid foundations in {topic}. Ready to explore {next_topic}?",
                "priority": 5,
            },
            "review_suggestion": {
                "title": "Quick review?",
                "template": "It's been a while since you worked with {topic}. A quick review might help.",
                "priority": 4,
            },
        }

    def get_insight_types(self) -> list[dict[str, Any]]:
        return [
            {
                "key": "learning_pattern",
                "label": "Learning Pattern",
                "severity": "info",
                "description": "Pattern in how the user learns best",
            },
            {
                "key": "struggle_area",
                "label": "Struggle Area",
                "severity": "warning",
                "description": "Topic that consistently causes difficulty",
            },
            {
                "key": "strength",
                "label": "Strength Identified",
                "severity": "info",
                "description": "Area where user shows aptitude",
            },
            {
                "key": "breakthrough",
                "label": "Breakthrough",
                "severity": "info",
                "description": "Significant understanding achieved",
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
Learning Style: {identity_type['label']}
Traits: {', '.join(identity_type['traits'])}
"""

        # Build progress context
        progress_context = ""
        exercises = project_mind.get_progress_field("exercises_completed", 0)
        projects = project_mind.get_progress_field("projects_completed", 0)
        topic = project_mind.get_context_field("current_topic", "the topic")
        if exercises > 0 or projects > 0:
            progress_context = f"""
Current topic: {topic}
Exercises completed: {exercises}
Projects completed: {projects}
"""

        # Build pattern context
        pattern_context = ""
        if user_mind.patterns:
            patterns = []
            if user_mind.patterns.get("strong_areas"):
                patterns.append(f"Strong in: {', '.join(user_mind.patterns['strong_areas'][:3])}")
            if user_mind.patterns.get("struggle_areas"):
                patterns.append(f"Struggles with: {', '.join(user_mind.patterns['struggle_areas'][:3])}")
            if user_mind.patterns.get("preferred_explanations"):
                patterns.append(f"Prefers: {user_mind.patterns['preferred_explanations']}")
            if patterns:
                pattern_context = "\n".join(patterns)

        return f"""You are a patient and knowledgeable Learning Coach.

## Your Role
You help users learn new skills and concepts. You adapt to their learning style,
meet them where they are, and help them progress at their own pace.

{identity_context}

## Current Stage: {stage_info['label']}
Tone: {stage_info['tone']}
{stage_info['guidance']}

## Progress
{progress_context if progress_context else "Just getting started."}

## Patterns & Insights
{pattern_context if pattern_context else "Still learning their style."}
Total sessions: {user_mind.total_interactions}

## Guidelines
- Adapt explanations to their learning style
- Use examples and analogies
- Break complex topics into digestible pieces
- Celebrate progress, no matter how small
- When they're stuck, try different approaches
- Reference what they've learned before
- Suggest practice when appropriate
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
        """Update state after interaction with learning-specific logic."""
        # Basic updates
        user_mind.increment_interactions()
        project_mind.increment_interactions()
        project_mind.update_momentum()

        # Update journey stage
        new_stage = self.detect_journey_stage(project_mind)
        if new_stage != project_mind.journey_stage:
            project_mind.journey_stage = new_stage

        # Detect patterns
        self._detect_patterns(user_mind, project_mind, message)

    def _detect_patterns(
        self, user_mind: UserMind, project_mind: ProjectMind, message: str
    ) -> None:
        """Detect learning-specific patterns."""
        message_lower = message.lower()

        # Track struggle indicators
        struggle_keywords = ["don't understand", "confused", "stuck", "help", "lost", "frustrated"]
        if any(kw in message_lower for kw in struggle_keywords):
            stuck_count = project_mind.get_progress_field("stuck_count", 0)
            project_mind.set_progress_field("stuck_count", stuck_count + 1)
        else:
            # Reset stuck count on non-struggle messages
            project_mind.set_progress_field("stuck_count", 0)

        # Track completion indicators
        completion_keywords = ["done", "finished", "completed", "got it", "makes sense", "understand now"]
        if any(kw in message_lower for kw in completion_keywords):
            exercises = project_mind.get_progress_field("exercises_completed", 0)
            project_mind.set_progress_field("exercises_completed", exercises + 1)

        # Track topic preferences
        if "example" in message_lower or "show me" in message_lower:
            user_mind.patterns["preferred_explanations"] = "examples"
        elif "why" in message_lower or "explain" in message_lower:
            user_mind.patterns["preferred_explanations"] = "conceptual"
        elif "practice" in message_lower or "exercise" in message_lower:
            user_mind.patterns["preferred_explanations"] = "hands-on"
