from __future__ import annotations

from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Generic repository for any static game entity.

    Subclass this to add custom indices and query methods.

    Example:
        class MissionRepository(BaseRepository[Mission]):
            def __init__(self, missions: tuple[Mission, ...]) -> None:
                super().__init__(missions)
                self._by_map_id: dict[int, list[Mission]] = {}
                for m in missions:
                    self._by_map_id.setdefault(m.map_id, []).append(m)

            def get_by_map(self, map_id: int) -> list[Mission]:
                return self._by_map_id.get(map_id, [])
    """

    def __init__(self, items: tuple[T, ...], id_attr: str = "id") -> None:
        self._items = items
        self._by_id: dict[int, T] = {getattr(i, id_attr): i for i in items}

    def get(self, id: int) -> T | None:
        """Return entity by ID, or None if not found."""
        return self._by_id.get(id)

    def get_or_raise(self, id: int) -> T:
        """Return entity by ID, raising KeyError if not found."""
        item = self._by_id.get(id)
        if item is None:
            raise KeyError(f"{type(self).__name__}: ID {id!r} not found")
        return item

    def all(self) -> tuple[T, ...]:
        """Return all entities in this repository."""
        return self._items

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)
