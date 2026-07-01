from __future__ import annotations

import json
from pathlib import Path

from hunterclassic.models.ammo import Ammo
from hunterclassic.models.animal import Animal
from hunterclassic.models.reserve import Reserve
from hunterclassic.models.weapon import Weapon
from hunterclassic.static_data.static_files import StaticFiles
from hunterclassic.static_data.validator import StaticDataValidator

_DEFAULT_STATIC_DIR = Path(__file__).parent.parent / "static"


class StaticDataLoader:
    """
    Loads and parses all static game data from JSON files.

    To add support for a new entity type (e.g., missions):
    1. Create a Pydantic model in hunterclassic.models.mission
    2. Add a parse method: _parse_missions(self, raw: list[dict]) -> tuple[Mission, ...]
    3. Add the file to load() and include in StaticFiles
    4. Add validation in StaticDataValidator if needed

    The loader is responsible for reading files and building models.
    Relationships between entities are resolved in repositories.
    """

    def __init__(self, static_dir: Path = _DEFAULT_STATIC_DIR) -> None:
        self._dir = static_dir

    def load(self) -> StaticFiles:
        raw_animals = self._read_json("animals.json")
        raw_weapons = self._read_json("weapons.json")
        raw_reserves = self._read_json("reserves.json")

        ammo_registry = self._build_ammo_registry(raw_weapons)
        animals = self._parse_animals(raw_animals)
        weapons = self._parse_weapons(raw_weapons, ammo_registry)
        reserves = self._parse_reserves(raw_reserves)

        self._validate_unique_ids("animals", [a.id for a in animals])
        self._validate_unique_ids("weapons", [w.id for w in weapons])
        self._validate_unique_ids("reserves", [r.id for r in reserves])

        files = StaticFiles(
            animals=animals,
            weapons=weapons,
            reserves=reserves,
            ammo_registry=ammo_registry,
        )
        StaticDataValidator().validate(files)
        return files

    def _read_json(self, filename: str) -> list[dict]:
        path = self._dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Static data file not found: {path}")
        with path.open(encoding="utf-8-sig") as f:
            return json.load(f)

    def _build_ammo_registry(self, raw_weapons: list[dict]) -> dict[int, Ammo]:
        registry: dict[int, Ammo] = {}
        for raw in raw_weapons:
            for raw_ammo in raw.get("fit", {}).get("3", []):
                ammo_id = raw_ammo["id"]
                if ammo_id not in registry:
                    registry[ammo_id] = Ammo(
                        id=ammo_id,
                        name=raw_ammo["name"],
                        image=raw_ammo["image"],
                    )
        return registry

    def _parse_animals(self, raw: list[dict]) -> tuple[Animal, ...]:
        return tuple(
            Animal(
                id=item["id"],
                name=item["name"],
                short=item["short"],
                define=item["define"],
                ethical_ammo_ids=frozenset(item.get("ethicalAmmo", [])),
            )
            for item in raw
        )

    def _parse_weapons(
        self, raw: list[dict], ammo_registry: dict[int, Ammo]
    ) -> tuple[Weapon, ...]:
        weapons = []
        for item in raw:
            ammo_ids = [a["id"] for a in item.get("fit", {}).get("3", [])]
            missing = [aid for aid in ammo_ids if aid not in ammo_registry]
            if missing:
                raise ValueError(
                    f"Weapon {item['id']} references unknown ammo IDs: {missing}"
                )
            weapons.append(
                Weapon(
                    id=item["id"],
                    name=item["name"],
                    shortname=item["shortname"] or "",
                    image=item["image"],
                    ammo=tuple(ammo_registry[aid] for aid in ammo_ids),
                )
            )
        return tuple(weapons)

    def _parse_reserves(self, raw: list[dict]) -> tuple[Reserve, ...]:
        return tuple(
            Reserve(
                id=item["id"],
                name=item["name"],
                define=item["define"],
                species_ids=frozenset(item.get("species", [])),
            )
            for item in raw
        )

    @staticmethod
    def _validate_unique_ids(entity: str, ids: list[int]) -> None:
        seen: set[int] = set()
        for id_ in ids:
            if id_ in seen:
                raise ValueError(f"Duplicate {entity} ID detected: {id_}")
            seen.add(id_)
