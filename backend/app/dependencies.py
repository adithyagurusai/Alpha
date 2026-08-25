from functools import lru_cache

from app.config.settings import Settings, get_settings
from app.graph.repository import KuzuGraphRepository
from app.query.deterministic_parser import DeterministicQueryParser
from app.query.engine import MedicalQueryEngine
from app.query.entity_resolver import EntityResolver
from app.query.orchestrator import QueryOrchestrator
from app.query.semantic.engine import SemanticQueryEngine
from app.query.semantic.kuzu_retriever import KuzuSemanticRetriever
from app.query.semantic.query_analyzer import SemanticQueryAnalyzer
from app.query.semantic.generator import GeminiAnswerGenerator
from app.services.medical_knowledge import MedicalKnowledgeService
from app.sources.evidence_provider import MedicalEvidenceProvider
from app.sources.fda import OpenFDADataSource
from app.sources.kuzu import KuzuEvidenceSource
from app.sources.label_selector import FDALabelSelector
from app.use_cases.medical_queries import MedicalQueryUseCase


@lru_cache
def get_app_settings() -> Settings:
    return get_settings()


def build_query_engine() -> QueryOrchestrator:
    settings = get_app_settings()

    repository = KuzuGraphRepository(
        settings.database_path
    )

    service = MedicalKnowledgeService(
        repository
    )

    use_case = MedicalQueryUseCase(
        service
    )

    parser = DeterministicQueryParser()

    resolver = EntityResolver(
        repository.connection
    )

    # --------------------------------------------------------------
    # FDA evidence
    # --------------------------------------------------------------

    graph_source = KuzuEvidenceSource(
        repository
    )

    fda_source = OpenFDADataSource(
        timeout=settings.fda_timeout_seconds
    )

    label_selector = FDALabelSelector()

    evidence_provider = MedicalEvidenceProvider(
        graph_source=graph_source,
        fda_source=fda_source,
        label_selector=label_selector,
    )

    # --------------------------------------------------------------
    # Deterministic engine
    # --------------------------------------------------------------

    deterministic_engine = MedicalQueryEngine(
        parser=parser,
        resolver=resolver,
        use_case=use_case,
        evidence_provider=evidence_provider,
    )

    # --------------------------------------------------------------
    # Semantic engine
    # --------------------------------------------------------------

    analyzer = SemanticQueryAnalyzer()

    retriever = KuzuSemanticRetriever(
        repository=repository,
        resolver=resolver,
        analyzer=analyzer,
    )

    generator = GeminiAnswerGenerator()

    semantic_engine = SemanticQueryEngine(
        retriever=retriever,
        generator=generator,
    )

    # --------------------------------------------------------------
    # Dual-mode orchestrator
    # --------------------------------------------------------------

    return QueryOrchestrator(
        deterministic_engine=deterministic_engine,
        semantic_engine=semantic_engine,
        parser=parser,
    )