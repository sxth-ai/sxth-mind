"""
Habit Coach Adapter

Example adapter for habit tracking and building.
Demonstrates journey stages for behavior change.
"""

from typing import Any

from sxth_mind.adapters.base import BaseAdapter
from sxth_mind.schemas import ProjectMind, UserMind


class HabitCoachAdapter(BaseAdapter):
    """
    Habit building/tracking adapter example.

    This adapter models a user building and maintaining habits.
    It demonstrates:
    - Identity types based on habit-building style
    - Journey stages based on habit formation
    - Pattern detection for consistency and struggles
    - Nudges for streak maintenance and recovery

    Usage:
        from sxth_mind import Mind
        from examples.habits import HabitCoachAdapter

        mind = Mind(adapter=HabitCoachAdapter())
        response = await mind.chat("user_1", "I want to start exercising")
    """

    @property
    def name(self) -> str:
        return "habits"

    @property
    def display_name(self) -> str:
        return "Habit Coach"

    # ═══════════════════════════════════════════════════════════════
    # Identity Model
    # ═══════════════════════════════════════════════════════════════

    def get_identity_types(self) -> list[dict[str, Any]]:
        """Habit-building personality types."""
        return [
            {
                "key": "all_or_nothing",
                "label": "All-or-Nothing",
                "traits": ["intense starts", "struggles with setbacks", "high standards"],
                "description": "Goes hard but may quit after missing a day",
            },
            {
                "key": "slow_builder",
                "label": "Slow Builder",
                "traits": ["gradual progress", "patient", "sustainable"],
                "description": "Prefers small consistent steps over big changes",
            },
            {
                "key": "accountability_seeker",
                "label": "Accountability Seeker",
                "traits": ["external motivation", "social", "check-ins"],
                "description": "Thrives with reminders and external support",
            },
            {
                "key": "self_motivated",
                "label": "Self-Motivated",
                "traits": ["internal drive", "independent", "self-tracking"],
                "description": "Doesn't need external motivation, self-directed",
            },
        ]

    def get_identity_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "style": {
                    "type": "string",
                    "enum": ["all_or_nothing", "slow_builder", "accountability_seeker", "self_motivated"],
                },
                "best_time": {"type": "string", "description": "Preferred time for habits"},
                "motivation_style": {"type": "string"},
                "past_successes": {"type": "array", "items": {"type": "string"}},
                "common_blockers": {"type": "array", "items": {"type": "string"}},
            },
        }

    # ═══════════════════════════════════════════════════════════════
    # Journey Model (Habit Formation Stages)
    # ═══════════════════════════════════════════════════════════════

    def get_journey_stages(self) -> list[dict[str, Any]]:
        """Habit formation stages."""
        return [
            {
                "key": "starting",
                "label": "Starting",
                "tone": "encouraging",
                "guidance": """User is just starting a new habit. Help with:
- Setting realistic expectations
- Defining a tiny, achievable version of the habit
- Identifying triggers and cues
- Building initial motivation
Be encouraging but realistic. Focus on starting small.""",
            },
            {
                "key": "struggling",
                "label": "Struggling",
                "tone": "supportive",
                "guidance": """User is struggling with consistency. Help with:
- Identifying what's blocking them
- Reducing friction
- Finding alternative approaches
- Maintaining motivation despite setbacks
Be compassionate. Normalize struggle as part of the process.""",
            },
            {
                "key": "building",
                "label": "Building Momentum",
                "tone": "motivating",
                "guidance": """User is building consistency. Help with:
- Celebrating small wins
- Increasing difficulty gradually
- Habit stacking
- Tracking progress
Reinforce the emerging pattern. Build confidence.""",
            },
            {
                "key": "consistent",
                "label": "Consistent",
                "tone": "reinforcing",
                "guidance": """User has achieved consistency. Help with:
- Maintaining the habit
- Adding variations or increasing challenge
- Connecting to deeper goals
- Preparing for potential disruptions
Celebrate the achievement. Help them level up.""",
            },
            {
                "key": "recovering",
                "label": "Recovering",
                "tone": "compassionate",
                "guidance": """User broke a streak and is recovering. Help with:
- Not catastrophizing the setback
- Getting back on track quickly
- Learning from what happened
- Rebuilding momentum
Be gentle. One miss doesn't erase progress.""",
            },
        ]

    def detect_journey_stage(self, project_mind: ProjectMind) -> str:
        """Detect stage based on project context and patterns."""
        # Check explicit stage
        stage = project_mind.get_context_field("habit_stage")
        if stage:
            return stage

        # Check for recovery situation
        days_since = project_mind.days_since_activity
        streak = project_mind.get_progress_field("current_streak", 0)

        if days_since > 3 and streak == 0:
            return "recovering"

        # Infer from patterns
        interactions = project_mind.interaction_count
        momentum = project_mind.momentum_score

        if interactions < 5:
            return "starting"
        elif momentum < 0.3:
            return "struggling"
        elif streak >= 14:
            return "consistent"
        elif streak >= 3:
            return "building"
        else:
            return "struggling"

    # ═══════════════════════════════════════════════════════════════
    # Proactive Intelligence
    # ═══════════════════════════════════════════════════════════════

    def get_nudge_templates(self) -> dict[str, dict[str, Any]]:
        return {
            "streak_reminder": {
                "title": "Keep your streak going!",
                "template": "You're on a {streak}-day streak with {habit}. Don't break the chain!",
                "priority": 7,
            },
            "missed_day": {
                "title": "One day doesn't define you",
                "template": "Missed yesterday? That's okay. Today is a fresh start for {habit}.",
                "priority": 6,
            },
            "milestone": {
                "title": "Milestone reached!",
                "template": "You've done {habit} for {streak} days! That's building real momentum.",
                "priority": 5,
            },
            "time_reminder": {
                "title": "Habit time",
                "template": "It's around the time you usually do {habit}. Ready?",
                "priority": 4,
            },
            "comeback": {
                "title": "Ready to restart?",
                "template": "It's been {days} days since {habit}. Want to get back on track?",
                "priority": 8,
            },
        }

    def get_insight_types(self) -> list[dict[str, Any]]:
        return [
            {
                "key": "pattern",
                "label": "Behavioral Pattern",
                "severity": "info",
                "description": "Recurring pattern in habit behavior",
            },
            {
                "key": "blocker",
                "label": "Blocker Identified",
                "severity": "warning",
                "description": "Something that consistently blocks the habit",
            },
            {
                "key": "success_factor",
                "label": "Success Factor",
                "severity": "info",
                "description": "Something that helps the habit stick",
            },
            {
                "key": "streak_risk",
                "label": "Streak at Risk",
                "severity": "warning",
                "description": "Patterns suggesting streak might break",
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
Habit-Building Style: {identity_type['label']}
Traits: {', '.join(identity_type['traits'])}
"""

        # Build progress context
        progress_context = ""
        streak = project_mind.get_progress_field("current_streak", 0)
        longest_streak = project_mind.get_progress_field("longest_streak", 0)
        if streak > 0 or longest_streak > 0:
            progress_context = f"""
Current streak: {streak} days
Longest streak: {longest_streak} days
"""

        # Build pattern context
        pattern_context = ""
        if user_mind.patterns:
            patterns = []
            if user_mind.patterns.get("best_time"):
                patterns.append(f"Best time: {user_mind.patterns['best_time']}")
            if user_mind.patterns.get("common_blockers"):
                patterns.append(f"Common blockers: {', '.join(user_mind.patterns['common_blockers'][:3])}")
            if patterns:
                pattern_context = "\n".join(patterns)

        return f"""You are a supportive Habit Coach helping users build lasting habits.

## Your Role
You help users start, maintain, and recover habits. You understand that
behavior change is hard and setbacks are normal. You're encouraging but realistic.

{identity_context}

## Current Stage: {stage_info['label']}
Tone: {stage_info['tone']}
{stage_info['guidance']}

## Progress
{progress_context if progress_context else "No streak data yet."}

## Patterns & History
{pattern_context if pattern_context else "No patterns detected yet."}
Total check-ins: {user_mind.total_interactions}

## Guidelines
- Be encouraging but don't be fake
- Celebrate small wins genuinely
- Normalize setbacks - they're part of the process
- Focus on consistency over perfection
- Reference past patterns when relevant
- Suggest tiny habits when they're struggling
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
        """Update state after interaction with habit-specific logic."""
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
        """Detect habit-specific patterns."""
        message_lower = message.lower()

        # Track blockers mentioned
        blockers = user_mind.patterns.get("common_blockers", [])
        blocker_keywords = {
            "tired": "fatigue",
            "exhausted": "fatigue",
            "busy": "time",
            "no time": "time",
            "forgot": "forgetfulness",
            "lazy": "motivation",
            "unmotivated": "motivation",
        }

        for keyword, blocker in blocker_keywords.items():
            if keyword in message_lower and blocker not in blockers:
                blockers.append(blocker)

        user_mind.patterns["common_blockers"] = blockers[-5:]  # Keep last 5

        # Track success mentions
        success_keywords = ["did it", "completed", "done", "finished", "streak"]
        if any(kw in message_lower for kw in success_keywords):
            completions = project_mind.get_progress_field("completions", 0)
            project_mind.set_progress_field("completions", completions + 1)

            # Update streak
            current_streak = project_mind.get_progress_field("current_streak", 0)
            project_mind.set_progress_field("current_streak", current_streak + 1)

            # Update longest streak
            longest = project_mind.get_progress_field("longest_streak", 0)
            if current_streak + 1 > longest:
                project_mind.set_progress_field("longest_streak", current_streak + 1)

        # Track skip/miss mentions
        skip_keywords = ["missed", "skipped", "didn't", "failed", "broke"]
        if any(kw in message_lower for kw in skip_keywords):
            project_mind.set_progress_field("current_streak", 0)
