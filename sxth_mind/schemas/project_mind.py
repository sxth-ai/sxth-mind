"""
ProjectMind Schema

The project-level cognitive model. Captures context, progress, and state
for a specific project/conversation thread.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


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

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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
        """Increment interaction count and update timestamp."""
        self.interaction_count += 1
        self.last_interaction = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_momentum(self) -> None:
        """Update momentum based on activity."""
        self.days_since_activity = 0
        # Simple momentum boost on activity
        self.momentum_score = min(1.0, self.momentum_score + 0.1)
        self.updated_at = datetime.utcnow()
