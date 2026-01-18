"""
UserMind Schema

The user-level cognitive model. Captures identity, patterns, and preferences
that persist across all projects/conversations for a user.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UserMind(BaseModel):
    """
    UserMind represents accumulated understanding about a user.

    This is the user-level cognitive model that captures:
    - Identity: Who the user is (archetype, role, style)
    - Patterns: Behavioral patterns detected over time
    - Preferences: Communication and interaction preferences
    - Trust: Relationship depth with the AI

    The identity_data field is flexible JSONB - adapters define
    what identity means for their domain.
    """

    # Identification
    id: str = Field(default="", description="Unique identifier")
    user_id: str = Field(..., description="External user ID from your system")

    # Trust and engagement
    trust_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Trust level (0.0-1.0), evolves with interactions",
    )
    total_interactions: int = Field(
        default=0,
        ge=0,
        description="Total interactions across all projects",
    )
    last_interaction: datetime | None = Field(
        default=None,
        description="Timestamp of last interaction",
    )

    # Communication preferences
    preferred_tone: str = Field(
        default="balanced",
        description="Preferred AI tone: direct, encouraging, patient, balanced",
    )
    response_style: str = Field(
        default="balanced",
        description="Preferred response style: brief, detailed, socratic, balanced",
    )

    # Nudge preferences
    nudge_frequency: str = Field(
        default="balanced",
        description="Nudge frequency: aggressive, balanced, minimal, off",
    )
    muted_topics: list[str] = Field(
        default_factory=list,
        description="Topics the user doesn't want nudges about",
    )

    # Domain-specific identity (adapter interprets this)
    identity_type: str | None = Field(
        default=None,
        description="Identity type key (e.g., 'founder', 'student', 'sales_rep')",
    )
    identity_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific identity attributes",
    )

    # Behavioral patterns detected over time
    patterns: dict[str, Any] = Field(
        default_factory=dict,
        description="Behavioral patterns (e.g., themes, frequencies, tendencies)",
    )

    # Additional preferences
    preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional user preferences",
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"extra": "allow"}

    # Helper methods for identity data access
    def get_identity_field(self, field: str, default: Any = None) -> Any:
        """Get a field from identity_data with a default."""
        return self.identity_data.get(field, default)

    def set_identity_field(self, field: str, value: Any) -> None:
        """Set a field in identity_data."""
        self.identity_data[field] = value

    def get_pattern(self, pattern_key: str, default: Any = None) -> Any:
        """Get a pattern by key."""
        return self.patterns.get(pattern_key, default)

    def set_pattern(self, pattern_key: str, value: Any) -> None:
        """Set a pattern."""
        self.patterns[pattern_key] = value

    def increment_interactions(self) -> None:
        """Increment interaction count and update timestamp."""
        self.total_interactions += 1
        self.last_interaction = datetime.utcnow()
        self.updated_at = datetime.utcnow()
