"""
A list of user-defined settings that can be changed by routines. Also contains a collection
of validator functions that can be used to enforce parameter types.
"""


#################################
#      Validator Functions      #
#################################

def validate_nonnegative_int(value):
    """
    Checks whether VALUE can be a valid non-negative integer.
    :param value:   The string to check.
    :return:        VALUE as an integer.
    """

    if int(value) >= 1:
        return int(value)
    raise ValueError(f"'{value}' is not a valid non-negative integer.")


def validate_boolean(value):
    """
    Checks whether VALUE is a valid Python boolean.
    This method will only be called with string value, as the value would have been a user input
    :param value:   The string to check.
    :return:        VALUE as a boolean
    """

    value = value.lower()
    if value in {'true', 'false'}:
        return True if value == 'true' else False
    elif int(value) in {0, 1}:
        return bool(int(value))
    raise ValueError(f"'{value}' is not a valid boolean.")


def validate_arrows(key):
    """
    Checks whether string KEY is an arrow key.
    :param key:     The key to check.
    :return:        KEY in lowercase if it is a valid arrow key.
    """

    if isinstance(key, str):
        key = key.lower()
        if key in ['','up', 'down', 'left', 'right', \
                'up+left','up+right','down+left','down+right',
                'left+up','right+up','left+down','right+down'
            ]:
            return key
    raise ValueError(f"'{key}' is not a valid arrow key.")


def validate_horizontal_arrows(key):
    """
    Checks whether string KEY is either a left or right arrow key.
    :param key:     The key to check.
    :return:        KEY in lowercase if it is a valid horizontal arrow key.
    """

    if isinstance(key, str):
        key = key.lower()
        if key in ['left', 'right','']:
            return key
    raise ValueError(f"'{key}' is not a valid horizontal arrow key.")

def validate_required(key):
    """
    Checks whether string KEY is either a left or right arrow key.
    :param key:     The key to check.
    :return:        KEY in lowercase if it is a valid horizontal arrow key.
    """

    if isinstance(key, str):
        key = key.lower()
        if key in ['']:
            raise ValueError(f"Key: '{key}' needs to be configured.")


#########################
#       Settings        #
#########################
# A dictionary that maps each setting to its validator function
SETTING_VALIDATORS = {
    'id': str,
    'full_screen':validate_boolean,
    'move_tolerance': float,
    'adjust_tolerance': float,
    'record_layout': validate_boolean,
    'buff_cooldown': validate_nonnegative_int,
    'platforms':str,
    'rent_frenzy':validate_boolean,
    'driver_key':validate_boolean,
    'auto_change_channel':validate_boolean,
    'partner' :str,
    'main_attack_skill_key' :str,
    'frenzy_key' :str,
    'home_scroll_key' :str,
    'rune_cd_min' : validate_nonnegative_int,
    'cd_value': str,
    'story_mode' : validate_boolean,
    'auto_revive' : validate_boolean,
    'is_shared_map': validate_boolean,
}


def reset():
    """Resets all settings to their default values."""

    global id, move_tolerance, adjust_tolerance, record_layout, buff_cooldown, rent_frenzy, platforms, driver_key
    global partner, main_attack_skill_key, frenzy_key, home_scroll_key
    id = ""
    move_tolerance = 9
    adjust_tolerance = 2
    record_layout = False
    buff_cooldown = 180
    platforms = ""
    partner = ''
    main_attack_skill_key = ''
    frenzy_key = ''
    home_scroll_key = ''
    rune_cd_min = 15
    cd_value = ''
    story_mode = False
    auto_revive = False
    is_shared_map = False
    # rent_frenzy = False
    # driver_key = False
    


# The allowed error from the destination when moving towards a Point
move_tolerance = 9

# The allowed error from a specific location while adjusting to that location
adjust_tolerance = 2

# Whether the bot should save new player positions to the current layout
record_layout = False

# The amount of time (in seconds) to wait between each call to the 'buff' command
buff_cooldown = 180

platforms = ""

rent_frenzy = False

full_screen = False

driver_key = False

# user id
id = ""

auto_change_channel = False

story_mode = False

auto_revive = False

rune_cd_min = 15

is_shared_map = False

#partner id
partner = ''
main_attack_skill_key = ''
frenzy_key = ''
home_scroll_key = ''
cd_value = ''

reset()
