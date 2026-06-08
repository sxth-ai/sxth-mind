"""Evidence sources — the rented raw substrate sxth-mind reads but does not own."""

from sxth_mind.evidence.base import EvidenceSource
from sxth_mind.evidence.local import LocalEvidenceSource

__all__ = ["EvidenceSource", "LocalEvidenceSource"]
