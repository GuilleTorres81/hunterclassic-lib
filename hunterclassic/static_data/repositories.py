from __future__ import annotations

from hunterclassic.models.ammo import Ammo
from hunterclassic.models.animal import Animal
from hunterclassic.models.loadout import EthicalLoadout
from hunterclassic.models.reserve import Reserve
from hunterclassic.models.weapon import Weapon
from hunterclassic.static_data.repository import BaseRepository


class AmmoRepository(BaseRepository[Ammo]):
    def __init__(self, ammo: tuple[Ammo, ...]) -> None:
        super().__init__(ammo)


class WeaponRepository(BaseRepository[Weapon]):
    def __init__(self, weapons: tuple[Weapon, ...]) -> None:
        super().__init__(weapons)
        self._by_shortname: dict[str, list[Weapon]] = {}
        self._by_ammo_id: dict[int, list[Weapon]] = {}
        self._weapon_ammo_ids: dict[int, frozenset[int]] = {}
        for w in weapons:
            self._by_shortname.setdefault(w.shortname, []).append(w)
            self._weapon_ammo_ids[w.id] = frozenset(a.id for a in w.ammo)
            for ammo in w.ammo:
                self._by_ammo_id.setdefault(ammo.id, []).append(w)

    def get_by_shortname(self, shortname: str) -> list[Weapon]:
        return self._by_shortname.get(shortname, [])

    def supports_ammo(self, ammo: Ammo) -> list[Weapon]:
        """All weapons that can fire the given ammo."""
        return self._by_ammo_id.get(ammo.id, [])

    def supports(self, weapon: Weapon, ammo: Ammo) -> bool:
        """Whether a specific weapon can fire a specific ammo."""
        return ammo.id in self._weapon_ammo_ids.get(weapon.id, frozenset())

    def supports_animal(self, weapon: Weapon, animal: Animal) -> bool:
        """Whether a weapon has at least one ethical ammo for the given animal."""
        return bool(self._weapon_ammo_ids.get(weapon.id, frozenset()) & animal.ethical_ammo_ids)

    def ethical_weapons_for(self, animal: Animal) -> list[Weapon]:
        """All weapons that have at least one ethical ammo for the given animal."""
        ethical_ids = set(animal.ethical_ammo_ids)
        seen: set[int] = set()
        result: list[Weapon] = []
        for ammo_id in ethical_ids:
            for weapon in self._by_ammo_id.get(ammo_id, []):
                if weapon.id not in seen:
                    seen.add(weapon.id)
                    result.append(weapon)
        return result

    def ethical_loadouts_for(self, animal: Animal) -> list[EthicalLoadout]:
        """All (weapon, ammo) combinations that are ethical for the given animal."""
        ethical_ids = set(animal.ethical_ammo_ids)
        loadouts: list[EthicalLoadout] = []
        for weapon in self._items:
            for ammo in weapon.ammo:
                if ammo.id in ethical_ids:
                    loadouts.append(EthicalLoadout(weapon=weapon, ammo=ammo))
        return loadouts


class AnimalRepository(BaseRepository[Animal]):
    def __init__(self, animals: tuple[Animal, ...]) -> None:
        super().__init__(animals)
        self._by_define: dict[str, Animal] = {a.define: a for a in animals}
        self._by_name: dict[str, Animal] = {a.name: a for a in animals}
        self._by_short: dict[str, list[Animal]] = {}
        for a in animals:
            self._by_short.setdefault(a.short, []).append(a)

    def get_by_define(self, define: str) -> Animal | None:
        return self._by_define.get(define)

    def get_by_name(self, name: str) -> Animal | None:
        return self._by_name.get(name)

    def get_by_short(self, short: str) -> list[Animal]:
        return self._by_short.get(short, [])

    def ethical_ammo_for(self, animal: Animal, ammo_repo: AmmoRepository) -> list[Ammo]:
        """Resolves ethical_ammo_ids to Ammo objects. Skips unknown IDs silently."""
        return [
            ammo
            for ammo_id in animal.ethical_ammo_ids
            if (ammo := ammo_repo.get(ammo_id)) is not None
        ]

    def is_ethical(self, animal: Animal, ammo: Ammo) -> bool:
        """Whether a given ammo is ethical for this animal."""
        return ammo.id in animal.ethical_ammo_ids

    def available_in(self, animal: Animal, reserve: Reserve) -> bool:
        """Whether an animal is present in a given reserve."""
        return animal.id in reserve.species_ids


class ReserveRepository(BaseRepository[Reserve]):
    def __init__(self, reserves: tuple[Reserve, ...]) -> None:
        super().__init__(reserves)
        self._by_define: dict[str, Reserve] = {r.define: r for r in reserves}
        self._by_name: dict[str, Reserve] = {r.name: r for r in reserves}
        self._reserves_by_animal_id: dict[int, list[Reserve]] = {}
        for r in reserves:
            for species_id in r.species_ids:
                self._reserves_by_animal_id.setdefault(species_id, []).append(r)

    def get_by_define(self, define: str) -> Reserve | None:
        return self._by_define.get(define)

    def get_by_name(self, name: str) -> Reserve | None:
        return self._by_name.get(name)

    def animals_in(self, reserve: Reserve, animal_repo: AnimalRepository) -> list[Animal]:
        """Resolves species_ids to Animal objects. Skips unknown IDs silently."""
        return [
            animal
            for species_id in reserve.species_ids
            if (animal := animal_repo.get(species_id)) is not None
        ]

    def reserves_for(self, animal: Animal) -> list[Reserve]:
        """All reserves where the given animal is present."""
        return self._reserves_by_animal_id.get(animal.id, [])

    def contains(self, reserve: Reserve, animal: Animal) -> bool:
        return animal.id in reserve.species_ids
