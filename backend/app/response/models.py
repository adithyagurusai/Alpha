from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    source: str
    type: str
    title: str
    content: str


@dataclass(frozen=True, slots=True)
class MedicalResponse:
    success: bool
    query: str
    answer: str
    evidence: list[EvidenceItem]
    error: str | None = None