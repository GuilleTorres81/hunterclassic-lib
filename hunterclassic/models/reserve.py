from pydantic import BaseModel, ConfigDict


class Reserve(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    define: str
    species_ids: frozenset[int]
