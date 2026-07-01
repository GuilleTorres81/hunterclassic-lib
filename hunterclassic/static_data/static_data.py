from __future__ import annotations

from hunterclassic.static_data.loader import StaticDataLoader
from hunterclassic.static_data.static_files import StaticFiles
from hunterclassic.static_data.repositories import (
    AmmoRepository,
    AnimalRepository,
    ReserveRepository,
    WeaponRepository,
)


class StaticData:
    """
    Single entry point for all static game data.

    Usage:
        static = StaticData.load()
        static.animals.get(55)
        static.animals.get_by_define("FALLOW_DEER")
        static.weapons.get(296)
        static.reserves.get(5)
    """

    def __init__(self, files: StaticFiles) -> None:
        self._animals = AnimalRepository(files.animals)
        self._weapons = WeaponRepository(files.weapons)
        self._reserves = ReserveRepository(files.reserves)
        self._ammo = AmmoRepository(tuple(files.ammo_registry.values()))

    @classmethod
    def load(cls) -> StaticData:
        return cls(StaticDataLoader().load())

    @property
    def animals(self) -> AnimalRepository:
        return self._animals

    @property
    def weapons(self) -> WeaponRepository:
        return self._weapons

    @property
    def reserves(self) -> ReserveRepository:
        return self._reserves

    @property
    def ammo(self) -> AmmoRepository:
        return self._ammo
