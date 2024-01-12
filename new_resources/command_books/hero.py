"""A collection of all commands that Adele can use to interact with the game. 	"""

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command, SkillCombination, Fall,BaseSkill
from src.common.vkeys import press, key_down, key_up

### image dir
IMAGE_DIR = config.RESOURCES_DIR + '/command_books/hero/'
# List of key mappings
class Key:
    WORLD_MAP = 'pageup'
    
    # Movement
    FLASH_JUMP = 'alt'
    UP_JUMP = 'shift'
    ROPE = 'c'
    # Buffs
    BUFF_1 = "f"
    BUFF_V = "v"
    BUFF_S = "s"
    BUFF_G = "g"
    BUFF_R = "r"
    BUFF_F4 = "f4"
    # Buffs Toggle

    # Attack Skills
    SKILL_Q = 'q' # 烈焰翔斬
    SKILL_1 = '1' # 狂暴攻擊
    SKILL_2 = '2' # 憤怒爆發
    SKILL_3 = '3' # 靈氣之刃
    SKILL_W = 'w' # 空間斬
    SKILL_A = 'a' # 劍之幻象
    SKILL_X = 'x' # 閃光斬
    SKILL_T = 't' # 蜘蛛之鏡

#########################
#       Commands        #
#########################
def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    num_presses = 2
    if direction == 'up' or direction == 'down':
        num_presses = 1
    # if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
    #     time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]
    jump = config.bot.config['Jump']
    if direction == 'left' or direction == 'right':
        if abs(d_x) >= 16:
            if abs(d_x) >= 23:
                FlashJump(direction='',triple_jump='false',fast_jump='true').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_w|skill_a|skill_1').execute()
            else:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_w|skill_a|skill_q').execute()
            # time.sleep(utils.rand_float(0.05, 0.12))
            if abs(d_x) <= 22:
                key_up(direction)
            utils.wait_for_is_standing(200)
        else:
            SkillCombination(direction='',jump='true',target_skills='skill_a|skill_q').execute()
            # time.sleep(utils.rand_float(0.05, 0.12))
            utils.wait_for_is_standing(200)
    
    if direction == 'up':
        utils.wait_for_is_standing(500)
        if abs(d_y) > 6 :
            if abs(d_y) > 36:
                press(jump, 1)
                time.sleep(utils.rand_float(0.1, 0.15))
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            elif abs(d_y) <21:
                UpJump().execute()
                SkillCombination(direction='',jump='false',target_skills='skill_a|skill_1').execute()
            else:
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            utils.wait_for_is_standing(300)
        else:
            press(jump, 1)
            time.sleep(utils.rand_float(0.1, 0.15))
    if direction == 'down':
        down_duration = 0.04
        if abs(d_y) > 20:
            down_duration = 0.14
        elif abs(d_y) > 13:
            down_duration = 0.1
        
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
            print("down stair")
            if abs(d_x) > 3:
                if d_x > 0:
                    Fall(direction='right',duration=down_duration).execute()
                else:
                    Fall(direction='left',duration=down_duration).execute()
            else:
                Fall(direction='',duration=down_duration).execute()
            SkillCombination(direction='',jump='false',target_skills='skill_a|skill_1').execute()
        time.sleep(utils.rand_float(0.02, 0.05))
      

class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        threshold = settings.adjust_tolerance
        d_x = self.target[0] - config.player_pos[0]
        d_y = self.target[1] - config.player_pos[1]
        while config.enabled and counter > 0 and (abs(d_x) > threshold or abs(d_y) > threshold):
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(utils.rand_float(0.01, 0.02))
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(utils.rand_float(0.01, 0.02))
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance:
                    if d_y < 0:
                        utils.wait_for_is_standing(1000)
                        UpJump('up').main()
                    else:
                        utils.wait_for_is_standing(1000)
                        key_down('down')
                        time.sleep(utils.rand_float(0.05, 0.07))
                        press(config.bot.config['Jump'], 2, down_time=0.1)
                        key_up('down')
                        time.sleep(utils.rand_float(0.17, 0.25))
                    counter -= 1
            d_x = self.target[0] - config.player_pos[0]
            d_y = self.target[1] - config.player_pos[1]
            toggle = not toggle


