from pydantic import BaseModel, ConfigDict


class Ammo(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    image: str
