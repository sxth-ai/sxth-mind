"""
Base Adapter Interface

Abstract base class that defines the contract for domain adapters.
Adapters define domain-specific behavior: identity types, journey stages,
nudge templates, and tools.
"""

from abc import ABC, abstractmethod
from typing import Any

from sxth_mind.schemas import ProjectMind, UserMind


class BaseAdapter(ABC):
    """
    Base class for domain adapters.

    Adapters define the domain-specific behavior:
    - Identity model (sales rep types, student types, etc.)
    - Journey stages and detection logic
    - Nudge templates and triggers
    - Insight types
    - System prompt customizations

    Example domains:
    - Sales: identity = rep style, stages = prospecting/negotiating/closing
    - Learning: identity = learning style, stages = beginner/intermediate/advanced
    - Habits: identity = personality type, stages = forming/maintaining/mastered
    """

    # ═══════════════════════════════════════════════════════════════
    # REQUIRED: Adapter Identity
    # ═══════════════════════════════════════════════════════════════

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique adapter name (e.g., 'sales', 'learning', 'habits')."""
        pass

    @property
    def display_name(self) -> str:
        """Human-readable adapter name."""
        return self.name.replace("_", " ").title()

    # ═══════════════════════════════════════════════════════════════
    # REQUIRED: Identity Model
    # ═══════════════════════════════════════════════════════════════

    @abstractmethod
    def get_identity_types(self) -> list[dict[str, Any]]:
        """
        Return available identity types for this domain.

        Example (Sales):
        [
            {"key": "hunter", "label": "Hunter", "traits": ["aggressive", "cold-outreach"]},
            {"key": "farmer", "label": "Farmer", "traits": ["relationship", "retention"]},
            {"key": "consultant", "label": "Consultant", "traits": ["advisory", "solutions"]},
        ]
        """
        pass

    def get_identity_schema(self) -> dict[str, Any]:
        """
        Return JSON schema for identity_data field validation.
        Override to add domain-specific validation.
        """
        return {"type": "object", "properties": {}, "additionalProperties": True}

    # ═══════════════════════════════════════════════════════════════
    # REQUIRED: Journey Model
    # ═══════════════════════════════════════════════════════════════

    @abstractmethod
    def get_journey_stages(self) -> list[dict[str, Any]]:
        """
        Return journey stage definitions.

        Each stage should have:
        - key: Unique identifier
        - label: Display name
        - tone: Recommended AI tone
        - guidance: Instructions for AI behavior at this stage
        """
        pass

    @abstractmethod
    def detect_journey_stage(self, project_mind: ProjectMind) -> str:
        """
        Detect current journey stage from project state.

        Returns stage key (must match a key from get_journey_stages).
        """
        pass

    def get_stage_guidance(self, stage: str) -> str:
        """Get AI guidance instructions for a stage."""
        stages = {s["key"]: s for s in self.get_journey_stages()}
        return stages.get(stage, {}).get("guidance", "")

    def get_stage_tone(self, stage: str) -> str:
        """Get recommended AI tone for a stage."""
        stages = {s["key"]: s for s in self.get_journey_stages()}
        return stages.get(stage, {}).get("tone", "balanced")

    # ═══════════════════════════════════════════════════════════════
    # REQUIRED: Proactive Intelligence
    # ═══════════════════════════════════════════════════════════════

    @abstractmethod
    def get_nudge_templates(self) -> dict[str, dict[str, Any]]:
        """
        Return nudge templates for this domain.

        Each template should have:
        - title: Short headline
        - template: Message with {placeholders}
        - priority: 1-10 (higher = more important)
        """
        pass

    @abstractmethod
    def get_insight_types(self) -> list[dict[str, Any]]:
        """
        Return insight types this domain supports.

        Example:
        [
            {"key": "pattern", "label": "Behavioral Pattern", "severity": "info"},
            {"key": "risk", "label": "Risk Detected", "severity": "warning"},
        ]
        """
        pass

    # ═══════════════════════════════════════════════════════════════
    # OPTIONAL: System Prompt Customization
    # ═══════════════════════════════════════════════════════════════

    def get_system_prompt(self, user_mind: UserMind, project_mind: ProjectMind) -> str:
        """
        Build the system prompt for this domain.

        Override to provide domain-specific AI personality and instructions.
        """
        stage = project_mind.journey_stage or self.detect_journey_stage(project_mind)
        stage_guidance = self.get_stage_guidance(stage)
        stage_tone = self.get_stage_tone(stage)

        identity_context = ""
        if user_mind.identity_type:
            identity_context = f"User identity type: {user_mind.identity_type}"

        return f"""You are a helpful AI assistant for {self.display_name}.

{identity_context}

Current journey stage: {stage}
Recommended tone: {stage_tone}

{stage_guidance}

Be helpful and adapt to the user's context and history.
"""

    def get_context_for_prompt(
        self, user_mind: UserMind, project_mind: ProjectMind
    ) -> dict[str, Any]:
        """
        Build context dict to include in prompts.

        Override to add domain-specific context.
        """
        return {
            "identity_type": user_mind.identity_type,
            "identity_data": user_mind.identity_data,
            "journey_stage": project_mind.journey_stage,
            "interaction_count": project_mind.interaction_count,
            "momentum_score": project_mind.momentum_score,
            "patterns": user_mind.patterns,
        }

    # ═══════════════════════════════════════════════════════════════
    # OPTIONAL: State Updates
    # ═══════════════════════════════════════════════════════════════

    def update_after_interaction(
        self,
        user_mind: UserMind,
        project_mind: ProjectMind,
        message: str,
        response: str,
    ) -> None:
        """
        Update minds after an interaction.

        Override to add domain-specific state updates (pattern detection, etc.)
        Default implementation just increments counters.
        """
        user_mind.increment_interactions()
        project_mind.increment_interactions()
        project_mind.update_momentum()

        # Update journey stage
        new_stage = self.detect_journey_stage(project_mind)
        if new_stage != project_mind.journey_stage:
            project_mind.journey_stage = new_stage
