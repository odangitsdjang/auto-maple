import functools
EXISTING = {
    "CHAR_MAIN": 270,
    "CHAR_BOSS_MULE_1": 250, # SHAD
    "CHAR_BOSS_MULE_2": 230, # DW
    "CHAR_BOSS_MULE_3": 214, # WA
    "CHAR_BOSS_MULE_4": 201, # MARKSMAN
    "CHAR_LEGION_1": 226, # KHALI
    "CHAR_LEGION_2": 210, # MERC
    "CHAR_LEGION_3": 210, # EVAN
    "CHAR_LEGION_4": 210, # BT
    "CHAR_LEGION_5": 210, # AB
    "CHAR_LEGION_6": 201, # ADELE
    "CHAR_LEGION_7": 201, # BUCC
    "CHAR_LEGION_8": 201, # FP
}

TARGET_LEGION = 8000
TOTAL_LEGION_CHARS_COUNTED = 42

legion_chars = [i for i in EXISTING.values()]
existing_legion_length = len(legion_chars)

EXISTING_SUM = functools.reduce(lambda acc, sum: acc + sum, EXISTING.values())

REMAINING_LEGION_COUNT = TOTAL_LEGION_CHARS_COUNTED - existing_legion_length
REMAINING_AVG_LVL_REQD = (TARGET_LEGION - EXISTING_SUM) / REMAINING_LEGION_COUNT


print(f"Average level required for {TARGET_LEGION} legion with {TOTAL_LEGION_CHARS_COUNTED} characters: {TARGET_LEGION/TOTAL_LEGION_CHARS_COUNTED}")
print(f"Remaining legions chars left to do: {REMAINING_LEGION_COUNT}, Average level required for those chars: {REMAINING_AVG_LVL_REQD}")


# bossDefense = 300 # in percentage (300%)

# def calculateActualIED(source):
#     actualIED = functools.reduce(lambda acc, ied: acc * (1-ied), source.values())
#     return (1 - round(actualIED, 4)) 

# actualIED = calculateActualIED(sources)
# print("Actual IED is " + str(actualIED))
# print("Calculating remaining defense of boss, with defense " + str(bossDefense) + "%")
# remainingDefense = bossDefense-(actualIED*bossDefense)
# print(str(remainingDefense)+"%")

# actualIED2 = calculateActualIED(sources2)
# print("Actual IED of the second set is " + str(actualIED2))
# print("Calculating second remaining defense of boss, with defense " + str(bossDefense) + "%")
# remainingDefense2 = bossDefense-(actualIED2*bossDefense)
# print(str(remainingDefense2)+"%")

# print("Calculate damage difference with more IED in source2")
# damageDealt = 1 - (remainingDefense / 100)
# damageDealt2 = 1- (remainingDefense2 / 100)
# print(str(round(damageDealt2/damageDealt * 100, 2)) + "%")

# print("Consider if the above upgrade is worth the damage loss from boss damage/att/etc")