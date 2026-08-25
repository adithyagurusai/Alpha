from typing import Protocol

from app.query.semantic.models import GraphContext


class AnswerGenerator(Protocol):
    """Generate an answer from retrieved graph context."""

    def generate(
        self,
        query: str,
        context: GraphContext,
    ) -> str:
        ...