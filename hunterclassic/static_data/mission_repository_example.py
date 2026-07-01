"""
Example: MissionRepository demonstrating repository extension pattern.
"""

from __future__ import annotations

from hunterclassic.models.mission import Mission
from hunterclassic.static_data.repository import BaseRepository


class MissionRepository(BaseRepository[Mission]):
    """
    Example repository for missions with custom indices.

    Demonstrates:
    - Adding a custom index (by_map_id)
    - Adding domain-specific query methods
    - Maintaining O(1) lookups
    """

    def __init__(self, missions: tuple[Mission, ...]) -> None:
        super().__init__(missions)
        self._by_map_id: dict[int, list[Mission]] = {}
        for m in missions:
            self._by_map_id.setdefault(m.map_id, []).append(m)

    def get_by_map(self, map_id: int) -> list[Mission]:
        """All missions for a specific reserve/map."""
        return self._by_map_id.get(map_id, [])

    def missions_in(self, reserve_id: int) -> list[Mission]:
        """Alias for get_by_map with domain-friendly name."""
        return self.get_by_map(reserve_id)
