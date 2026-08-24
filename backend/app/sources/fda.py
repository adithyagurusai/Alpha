from typing import Any, Protocol

import requests

from app.sources.models import ExternalEvidence


class FDADataSource(Protocol):
    """Interface for external FDA evidence providers."""

    def search_drug(
        self,
        drug_name: str,
    ) -> list[ExternalEvidence]:
        ...


class MockFDADataSource:
    """
    Deterministic FDA source for development and testing.
    """

    def __init__(
        self,
        evidence: dict[str, list[ExternalEvidence]],
    ) -> None:
        self.evidence = {
            key.upper(): value
            for key, value in evidence.items()
        }

    def search_drug(
        self,
        drug_name: str,
    ) -> list[ExternalEvidence]:
        return self.evidence.get(
            drug_name.upper(),
            [],
        )


class OpenFDADataSource:
    """
    OpenFDA drug-label client.

    This class is responsible only for:
    - calling OpenFDA
    - selecting label records
    - converting FDA fields into ExternalEvidence
    """

    BASE_URL = "https://api.fda.gov/drug/label.json"

    SECTION_FIELDS = {
        "contraindications": "contraindications",
        "adverse_reactions": "adverse_reactions",
        "drug_interactions": "drug_interactions",
        "warnings_and_cautions": "warnings_and_cautions",
    }

    def __init__(
        self,
        timeout: float = 10.0,
        session: requests.Session | None = None,
    ) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()

    def search_drug(
        self,
        drug_name: str,
    ) -> list[ExternalEvidence]:
        name = drug_name.strip()

        if not name:
            return []

        response = self.session.get(
            self.BASE_URL,
            params={
                "search": (
                    f'openfda.generic_name:"{name}"'
                ),
                "limit": 10,
            },
            timeout=self.timeout,
        )

        if response.status_code == 404:
            return []

        response.raise_for_status()

        payload: dict[str, Any] = response.json()

        results = payload.get("results", [])

        if not isinstance(results, list):
            return []

        evidence: list[ExternalEvidence] = []

        for record in results:
            if not isinstance(record, dict):
                continue

            evidence.extend(
                self._extract_evidence(record)
            )

        return evidence

    def _extract_evidence(
        self,
        record: dict[str, Any],
    ) -> list[ExternalEvidence]:
        evidence: list[ExternalEvidence] = []

        label_id = self._first_string(
            record.get("id")
        )

        set_id = self._first_string(
            record.get("set_id")
        )

        effective_time = self._first_string(
            record.get("effective_time")
        )

        version = self._first_string(
            record.get("version")
        )

        title = self._extract_title(record)

        for evidence_type, field in self.SECTION_FIELDS.items():
            values = self._extract_text_values(
                record.get(field)
            )

            for value in values:
                evidence.append(
                    ExternalEvidence(
                        source="OpenFDA",
                        evidence_type=evidence_type,
                        title=title,
                        content=value,
                        label_id=label_id,
                        set_id=set_id,
                        effective_time=effective_time,
                        version=version,
                    )
                )

        return evidence

    @staticmethod
    def _extract_text_values(
        value: Any,
    ) -> list[str]:
        if value is None:
            return []

        if isinstance(value, str):
            value = value.strip()

            return [value] if value else []

        if isinstance(value, list):
            values: list[str] = []

            for item in value:
                if isinstance(item, str):
                    text = item.strip()

                    if text:
                        values.append(text)

            return values

        return []

    @staticmethod
    def _first_string(value: Any) -> str | None:
        if isinstance(value, str):
            value = value.strip()

            return value or None

        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    text = item.strip()

                    if text:
                        return text

        return None

    @staticmethod
    def _extract_title(
        record: dict[str, Any],
    ) -> str:
        openfda = record.get("openfda")

        if isinstance(openfda, dict):
            brand_names = openfda.get("brand_name")

            if isinstance(brand_names, list):
                for name in brand_names:
                    if isinstance(name, str):
                        name = name.strip()

                        if name:
                            return name

        return "FDA Drug Label"