# Extending the Static Data System

## Architecture Overview

```
hunterclassic/
    models/              # Pydantic models (frozen, immutable)
        animal.py
        weapon.py
        ammo.py
        reserve.py
        loadout.py
        mission.py       # ← New model

    static/              # JSON data files
        animals.json
        weapons.json
        reserves.json
        missions.json    # ← New file

    static_data/         # Data loading and querying
        loader.py        # Reads JSON → models
        static_files.py  # Container for all loaded data
        validator.py     # Cross-collection integrity checks
        repository.py    # BaseRepository[T] generic
        repositories.py  # Animal/Weapon/Reserve/AmmoRepository
        mission_repository_example.py  # ← Example
        static_data.py   # Public API facade
        cache.py         # Optional caching layer
```

## Adding a New Entity Type

### 1. Create the Model
```python
# hunterclassic/models/mission.py
from pydantic import BaseModel, ConfigDict

class Mission(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    map_id: int  # References Reserve.id
    objective: str
    reward_xp: int
```

### 2. Add to Models Package
```python
# hunterclassic/models/__init__.py
from hunterclassic.models.mission import Mission

__all__ = [..., "Mission"]
```

### 3. Add JSON Data File
Place `missions.json` in `hunterclassic/static/` with the same structure as existing files.

### 4. Extend the Loader
```python
# hunterclassic/static_data/loader.py
class StaticDataLoader:
    def load(self) -> StaticFiles:
        raw_missions = self._read_json("missions.json")
        missions = self._parse_missions(raw_missions)
        # ... existing code ...
        return StaticFiles(
            missions=missions,  # Add to StaticFiles
            # ... existing fields ...
        )

    def _parse_missions(self, raw: list[dict]) -> tuple[Mission, ...]:
        return tuple(
            Mission(
                id=item["id"],
                name=item["name"],
                map_id=item["mapId"],
                objective=item["objective"],
                reward_xp=item["rewardXp"],
            )
            for item in raw
        )
```

### 5. Update StaticFiles
```python
# hunterclassic/static_data/static_files.py
@dataclass(frozen=True)
class StaticFiles:
    missions: tuple[Mission, ...]  # Add this
    # ... existing fields ...
```

### 6. Create Repository
```python
# hunterclassic/static_data/repositories.py
class MissionRepository(BaseRepository[Mission]):
    def __init__(self, missions: tuple[Mission, ...]) -> None:
        super().__init__(missions)
        self._by_map_id: dict[int, list[Mission]] = {}
        for m in missions:
            self._by_map_id.setdefault(m.map_id, []).append(m)

    def get_by_map(self, map_id: int) -> list[Mission]:
        return self._by_map_id.get(map_id, [])
```

### 7. Update StaticData
```python
# hunterclassic/static_data/static_data.py
class StaticData:
    def __init__(self, files: StaticFiles) -> None:
        self._missions = MissionRepository(files.missions)
        # ... existing repositories ...

    @property
    def missions(self) -> MissionRepository:
        return self._missions
```

### 8. Add Validation (Optional)
```python
# hunterclassic/static_data/validator.py
class StaticDataValidator:
    def validate(self, files: StaticFiles) -> None:
        reserve_ids = {r.id for r in files.reserves}
        # Validate mission.map_id references existing reserves
        for mission in files.missions:
            if mission.map_id not in reserve_ids:
                raise ValueError(...)
```

## Design Principles

### 1. Models are Frozen
- All models use `model_config = ConfigDict(frozen=True)`
- No mutation after creation
- Hashable for use in sets/dicts

### 2. IDs in Models, Objects in Repositories
- Models store foreign keys as IDs: `map_id: int`
- Repositories resolve IDs to objects: `missions_in(reserve)`
- This avoids circular dependencies

### 3. O(1) Lookups
- Build indices in `__init__` of repositories
- All queries should be constant time
- Use `dict` and `set` operations

### 4. Separation of Concerns
- **Loader**: reads files → models
- **Validator**: checks integrity across collections
- **Repository**: indexes and queries
- **StaticData**: public API facade

## Example Queries for New Entity

```python
static = StaticData.load()

# Basic lookups
mission = static.missions.get(123)
all_missions = static.missions.all()

# Custom index query
hirschfelden_missions = static.missions.get_by_map(5)

# Cross-entity relationships
hirschfelden = static.reserves.get(5)
missions_there = static.missions.get_by_map(hirschfelden.id)
```

## Testing New Entities

1. Unit test the model
2. Unit test the repository indices
3. Integration test with real JSON data
4. Validate cross-references work

## Common Patterns

### One-to-Many Relationships
```python
# In ReserveRepository
def missions_in(self, reserve: Reserve, mission_repo: MissionRepository) -> list[Mission]:
    return mission_repo.get_by_map(reserve.id)
```

### Many-to-One Relationships
```python
# In MissionRepository
def reserve_for(self, mission: Mission, reserve_repo: ReserveRepository) -> Reserve | None:
    return reserve_repo.get(mission.map_id)
```

### Boolean Checks
```python
# In MissionRepository
def is_in_reserve(self, mission: Mission, reserve: Reserve) -> bool:
    return mission.map_id == reserve.id
```
