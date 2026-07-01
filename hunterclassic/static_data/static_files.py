from __future__ import annotations

from dataclasses import dataclass

from hunterclassic.models.ammo import Ammo
from hunterclassic.models.animal import Animal
from hunterclassic.models.reserve import Reserve
from hunterclassic.models.weapon import Weapon


@dataclass(frozen=True)
class StaticFiles:
    animals: tuple[Animal, ...]
    weapons: tuple[Weapon, ...]
    reserves: tuple[Reserve, ...]
    ammo_registry: dict[int, Ammo]
