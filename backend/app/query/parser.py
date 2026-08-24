from dataclasses import dataclass
from enum import Enum


class ParsedIntent(str, Enum):
    DRUG_TARGET = "drug_target"
    DRUG_DISEASE = "drug_disease"
    DRUG_INTERACTION = "drug_interaction"
    TARGET_PATHWAY = "target_pathway"
    TARGET_DISEASE = "target_disease"
    DRUG_CONTRAINDICATION = "drug_contraindication"
    DRUG_ADVERSE_EFFECT = "drug_adverse_effect"


@dataclass(frozen=True, slots=True)
class ParsedQuery:
    intent: ParsedIntent
    entity: str