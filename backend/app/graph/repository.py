from pathlib import Path
from typing import Any, cast

import kuzu

from app.domain.entities import (
    Drug,
    DrugIndication,
    DrugInteraction,
    DrugTarget,
    Disease,
    FDASection,
    FDALabel,
    Pathway,
    Target,
    TargetDiseaseAssociation,
    TargetPathway,
)


class KuzuGraphRepository:
    """Read-only repository for the Xpharma Kuzu medical graph."""

    def __init__(self, database_path: str | Path) -> None:
        self.database = kuzu.Database(str(database_path))
        self.connection = kuzu.Connection(self.database)

    def close(self) -> None:
        """Close the Kuzu connection."""
        self.connection.close()

    @staticmethod
    def _row_values(row: Any) -> tuple[Any, ...]:
        """
        Normalize a Kuzu result row for type checking.

        Kuzu's Python type information exposes query rows as a broad union.
        The repository is the boundary where those values become typed
        application data.
        """
        return cast(tuple[Any, ...], row)

    def get_drug_targets(self, drug_id: int) -> list[DrugTarget]:
        """Return all targets associated with a drug."""
        result = self.connection.execute(
            """
            MATCH (drug:Drug)-[:TARGETS]->(target:Target)
            WHERE drug.id = $drug_id
            RETURN
                drug.id,
                drug.name,
                target.id,
                target.name,
                target.external_id,
                target.approved_name,
                target.target_class
            ORDER BY target.name;
            """,
            {"drug_id": drug_id},
        )

        rows: list[DrugTarget] = []

        for row in result.get_all():
            (
                retrieved_drug_id,
                drug_name,
                target_id,
                target_name,
                external_id,
                approved_name,
                target_class,
            ) = row

            rows.append(
                DrugTarget(
                    drug_id=cast(int, retrieved_drug_id),
                    drug_name=cast(str, drug_name),
                    target=Target(
                        id=cast(int, target_id),
                        name=cast(str, target_name),
                        external_id=cast(str, external_id),
                        approved_name=cast(str, approved_name),
                        target_class=cast(str, target_class),
                    ),
                )
            )

        return rows

    def get_drug_indications(
        self,
        drug_id: int,
    ) -> list[DrugIndication]:
        """Return diseases for which a drug has a clinical indication."""
        result = self.connection.execute(
            """
            MATCH (drug:Drug)-[r:INDICATED_FOR]->(disease:Disease)
            WHERE drug.id = $drug_id
            RETURN
                drug.id,
                drug.name,
                disease.id,
                disease.name,
                r.max_clinical_stage
            ORDER BY disease.name;
            """,
            {"drug_id": drug_id},
        )

        rows: list[DrugIndication] = []

        while result.has_next():
            row = self._row_values(result.get_next())

            (
                retrieved_drug_id,
                drug_name,
                disease_id,
                disease_name,
                clinical_stage,
            ) = row

            rows.append(
                DrugIndication(
                    drug_id=cast(int, retrieved_drug_id),
                    drug_name=cast(str, drug_name),
                    disease=Disease(
                        id=cast(int, disease_id),
                        name=cast(str, disease_name),
                    ),
                    max_clinical_stage=cast(str, clinical_stage),
                )
            )

        return rows

    def get_drug_interactions(
        self,
        drug_id: int,
    ) -> list[DrugInteraction]:
        """Return drugs that interact with the specified drug."""
        result = self.connection.execute(
            """
            MATCH (drug:Drug)-[:INTERACTS_WITH]->(other:Drug)
            WHERE drug.id = $drug_id
            RETURN
                drug.id,
                drug.name,
                other.id,
                other.name
            ORDER BY other.name;
            """,
            {"drug_id": drug_id},
        )

        rows: list[DrugInteraction] = []

        while result.has_next():
            row = self._row_values(result.get_next())

            (
                retrieved_drug_id,
                drug_name,
                other_id,
                other_name,
            ) = row

            rows.append(
                DrugInteraction(
                    drug_id=cast(int, retrieved_drug_id),
                    drug_name=cast(str, drug_name),
                    interacting_drug=Drug(
                        id=cast(int, other_id),
                        name=cast(str, other_name),
                    ),
                )
            )

        return rows

    def get_target_pathways(
        self,
        target_id: int,
    ) -> list[TargetPathway]:
        """Return pathways associated with a target."""
        result = self.connection.execute(
            """
            MATCH (target:Target)-[:PARTICIPATES_IN]->(pathway:Pathway)
            WHERE target.id = $target_id
            RETURN
                target.id,
                target.name,
                pathway.id,
                pathway.name
            ORDER BY pathway.name;
            """,
            {"target_id": target_id},
        )

        rows: list[TargetPathway] = []

        while result.has_next():
            row = self._row_values(result.get_next())

            (
                retrieved_target_id,
                target_name,
                pathway_id,
                pathway_name,
            ) = row

            rows.append(
                TargetPathway(
                    target_id=cast(int, retrieved_target_id),
                    target_name=cast(str, target_name),
                    pathway=Pathway(
                        id=cast(int, pathway_id),
                        name=cast(str, pathway_name),
                    ),
                )
            )

        return rows

    def get_target_disease_associations(
        self,
        target_id: int,
    ) -> list[TargetDiseaseAssociation]:
        """Return diseases associated with a target."""
        result = self.connection.execute(
            """
            MATCH (target:Target)-[r:ASSOCIATED_WITH]->(disease:Disease)
            WHERE target.id = $target_id
            RETURN
                target.id,
                target.name,
                disease.id,
                disease.name,
                r.score
            ORDER BY r.score DESC, disease.name;
            """,
            {"target_id": target_id},
        )

        rows: list[TargetDiseaseAssociation] = []

        while result.has_next():
            row = self._row_values(result.get_next())

            (
                retrieved_target_id,
                target_name,
                disease_id,
                disease_name,
                score,
            ) = row

            rows.append(
                TargetDiseaseAssociation(
                    target_id=cast(int, retrieved_target_id),
                    target_name=cast(str, target_name),
                    disease=Disease(
                        id=cast(int, disease_id),
                        name=cast(str, disease_name),
                    ),
                    score=cast(float, score),
                )
            )

        return rows

    def get_latest_fda_label(
        self,
        drug_id: int,
    ) -> FDALabel | None:
        """Return the latest FDA label associated with a drug."""
        result = self.connection.execute(
            """
            MATCH (drug:Drug)-[:HAS_FDA_LABEL]->(label:FDALabel)
            WHERE drug.id = $drug_id
            RETURN
                label.id,
                label.set_id,
                label.effective_time,
                label.version,
                label.spl_id,
                label.title
            ORDER BY label.effective_time DESC, label.version DESC
            LIMIT 1;
            """,
            {"drug_id": drug_id},
        )

        if not result.has_next():
            return None

        row = self._row_values(result.get_next())

        (
            label_id,
            set_id,
            effective_time,
            version,
            spl_id,
            title,
        ) = row

        return FDALabel(
            id=cast(str, label_id),
            set_id=cast(str, set_id),
            effective_time=cast(str, effective_time),
            version=cast(str, version),
            spl_id=cast(str, spl_id),
            title=cast(str, title),
        )

    def get_fda_sections(
        self,
        drug_id: int,
        section: str | None = None,
        ) -> list[FDASection]:
        """Return sections from the latest FDA label for a drug."""

        if section is None:
            result = self.connection.execute(
                """
                MATCH (drug:Drug)-[:HAS_FDA_LABEL]->(label:FDALabel)
                WHERE drug.id = $drug_id

                WITH drug, label
                ORDER BY label.effective_time DESC, label.version DESC
                LIMIT 1

                MATCH (label)-[:HAS_SECTION]->(section:FDASection)

                RETURN
                    section.id,
                    section.section,
                    section.text

                ORDER BY section.section;
                """,
                {"drug_id": drug_id},
            )
        else:
            result = self.connection.execute(
                """
                MATCH (drug:Drug)-[:HAS_FDA_LABEL]->(label:FDALabel)
                WHERE drug.id = $drug_id

                WITH drug, label
                ORDER BY label.effective_time DESC, label.version DESC
                LIMIT 1

                MATCH (label)-[:HAS_SECTION]->(section:FDASection)
                WHERE section.section = $section

                RETURN
                    section.id,
                    section.section,
                    section.text

                ORDER BY section.section;
                """,
                {
                    "drug_id": drug_id,
                    "section": section,
                },
            )

        rows: list[FDASection] = []

        while result.has_next():
            (
                section_id,
                section_name,
                text,
            ) = result.get_next()

            rows.append(
                FDASection(
                    id=str(section_id),
                    section=str(section_name),
                    text=str(text),
                )
            )

        return rows