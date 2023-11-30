import functools
EXISTING = {
    "CHAR_MAIN": 271,
    "CHAR_BOSS_MULE_1": 251, # SHAD
    "CHAR_BOSS_MULE_2": 230, # DW
    "CHAR_BOSS_MULE_3": 215, # WA
    "CHAR_BOSS_MULE_4": 200, # MARKSMAN
    "CHAR_BOSS_MULE_5": 260, # BISHOP
    # "CHAR_BOSS_MULE_6": 201, # 
    "CHAR_LEGION_1": 226, # KHALI
    "CHAR_LEGION_2": 210, # MERC
    "CHAR_LEGION_3": 210, # EVAN
    "CHAR_LEGION_4": 210, # BT
    "CHAR_LEGION_5": 210, # AB
    "CHAR_LEGION_6": 201, # ADELE
    "CHAR_LEGION_7": 207, # BUCC
    "CHAR_LEGION_8": 201, # FP
    "CHAR_LEGION_9": 200, # HERO
    "CHAR_LEGION_10": 200, # nl
    # "CHAR_LEGION_11": 210, 
    "CHAR_LEGION_12": 200, # WH
    "CHAR_LEGION_13": 200, # SHADE
    "CHAR_LEGION_14": 200, # MECHANIC
    "CHAR_LEGION_15": 206, # LUMI
    "CHAR_LEGION_16": 180, # HAYATO
    "CHAR_LEGION_17": 180, # DA

    # TODO CHARS
    "CHAR_UNDERLEVELED_1": 163, # Zero
    "CHAR_UNDERLEVELED_2": 142, # Lara
    "CHAR_UNDERLEVELED_3": 140, # Aran
    "CHAR_UNDERLEVELED_4": 140, # Kanna
    "CHAR_UNDERLEVELED_5": 140, # HY
    "CHAR_UNDERLEVELED_6": 140, # Phantom
    "CHAR_UNDERLEVELED_7": 140, # Illium
    "CHAR_UNDERLEVELED_8": 141, # PF
    "CHAR_UNDERLEVELED_9": 101, # Xenon
    "CHAR_UNDERLEVELED_10": 140, # Ark
    "CHAR_UNDERLEVELED_11": 150, # Kinesis
    "CHAR_UNDERLEVELED_12": 164, # DS
    "CHAR_UNDERLEVELED_13": 150, # Blaster
    "CHAR_UNDERLEVELED_14": 0, # Cadena
    "CHAR_UNDERLEVELED_15": 102, # BaM
}

TARGET_LEGION = 8000
TOTAL_LEGION_CHARS_COUNTED = 42

legion_chars = [i for i in EXISTING.values()]
existing_legion_length = len(legion_chars)

EXISTING_SUM = functools.reduce(lambda acc, sum: acc + sum, EXISTING.values())

REMAINING_LEGION_COUNT = TOTAL_LEGION_CHARS_COUNTED - existing_legion_length
REMAINING_AVG_LVL_REQD = (TARGET_LEGION - EXISTING_SUM) / REMAINING_LEGION_COUNT

# TODO: Write functionality if more than 42 characters exist, top 42's legion, average of that 42,and how many levels [x] characters of that 42 need to be brought up to hit TARGET_LEGION
# top_42_chars = EXISTING ...
# remaining_chars = EXISTING ...


print(f"Average level required for {TARGET_LEGION} legion with {TOTAL_LEGION_CHARS_COUNTED} characters: {TARGET_LEGION/TOTAL_LEGION_CHARS_COUNTED}")
print(f"Current legion score: {EXISTING_SUM} with {existing_legion_length} characters, Average level of existing chars: {EXISTING_SUM/existing_legion_length}")
print(f"Remaining legions chars left to do: {REMAINING_LEGION_COUNT}, Average level required for those chars: {REMAINING_AVG_LVL_REQD}")
