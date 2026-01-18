"""
Baseline Nudge Engine

Rule-based nudge generation. Checks conditions and generates nudges
based on adapter templates.
"""

from uuid import uuid4

from sxth_mind.adapters.base import BaseAdapter
from sxth_mind.schemas import Nudge, ProjectMind, UserMind
from sxth_mind.storage.base import BaseStorage


class BaselineNudgeEngine:
    """
    Rule-based nudge engine.

    Generates nudges based on:
    - Inactivity (days since last interaction)
    - Momentum drops
    - Stage-specific triggers
    - Pattern-based triggers

    This is intentionally simple and deterministic.
    For adaptive nudge timing that learns from user behavior,
    see Brain Engine Cloud.

    Usage:
        engine = BaselineNudgeEngine(adapter, storage)
        nudges = await engine.check_and_generate(user_id)
    """

    def __init__(self, adapter: BaseAdapter, storage: BaseStorage):
        self.adapter = adapter
        self.storage = storage

    async def check_and_generate(
        self,
        user_id: str,
        project_id: str | None = None,
    ) -> list[Nudge]:
        """
        Check conditions and generate nudges for a user.

        Args:
            user_id: User to check
            project_id: Optional specific project (checks all if None)

        Returns:
            List of newly generated nudges
        """
        user_mind = await self.storage.get_user_mind(user_id)
        if not user_mind:
            return []

        # Check if nudges are disabled
        if user_mind.nudge_frequency == "off":
            return []

        # Get project minds to check
        if project_id:
            project_mind = await self.storage.get_project_mind(user_id, project_id)
            project_minds = [project_mind] if project_mind else []
        else:
            project_minds = await self.storage.get_project_minds_for_user(user_id)

        generated = []
        templates = self.adapter.get_nudge_templates()

        for project_mind in project_minds:
            # Check each rule
            nudges = self._check_rules(user_mind, project_mind, templates)
            generated.extend(nudges)

        # Save generated nudges
        for nudge in generated:
            await self.storage.save_nudge(nudge)

        return generated

    def _check_rules(
        self,
        user_mind: UserMind,
        project_mind: ProjectMind,
        templates: dict,
    ) -> list[Nudge]:
        """Check all rules and generate matching nudges."""
        nudges = []

        # Rule: Inactivity
        if "inactivity" in templates or "stalled_deal" in templates or "comeback" in templates:
            nudge = self._check_inactivity(user_mind, project_mind, templates)
            if nudge:
                nudges.append(nudge)

        # Rule: Momentum drop
        if "momentum_drop" in templates:
            nudge = self._check_momentum_drop(user_mind, project_mind, templates)
            if nudge:
                nudges.append(nudge)

        # Rule: Streak at risk (for habits)
        if "streak_reminder" in templates:
            nudge = self._check_streak_risk(user_mind, project_mind, templates)
            if nudge:
                nudges.append(nudge)

        # Rule: Milestone reached
        if "milestone" in templates:
            nudge = self._check_milestone(user_mind, project_mind, templates)
            if nudge:
                nudges.append(nudge)

        return nudges

    def _check_inactivity(
        self,
        user_mind: UserMind,
        project_mind: ProjectMind,
        templates: dict,
    ) -> Nudge | None:
        """Check for inactivity and generate nudge if needed."""
        days = project_mind.days_since_activity

        # Determine threshold based on nudge frequency
        threshold = self._get_inactivity_threshold(user_mind.nudge_frequency)

        if days < threshold:
            return None

        # Find appropriate template
        template_key = None
        if "comeback" in templates and days >= 7:
            template_key = "comeback"
        elif "stalled_deal" in templates and days >= 5:
            template_key = "stalled_deal"
        elif "inactivity" in templates:
            template_key = "inactivity"

        if not template_key:
            return None

        template = templates[template_key]

        return Nudge(
            id=str(uuid4()),
            project_mind_id=project_mind.id,
            nudge_type=template_key,
            title=template["title"],
            message=template["template"].format(
                days=days,
                deal_name=project_mind.project_id,
                habit=project_mind.get_context_field("habit_name", "your habit"),
            ),
            priority=template.get("priority", 5),
            context={
                "days_inactive": days,
                "project_id": project_mind.project_id,
            },
        )

    def _check_momentum_drop(
        self,
        user_mind: UserMind,
        project_mind: ProjectMind,
        templates: dict,
    ) -> Nudge | None:
        """Check for momentum drop."""
        if project_mind.momentum_score >= 0.3:
            return None

        # Only trigger if they had momentum before
        if project_mind.interaction_count < 5:
            return None

        template = templates["momentum_drop"]

        return Nudge(
            id=str(uuid4()),
            project_mind_id=project_mind.id,
            nudge_type="momentum_drop",
            title=template["title"],
            message=template["template"].format(
                deal_name=project_mind.project_id,
            ),
            priority=template.get("priority", 5),
            context={
                "momentum": project_mind.momentum_score,
                "project_id": project_mind.project_id,
            },
        )

    def _check_streak_risk(
        self,
        user_mind: UserMind,
        project_mind: ProjectMind,
        templates: dict,
    ) -> Nudge | None:
        """Check if streak is at risk (for habits)."""
        streak = project_mind.get_progress_field("current_streak", 0)

        # Only remind if they have a streak worth protecting
        if streak < 3:
            return None

        # Check if it's been a day without activity
        if project_mind.days_since_activity < 1:
            return None

        template = templates["streak_reminder"]

        return Nudge(
            id=str(uuid4()),
            project_mind_id=project_mind.id,
            nudge_type="streak_reminder",
            title=template["title"],
            message=template["template"].format(
                streak=streak,
                habit=project_mind.get_context_field("habit_name", "your habit"),
            ),
            priority=template.get("priority", 5),
            context={
                "streak": streak,
                "project_id": project_mind.project_id,
            },
        )

    def _check_milestone(
        self,
        user_mind: UserMind,
        project_mind: ProjectMind,
        templates: dict,
    ) -> Nudge | None:
        """Check for milestone achievements."""
        streak = project_mind.get_progress_field("current_streak", 0)

        # Milestone thresholds
        milestones = [7, 14, 21, 30, 60, 90]

        # Check if just hit a milestone
        if streak not in milestones:
            return None

        # Check if already notified for this milestone
        notified = project_mind.get_context_field("milestones_notified", [])
        if streak in notified:
            return None

        template = templates["milestone"]

        # Mark as notified
        notified.append(streak)
        project_mind.set_context_field("milestones_notified", notified)

        return Nudge(
            id=str(uuid4()),
            project_mind_id=project_mind.id,
            nudge_type="milestone",
            title=template["title"],
            message=template["template"].format(
                streak=streak,
                habit=project_mind.get_context_field("habit_name", "your habit"),
            ),
            priority=template.get("priority", 5),
            context={
                "streak": streak,
                "milestone": streak,
                "project_id": project_mind.project_id,
            },
        )

    def _get_inactivity_threshold(self, frequency: str) -> int:
        """Get inactivity threshold based on nudge frequency preference."""
        thresholds = {
            "aggressive": 2,
            "balanced": 5,
            "minimal": 10,
            "off": 999,  # Effectively disabled
        }
        return thresholds.get(frequency, 5)


async def generate_nudges_for_all_users(
    adapter: BaseAdapter,
    storage: BaseStorage,
) -> dict[str, list[Nudge]]:
    """
    Generate nudges for all users (batch job).

    This would typically be run on a schedule (e.g., daily).

    Note: This is a placeholder. In a real implementation, you'd:
    1. Add a get_all_user_ids() method to storage
    2. Iterate over all users and generate nudges

    Returns:
        Dict mapping user_id to list of generated nudges
    """
    # Placeholder - shows the pattern for batch nudge generation
    # engine = BaselineNudgeEngine(adapter, storage)
    # results = {}
    # user_ids = await storage.get_all_user_ids()
    # for user_id in user_ids:
    #     nudges = await engine.check_and_generate(user_id)
    #     if nudges:
    #         results[user_id] = nudges
    # return results

    _ = adapter, storage  # Mark as used
    return {}
