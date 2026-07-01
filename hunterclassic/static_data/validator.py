from __future__ import annotations

from hunterclassic.static_data.static_files import StaticFiles


class StaticDataValidator:
    """
    Cross-collection integrity checks run after all data is loaded.
    Raises ValueError with a descriptive message on the first violation found.
    """

    def validate(self, files: StaticFiles) -> None:
        animal_ids = {a.id for a in files.animals}
        ammo_ids = set(files.ammo_registry)

        self._validate_unique_defines(
            "animals", [a.define for a in files.animals]
        )
        self._validate_unique_defines(
            "reserves", [r.define for r in files.reserves]
        )
        self._validate_ethical_ammo_refs(files, ammo_ids)
        self._validate_species_refs(files, animal_ids)

    @staticmethod
    def _validate_unique_defines(entity: str, defines: list[str]) -> None:
        seen: set[str] = set()
        for define in defines:
            if define in seen:
                raise ValueError(
                    f"Duplicate {entity} define detected: {define!r}"
                )
            seen.add(define)

    @staticmethod
    def _validate_ethical_ammo_refs(
        files: StaticFiles, ammo_ids: set[int]
    ) -> None:
        for animal in files.animals:
            broken = animal.ethical_ammo_ids - ammo_ids
            if broken:
                raise ValueError(
                    f"Animal {animal.define!r} references unknown ammo IDs: {sorted(broken)}"
                )

    @staticmethod
    def _validate_species_refs(
        files: StaticFiles, animal_ids: set[int]
    ) -> None:
        for reserve in files.reserves:
            broken = reserve.species_ids - animal_ids
            if broken:
                raise ValueError(
                    f"Reserve {reserve.define!r} references unknown animal IDs: {sorted(broken)}"
                )
