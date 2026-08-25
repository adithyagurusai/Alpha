from typing import Protocol

from app.query.semantic.models import GraphContext


class SemanticRetriever(Protocol):
    """Retrieve graph context for semantic queries."""

    def retrieve(
        self,
        query: str,
    ) -> GraphContext:
        ...