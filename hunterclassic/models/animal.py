from pydantic import BaseModel, ConfigDict


class Animal(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    short: str
    define: str
    ethical_ammo_ids: frozenset[int]
