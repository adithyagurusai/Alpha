from dataclasses import dataclass
from enum import Enum


class ParsedIntent(str, Enum):
    DRUG_TARGET = "drug_target"
    DRUG_DISEASE = "drug_disease"

    TARGET_PATHWAY = "target_pathway"
    TARGET_DISEASE = "target_disease"
    TARGET_CLASS = "target_class"
    TARGET_PROTEIN = "target_protein"
    TARGET_GO = "target_go"
    TARGET_TRACTABILITY = "target_tractability"


@dataclass(frozen=True, slots=True)
class ParsedQuery:
    intent: ParsedIntent
    entity: str


class DeterministicQueryParser:
    """Classify supported Xpharma graph queries using explicit rules."""

    def parse(self, query: str) -> ParsedQuery | None:
        normalized = self._normalize(query)

        rules = (
            # Drug → Target
            (
                ParsedIntent.DRUG_TARGET,
                "what does ",
                " target",
            ),
            (
                ParsedIntent.DRUG_TARGET,
                "what are the targets of ",
                "",
            ),
            (
                ParsedIntent.DRUG_TARGET,
                "targets of ",
                "",
            ),

            # Drug → Disease
            (
                ParsedIntent.DRUG_DISEASE,
                "what diseases does ",
                " treat",
            ),
            (
                ParsedIntent.DRUG_DISEASE,
                "what is ",
                " used for",
            ),
            (
                ParsedIntent.DRUG_DISEASE,
                "indications for ",
                "",
            ),
            (
                ParsedIntent.DRUG_DISEASE,
                "what are the indications for ",
                "",
            ),

            # Target → Pathway
            (
                ParsedIntent.TARGET_PATHWAY,
                "what pathways is ",
                " involved in",
            ),
            (
                ParsedIntent.TARGET_PATHWAY,
                "what pathways does ",
                " participate in",
            ),
            (
                ParsedIntent.TARGET_PATHWAY,
                "pathways for ",
                "",
            ),
            (
                ParsedIntent.TARGET_PATHWAY,
                "pathways of ",
                "",
            ),

            # Target → Disease
            (
                ParsedIntent.TARGET_DISEASE,
                "what diseases is ",
                " associated with",
            ),
            (
                ParsedIntent.TARGET_DISEASE,
                "diseases associated with ",
                "",
            ),
            (
                ParsedIntent.TARGET_DISEASE,
                "what diseases are associated with ",
                "",
            ),

            # Target → Class
            (
                ParsedIntent.TARGET_CLASS,
                "what class is ",
                "",
            ),
            (
                ParsedIntent.TARGET_CLASS,
                "what is the target class of ",
                "",
            ),
            (
                ParsedIntent.TARGET_CLASS,
                "target class of ",
                "",
            ),
            (
                ParsedIntent.TARGET_CLASS,
                "classification of ",
                "",
            ),

            # Target → Protein
            (
                ParsedIntent.TARGET_PROTEIN,
                "what proteins are associated with ",
                "",
            ),
            (
                ParsedIntent.TARGET_PROTEIN,
                "proteins associated with ",
                "",
            ),
            (
                ParsedIntent.TARGET_PROTEIN,
                "proteins for ",
                "",
            ),

            # Target → GO
            (
                ParsedIntent.TARGET_GO,
                "what go terms are associated with ",
                "",
            ),
            (
                ParsedIntent.TARGET_GO,
                "go terms associated with ",
                "",
            ),
            (
                ParsedIntent.TARGET_GO,
                "go terms for ",
                "",
            ),

            # Target → Tractability
            (
                ParsedIntent.TARGET_TRACTABILITY,
                "what is the tractability of ",
                "",
            ),
            (
                ParsedIntent.TARGET_TRACTABILITY,
                "tractability of ",
                "",
            ),
            (
                ParsedIntent.TARGET_TRACTABILITY,
                "how tractable is ",
                "",
            ),
        )

        for intent, prefix, suffix in rules:
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
        """
        Normalize query formatting without changing
        the casing of biomedical entity identifiers.
        """
        return " ".join(
            query.strip().rstrip("?").split()
        )

    @staticmethod
    def _extract_entity(
        query: str,
        prefix: str,
        suffix: str,
    ) -> str | None:

        # Query language is case-insensitive, but entity
        # identifiers must retain their original casing.
        query_lower = query.lower()

        if not query_lower.startswith(prefix):
            return None

        if suffix:
            if not query_lower.endswith(suffix):
                return None

            entity = query[
                len(prefix):-len(suffix)
            ].strip()
        else:
            entity = query[len(prefix):].strip()

        if not entity:
            return None

        return entity