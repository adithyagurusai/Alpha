from dataclasses import dataclass

import kuzu

from app.domain.entities import Disease, Drug, Target


@dataclass(frozen=True, slots=True)
class ResolvedDrug:
    drug: Drug


@dataclass(frozen=True, slots=True)
class ResolvedTarget:
    target: Target


@dataclass(frozen=True, slots=True)
class ResolvedDisease:
    disease: Disease


class EntityResolver:
    """Resolve user-facing names to canonical Xpharma graph entities."""

    def __init__(
        self,
        connection: kuzu.Connection,
    ) -> None:
        self.connection = connection

    def resolve_drug(
        self,
        name: str,
    ) -> ResolvedDrug | None:

        result = self.connection.execute(
            """
            MATCH (drug:Drug)
            WHERE upper(trim(drug.name)) =
                  upper(trim($name))
            RETURN
                drug.id,
                drug.name
            LIMIT 1;
            """,
            {"name": name},
        )

        if not result.has_next():
            return None

        drug_id, drug_name = result.get_next()

        return ResolvedDrug(
            drug=Drug(
                id=str(drug_id),
                name=str(drug_name),
            )
        )

    def resolve_target(
        self,
        name: str,
    ) -> ResolvedTarget | None:

        result = self.connection.execute(
            """
            MATCH (target:Target)
            WHERE target.name = $name
            OR target.approved_name = $name
            OR target.external_id = $name
            RETURN
                target.id,
                target.name,
                target.external_id,
                target.approved_name
            LIMIT 1;
            """,
            {"name": name},
        )

        if not result.has_next():
            return None

        (
            target_id,
            target_name,
            external_id,
            approved_name,
        ) = result.get_next()

        return ResolvedTarget(
            target=Target(
                id=int(target_id),
                name=str(target_name),
                external_id=str(external_id),
                approved_name=str(approved_name),
            )
        )

    def resolve_disease(
        self,
        name: str,
    ) -> ResolvedDisease | None:

        result = self.connection.execute(
            """
            MATCH (disease:Disease)
            WHERE upper(trim(disease.name)) =
                  upper(trim($name))
            RETURN
                disease.id,
                disease.name
            LIMIT 1;
            """,
            {"name": name},
        )

        if not result.has_next():
            return None

        disease_id, disease_name = result.get_next()

        return ResolvedDisease(
            disease=Disease(
                id=str(disease_id),
                name=str(disease_name),
            )
        )