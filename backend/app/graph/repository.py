from pathlib import Path
from typing import Any, cast

import kuzu

from app.domain.entities import (
    Disease,
    Drug,
    DrugIndication,
    DrugTarget,
    Pathway,
    Target,
    TargetClass,
    TargetDiseaseAssociation,
    TargetGO,
    TargetPathway,
    TargetProtein,
    TargetTractability,
)


class KuzuGraphRepository:
    """Read-only repository for the Xpharma Kuzu medical graph."""

    def __init__(self, database_path: str | Path) -> None:
        self.database = kuzu.Database(str(database_path))
        self.connection = kuzu.Connection(self.database)

    def close(self) -> None:
        self.connection.close()

    @staticmethod
    def _row_values(row: Any) -> tuple[Any, ...]:
        return cast(tuple[Any, ...], row)

    # ================================================================
    # DRUG
    # ================================================================

    def get_drug(self, drug_id: str) -> Drug | None:
        result = self.connection.execute(
            """
            MATCH (drug:Drug)
            WHERE drug.id = $drug_id
            RETURN drug.id, drug.name
            LIMIT 1;
            """,
            {"drug_id": drug_id},
        )

        if not result.has_next():
            return None

        row = self._row_values(result.get_next())

        return Drug(
            id=cast(str, row[0]),
            name=cast(str, row[1]),
        )

    # ================================================================
    # DRUG → TARGET
    # ================================================================

    def get_drug_targets(
        self,
        drug_id: str,
    ) -> list[DrugTarget]:

        result = self.connection.execute(
            """
            MATCH (drug:Drug)-[r:TARGETS]->(target:Target)
            WHERE drug.id = $drug_id
            RETURN
                drug.id,
                drug.name,
                target.id,
                target.name,
                target.external_id,
                target.approved_name,
                r.action_type,
                r.mechanism_of_action
            ORDER BY target.name;
            """,
            {"drug_id": drug_id},
        )

        rows: list[DrugTarget] = []

        while result.has_next():
            row = self._row_values(result.get_next())

            (
                retrieved_drug_id,
                drug_name,
                target_id,
                target_name,
                external_id,
                approved_name,
                _action_type,
                _mechanism_of_action,
            ) = row

            rows.append(
                DrugTarget(
                    drug_id=cast(str, retrieved_drug_id),
                    drug_name=cast(str, drug_name),
                    target=Target(
                        id=cast(int, target_id),
                        name=cast(str, target_name),
                        external_id=cast(str, external_id),
                        approved_name=cast(str, approved_name),
                    ),
                )
            )

        return rows

    # ================================================================
    # DRUG → DISEASE
    # ================================================================

    def get_drug_indications(
        self,
        drug_id: str,
    ) -> list[DrugIndication]:

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
                    drug_id=cast(str, retrieved_drug_id),
                    drug_name=cast(str, drug_name),
                    disease=Disease(
                        id=cast(str, disease_id),
                        name=cast(str, disease_name),
                    ),
                    max_clinical_stage=cast(str, clinical_stage),
                )
            )

        return rows

    # ================================================================
    # DISEASE
    # ================================================================

    def get_disease(
        self,
        disease_id: str,
    ) -> Disease | None:

        result = self.connection.execute(
            """
            MATCH (disease:Disease)
            WHERE disease.id = $disease_id
            RETURN disease.id, disease.name
            LIMIT 1;
            """,
            {"disease_id": disease_id},
        )

        if not result.has_next():
            return None

        row = self._row_values(result.get_next())

        return Disease(
            id=cast(str, row[0]),
            name=cast(str, row[1]),
        )

    # ================================================================
    # TARGET
    # ================================================================

    def get_target(
        self,
        target_id: int,
    ) -> Target | None:

        result = self.connection.execute(
            """
            MATCH (target:Target)
            WHERE target.id = $target_id
            RETURN
                target.id,
                target.name,
                target.external_id,
                target.approved_name
            LIMIT 1;
            """,
            {"target_id": target_id},
        )

        if not result.has_next():
            return None

        row = self._row_values(result.get_next())

        return Target(
            id=cast(int, row[0]),
            name=cast(str, row[1]),
            external_id=cast(str, row[2]),
            approved_name=cast(str, row[3]),
        )

    # ================================================================
    # TARGET → DISEASE
    # ================================================================

    def get_target_disease_associations(
        self,
        target_id: int,
    ) -> list[TargetDiseaseAssociation]:

        result = self.connection.execute(
            """
            MATCH (target:Target)-[r:ASSOCIATED_WITH]->(disease:Disease)
            WHERE target.id = $target_id
            RETURN
                target.id,
                target.name,
                disease.id,
                disease.name,
                r.association_score
            ORDER BY
                r.association_score DESC,
                disease.name;
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
                        id=cast(str, disease_id),
                        name=cast(str, disease_name),
                    ),
                    score=cast(float, score),
                )
            )

        return rows

    # ================================================================
    # TARGET → PATHWAY
    # ================================================================

    def get_target_pathways(
        self,
        target_id: int,
    ) -> list[TargetPathway]:

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
                        id=cast(str, pathway_id),
                        name=cast(str, pathway_name),
                    ),
                )
            )

        return rows

    # ================================================================
    # TARGET → TARGET CLASS
    # ================================================================

    def get_target_classes(
        self,
        target_id: int,
    ) -> list[TargetClass]:

        result = self.connection.execute(
            """
            MATCH (target:Target)-[:HAS_TARGET_CLASS]->(class:TargetClass)
            WHERE target.id = $target_id
            RETURN
                class.class_key,
                class.id,
                class.label,
                class.level
            ORDER BY class.level;
            """,
            {"target_id": target_id},
        )

        rows: list[TargetClass] = []

        while result.has_next():
            row = self._row_values(result.get_next())

            class_key, class_id, label, level = row

            rows.append(
                TargetClass(
                    class_key=cast(str, class_key),
                    id=cast(int, class_id),
                    label=cast(str, label),
                    level=cast(str, level),
                )
            )

        return rows

    # ================================================================
    # TARGET → PROTEIN
    # ================================================================

    def get_target_proteins(
        self,
        target_id: int,
    ) -> list[TargetProtein]:

        result = self.connection.execute(
            """
            MATCH (target:Target)-[:HAS_PROTEIN]->(protein:Protein)
            WHERE target.id = $target_id
            RETURN
                protein.protein_key,
                protein.id,
                protein.source
            ORDER BY protein.source, protein.id;
            """,
            {"target_id": target_id},
        )

        rows: list[TargetProtein] = []

        while result.has_next():
            protein_key, protein_id, source = result.get_next()

            rows.append(
                TargetProtein(
                    protein_key=cast(str, protein_key),
                    id=cast(str, protein_id),
                    source=cast(str, source),
                )
            )

        return rows

    # ================================================================
    # TARGET → GO
    # ================================================================

    def get_target_go(
        self,
        target_id: int,
    ) -> list[TargetGO]:

        result = self.connection.execute(
            """
            MATCH (target:Target)-[:HAS_GO]->(go:GO)
            WHERE target.id = $target_id
            RETURN go.id
            ORDER BY go.id;
            """,
            {"target_id": target_id},
        )

        rows: list[TargetGO] = []

        while result.has_next():
            row = self._row_values(result.get_next())

            rows.append(
                TargetGO(id=cast(str, row[0]))
            )

        return rows

    # ================================================================
    # TARGET → TRACTABILITY
    # ================================================================

    def get_target_tractability(
        self,
        target_id: int,
    ) -> list[TargetTractability]:

        result = self.connection.execute(
            """
            MATCH (target:Target)-[:HAS_TRACTABILITY]->(
                tractability:Tractability
            )
            WHERE target.id = $target_id
            RETURN
                tractability.tractability_key,
                tractability.modality,
                tractability.id,
                tractability.value
            ORDER BY
                tractability.modality,
                tractability.id,
                tractability.value;
            """,
            {"target_id": target_id},
        )

        rows: list[TargetTractability] = []

        while result.has_next():
            (
                tractability_key,
                modality,
                tractability_id,
                value,
            ) = result.get_next()

            rows.append(
                TargetTractability(
                    tractability_key=cast(str, tractability_key),
                    modality=cast(str, modality),
                    id=cast(str, tractability_id),
                    value=cast(bool, value),
                )
            )

        return rows