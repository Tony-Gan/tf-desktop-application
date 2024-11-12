from dataclasses import dataclass
from typing import Dict


@dataclass
class Occupation:
    name: str
    skill_points_formula: str

    def __str__(self):
        return self.name

    def format_formula_for_display(self) -> str:
        return self.skill_points_formula.replace('*', '×').replace('MAX', 'max')

    def _calculate_max_stats(self, stats_str: str, stats: Dict[str, int]) -> int:
        stats_list = [s.strip() for s in stats_str.split(',')]
        return max(stats[stat] for stat in stats_list)

    def calculate_skill_points(self, stats: Dict[str, int]) -> int:
        parts = self.skill_points_formula.split('+')
        total = 0

        for part in parts:
            part = part.strip()
            if 'MAX(' in part:
                stat_str = part[part.find('(') + 1:part.find(')')]
                max_value = self._calculate_max_stats(stat_str, stats)
                multiplier = int(part[part.find('*') + 1:])
                total += max_value * multiplier
            else:
                stat = part[:part.find('*')]
                multiplier = int(part[part.find('*') + 1:])
                total += stats[stat] * multiplier

        return total


OCCUPATIONS = [
    # 探索类职业
    Occupation("Private Detective", "EDU*2+MAX(DEX,STR)*2"),
    Occupation("Antiquarian", "EDU*2+APP*2"),
    Occupation("Archaeologist", "EDU*4+DEX*1"),
    Occupation("Explorer", "EDU*2+MAX(DEX,STR,CON)*2"),
    Occupation("Librarian", "EDU*4"),
    Occupation("Historian", "EDU*4"),
    Occupation("Treasure Hunter", "EDU*2+MAX(STR,DEX,CON)*2"),
    Occupation("Cartographer", "EDU*3+DEX*1"),
    Occupation("Naturalist", "EDU*3+POW*1"),
    Occupation("Survivalist", "EDU*2+CON*2"),
    Occupation("Expedition Leader", "EDU*2+APP*2+POW*1"),
    
    # 专业人士
    Occupation("Doctor", "EDU*4"),
    Occupation("Professor", "EDU*4"),
    Occupation("Lawyer", "EDU*4"),
    Occupation("Engineer", "EDU*4+DEX*1"),
    Occupation("Journalist", "EDU*2+MAX(APP,DEX,POW)*2"),
    Occupation("Accountant", "EDU*4"),
    Occupation("Psychologist", "EDU*4"),
    Occupation("Pilot", "EDU*2+DEX*2"),
    Occupation("Veterinarian", "EDU*4"),
    Occupation("Pharmacist", "EDU*4"),
    Occupation("Architect", "EDU*4"),
    Occupation("Paramedic", "EDU*3+DEX*1"),
    Occupation("Forensic Scientist", "EDU*4"),

    # 警察与军队
    Occupation("Police Officer", "EDU*2+MAX(STR,DEX,POW)*2"),
    Occupation("Soldier", "EDU*2+MAX(STR,DEX,CON)*2"),
    Occupation("Marine", "EDU*2+STR*2+DEX*1"),
    Occupation("Firefighter", "EDU*2+STR*2"),
    Occupation("Detective", "EDU*2+DEX*2"),
    Occupation("SWAT Officer", "EDU*2+MAX(STR,DEX,POW)*2"),
    Occupation("Sniper", "DEX*4"),
    Occupation("Explosives Expert", "EDU*3+DEX*1"),
    Occupation("Military Officer", "EDU*3+APP*1"),
    Occupation("K-9 Unit Officer", "EDU*2+STR*2"),

    # 艺术与表演
    Occupation("Actor", "APP*4"),
    Occupation("Artist", "EDU*2+APP*2"),
    Occupation("Musician", "EDU*2+DEX*2"),
    Occupation("Photographer", "EDU*2+DEX*2"),
    Occupation("Writer", "EDU*4"),
    Occupation("Ballet Dancer", "DEX*4"),
    Occupation("Circus Performer", "DEX*3+APP*1"),
    Occupation("Film Director", "EDU*3+APP*1"),
    Occupation("Poet", "EDU*4"),
    Occupation("Voice Actor", "APP*4"),

    # 商业类职业
    Occupation("Businessman", "EDU*2+APP*2"),
    Occupation("Shopkeeper", "EDU*2+APP*2"),
    Occupation("Banker", "EDU*4"),
    Occupation("Real Estate Agent", "EDU*2+APP*2"),
    Occupation("Investor", "EDU*3+APP*1"),
    Occupation("Real Estate Developer", "EDU*3+APP*1"),
    Occupation("Insurance Agent", "EDU*2+APP*2"),
    Occupation("Corporate Executive", "EDU*3+APP*1"),
    Occupation("Stockbroker", "EDU*3+DEX*1"),

    # 冒险者与流浪者
    Occupation("Explorer", "EDU*2+DEX*2"),
    Occupation("Sailor", "EDU*2+DEX*2"),
    Occupation("Smuggler", "EDU*2+DEX*2"),
    Occupation("Criminal", "EDU*2+DEX*2"),
    Occupation("Drifter", "DEX*4"),
    Occupation("Big Game Hunter", "STR*3+DEX*1"),
    Occupation("Treasure Diver", "DEX*3+CON*1"),
    Occupation("Mountain Climber", "STR*2+DEX*2"),
    Occupation("Desert Nomad", "CON*3+POW*1"),
    Occupation("Urban Explorer", "DEX*3+EDU*1"),
    
    # 宗教与灵性
    Occupation("Priest", "EDU*4"),
    Occupation("Occultist", "EDU*2+POW*2"),
    Occupation("Shaman", "POW*4"),
    Occupation("Cultist", "POW*4"),
    Occupation("Cult Leader", "POW*3+APP*1"),
    Occupation("Faith Healer", "POW*4"),
    Occupation("Medium", "POW*4"),
    Occupation("Astrologer", "EDU*3+POW*1"),
    Occupation("Exorcist", "EDU*2+POW*2"),

    # 科技与科学
    Occupation("Scientist", "EDU*4"),
    Occupation("Astronomer", "EDU*4"),
    Occupation("Chemist", "EDU*4"),
    Occupation("Physicist", "EDU*4"),
    Occupation("Biologist", "EDU*4"),
    Occupation("Computer Scientist", "EDU*4"),
    Occupation("Data Analyst", "EDU*4"),
    Occupation("Robotics Engineer", "EDU*4"),
    Occupation("Cybersecurity Expert", "EDU*4"),
    Occupation("Quantum Physicist", "EDU*4"),
    Occupation("Meteorologist", "EDU*4"),

    # 军事与安全
    Occupation("Bodyguard", "STR*2+DEX*2"),
    Occupation("Bounty Hunter", "DEX*2+STR*2"),
    Occupation("Mercenary", "STR*2+DEX*2"),
    Occupation("Security Guard", "DEX*2+STR*2"),
    Occupation("Combat Medic", "EDU*3+CON*1"),
    Occupation("Demolition Specialist", "DEX*3+EDU*1"),
    Occupation("Martial Artist", "DEX*4"),
    Occupation("Bodyguard", "STR*3+DEX*1"),
    Occupation("Sharpshooter", "DEX*4"),

    # 其他经典职业
    Occupation("Farmer", "EDU*2+STR*2"),
    Occupation("Bartender", "EDU*2+APP*2"),
    Occupation("Waiter", "APP*4"),
    Occupation("Chef", "DEX*4"),
    Occupation("Taxi Driver", "DEX*2+EDU*2"),
    Occupation("Street Performer", "APP*4"),
    Occupation("Fortune Teller", "POW*4"),
    Occupation("Blacksmith", "STR*3+DEX*1"),
    Occupation("Butcher", "STR*3+CON*1"),
    Occupation("Florist", "DEX*2+APP*2"),
    Occupation("Baker", "DEX*3+CON*1"),
    Occupation("Fisherman", "STR*2+CON*2"),

    # 中国特色
    Occupation("Traditional Herbalist", "EDU*4+POW*1"),
    Occupation("Feng Shui Consultant", "POW*4+EDU*1"),
    Occupation("Calligrapher", "DEX*3+EDU*1"),
    Occupation("Tai Chi Instructor", "DEX*3+POW*1"),
    Occupation("Tea Master", "APP*3+EDU*1"),
    Occupation("Acrobat", "DEX*4"),
    Occupation("Taoist Priest", "EDU*3+POW*2"),
    Occupation("Martial Arts Coach", "STR*3+DEX*1"),
    Occupation("Peking Opera Performer", "APP*3+DEX*1"),
    Occupation("Chinese Chess Master", "EDU*4"),

    # 日本特色
    Occupation("Samurai", "STR*3+DEX*2"),
    Occupation("Ninja", "DEX*4"),
    Occupation("Shinto Priest", "EDU*3+POW*2"),
    Occupation("Geisha", "APP*4"),
    Occupation("Kendo Instructor", "STR*2+DEX*2"),
    Occupation("Potter", "DEX*3+EDU*1"),
    Occupation("Manga Artist", "DEX*3+EDU*1"),
    Occupation("Game Developer", "EDU*3+DEX*1"),
    Occupation("Iaido Master", "DEX*4"),
    Occupation("Sushi Chef", "DEX*4"),

    # 韩国特色
    Occupation("Taekwondo Instructor", "DEX*4"),
    Occupation("Traditional Korean Doctor", "EDU*4+POW*1"),
    Occupation("Ceramic Artist", "DEX*3+EDU*1"),
    Occupation("Samulnori Drummer", "DEX*3+STR*1"),
    Occupation("K-POP Idol", "APP*4"),
    Occupation("Kimchi Specialist", "DEX*3+CON*1"),
    Occupation("Online Streamer", "APP*3+EDU*1"),
    Occupation("Korean Cuisine Chef", "DEX*4"),

    # 东南亚特色
    Occupation("Yoga Guru", "POW*4+DEX*1"),
    Occupation("Bollywood Actor", "APP*4"),
    Occupation("Meditation Instructor", "POW*4"),
    Occupation("Street Performer", "APP*3+DEX*1"),
    Occupation("Muay Thai Fighter", "STR*3+DEX*1"),
    Occupation("Indian Astrologer", "POW*4"),
    Occupation("Buddhist Monk", "EDU*3+POW*2"),
    Occupation("Traditional Dancer", "DEX*4"),

    # 现代亚洲扩展
    Occupation("IT Specialist", "EDU*4"),
    Occupation("E-Sports Player", "DEX*4"),
    Occupation("Manga Assistant", "DEX*3+EDU*1"),
    Occupation("Crafts Merchant", "APP*3+EDU*1"),
    Occupation("Mobile Repair Technician", "DEX*3+EDU*1"),
    Occupation("Japanese Cuisine Chef", "DEX*4"),
    Occupation("Tea Ceremony Master", "APP*3+DEX*1"),
    Occupation("Kite Maker", "DEX*3+STR*1"),

    # 亚洲流浪者与冒险者
    Occupation("Ronin", "STR*3+DEX*1"),
    Occupation("Street Fighter", "DEX*3+STR*1"),
    Occupation("Snake Charmer", "POW*4"),
    Occupation("Wandering Monk", "POW*3+EDU*1"),
    Occupation("Bamboo Craftsman", "DEX*4")
]

