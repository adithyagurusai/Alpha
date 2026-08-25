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
from app.query.engine import QueryResult
from app.response.models import EvidenceItem, MedicalResponse


class MedicalResponseFormatter:
    """Convert Xpharma graph query results into user-facing responses."""

    def format(
        self,
        query: str,
        result: QueryResult,
    ) -> MedicalResponse:

        if not result.success:
            return MedicalResponse(
                success=False,
                query=query,
                answer=(
                    result.message
                    or "Unable to answer the query."
                ),
                evidence=[],
                error=result.message,
            )

        if result.intent is None:
            return MedicalResponse(
                success=False,
                query=query,
                answer="Unable to determine the query intent.",
                evidence=[],
                error="Missing query intent.",
            )

        data = result.data or []

        # ------------------------------------------------------------
        # Drug queries
        # ------------------------------------------------------------

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

        # ------------------------------------------------------------
        # Target queries
        # ------------------------------------------------------------

        if result.intent.value == "target_pathway":
            return self._format_target_pathways(
                query,
                data,
            )

        if result.intent.value == "target_disease":
            return self._format_target_diseases(
                query,
                data,
            )

        if result.intent.value == "target_class":
            return self._format_target_classes(
                query,
                data,
            )

        if result.intent.value == "target_protein":
            return self._format_target_proteins(
                query,
                data,
            )

        if result.intent.value == "target_go":
            return self._format_target_go(
                query,
                data,
            )

        if result.intent.value == "target_tractability":
            return self._format_target_tractability(
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

    # ================================================================
    # DRUG → TARGET
    # ================================================================

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
                        f"{drug_name} targets "
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

    # ================================================================
    # DRUG → DISEASE
    # ================================================================

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
            f"{drug_name} clinical-stage disease associations:"
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
                        f"{drug_name} is associated with "
                        f"{indication.disease.name} "
                        f"at {indication.max_clinical_stage}."
                    ),
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\n".join(lines),
            evidence=evidence,
        )

    # ================================================================
    # TARGET → PATHWAY
    # ================================================================

    def _format_target_pathways(
        self,
        query: str,
        data: object,
    ) -> MedicalResponse:

        pathways = data if isinstance(data, list) else []

        if not pathways:
            return MedicalResponse(
                success=True,
                query=query,
                answer="No pathway relationships were found.",
                evidence=[],
            )

        target_name = pathways[0].target_name

        lines = [
            f"{target_name} participates in:"
        ]

        evidence: list[EvidenceItem] = []

        for item in pathways:
            pathway: TargetPathway = item

            lines.append(
                f"- {pathway.pathway.name}"
            )

            evidence.append(
                EvidenceItem(
                    source="Kuzu medical graph",
                    type="PATHWAY_RELATIONSHIP",
                    title=pathway.pathway.name,
                    content=(
                        f"{target_name} participates in "
                        f"{pathway.pathway.name}."
                    ),
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\n".join(lines),
            evidence=evidence,
        )

    # ================================================================
    # TARGET → DISEASE
    # ================================================================

    def _format_target_diseases(
        self,
        query: str,
        data: object,
    ) -> MedicalResponse:

        associations = (
            data if isinstance(data, list) else []
        )

        if not associations:
            return MedicalResponse(
                success=True,
                query=query,
                answer="No disease associations were found.",
                evidence=[],
            )

        target_name = associations[0].target_name

        lines = [
            f"{target_name} is associated with:"
        ]

        evidence: list[EvidenceItem] = []

        for item in sorted(associations, key=lambda x: x.score, reverse=True)[:10]:
            association: TargetDiseaseAssociation = item

            lines.append(
                f"- {association.disease.name} "
                f"(score: {association.score:.4f})"
            )

            evidence.append(
                EvidenceItem(
                    source="Kuzu medical graph",
                    type="DISEASE_ASSOCIATION",
                    title=association.disease.name,
                    content=(
                        f"{target_name} is associated with "
                        f"{association.disease.name} "
                        f"with an association score of "
                        f"{association.score:.4f}."
                    ),
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\n".join(lines),
            evidence=evidence,
        )

    # ================================================================
    # TARGET → CLASS
    # ================================================================

    def _format_target_classes(
        self,
        query: str,
        data: object,
    ) -> MedicalResponse:

        classes = data if isinstance(data, list) else []

        if not classes:
            return MedicalResponse(
                success=True,
                query=query,
                answer="No target classification was found.",
                evidence=[],
            )

        lines = [
            "Target classification:"
        ]

        evidence: list[EvidenceItem] = []

        for item in classes:
            target_class: TargetClass = item

            lines.append(
                f"- {target_class.level}: "
                f"{target_class.label}"
            )

            evidence.append(
                EvidenceItem(
                    source="Kuzu medical graph",
                    type="TARGET_CLASS",
                    title=target_class.label,
                    content=(
                        f"{target_class.level}: "
                        f"{target_class.label}."
                    ),
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\n".join(lines),
            evidence=evidence,
        )

    # ================================================================
    # TARGET → PROTEIN
    # ================================================================

    def _format_target_proteins(
        self,
        query: str,
        data: object,
    ) -> MedicalResponse:

        proteins = data if isinstance(data, list) else []

        if not proteins:
            return MedicalResponse(
                success=True,
                query=query,
                answer="No associated proteins were found.",
                evidence=[],
            )

        lines = [
            "Associated proteins:"
        ]

        evidence: list[EvidenceItem] = []

        for item in proteins:
            protein: TargetProtein = item

            lines.append(
                f"- {protein.id} "
                f"({protein.source})"
            )

            evidence.append(
                EvidenceItem(
                    source="Kuzu medical graph",
                    type="PROTEIN_ASSOCIATION",
                    title=protein.id,
                    content=(
                        f"Protein {protein.id} "
                        f"from {protein.source}."
                    ),
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\n".join(lines),
            evidence=evidence,
        )

    # ================================================================
    # TARGET → GO
    # ================================================================

    def _format_target_go(
        self,
        query: str,
        data: object,
    ) -> MedicalResponse:

        terms = data if isinstance(data, list) else []

        if not terms:
            return MedicalResponse(
                success=True,
                query=query,
                answer="No GO terms were found.",
                evidence=[],
            )

        lines = [
            "Associated GO terms:"
        ]

        evidence: list[EvidenceItem] = []

        for item in terms:
            go: TargetGO = item

            lines.append(
                f"- {go.id}"
            )

            evidence.append(
                EvidenceItem(
                    source="Kuzu medical graph",
                    type="GO_ASSOCIATION",
                    title=go.id,
                    content=(
                        f"Associated Gene Ontology term: "
                        f"{go.id}."
                    ),
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\n".join(lines),
            evidence=evidence,
        )

    # ================================================================
    # TARGET → TRACTABILITY
    # ================================================================

    def _format_target_tractability(
        self,
        query: str,
        data: object,
    ) -> MedicalResponse:

        tractability = (
            data if isinstance(data, list) else []
        )

        if not tractability:
            return MedicalResponse(
                success=True,
                query=query,
                answer="No tractability information was found.",
                evidence=[],
            )

        lines = [
            "Target tractability:"
        ]

        evidence: list[EvidenceItem] = []

        for item in tractability:
            value: TargetTractability = item

            status = "Yes" if value.value else "No"

            lines.append(
                f"- {value.id} | "
                f"modality: {value.modality} | "
                f"value: {status}"
            )

            evidence.append(
                EvidenceItem(
                    source="Kuzu medical graph",
                    type="TRACTABILITY",
                    title=value.id,
                    content=(
                        f"{value.id} | "
                        f"modality: {value.modality} | "
                        f"value: {status}."
                    ),
                )
            )

        return MedicalResponse(
            success=True,
            query=query,
            answer="\\n".join(lines),
            evidence=evidence,
        )
