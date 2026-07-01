from pydantic import BaseModel, ConfigDict

from hunterclassic.models.ammo import Ammo
from hunterclassic.models.weapon import Weapon


class EthicalLoadout(BaseModel):
    model_config = ConfigDict(frozen=True)

    weapon: Weapon
    ammo: Ammo
