from PyQt6.QtGui import QFont

LABEL_FONT = QFont("Inconsolata SemiBold")
LABEL_FONT.setPointSize(10)

EDIT_FONT = QFont("Inconsolatav")
EDIT_FONT.setPointSize(10)

GROUPED_SKILLS = {'art', 'science', 'survival', 'pilot'}
SPECIAL_SKILLS = {'fighting', 'firearms'}

PARENT_SKILL_DEFAULTS = {
    "art": 5,
    "fighting": 5,
    "firearms": 10,
    "language": 1,
    "pilot": 1,
    "science": 1,
    "survival": 10,
}

DEFAULT_SKILLS = {
    "accounting": 5,
    "anthropology": 1,
    "appraise": 5,
    "archaeology": 1,
    "art:painting": 5,
    "art:sculpture": 5,
    "art:acting": 5,
    "art:photography": 5,
    "art:writing": 5,
    "charm": 15,
    "climb": 20,
    "credit_rating": 0,
    "cthulhu_mythos": 0,
    "disguise": 5,
    "dodge": 0,
    "drive_auto": 20,
    "electrical_repair": 10,
    "electronics": 1,
    "fast_talk": 5,
    "fighting:brawl": 25,
    "fighting:chainsaw": 10,
    "fighting:flail": 10,
    "fighting:garrote": 15,
    "fighting:sword": 20,
    "fighting:whip": 5,
    "firearms:handgun": 20,
    "firearms:heavy_weapons": 10,
    "firearms:rifle": 25,
    "firearms:shotgun": 25,
    "firearms:smg": 15,
    "first_aid": 30,
    "history": 5,
    "intimidate": 15,
    "jump": 20,
    "language:own": 1,
    "language:english": 1,
    "language:spanish": 1,
    "language:latin": 1,
    "language:french": 1,
    "law": 5,
    "library_use": 20,
    "listen": 20,
    "locksmith": 1,
    "mechanical_repair": 10,
    "medicine": 1,
    "natural_world": 10,
    "navigate": 10,
    "occult": 5,
    "operate_heavy_machinery": 1,
    "persuade": 10,
    "pilot:airplane": 1,
    "pilot:boat": 1,
    "pilot:submarine": 1,
    "psychoanalysis": 1,
    "psychology": 10,
    "ride": 5,
    "science:astronomy": 1,
    "science:biology": 1,
    "science:chemistry": 1,
    "science:geology": 1,
    "science:physics": 1,
    "sleight_of_hand": 10,
    "spot_hidden": 25,
    "stealth": 20,
    "survival:desert": 10,
    "survival:forest": 10,
    "survival:mountain": 10,
    "survival:sea": 10,
    "swim": 20,
    "throw": 20,
    "track": 10
}

WEAPON_TYPES = {
    "Knife, Small": ("fighting:brawl", "1d4+db", 0),
    "Knife, Medium": ("fighting:brawl", "1d4+2+db", 0),
    "Knife, Large": ("fighting:brawl", "1d8+db", 0)
}