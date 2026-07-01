from pydantic import BaseModel, ConfigDict

from hunterclassic.models.ammo import Ammo


class Weapon(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    shortname: str
    image: str
    ammo: tuple[Ammo, ...]
