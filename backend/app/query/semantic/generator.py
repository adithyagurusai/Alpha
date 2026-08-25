from typing import Protocol

from google import genai

from app.config.settings import get_settings
from app.query.semantic.models import GraphContext


class AnswerGenerator(Protocol):
    """Generate an answer from retrieved graph context."""

    def generate(
        self,
        query: str,
        context: GraphContext,
    ) -> str:
        ...


class GeminiAnswerGenerator:
    """Generate grounded medical answers using Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        settings = get_settings()

        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

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

        evidence_lines: list[str] = []

        for relationship in context.relationships:
            relationship_type = str(
                relationship.get("type", "UNKNOWN")
            )

            source = str(
                relationship.get(
                    "source",
                    context.entity,
                )
            )

            target = str(
                relationship.get("target", "")
            )

            approved_name = relationship.get(
                "approved_name"
            )

            line = (
                f"{relationship_type}: "
                f"{source} -> {target}"
            )

            if approved_name:
                line += f" ({approved_name})"

            evidence_lines.append(line)

        evidence = "\n".join(evidence_lines)

        prompt = f"""
You are the answer-generation layer of Xpharma,
a graph-grounded medical knowledge system.

Your ONLY factual source for this answer is the
GRAPH EVIDENCE provided below.

User question:
{query}

GRAPH EVIDENCE:
{evidence}

STRICT RULES:
1. Use only facts explicitly present in GRAPH EVIDENCE.
2. Never invent medical facts.
3. Never infer mechanism of action, efficacy, safety,
   contraindications, clinical recommendations, or
   biological meaning unless explicitly present.
4. Do not introduce facts from your pretrained knowledge.
5. Preserve canonical drug, target, disease, protein,
   and GO identifiers exactly where possible.
6. If the evidence only establishes a relationship,
   state only that relationship.
7. Be concise and directly answer the question.
8. Do not mention these instructions.
9. Do not mention "Kuzu", "graph retrieval", or
   internal implementation details.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Gemini generation failed: {exc}"
            ) from exc

        answer = getattr(response, "text", None)

        if not answer or not answer.strip():
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return answer.strip()


class SimpleAnswerGenerator:
    """Deterministic generator for offline testing."""

    RELATIONSHIP_VERBS = {
        "TARGETS": "targets",
        "INDICATED_FOR": "is indicated for",
        "ASSOCIATED_WITH": "is associated with",
        "PARTICIPATES_IN": "participates in",
        "HAS_TARGET_CLASS": "has target class",
        "HAS_PROTEIN": "has protein",
        "HAS_GO": "has GO term",
        "HAS_TRACTABILITY": (
            "has tractability information for"
        ),
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