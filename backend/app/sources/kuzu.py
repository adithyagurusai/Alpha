from app.graph.repository import KuzuGraphRepository
from app.sources.models import ExternalEvidence


class KuzuEvidenceSource:
    """Expose FDA evidence stored in Kuzu as normalized evidence."""

    def __init__(
        self,
        repository: KuzuGraphRepository,
    ) -> None:
        self.repository = repository

    def get_fda_sections(
        self,
        drug_id: int,
        section: str,
    ) -> list[ExternalEvidence]:

        sections = self.repository.get_fda_sections(
            drug_id,
            section,
        )

        return [
            ExternalEvidence(
                source="Kuzu medical graph",
                evidence_type=item.section,
                title=item.section,
                content=item.text,
            )
            for item in sections
        ]