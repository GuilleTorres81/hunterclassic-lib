from __future__ import annotations

from hunterclassic.static_data.static_data import StaticData


class StaticDataCache:
    """
    Ensures StaticData is loaded once and reused on subsequent calls.

    Usage:
        cache = StaticDataCache()
        static = cache.get()   # loads from disk
        static = cache.get()   # returns cached instance
        cache.invalidate()     # forces reload on next get()
    """

    def __init__(self) -> None:
        self._instance: StaticData | None = None

    def get(self) -> StaticData:
        if self._instance is None:
            self._instance = StaticData.load()
        return self._instance

    def invalidate(self) -> None:
        self._instance = None

    @property
    def is_loaded(self) -> bool:
        return self._instance is not None
