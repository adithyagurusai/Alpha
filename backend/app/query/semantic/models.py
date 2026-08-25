from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GraphContext:
    """Context retrieved from the medical knowledge graph."""

    entity: str
    relationships: list[dict[str, object]]


@dataclass(frozen=True, slots=True)
class SemanticResult:
    """Result produced by the semantic query path."""

    success: bool
    query: str
    answer: str
    context: GraphContext | None = None
    error: str | None = None