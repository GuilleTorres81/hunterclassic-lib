from hunterclassic.models.animal import Animal
from hunterclassic.models.reserve import Reserve
from hunterclassic.models.weapon import Weapon
from hunterclassic.static_data.static_data import StaticData


def animals_huntable_with_weapon(weapon: Weapon, static: StaticData) -> list[Animal]:
    """All animals that can be ethically hunted with a given weapon."""
    return [a for a in static.animals.all() if static.weapons.supports_animal(weapon, a)]


def animals_huntable_with_weapons(
    weapons: list[Weapon],
    reserve: Reserve,
    static: StaticData,
) -> list[Animal]:
    """Animals in a reserve huntable with at least one of the given weapons."""
    # if len(weapons) > 3:
    #     raise ValueError("Maximum 3 weapons allowed")
    huntable_ids = {a.id for w in weapons for a in animals_huntable_with_weapon(w, static)}
    return [a for a in static.reserves.animals_in(reserve, static.animals) if a.id in huntable_ids]


def uncovered_animals(
    weapons: list[Weapon],
    reserve: Reserve,
    static: StaticData,
) -> list[Animal]:
    """Animals in a reserve that cannot be ethically hunted with any of the given weapons."""
    covered_ids = {a.id for a in animals_huntable_with_weapons(weapons, reserve, static)}
    return [a for a in static.reserves.animals_in(reserve, static.animals) if a.id not in covered_ids]


def coverage_ratio(
    weapons: list[Weapon],
    reserve: Reserve,
    static: StaticData,
) -> float:
    """Fraction of animals in a reserve covered by the given weapons (0.0 – 1.0)."""
    all_animals = static.reserves.animals_in(reserve, static.animals)
    if not all_animals:
        return 0.0
    covered = animals_huntable_with_weapons(weapons, reserve, static)
    return len(covered) / len(all_animals)
