from app.query.semantic.generator import AnswerGenerator
from app.query.semantic.models import SemanticResult
from app.query.semantic.retriever import SemanticRetriever


class SemanticQueryEngine:
    """Execute natural-language queries through graph retrieval."""

    def __init__(
        self,
        retriever: SemanticRetriever,
        generator: AnswerGenerator,
    ) -> None:
        self.retriever = retriever
        self.generator = generator

    def execute(
        self,
        query: str,
    ) -> SemanticResult:

        context = self.retriever.retrieve(query)

        if not context.relationships:
            return SemanticResult(
                success=False,
                query=query,
                answer="No relevant graph evidence was found.",
                context=context,
                error="No graph relationships found.",
            )

        answer = self.generator.generate(
            query,
            context,
        )

        return SemanticResult(
            success=True,
            query=query,
            answer=answer,
            context=context,
        )