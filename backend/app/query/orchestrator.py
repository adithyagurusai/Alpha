from app.query.deterministic_parser import (
    DeterministicQueryParser,
)
from app.query.engine import MedicalQueryEngine
from app.query.modes import QueryMode
from app.query.results import (
    UnifiedQueryResult,
    from_deterministic,
    from_semantic,
)
from app.query.semantic.engine import SemanticQueryEngine


class QueryOrchestrator:
    """Route queries between deterministic and semantic execution."""

    def __init__(
        self,
        deterministic_engine: MedicalQueryEngine,
        semantic_engine: SemanticQueryEngine,
        parser: DeterministicQueryParser,
    ) -> None:
        self.deterministic_engine = deterministic_engine
        self.semantic_engine = semantic_engine
        self.parser = parser

    def execute(
        self,
        query: str,
        mode: QueryMode = QueryMode.AUTO,
    ) -> UnifiedQueryResult:

        if mode == QueryMode.DETERMINISTIC:
            result = self.deterministic_engine.execute(
                query
            )

            return from_deterministic(
                query,
                result,
            )

        if mode == QueryMode.SEMANTIC:
            result = self.semantic_engine.execute(
                query
            )

            return from_semantic(result)

        parsed = self.parser.parse(query)

        if parsed is not None:
            result = self.deterministic_engine.execute(
                query
            )

            return from_deterministic(
                query,
                result,
            )

        result = self.semantic_engine.execute(
            query
        )

        return from_semantic(result)