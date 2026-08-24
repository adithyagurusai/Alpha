from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExternalEvidence:
    """Normalized evidence returned by an external source."""

    source: str
    evidence_type: str
    title: str
    content: str

    label_id: str | None = None
    set_id: str | None = None
    effective_time: str | None = None
    version: str | None = None