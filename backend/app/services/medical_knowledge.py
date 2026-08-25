from app.domain.entities import (
    DrugIndication,
    DrugTarget,
    TargetClass,
    TargetDiseaseAssociation,
    TargetGO,
    TargetPathway,
    TargetProtein,
    TargetTractability,
)
from app.graph.repository import KuzuGraphRepository


class MedicalKnowledgeService:
    """Application service for Xpharma medical graph retrieval."""

    def __init__(
        self,
        repository: KuzuGraphRepository,
    ) -> None:
        self.repository = repository

    def get_drug_targets(
        self,
        drug_id: str,
    ) -> list[DrugTarget]:
        return self.repository.get_drug_targets(drug_id)

    def get_drug_indications(
        self,
        drug_id: str,
    ) -> list[DrugIndication]:
        return self.repository.get_drug_indications(drug_id)

    def get_target_pathways(
        self,
        target_id: int,
    ) -> list[TargetPathway]:
        return self.repository.get_target_pathways(target_id)

    def get_target_classes(
        self,
        target_id: int,
    ) -> list[TargetClass]:
        return self.repository.get_target_classes(target_id)

    def get_target_disease_associations(
        self,
        target_id: int,
    ) -> list[TargetDiseaseAssociation]:
        return self.repository.get_target_disease_associations(
            target_id
        )

    def get_target_proteins(
        self,
        target_id: int,
    ) -> list[TargetProtein]:
        return self.repository.get_target_proteins(target_id)

    def get_target_go(
        self,
        target_id: int,
    ) -> list[TargetGO]:
        return self.repository.get_target_go(target_id)

    def get_target_tractability(
        self,
        target_id: int,
    ) -> list[TargetTractability]:
        return self.repository.get_target_tractability(
            target_id
        )