from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Drug:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class Target:
    id: int
    name: str
    external_id: str
    approved_name: str


@dataclass(frozen=True, slots=True)
class Disease:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class Pathway:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class TargetClass:
    class_key: str
    id: int
    label: str
    level: str


@dataclass(frozen=True, slots=True)
class DrugTarget:
    drug_id: str
    drug_name: str
    target: Target


@dataclass(frozen=True, slots=True)
class DrugIndication:
    drug_id: str
    drug_name: str
    disease: Disease
    max_clinical_stage: str


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
class TargetProtein:
    protein_key: str
    id: str
    source: str


@dataclass(frozen=True, slots=True)
class TargetGO:
    id: str


@dataclass(frozen=True, slots=True)
class TargetTractability:
    tractability_key: str
    modality: str
    id: str
    value: bool