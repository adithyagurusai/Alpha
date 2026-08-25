from app.query.semantic.models import GraphContext


class SimpleAnswerGenerator:
    """Generate concise deterministic answers from graph context."""

    RELATIONSHIP_VERBS = {
        "TARGETS": "targets",
        "INDICATED_FOR": "is indicated for",
        "ASSOCIATED_WITH": "is associated with",
        "PARTICIPATES_IN": "participates in",
        "HAS_TARGET_CLASS": "has target class",
        "HAS_PROTEIN": "has protein",
        "HAS_GO": "has GO term",
        "HAS_TRACTABILITY": "has tractability information for",
    }

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

        lines: list[str] = []

        for relationship in context.relationships:
            relationship_type = str(
                relationship.get("type", "")
            )

            target = str(
                relationship.get("target", "")
            )

            verb = self.RELATIONSHIP_VERBS.get(
                relationship_type,
                "has a relationship with",
            )

            approved_name = relationship.get(
                "approved_name"
            )

            if (
                relationship_type == "TARGETS"
                and approved_name
            ):
                lines.append(
                    f"{context.entity} {verb} "
                    f"{target} "
                    f"({approved_name})."
                )
            else:
                lines.append(
                    f"{context.entity} {verb} "
                    f"{target}."
                )

        return "\n".join(lines)