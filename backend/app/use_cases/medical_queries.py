from app.domain.entities import (
    DrugIndication,
    DrugInteraction,
    DrugTarget,
    FDASection,
    FDALabel,
    TargetDiseaseAssociation,
    TargetPathway,
)
from app.services.medical_knowledge import MedicalKnowledgeService


class MedicalQueryUseCase:
    """Execute deterministic medical knowledge queries."""

    def __init__(
        self,
        service: MedicalKnowledgeService,
    ) -> None:
        self.service = service

    def drug_targets(self, drug_id: int) -> list[DrugTarget]:
        return self.service.get_drug_targets(drug_id)

    def drug_indications(
        self,
        drug_id: int,
    ) -> list[DrugIndication]:
        return self.service.get_drug_indications(drug_id)

    def drug_interactions(
        self,
        drug_id: int,
    ) -> list[DrugInteraction]:
        return self.service.get_drug_interactions(drug_id)

    def target_pathways(
        self,
        target_id: int,
    ) -> list[TargetPathway]:
        return self.service.get_target_pathways(target_id)

    def target_diseases(
        self,
        target_id: int,
    ) -> list[TargetDiseaseAssociation]:
        return self.service.get_target_disease_associations(target_id)

    def latest_fda_label(
        self,
        drug_id: int,
    ) -> FDALabel | None:
        return self.service.get_latest_fda_label(drug_id)

    def fda_sections(
        self,
        drug_id: int,
        section: str | None = None,
    ) -> list[FDASection]:
        return self.service.get_fda_sections(
            drug_id,
            section,
        )