class Buff(Command):
    """Uses each of Adele's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.cd120_buff_time = 0
        self.cd150_buff_time = 0
        self.cd180_buff_time = 0
        self.cd200_buff_time = 0
        self.cd240_buff_time = 0
        self.cd900_buff_time = 0
        self.decent_buff_time = 0

    def main(self):
        # buffs = [Key.SPEED_INFUSION, Key.HOLY_SYMBOL, Key.SHARP_EYE, Key.COMBAT_ORDERS, Key.ADVANCED_BLESSING]
        now = time.time()
        utils.wait_for_is_standing(2000)
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 120:
            press(Key.BUFF_R, 1,up_time=0.3)
            time.sleep(utils.rand_float(0.1, 0.3))
            press(Key.BUFF_1, 1,up_time=0.4)
            time.sleep(utils.rand_float(0.1, 0.3))
            self.cd120_buff_time = now
        if self.cd150_buff_time == 0 or now - self.cd150_buff_time > 150:
            press(Key.BUFF_G, 1,up_time=0.5)
            time.sleep(utils.rand_float(0.2, 0.3))
            self.cd150_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 180:
            press(Key.BUFF_F4, 1,up_time=0.3)
            time.sleep(utils.rand_float(0.2, 0.3))
            press(Key.BUFF_V, 1,up_time=0.2)
            time.sleep(utils.rand_float(0.2, 0.3))
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
            press(Key.BUFF_S, 1,up_time=0.2)
            time.sleep(utils.rand_float(0.2, 0.3))
            self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
            # press(Key.BUFF_2, 2)
            # time.sleep(utils.rand_float(0.5, 0.7))
            self.cd900_buff_time = now
        # if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
        #     for key in buffs:
        #       press(key, 3, up_time=0.3)
        #       self.decent_buff_time = now		


class FlashJump(Command):
    """Performs a flash jump in the given direction."""
    _display_name = '二段跳'

    def __init__(self, direction="left",triple_jump="False",fast_jump="true",jump='true',combo='true'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.triple_jump = settings.validate_boolean(triple_jump)
        self.fast_jump = settings.validate_boolean(fast_jump)

    def main(self):
        self.player_jump(self.direction)
        if self.fast_jump:
            time.sleep(utils.rand_float(0.09, 0.12)) # fast flash jump gap
        else:
            time.sleep(utils.rand_float(0.25, 0.35)) # slow flash jump gap
        if self.direction == 'up':
            press(Key.FLASH_JUMP, 1)
        else:
            press(Key.FLASH_JUMP, 1,up_time=0.05)
            if self.triple_jump:
                time.sleep(utils.rand_float(0.05, 0.08))
                press(Key.FLASH_JUMP, 1,down_time=0.07,up_time=0.04) # if this job can do triple jump
        key_up(self.direction,up_time=0.01)
        time.sleep(utils.rand_float(0.04, 0.06))
			
class UpJump(Command):
    """Performs a up jump in the given direction."""
    _display_name = '上跳'

    def __init__(self,jump='false', direction='',combo='true'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        utils.wait_for_is_standing(500)
        press(Key.UP_JUMP, 1)
        key_down(self.direction)
        time.sleep(utils.rand_float(0.35, 0.4))
        if 'left' in self.direction or 'right' in self.direction:
            press(config.bot.config['Jump'], 1)
        key_up(self.direction)
        

class Rope(Command):
    """Performs a up jump in the given direction."""
    _display_name = '連接繩索'

    def __init__(self, jump = 'false'):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            utils.wait_for_is_standing(500)
            press(config.bot.config['Jump'], 1)
            time.sleep(utils.rand_float(0.03, 0.05))
        press(Key.ROPE, 1, up_time=0.1)
        time.sleep(utils.rand_float(1.2, 1.4))

# 烈焰翔斬
class Skill_Q(Command):
    """Attacks using '烈焰翔斬' in a given direction."""
    _display_name = '烈焰翔斬'

    def __init__(self, direction='',jump='false',combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            self.player_jump(self.direction)
            time.sleep(utils.rand_float(0.02, 0.05))
        else:
            key_down(self.direction)
        press(Key.SKILL_Q, 1)
        key_up(self.direction,up_time=0.02)
        time.sleep(utils.rand_float(0.4, 0.45))

# 狂暴攻擊
class Skill_1(Command):
    """Attacks using '狂暴攻擊' in a given direction."""
    _display_name = '狂暴攻擊'

    def __init__(self, direction='',jump='false',combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            self.player_jump(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
        else:
            key_down(self.direction)
        press(Key.SKILL_1, 1)
        key_up(self.direction,up_time=0.01)
        time.sleep(utils.rand_float(0.35, 0.40))

# 憤怒爆發
class Skill_2(Command):
    """Attacks using '憤怒爆發' in a given direction."""
    _display_name = '憤怒爆發'
    skill_cool_down = 10

    def __init__(self, direction='',jump='false',combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        if self.check_is_skill_ready():
            utils.wait_for_is_standing(500)
            key_down(self.direction)
            press(Key.SKILL_2, 1, up_time=0.1)
            # if config.stage_fright and utils.bernoulli(0.7):
            #     time.sleep(utils.rand_float(0.1, 0.2))
            key_up(self.direction)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(0.6, 0.7))

# 靈氣之刃
class Skill_3(Command):
    """Attacks using '靈氣之刃' in a given direction."""
    _display_name = '靈氣之刃'
    skill_cool_down = 7

    def __init__(self, direction='up',jump='false',combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                utils.wait_for_is_standing(300)
                key_down(self.direction)
                press(config.bot.config['Jump'], 1)
            else:
                key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(Key.SKILL_3, 1, up_time=0.1)
            # if config.stage_fright and utils.bernoulli(0.7):
            #     time.sleep(utils.rand_float(0.1, 0.2))
            key_up(self.direction)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(0.4, 0.45))

# 空間斬
class Skill_W(Command):
    """Attacks using '空間斬' in a given direction."""
    _display_name = '空間斬'
    skill_cool_down = 20

    def __init__(self, direction='',jump='false',combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                self.player_jump(self.direction)
                time.sleep(utils.rand_float(0.02, 0.05))
            else:
                key_down(self.direction)
            press(Key.SKILL_W, 1)
            key_up(self.direction,up_time=0.02)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(1.3, 1.4))

# 劍之幻象
class Skill_A(Command):
    """Attacks using '劍之幻象' in a given direction."""
    _display_name = '劍之幻象'
    skill_cool_down = 30

    def __init__(self, direction='',jump='false',combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                utils.wait_for_is_standing(500)
                key_down(self.direction)
                press(config.bot.config['Jump'], 1)
            else:
                key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(Key.SKILL_A, 1, up_time=0.1)
            key_up(self.direction)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(0.5, 0.55))

# 閃光斬
class Skill_X(Command):
    """Attacks using '閃光斬' in a given direction."""
    _display_name = '閃光斬'
    skill_cool_down = 7

    def __init__(self, direction='',jump='false',combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                utils.wait_for_is_standing(500)
                press(config.bot.config['Jump'], 1)
            key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(Key.SKILL_X, 1, up_time=0.1)
            # if config.stage_fright and utils.bernoulli(0.7):
            #     time.sleep(utils.rand_float(0.1, 0.2))
            key_up(self.direction)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(0.4, 0.46))

class Skill_T(BaseSkill):
    _display_name ='蜘蛛之鏡'
    key=Key.SKILL_T
    delay=0.8
    rep_interval=0.25
    skill_cool_down=240
    ground_skill=False
    buff_time=0
    combo_delay = 0.3