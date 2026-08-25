from app.graph.repository import KuzuGraphRepository
from app.query.entity_resolver import EntityResolver
from app.query.semantic.models import GraphContext
from app.query.semantic.query_analyzer import SemanticQueryAnalyzer


class KuzuSemanticRetriever:
    """Retrieve relevant graph context for semantic queries."""

    def __init__(
        self,
        repository: KuzuGraphRepository,
        resolver: EntityResolver,
        analyzer: SemanticQueryAnalyzer,
    ) -> None:
        self.repository = repository
        self.resolver = resolver
        self.analyzer = analyzer

    def retrieve(
        self,
        query: str,
    ) -> GraphContext:

        parsed = self.analyzer.analyze(query)

        if not parsed.entity:
            return GraphContext(
                entity=query,
                relationships=[],
            )

        if (
            parsed.relation == "relationship"
            and parsed.related_entity
        ):
            return self._retrieve_relationship(
                parsed.entity,
                parsed.related_entity,
            )

        resolved_drug = self.resolver.resolve_drug(
            parsed.entity
        )

        if resolved_drug is not None:
            return self._retrieve_drug(
                resolved_drug.drug.id,
                resolved_drug.drug.name,
                parsed.relation,
            )

        resolved_target = self.resolver.resolve_target(
            parsed.entity
        )

        if resolved_target is not None:
            return self._retrieve_target(
                resolved_target.target.id,
                resolved_target.target.name,
                parsed.relation,
            )

        return GraphContext(
            entity=parsed.entity,
            relationships=[],
        )

    def _retrieve_relationship(
        self,
        entity_name: str,
        related_entity_name: str,
    ) -> GraphContext:

        drug = self.resolver.resolve_drug(
            entity_name
        )

        if drug is not None:
            targets = self.repository.get_drug_targets(
                drug.drug.id
            )

            relationships: list[dict[str, object]] = []

            for item in targets:
                if (
                    item.target.name.upper()
                    == related_entity_name.upper()
                    or item.target.approved_name.upper()
                    == related_entity_name.upper()
                ):
                    relationships.append(
                        {
                            "type": "TARGETS",
                            "source": drug.drug.name,
                            "target": item.target.name,
                            "target_id": item.target.id,
                            "approved_name": (
                                item.target.approved_name
                            ),
                        }
                    )

            return GraphContext(
                entity=drug.drug.name,
                relationships=relationships,
            )

        target = self.resolver.resolve_target(
            entity_name
        )

        if target is not None:
            diseases = (
                self.repository
                .get_target_disease_associations(
                    target.target.id
                )
            )

            relationships: list[dict[str, object]] = []

            for item in diseases:
                if (
                    item.disease.name.upper()
                    == related_entity_name.upper()
                ):
                    relationships.append(
                        {
                            "type": "ASSOCIATED_WITH",
                            "source": target.target.name,
                            "target": item.disease.name,
                            "disease_id": item.disease.id,
                            "score": item.score,
                        }
                    )

            return GraphContext(
                entity=target.target.name,
                relationships=relationships,
            )

        return GraphContext(
            entity=entity_name,
            relationships=[],
        )

    def _retrieve_drug(
        self,
        drug_id: str,
        drug_name: str,
        relation: str | None,
    ) -> GraphContext:

        relationships: list[dict[str, object]] = []

        if relation == "targets":
            for item in self.repository.get_drug_targets(
                drug_id
            ):
                relationships.append(
                    {
                        "type": "TARGETS",
                        "source": drug_name,
                        "target": item.target.name,
                        "target_id": item.target.id,
                        "approved_name": (
                            item.target.approved_name
                        ),
                    }
                )

        elif relation == "indications":
            for item in self.repository.get_drug_indications(
                drug_id
            ):
                relationships.append(
                    {
                        "type": "INDICATED_FOR",
                        "source": drug_name,
                        "target": item.disease.name,
                        "disease_id": item.disease.id,
                        "clinical_stage": (
                            item.max_clinical_stage
                        ),
                    }
                )

        return GraphContext(
            entity=drug_name,
            relationships=relationships,
        )

    def _retrieve_target(
        self,
        target_id: int,
        target_name: str,
        relation: str | None,
    ) -> GraphContext:

        relationships: list[dict[str, object]] = []

        if relation == "diseases":
            for item in (
                self.repository
                .get_target_disease_associations(
                    target_id
                )
            ):
                relationships.append(
                    {
                        "type": "ASSOCIATED_WITH",
                        "source": target_name,
                        "target": item.disease.name,
                        "disease_id": item.disease.id,
                        "score": item.score,
                    }
                )

        elif relation == "pathways":
            for item in self.repository.get_target_pathways(
                target_id
            ):
                relationships.append(
                    {
                        "type": "PARTICIPATES_IN",
                        "source": target_name,
                        "target": item.pathway.name,
                        "pathway_id": item.pathway.id,
                    }
                )

        elif relation == "classes":
            for item in self.repository.get_target_classes(
                target_id
            ):
                relationships.append(
                    {
                        "type": "HAS_TARGET_CLASS",
                        "source": target_name,
                        "target": item.label,
                        "class_id": item.id,
                        "level": item.level,
                    }
                )

        elif relation == "proteins":
            for item in self.repository.get_target_proteins(
                target_id
            ):
                relationships.append(
                    {
                        "type": "HAS_PROTEIN",
                        "source": target_name,
                        "target": item.id,
                        "protein_key": item.protein_key,
                        "source_db": item.source,
                    }
                )

        elif relation == "go":
            for item in self.repository.get_target_go(
                target_id
            ):
                relationships.append(
                    {
                        "type": "HAS_GO",
                        "source": target_name,
                        "target": item.id,
                    }
                )

        elif relation == "tractability":
            for item in (
                self.repository
                .get_target_tractability(
                    target_id
                )
            ):
                relationships.append(
                    {
                        "type": "HAS_TRACTABILITY",
                        "source": target_name,
                        "target": item.id,
                        "modality": item.modality,
                        "value": item.value,
                    }
                )

        return GraphContext(
            entity=target_name,
            relationships=relationships,
        )