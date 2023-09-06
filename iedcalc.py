import functools

sources = {
    "HYPER_STATS": 0.3,
    "AMBITION_55": 0.055,
    "SETUP_TITLE_ETERNAL_FLAME": 0.2,
    "EQUIP_CRA_HAT": 0.1,
    "EQUIP_CRA_TOP": 0.05,
    "EQUIP_CRA_BOT": 0.05,
    "EQUIP_ABSOLAB_WEAPON": 0.1,
    "EQUIP_ABSOLAB_SET": 0.1,
    "EQUIP_BOSS_SET": 0.1,
    "SKILL_ARMOR_BREAK": 0.4,
    "SKILL_MARKSMANSHIP": 0.25,
    "SKILL_SHARP_EYES": 0.05,
    "SKILL_NODE": 0.2,
    "SKILL_LINK_HOYOUNG": 0.1,
    "LEGION_BT": 0.03,
    "FAMILIAR_1": 0.4,
}

sources2 = {
    "HYPER_STATS": 0.3,
    "AMBITION_55": 0.055,
    "SETUP_TITLE_ETERNAL_FLAME": 0.2,
    "EQUIP_CRA_HAT": 0.1,
    "EQUIP_CRA_TOP": 0.05,
    "EQUIP_CRA_BOT": 0.05,
    "EQUIP_ABSOLAB_WEAPON": 0.1,
    "EQUIP_ABSOLAB_SET": 0.1,
    "EQUIP_BOSS_SET": 0.1,
    "SKILL_ARMOR_BREAK": 0.4,
    "SKILL_MARKSMANSHIP": 0.25,
    "SKILL_SHARP_EYES": 0.05,
    "SKILL_NODE": 0.2,
    "SKILL_LINK_HOYOUNG": 0.1,
    "LEGION_BT": 0.03,
    "FAMILIAR_1": 0.4,
    "FAMILIAR_2": 0.3,
}

bossDefense = 300 # in percentage (300%)

def calculateActualIED(source):
    actualIED = functools.reduce(lambda acc, ied: acc * (1-ied), source.values())
    return (1 - round(actualIED, 4)) 

actualIED = calculateActualIED(sources)
print("Actual IED is " + str(actualIED))
print("Calculating remaining defense of boss, with defense " + str(bossDefense) + "%")
remainingDefense = bossDefense-(actualIED*bossDefense)
print(str(remainingDefense)+"%")

actualIED2 = calculateActualIED(sources2)
print("Actual IED of the second set is " + str(actualIED2))
print("Calculating second remaining defense of boss, with defense " + str(bossDefense) + "%")
remainingDefense2 = bossDefense-(actualIED2*bossDefense)
print(str(remainingDefense2)+"%")

print("Calculate damage difference with more IED in source2")
damageDealt = 1 - (remainingDefense / 100)
damageDealt2 = 1- (remainingDefense2 / 100)
print(str(round(damageDealt2/damageDealt * 100, 2)) + "%")

print("Consider if the above upgrade is worth the damage loss from boss damage/att/etc")