from hunterclassic.models.ammo import Ammo
from hunterclassic.models.animal import Animal
from hunterclassic.models.weapon import Weapon
from hunterclassic.static_data.static_data import StaticData


def ammo_for_weapon(weapon: Weapon) -> tuple[Ammo, ...]:
    """All ammo compatible with a given weapon."""
    return weapon.ammo


def weapons_for_ammo(ammo: Ammo, static: StaticData) -> list[Weapon]:
    """All weapons that can fire a given ammo."""
    return static.weapons.supports_ammo(ammo)


def ammo_ethical_for_animal(weapon: Weapon, animal: Animal) -> list[Ammo]:
    """Ammo from a weapon that is ethical for a given animal."""
    return [a for a in weapon.ammo if a.id in animal.ethical_ammo_ids]
