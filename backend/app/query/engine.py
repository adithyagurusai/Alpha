from dataclasses import dataclass

from app.domain.entities import (
    DrugIndication,
    DrugInteraction,
    DrugTarget,
    FDASection,
)
from app.query.deterministic_parser import DeterministicQueryParser
from app.query.entity_resolver import EntityResolver
from app.query.parser import ParsedIntent
from app.sources.evidence_provider import MedicalEvidenceProvider
from app.sources.models import ExternalEvidence
from app.use_cases.medical_queries import MedicalQueryUseCase


@dataclass(frozen=True, slots=True)
class QueryResult:
    """Structured result returned by the query engine."""

    success: bool
    intent: ParsedIntent | None
    entity: str | None
    data: object | None
    message: str | None = None


class MedicalQueryEngine:
    """Execute supported natural-language medical queries."""

    def __init__(
        self,
        parser: DeterministicQueryParser,
        resolver: EntityResolver,
        use_case: MedicalQueryUseCase,
        evidence_provider: MedicalEvidenceProvider,
    ) -> None:
        self.parser = parser
        self.resolver = resolver
        self.use_case = use_case
        self.evidence_provider = evidence_provider

    def execute(self, query: str) -> QueryResult:
        parsed = self.parser.parse(query)

        if parsed is None:
            return QueryResult(
                success=False,
                intent=None,
                entity=None,
                data=None,
                message="Unsupported medical query.",
            )

        if parsed.intent in {
            ParsedIntent.DRUG_TARGET,
            ParsedIntent.DRUG_DISEASE,
            ParsedIntent.DRUG_INTERACTION,
            ParsedIntent.DRUG_CONTRAINDICATION,
            ParsedIntent.DRUG_ADVERSE_EFFECT,
        }:
            resolved = self.resolver.resolve_drug(
                parsed.entity
            )

            if resolved is None:
                return QueryResult(
                    success=False,
                    intent=parsed.intent,
                    entity=parsed.entity,
                    data=None,
                    message=(
                        f"Drug '{parsed.entity}' "
                        "was not found."
                    ),
                )

            drug_id = resolved.drug.id
            drug_name = resolved.drug.name

            if parsed.intent == ParsedIntent.DRUG_TARGET:
                data: list[DrugTarget] = (
                    self.use_case.drug_targets(drug_id)
                )

            elif parsed.intent == ParsedIntent.DRUG_DISEASE:
                data = self.use_case.drug_indications(
                    drug_id
                )

            elif parsed.intent == ParsedIntent.DRUG_INTERACTION:
                data = self.use_case.drug_interactions(
                    drug_id
                )

            elif parsed.intent == ParsedIntent.DRUG_CONTRAINDICATION:
                data = self.evidence_provider.get_fda_evidence(
                    drug_id=drug_id,
                    drug_name=drug_name,
                    section="contraindications",
                )

            else:
                data = self.evidence_provider.get_fda_evidence(
                    drug_id=drug_id,
                    drug_name=drug_name,
                    section="adverse_reactions",
                )

            return QueryResult(
                success=True,
                intent=parsed.intent,
                entity=parsed.entity,
                data=data,
            )

        return QueryResult(
            success=False,
            intent=parsed.intent,
            entity=parsed.entity,
            data=None,
            message="This query intent is not implemented.",
        )