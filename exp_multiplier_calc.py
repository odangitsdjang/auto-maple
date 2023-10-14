import functools 
# list all buffs, comment out buffs that are not active
# Use this calculator if lazy: https://docs.google.com/spreadsheets/d/1fs7e1cJtHlMJrzAc2LdSX-DevGeyCvQf1iEbia0ePI8/edit?usp=sharing
Buffs = {
    # Atmospheric
    "Mvp": 0.5,

    # Items
    # "MP_Gold": 0.1,
    # "EXP_Accumulation": 0.1,
    "2x_exp_coupon": 1.0,
    # "3x_exp_coupon": 2.0,
    "Budding_Sprout_Title": 0.1,
    "Pendant": 0.3,

    # Links
    "Merc_lv2": 0.15,
    # "Merc_lv3": 0.2,

    # Legion
    # "Zero_legion": 0.1,
    "Legion_Grid": 0.03,
    
    # Stats
    # "Hyper_Stat": 0.1,

    # Skills
    # "Decent_HS": 0.2,
    # "Pirate_Dice_1": 0.3,
    # "Pirate_Dice_2": 0.4,
    # "Pirate_Dice_3": 0.5,

    # Etc
    # "Burning_map": 0.5, 
    # "Night_Troupe": 0.05,
}

Buffs2 = {
    # Atmospheric
    "Mvp": 0.5,

    # Items
    # "MP_Gold": 0.1,
    "2x_exp_coupon": 1.0,
    "Budding_Sprout_Title": 0.1,
    "Pendant": 0.3,

    # Links
    "Merc_lv2": 0.15,

    # Legion
    "Legion_Grid": 0.03,
    
    # Stats
    # "Hyper_Stat": 0.1,

    # "Night_Troupe": 0.05,
}

buffs_multiplier = functools.reduce(lambda a, b: a+b, Buffs.values())
buffs2_multiplier = functools.reduce(lambda a, b: a+b, Buffs2.values())

print(buffs_multiplier)
print(buffs2_multiplier)

# Evan, Aran, Night Troupe buffs separate 
rune_buff_duration = 5
rune_buff_multiplier = 2
rune_buff_multiplier_event = 3

rune_buff_cd = 15 # this code only works if value is 15 or 10

kills_per_minute = 250
kills_per_minute2 = 250

kills_per_15_multiplier = (kills_per_minute *  buffs_multiplier * (15 - rune_buff_duration)) + (kills_per_minute * (buffs_multiplier + rune_buff_multiplier) * rune_buff_duration)
kills_per_15_multiplier2 = (kills_per_minute2 *  buffs2_multiplier * (15 - rune_buff_duration)) + (kills_per_minute2 * (buffs2_multiplier + rune_buff_multiplier_event) * rune_buff_duration)

# TODO: only used if rune buff cd == 10 minutes
kills_per_10 = -1
kills_per_10_2 = -1

kills_per_hour_multiplier = kills_per_15_multiplier * 4 if rune_buff_cd == 15 else kills_per_10 * 6
kills_per_hour_multiplier2 = kills_per_15_multiplier2 * 4 if rune_buff_cd == 15 else kills_per_10_2 * 6

# TODO: add spiegelman buff (2.5 min) every 500 kills calculation into 2nd multiplier calcuation
print(f"kills_per_hour_multiplier2/kills_per_hour_multiplier:  {kills_per_hour_multiplier2}/{kills_per_hour_multiplier}")
print(f"Second multiplier is better by: {((kills_per_hour_multiplier2/kills_per_hour_multiplier - 1) * 100 ):.2f}%")
