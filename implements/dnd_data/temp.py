class RaceModel:
    def __init__(self):
        self.name: str = ""              # 种族名称（如"精灵"）
        self.subraces: list[Subrace] = []  # 子种族列表
        self.source: str = ""            # 来源书籍（PHB/XGE/TCE等）
        self.traits: list[Trait] = []     # 通用种族特性（所有子种族共享）
        self.age_range: tuple[int, int] = (0, 100)  # 典型年龄范围
        self.size: str = "Medium"        # 体型分类（Medium/Small）
        self.speed: dict[str, int] = {"walk": 30}  # 移动速度（包含游泳/飞行等）
        self.languages: LanguageSet = LanguageSet()  # 语言配置
        self.use_tce_rules: bool = False  # 是否使用TCE自定义属性规则

class Subrace:
    def __init__(self):
        self.name: str = ""              # 子种族名称（如"高等精灵"）
        self.asi: dict[str, int] = {}     # 属性加值（兼容PHB固定值和TCE可选值）
        self.traits: list[Trait] = []     # 子种族专属特性
        self.source: str = ""            # 子种族来源

class Trait:
    def __init__(self):
        self.name: str = ""              # 特性名称
        self.description: str = ""       # 特性描述
        self.type: str = "Passive"       # 特性类型（Passive/Active/Spell）
        # 特殊字段（根据类型变化）
        self.spells: list[Spell] = []     # 如果是法术型特性
        self.skills: list[str] = []       # 技能熟练项
        self.resistances: list[str] = []  # 伤害抗性类型
        self.actions: list[Action] = []   # 包含的动作（如龙裔喷吐武器）

class LanguageSet:
    def __init__(self):
        self.base: list[str] = ["Common"]  # 自动掌握的语言
        self.optional: int = 0            # 可选语言数量
        self.options: list[str] = []       # 可选语言列表

class Spell:
    def __init__(self):
        self.name: str = ""
        self.level: int = 0
        self.school: str = ""
        self.source: str = ""
        self.description: str = ""
        self.tags: list[str] = []

class Action:
    def __init__(self):
        self.name: str = ""
        self.type: str = ""               # 动作类型（Attack/Utility等）
        self.range: str = ""              # 作用范围
        self.damage: str = ""             # 伤害公式（如"2d6 fire"）