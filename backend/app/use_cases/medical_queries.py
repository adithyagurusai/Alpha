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
from app.services.medical_knowledge import MedicalKnowledgeService


class MedicalQueryUseCase:
    """Execute deterministic Xpharma medical graph queries."""

    def __init__(
        self,
        service: MedicalKnowledgeService,
    ) -> None:
        self.service = service

    # ================================================================
    # DRUG
    # ================================================================

    def drug_targets(
        self,
        drug_id: str,
    ) -> list[DrugTarget]:
        return self.service.get_drug_targets(drug_id)

    def drug_indications(
        self,
        drug_id: str,
    ) -> list[DrugIndication]:
        return self.service.get_drug_indications(drug_id)

    # ================================================================
    # TARGET
    # ================================================================

    def target_pathways(
        self,
        target_id: int,
    ) -> list[TargetPathway]:
        return self.service.get_target_pathways(target_id)

    def target_disease_associations(
        self,
        target_id: int,
    ) -> list[TargetDiseaseAssociation]:
        return self.service.get_target_disease_associations(
            target_id
        )

    def target_classes(
        self,
        target_id: int,
    ) -> list[TargetClass]:
        return self.service.get_target_classes(target_id)

    def target_proteins(
        self,
        target_id: int,
    ) -> list[TargetProtein]:
        return self.service.get_target_proteins(target_id)

    def target_go(
        self,
        target_id: int,
    ) -> list[TargetGO]:
        return self.service.get_target_go(target_id)

    def target_tractability(
        self,
        target_id: int,
    ) -> list[TargetTractability]:
        return self.service.get_target_tractability(
            target_id
        )