from app.graph.repository import KuzuGraphRepository
from app.domain.entities import (
    DrugIndication,
    DrugInteraction,
    DrugTarget,
    FDASection,
    FDALabel,
    TargetDiseaseAssociation,
    TargetPathway,
)


class MedicalKnowledgeService:
    """Application service for medical knowledge retrieval."""

    def __init__(self, repository: KuzuGraphRepository) -> None:
        self.repository = repository

    def get_drug_targets(self, drug_id: int) -> list[DrugTarget]:
        return self.repository.get_drug_targets(drug_id)

    def get_drug_indications(
        self,
        drug_id: int,
    ) -> list[DrugIndication]:
        return self.repository.get_drug_indications(drug_id)

    def get_drug_interactions(
        self,
        drug_id: int,
    ) -> list[DrugInteraction]:
        return self.repository.get_drug_interactions(drug_id)

    def get_target_pathways(
        self,
        target_id: int,
    ) -> list[TargetPathway]:
        return self.repository.get_target_pathways(target_id)

    def get_target_disease_associations(
        self,
        target_id: int,
    ) -> list[TargetDiseaseAssociation]:
        return self.repository.get_target_disease_associations(target_id)

    def get_latest_fda_label(
        self,
        drug_id: int,
    ) -> FDALabel | None:
        return self.repository.get_latest_fda_label(drug_id)

    def get_fda_sections(
        self,
        drug_id: int,
        section: str | None = None,
    ) -> list[FDASection]:
        return self.repository.get_fda_sections(
            drug_id,
            section,
        )