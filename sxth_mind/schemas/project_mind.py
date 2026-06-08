"""
ProjectMind Schema

The project-level cognitive model. Captures context, progress, and state
for a specific project/conversation thread.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from sxth_mind._time import utcnow

# Momentum lost per day of inactivity.
MOMENTUM_DECAY_PER_DAY = 0.1
# Momentum gained when the user interacts.
MOMENTUM_BOOST = 0.1
# Fraction of the remaining gap to full trust closed per interaction.
TRUST_GROWTH_RATE = 0.02


class ProjectMind(BaseModel):
    """
    ProjectMind represents accumulated understanding about a project.

    This is the project-level cognitive model that captures:
    - Journey stage: Where the user is in their journey
    - Momentum: Engagement level and activity patterns
    - Context: Domain-specific project context
    - Progress: What's been accomplished, what's stuck

    A user can have multiple ProjectMinds (one per project/thread).
    The context_data and progress_data fields are flexible - adapters
    define what these mean for their domain.
    """

    # Identification
    id: str = Field(default="", description="Unique identifier")
    user_mind_id: str = Field(..., description="Reference to parent UserMind")
    project_id: str = Field(..., description="External project ID from your system")

    # Project type hint for the adapter
    project_type: str | None = Field(
        default=None,
        description="Project type (e.g., 'deal', 'study_path', 'habit')",
    )

    # Journey stage (adapter-defined)
    journey_stage: str | None = Field(
        default=None,
        description="Current journey stage (adapter-specific)",
    )

    # Engagement metrics
    momentum_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Engagement momentum (0.0-1.0)",
    )
    days_since_activity: int = Field(
        default=0,
        ge=0,
        description="Days since last activity",
    )

    # Relationship state for this project
    trust_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Trust score for this project (0.0-1.0)",
    )
    interaction_count: int = Field(
        default=0,
        ge=0,
        description="Interactions on this project",
    )
    last_interaction: datetime | None = Field(
        default=None,
        description="Last interaction on this project",
    )

    # Nudge preferences (project-level overrides)
    nudge_frequency_override: str | None = Field(
        default=None,
        description="Override nudge frequency for this project",
    )
    muted_topics_override: list[str] | None = Field(
        default=None,
        description="Override muted topics for this project",
    )

    # Domain-specific context (adapter interprets this)
    context_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific project context",
    )

    # Domain-specific progress tracking
    progress_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific progress data",
    )

    # Derived conversation understanding (OWNED belief state, not raw bytes).
    # The raw messages live in an EvidenceSource; these are the consolidated,
    # cognition-produced views of them. Populated by summarization/consolidation.
    conversation_summary: str | None = Field(
        default=None,
        description="Running summary of conversation history beyond the recent window",
    )
    topics: list[str] = Field(
        default_factory=list,
        description="Key topics/themes derived from conversation",
    )

    # Timestamps
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    model_config = {"extra": "allow"}

    # Helper methods for context/progress access
    def get_context_field(self, field: str, default: Any = None) -> Any:
        """Get a field from context_data with a default."""
        return self.context_data.get(field, default)

    def set_context_field(self, field: str, value: Any) -> None:
        """Set a field in context_data."""
        self.context_data[field] = value

    def get_progress_field(self, field: str, default: Any = None) -> Any:
        """Get a field from progress_data with a default."""
        return self.progress_data.get(field, default)

    def set_progress_field(self, field: str, value: Any) -> None:
        """Set a field in progress_data."""
        self.progress_data[field] = value

    def increment_interactions(self) -> None:
        """Increment interaction count, refresh trust, and update timestamps."""
        self.interaction_count += 1
        self.last_interaction = utcnow()
        self.days_since_activity = 0
        # Trust grows toward 1.0, with diminishing returns as it approaches.
        self.trust_score = min(
            1.0, self.trust_score + (1.0 - self.trust_score) * TRUST_GROWTH_RATE
        )
        self.updated_at = utcnow()

    def update_momentum(self) -> None:
        """Boost momentum after an interaction."""
        self.days_since_activity = 0
        self.momentum_score = min(1.0, self.momentum_score + MOMENTUM_BOOST)
        self.updated_at = utcnow()

    def refresh_inactivity(self) -> int:
        """
        Recompute ``days_since_activity`` from ``last_interaction``.

        This is what makes time-based nudges fire: the field is derived from
        the wall clock rather than only being reset to 0 on each interaction.
        If ``last_interaction`` was never set, the existing value is preserved
        (callers may set it explicitly, e.g. in tests or migrations).
        """
        if self.last_interaction is not None:
            delta = utcnow() - self.last_interaction
            self.days_since_activity = max(0, delta.days)
        return self.days_since_activity

    def apply_momentum_decay(self) -> None:
        """
        Decay momentum based on how long the project has been inactive.

        Call ``refresh_inactivity()`` first so ``days_since_activity`` reflects
        the wall clock. Without this, momentum would only ever increase.
        """
        if self.days_since_activity > 0:
            self.momentum_score = max(
                0.0,
                self.momentum_score
                - MOMENTUM_DECAY_PER_DAY * self.days_since_activity,
            )
            self.updated_at = utcnow()
