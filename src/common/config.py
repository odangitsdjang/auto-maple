"""A collection of variables shared across multiple modules."""


#########################
#       Constants       #
#########################
RESOURCES_DIR = 'new_resources'


#################################
#       Global Variables        #
#################################
# The player's position relative to the minimap
player_pos = (0, 0)

# Describes whether the main bot loop is currently running or not
enabled = False

# If there is another player in the map, Auto Maple will purposely make random human-like mistakes
stage_fright = False

# record the player's current states
player_states = {
  'is_standing':True,
  'fly_mode':True,
  'movement_state':0,
  'in_bottom_platform':False,
}

MOVEMENT_STATE_STANDING = 0
MOVEMENT_STATE_JUMPING = 1
MOVEMENT_STATE_FALLING = 2

# skill cd timer
skill_cd_timer = {}

# is_skill_ready
is_skill_ready_collector = {}

# Represents the current shortest path that the bot is taking
path = []

# jump button
jump_button = 'alt'

#############################
#       Shared Modules      #
#############################
# A Routine object that manages the 'machine code' of the current routine
routine = None

# Stores the Layout object associated with the current routine
layout = None

# Shares the main bot loop
bot = None

# Shares the video capture loop
capture = None

# Shares the keyboard listener
listener = None

# Shares the gui to all modules
gui = None
