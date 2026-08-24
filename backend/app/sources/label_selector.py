from dataclasses import dataclass
from datetime import datetime

from app.sources.models import ExternalEvidence


@dataclass(frozen=True, slots=True)
class SelectedFDAEvidence:
    """Evidence belonging to the selected FDA label."""

    evidence: list[ExternalEvidence]


class FDALabelSelector:
    """
    Select the newest FDA label from OpenFDA candidates.

    Selection order:

    1. Requested evidence type.
    2. Newest effective_time.
    3. Highest numeric version.
    """

    def select(
        self,
        evidence: list[ExternalEvidence],
        evidence_type: str | None = None,
    ) -> SelectedFDAEvidence:

        candidates = evidence

        if evidence_type is not None:
            candidates = [
                item
                for item in candidates
                if item.evidence_type == evidence_type
            ]

        if not candidates:
            return SelectedFDAEvidence(
                evidence=[]
            )

        label_groups: dict[
            tuple[str | None, str | None],
            list[ExternalEvidence],
        ] = {}

        for item in candidates:
            key = (
                item.label_id,
                item.set_id,
            )

            label_groups.setdefault(
                key,
                [],
            ).append(item)

        best_group = max(
            label_groups.values(),
            key=self._label_sort_key,
        )

        return SelectedFDAEvidence(
            evidence=best_group
        )

    @classmethod
    def _label_sort_key(
        cls,
        evidence: list[ExternalEvidence],
    ) -> tuple[datetime, int]:

        if not evidence:
            return datetime.min, 0

        item = evidence[0]

        return (
            cls._parse_date(
                item.effective_time
            ),
            cls._parse_version(
                item.version
            ),
        )

    @staticmethod
    def _parse_date(
        value: str | None,
    ) -> datetime:

        if not value:
            return datetime.min

        try:
            return datetime.strptime(
                value,
                "%Y%m%d",
            )
        except ValueError:
            return datetime.min

    @staticmethod
    def _parse_version(
        value: str | None,
    ) -> int:

        if not value:
            return 0

        try:
            return int(value)
        except ValueError:
            return 0