from app.domain.entities import (
    DrugIndication,
    DrugInteraction,
    DrugTarget,
    FDASection,
)
from app.query.engine import QueryResult
from app.response.models import EvidenceItem, MedicalResponse


class MedicalResponseFormatter:
    """Convert structured query results into user-facing responses."""

    def format(
        self,
        query: str,
        result: QueryResult,
    ) -> MedicalResponse:

        if not result.success:
            return MedicalResponse(
                success=False,
                query=query,
                answer=result.message or "Unable to answer the query.",
                evidence=[],
                error=result.message,
            )

        data = result.data or []

        if result.intent is None:
            return MedicalResponse(
                success=False,
                query=query,
                answer="Unable to determine the query intent.",
                evidence=[],
                error="Missing query intent.",
            )

        if result.intent.value == "drug_target":
            return self._format_drug_targets(
                query,
                data,
            )

        if result.intent.value == "drug_disease":
            return self._format_drug_indications(
                query,
                data,
            )

        if result.intent.value == "drug_interaction":
            return self._format_drug_interactions(
                query,
                data,
            )

        if result.intent.value in {
            "drug_contraindication",
            "drug_adverse_effect",
        }:
            return self._format_fda_sections(
                query,
                data,
            )

        return MedicalResponse(
            success=False,
            query=query,
            answer="This query type is not supported.",
            evidence=[],
            error="Unsupported response type.",
        )

    def _format_drug_targets(
        self,
        query: str,
        data: object,
    ) -> MedicalResponse:

        targets = data if isinstance(data, list) else []

        if not targets:
            return MedicalResponse(
                success=True,
                query=query,
                answer="No target relationships were found.",
                evidence=[],
            )

        drug_name = targets[0].drug_name

        lines = [
            f"{drug_name} targets:"
        ]

        evidence: list[EvidenceItem] = []

        for item in targets:
            target: DrugTarget = item

            lines.append(
                f"- {target.target.name}: "
                f"{target.target.approved_name}"
            )

            evidence.append(
                EvidenceItem(
                    source="Kuzu medical graph",
                    type="TARGET_RELATIONSHIP",
                    title=target.target.name,
                    content=(
                        f"{target.drug_name} targets "
                        f"{target.target.name}."
                    ),
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\n".join(lines),
            evidence=evidence,
        )

    def _format_drug_indications(
        self,
        query: str,
        data: object,
    ) -> MedicalResponse:

        indications = data if isinstance(data, list) else []

        if not indications:
            return MedicalResponse(
                success=True,
                query=query,
                answer="No clinical indications were found.",
                evidence=[],
            )

        drug_name = indications[0].drug_name

        lines = [
            f"{drug_name} clinical indications:"
        ]

        evidence: list[EvidenceItem] = []

        for item in indications:
            indication: DrugIndication = item

            lines.append(
                f"- {indication.disease.name} "
                f"({indication.max_clinical_stage})"
            )

            evidence.append(
                EvidenceItem(
                    source="Kuzu medical graph",
                    type="CLINICAL_INDICATION",
                    title=indication.disease.name,
                    content=(
                        f"{drug_name} is indicated for "
                        f"{indication.disease.name}."
                    ),
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\n".join(lines),
            evidence=evidence,
        )

    def _format_drug_interactions(
        self,
        query: str,
        data: object,
    ) -> MedicalResponse:

        interactions = data if isinstance(data, list) else []

        if not interactions:
            return MedicalResponse(
                success=True,
                query=query,
                answer="No drug interactions were found.",
                evidence=[],
            )

        drug_name = interactions[0].drug_name

        lines = [
            f"{drug_name} interactions:"
        ]

        evidence: list[EvidenceItem] = []

        for item in interactions:
            interaction: DrugInteraction = item

            lines.append(
                f"- {interaction.interacting_drug.name}"
            )

            evidence.append(
                EvidenceItem(
                    source="Kuzu medical graph",
                    type="DRUG_INTERACTION",
                    title=interaction.interacting_drug.name,
                    content=(
                        f"{drug_name} interacts with "
                        f"{interaction.interacting_drug.name}."
                    ),
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\n".join(lines),
            evidence=evidence,
        )

    def _format_fda_sections(
        self,
        query: str,
        data: object,
    ) -> MedicalResponse:

        evidence_items = (
            data
            if isinstance(data, list)
            else []
        )

        if not evidence_items:
            return MedicalResponse(
                success=True,
                query=query,
                answer="No FDA evidence was found.",
                evidence=[],
            )

        first = evidence_items[0]

        lines = [
            f"FDA evidence — {first.evidence_type}:"
        ]

        evidence: list[EvidenceItem] = []

        for item in evidence_items:
            lines.append(
                f"\n{item.content}"
            )

            evidence.append(
                EvidenceItem(
                    source=item.source,
                    type=item.evidence_type,
                    title=item.title,
                    content=item.content,
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\n".join(lines),
            evidence=evidence,
        )