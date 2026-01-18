"""
Insight Schema

Patterns and observations detected by the Mind.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Insight(BaseModel):
    """
    An insight detected by the Mind.

    Insights are patterns, contradictions, or notable observations
    that the Mind surfaces for awareness.
    """

    id: str = Field(default="", description="Unique identifier")
    user_mind_id: str | None = Field(
        default=None, description="Reference to UserMind (if user-level)"
    )
    project_mind_id: str | None = Field(
        default=None, description="Reference to ProjectMind (if project-level)"
    )

    # Insight content
    insight_type: str = Field(
        ..., description="Type of insight (from adapter insight_types)"
    )
    title: str = Field(..., description="Short headline")
    description: str = Field(..., description="Full insight description")

    # Severity/importance
    severity: Literal["info", "warning", "critical"] = Field(
        default="info",
        description="Severity level",
    )

    # Evidence
    evidence: list[str] = Field(
        default_factory=list,
        description="Supporting evidence/examples",
    )

    # State
    acknowledged: bool = Field(
        default=False,
        description="Whether user has acknowledged this insight",
    )
    acknowledged_at: datetime | None = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"extra": "allow"}

    def acknowledge(self) -> None:
        """Mark insight as acknowledged."""
        self.acknowledged = True
        self.acknowledged_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
