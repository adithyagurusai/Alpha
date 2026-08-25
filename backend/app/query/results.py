from dataclasses import dataclass

from app.query.engine import QueryResult
from app.query.semantic.models import SemanticResult
from app.response.formatter import MedicalResponseFormatter


@dataclass(frozen=True, slots=True)
class UnifiedQueryResult:
    """Common result contract for deterministic and semantic queries."""

    success: bool
    query: str
    answer: str
    evidence: list[dict[str, object]]
    error: str | None = None
    mode: str = "unknown"


def from_deterministic(
    query: str,
    result: QueryResult,
) -> UnifiedQueryResult:
    """Convert a deterministic result into the unified response."""

    formatter = MedicalResponseFormatter()

    response = formatter.format(
        query,
        result,
    )

    evidence = [
        {
            "source": item.source,
            "type": item.type,
            "title": item.title,
            "content": item.content,
        }
        for item in response.evidence
    ]

    return UnifiedQueryResult(
        success=response.success,
        query=response.query,
        answer=response.answer,
        evidence=evidence,
        error=response.error,
        mode="deterministic",
    )


def from_semantic(
    result: SemanticResult,
) -> UnifiedQueryResult:
    """Convert a semantic result into the unified response."""

    evidence: list[dict[str, object]] = []

    if result.context is not None:
        for relationship in result.context.relationships:
            relationship_type = str(
                relationship.get(
                    "type",
                    "graph",
                )
            )

            source = str(
                relationship.get(
                    "source",
                    result.context.entity,
                )
            )

            target = str(
                relationship.get(
                    "target",
                    "",
                )
            )

            evidence.append(
                {
                    "source": "Kuzu medical graph",
                    "type": relationship_type,
                    "title": target,
                    "content": (
                        f"{source} "
                        f"{_relationship_verb(relationship_type)} "
                        f"{target}."
                    ),
                }
            )

    return UnifiedQueryResult(
        success=result.success,
        query=result.query,
        answer=result.answer,
        evidence=evidence,
        error=result.error,
        mode="semantic",
    )


def _relationship_verb(
    relationship_type: str,
) -> str:
    """Convert graph relationship types into readable evidence text."""

    verbs = {
        "TARGETS": "targets",
        "INDICATED_FOR": "is indicated for",
        "ASSOCIATED_WITH": "is associated with",
        "PARTICIPATES_IN": "participates in",
        "HAS_TARGET_CLASS": "has target class",
        "HAS_PROTEIN": "has protein",
        "HAS_GO": "has GO term",
        "HAS_TRACTABILITY": "has tractability attribute",
    }

    return verbs.get(
        relationship_type,
        "has relationship with",
    )