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


class DeterministicQueryParser:
    """Classify supported medical queries using explicit rules."""

    def parse(self, query: str) -> ParsedQuery | None:
        normalized = self._normalize(query)

        rules = (
            (
                ParsedIntent.DRUG_TARGET,
                (
                    "what does ",
                    " target",
                ),
            ),
            (
                ParsedIntent.DRUG_DISEASE,
                (
                    "what diseases does ",
                    " treat",
                ),
            ),
            (
                ParsedIntent.DRUG_DISEASE,
                (
                    "what is ",
                    " used for",
                ),
            ),
            (
                ParsedIntent.DRUG_DISEASE,
                (
                    "indications for ",
                    "",
                ),
            ),
            (
                ParsedIntent.DRUG_INTERACTION,
                (
                    "what drugs interact with ",
                    "",
                ),
            ),
            (
                ParsedIntent.DRUG_INTERACTION,
                (
                    "drug interactions for ",
                    "",
                ),
            ),
            (
                ParsedIntent.DRUG_INTERACTION,
                (
                    "interactions of ",
                    "",
                ),
            ),
            (
                ParsedIntent.DRUG_CONTRAINDICATION,
                (
                    "what are the contraindications of ",
                    "",
                ),
            ),
            (
                ParsedIntent.DRUG_CONTRAINDICATION,
                (
                    "contraindications for ",
                    "",
                ),
            ),
            (
                ParsedIntent.DRUG_ADVERSE_EFFECT,
                (
                    "what are the adverse effects of ",
                    "",
                ),
            ),
            (
                ParsedIntent.DRUG_ADVERSE_EFFECT,
                (
                    "what are the side effects of ",
                    "",
                ),
            ),
            (
                ParsedIntent.DRUG_ADVERSE_EFFECT,
                (
                    "side effects of ",
                    "",
                ),
            ),
        )

        for intent, (prefix, suffix) in rules:
            entity = self._extract_entity(
                normalized,
                prefix,
                suffix,
            )

            if entity:
                return ParsedQuery(
                    intent=intent,
                    entity=entity,
                )

        return None

    @staticmethod
    def _normalize(query: str) -> str:
        return " ".join(
            query.strip().lower().rstrip("?").split()
        )

    @staticmethod
    def _extract_entity(
        query: str,
        prefix: str,
        suffix: str,
    ) -> str | None:
        if not query.startswith(prefix):
            return None

        if suffix:
            if not query.endswith(suffix):
                return None

            entity = query[
                len(prefix):-len(suffix)
            ].strip()
        else:
            entity = query[len(prefix):].strip()

        if not entity:
            return None

        return entity.upper()