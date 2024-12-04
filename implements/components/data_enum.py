from enum import Enum


class Penetration(Enum):
    YES = "Yes"
    NO = "No"


class Category(Enum):
    COLD_WEAPON = "冷兵器"
    THROWN_WEAPO = "投掷武器"
    HANDGUN = "手枪"
    RIFLE = "步枪"
    SHOTGUN = "霰弹枪"
    SMG = "冲锋枪"
    EXPLOSIVE = "爆炸物"
    HEAVY_WEAPON = "重型武器"
    ARTILLERY = "火炮"

