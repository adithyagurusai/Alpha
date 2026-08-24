from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Drug:
    id: int
    name: str


@dataclass(frozen=True, slots=True)
class Target:
    id: int
    name: str
    external_id: str
    approved_name: str
    target_class: str


@dataclass(frozen=True, slots=True)
class Disease:
    id: int
    name: str


@dataclass(frozen=True, slots=True)
class Pathway:
    id: int
    name: str


@dataclass(frozen=True, slots=True)
class DrugTarget:
    drug_id: int
    drug_name: str
    target: Target


@dataclass(frozen=True, slots=True)
class DrugIndication:
    drug_id: int
    drug_name: str
    disease: Disease
    max_clinical_stage: str


@dataclass(frozen=True, slots=True)
class DrugInteraction:
    drug_id: int
    drug_name: str
    interacting_drug: Drug


@dataclass(frozen=True, slots=True)
class TargetPathway:
    target_id: int
    target_name: str
    pathway: Pathway


@dataclass(frozen=True, slots=True)
class TargetDiseaseAssociation:
    target_id: int
    target_name: str
    disease: Disease
    score: float


@dataclass(frozen=True, slots=True)
class FDALabel:
    id: str
    set_id: str
    effective_time: str
    version: str
    spl_id: str
    title: str


@dataclass(frozen=True, slots=True)
class FDASection:
    id: str
    section: str
    text: str