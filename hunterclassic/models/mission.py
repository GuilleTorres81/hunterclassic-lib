"""
Example extension: Mission model and repository.

This demonstrates how to add a new entity type to the static data system.

Steps to integrate:
1. Add missions.json to hunterclassic/static/
2. Add Mission to hunterclassic.models.__init__
3. Add parse_missions to StaticDataLoader
4. Add missions field to StaticFiles
5. Add MissionRepository to StaticData
6. Add validation if needed
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Mission(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    map_id: int  # References Reserve.id
    objective: str
    reward_xp: int
