from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class SemanticQuery:
    """Normalized information extracted from a semantic query."""

    entity: str | None
    related_entity: str | None
    relation: str | None


class SemanticQueryAnalyzer:
    """Extract entities and relationship intent from a query."""

    SINGLE_ENTITY_RULES = (
        (
            r"what does (.+?) target",
            "targets",
        ),
        (
            r"what are the targets of (.+)",
            "targets",
        ),
        (
            r"what diseases does (.+?) treat",
            "indications",
        ),
        (
            r"what diseases is (.+?) associated with",
            "diseases",
        ),
        (
            r"what proteins are associated with (.+)",
            "proteins",
        ),
        (
            r"what go terms are associated with (.+)",
            "go",
        ),
        (
            r"what is the tractability of (.+)",
            "tractability",
        ),
        (
            r"what pathways does (.+?) participate in",
            "pathways",
        ),
        (
            r"what class does (.+?) belong to",
            "classes",
        ),
    )

    def analyze(
        self,
        query: str,
    ) -> SemanticQuery:

        normalized = " ".join(
            query.strip()
            .rstrip("?")
            .split()
        )

        relationship = re.fullmatch(
            r"how is (.+?) related to (.+)",
            normalized,
            flags=re.IGNORECASE,
        )

        if relationship:
            return SemanticQuery(
                entity=relationship.group(1).strip(),
                related_entity=relationship.group(2).strip(),
                relation="relationship",
            )

        for pattern, relation in self.SINGLE_ENTITY_RULES:
            match = re.fullmatch(
                pattern,
                normalized,
                flags=re.IGNORECASE,
            )

            if match:
                return SemanticQuery(
                    entity=match.group(1).strip(),
                    related_entity=None,
                    relation=relation,
                )

        return SemanticQuery(
            entity=None,
            related_entity=None,
            relation=None,
        )