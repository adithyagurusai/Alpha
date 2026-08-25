from app.query.semantic.models import GraphContext


class SimpleAnswerGenerator:
    """Generate deterministic answers from graph context."""

    def generate(
        self,
        query: str,
        context: GraphContext,
    ) -> str:

        if not context.relationships:
            return (
                f"No relevant graph relationships were found "
                f"for {context.entity}."
            )

        lines = [
            f"Graph evidence for {context.entity}:"
        ]

        for relationship in context.relationships:
            relationship_type = relationship["type"]
            target = relationship["target"]

            lines.append(
                f"- {relationship_type}: "
                f"{context.entity} → {target}"
            )

        return "\n".join(lines)