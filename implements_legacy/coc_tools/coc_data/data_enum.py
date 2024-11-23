from enum import Enum


class Penetration(Enum):
    YES = "Yes"
    NO = "No"


class Category(Enum):
    COLD_WEAPON = "Cold Weapon"
    THROWN_WEAPO = "Thrown Weapon"
    HANDGUN = "Handgun"
    RIFLE = "Rifle"
    SHOTGUN = "Shotgun"
    SMG = "SMG"
    EXPLOSIVE = "Explosive"
    HEAVY_WEAPON = "Heavy Weapon"
    ARTILLERY = "Artillery"

