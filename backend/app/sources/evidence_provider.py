from app.sources.fda import FDADataSource
from app.sources.label_selector import FDALabelSelector
from app.sources.models import ExternalEvidence


class MedicalEvidenceProvider:
    """
    Resolve external FDA evidence.

    FDA data is intentionally kept outside the Open Targets/Kuzu graph.
    """

    def __init__(
        self,
        fda_source: FDADataSource,
        label_selector: FDALabelSelector,
    ) -> None:
        self.fda_source = fda_source
        self.label_selector = label_selector

    def get_fda_evidence(
        self,
        drug_name: str,
        section: str,
    ) -> list[ExternalEvidence]:

        external_evidence = self.fda_source.search_drug(
            drug_name
        )

        section_evidence = [
            item
            for item in external_evidence
            if item.evidence_type == section
        ]

        selected = self.label_selector.select(
            section_evidence,
            evidence_type=section,
        )

        return selected.evidence