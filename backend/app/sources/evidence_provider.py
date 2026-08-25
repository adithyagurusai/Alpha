from typing import Protocol

from app.sources.fda import FDADataSource
from app.sources.label_selector import FDALabelSelector
from app.sources.models import ExternalEvidence


class GraphEvidenceSource(Protocol):
    """Interface for FDA evidence stored in the local graph."""

    def get_fda_sections(
        self,
        drug_id: int,
        section: str,
    ) -> list[ExternalEvidence]:
        ...


class MedicalEvidenceProvider:
    """
    Resolve FDA evidence using Kuzu first and OpenFDA fallback.

    Priority:
        1. Kuzu
        2. OpenFDA
    """

    def __init__(
        self,
        graph_source: GraphEvidenceSource,
        fda_source: FDADataSource,
        label_selector: FDALabelSelector,
    ) -> None:
        self.graph_source = graph_source
        self.fda_source = fda_source
        self.label_selector = label_selector

    def get_fda_evidence(
        self,
        drug_id: int,
        drug_name: str,
        section: str,
    ) -> list[ExternalEvidence]:

        graph_evidence = self.graph_source.get_fda_sections(
            drug_id,
            section,
        )

        if graph_evidence:
            return graph_evidence

        external_evidence = self.fda_source.search_drug(
            drug_name
        )

        section_evidence = [
            item
            for item in external_evidence
            if item.evidence_type == section
        ]

        if not section_evidence:
            return []

        selected = self.label_selector.select(
            section_evidence,
            evidence_type=section,
        )

        return selected.evidence