from dataclasses import dataclass

from app.query.deterministic_parser import (
    DeterministicQueryParser,
    ParsedIntent,
)
from app.query.entity_resolver import EntityResolver
from app.sources.evidence_provider import MedicalEvidenceProvider
from app.use_cases.medical_queries import MedicalQueryUseCase


@dataclass(frozen=True, slots=True)
class QueryResult:
    """Structured result returned by the deterministic query engine."""

    success: bool
    intent: ParsedIntent | None
    entity: str | None
    data: object | None
    message: str | None = None


class MedicalQueryEngine:
    """Execute supported Xpharma graph queries."""

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

            if parsed.intent == ParsedIntent.DRUG_TARGET:
                data = self.use_case.drug_targets(
                    drug_id
                )
            else:
                data = self.use_case.drug_indications(
                    drug_id
                )

            return QueryResult(
                success=True,
                intent=parsed.intent,
                entity=parsed.entity,
                data=data,
            )

        if parsed.intent in {
            ParsedIntent.TARGET_PATHWAY,
            ParsedIntent.TARGET_DISEASE,
            ParsedIntent.TARGET_CLASS,
            ParsedIntent.TARGET_PROTEIN,
            ParsedIntent.TARGET_GO,
            ParsedIntent.TARGET_TRACTABILITY,
        }:
            resolved = self.resolver.resolve_target(
                parsed.entity
            )

            if resolved is None:
                return QueryResult(
                    success=False,
                    intent=parsed.intent,
                    entity=parsed.entity,
                    data=None,
                    message=(
                        f"Target '{parsed.entity}' "
                        "was not found."
                    ),
                )

            target_id = resolved.target.id

            if parsed.intent == ParsedIntent.TARGET_PATHWAY:
                data = self.use_case.target_pathways(
                    target_id
                )

            elif parsed.intent == ParsedIntent.TARGET_DISEASE:
                data = self.use_case.target_disease_associations(
                    target_id
                )

            elif parsed.intent == ParsedIntent.TARGET_CLASS:
                data = self.use_case.target_classes(
                    target_id
                )

            elif parsed.intent == ParsedIntent.TARGET_PROTEIN:
                data = self.use_case.target_proteins(
                    target_id
                )

            elif parsed.intent == ParsedIntent.TARGET_GO:
                data = self.use_case.target_go(
                    target_id
                )

            else:
                data = self.use_case.target_tractability(
                    target_id
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