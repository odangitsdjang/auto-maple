"""A collection of all commands that Adele can use to interact with the game. 	"""

from turtle import right
from src.common import config, settings, utils
import time
import math
from src.routine.components import Command, SkillCombination, Fall, BaseSkill
from src.common.vkeys import press, key_down, key_up

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/hayato/'

# List of key mappings
class Key:
    WORLD_MAP = 'pageup'
    
    # Movement
    FLASH_JUMP = 'alt'
    UP_JUMP = 'c'

    # Buffs
    BUFF_1 = 'f1' #公主的加護
    BUFF_2 = '6' # 幻靈武具
    BUFF_3 = 'ctrl' # 露希達寶珠
    BUFF_4 = 'f2' # 紋櫻公主的祝福

    # Buffs Toggle

    # Attack Skills
    MAIN_GROUP_ATTACK_SKILL = 'a' # 三連斬
    SKILL_A = 'a' # 連接五影用三連斬
    SKILL_1 = 'd' # 曉月大太刀
    SKILL_2 = 'w' # 剎那斬
    SKILL_22 = '2' # 幽暗戒指
    SKILL_3 = 'e' # 指令五影劍
    SKILL_33 = 's' # 五影劍
    SKILL_4 = 'q' # 神速無雙
    SKILL_5 = '4' # 曉月流奧義-劍神
    SKILL_6 = '5' # 集結曉之陣
    SKILL_7 = 'r' # 嘯月光斬
    SKILL_8 = '3' # 百人一閃/疾風五月雨刃
    SKILL_9 = 'f' # 一閃
    SKILL_10 = 'x' # 斷空閃
    SKILL_11 = '1' # 瞬殺斬
    SKILL_12 = 'f' # 一閃角
    SKILL_V = 'v' # 鷹爪閃
    SKILL_Z = 'z' # 連刃斬


#########################
#       Commands        #
#########################
def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]
    jump = config.bot.config['Jump']
    
    if direction == 'left' or direction == 'right':
        if abs(d_x) > 20:
            if abs(d_x) >= 33:
                if utils.bernoulli(0.2+0.3*(abs(d_x)-33)/100):
                    Skill_10(direction='',combo='true').execute()
                    MainGroupAttackSkill(direction='',attacks='1').execute()
                else:
                    FlashJump(direction='',triple_jump='true',fast_jump='false').execute()
                    SkillCombination(direction='',jump='false',target_skills='skill_1+skill_2|skill_a+skill_33|skill_3|MainGroupAttackSkill').execute()
            else:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                # MainGroupAttackSkill(direction='',attacks='3').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_1+skill_2|skill_a+skill_33|skill_3|MainGroupAttackSkill').execute()
                time.sleep(utils.rand_float(0.2, 0.25))
        elif abs(d_x) >= 13:
            Skill_Z().execute()
            key_up(direction)
        else:
            time.sleep(utils.rand_float(0.1, 0.15))
        utils.wait_for_is_standing(300)
    
    if direction == 'up':
        if abs(d_y) > 6 :
            if abs(d_y) > 23:
                UpJump(direction='',jump='true',combo='true').execute()
            else:
                UpJump(direction='',jump='false',combo='true').execute()
            # MainGroupAttackSkill(direction='',attacks='1').execute()
            Skill_4().execute()
            SkillCombination(direction='',jump='false',target_skills='skill_1+skill_2|MainGroupAttackSkill').execute()
            utils.wait_for_is_standing(300)
        else:
            press(jump, 1)
            time.sleep(utils.rand_float(0.1, 0.15))
    if direction == 'down':
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
            print("down stair")
            time.sleep(utils.rand_float(0.05, 0.07))
            press(jump, 1)
            time.sleep(utils.rand_float(0.08, 0.12))
            key_up('down')
            if abs(d_x) > 5:
                if d_x > 0:
                    key_down('right')
                    press(jump, 1)
                    key_up('right')
                else:
                    key_down('left')
                    press(jump, 1)
                    key_up('left')
            SkillCombination(direction='',jump='false',target_skills='skill_1+skill_2|skill_a+skill_33|skill_3|MainGroupAttackSkill').execute()
        time.sleep(utils.rand_float(0.05, 0.1))
      

class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5,direction="",jump='false',combo='false'):
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
                        key_down('left',down_time=0.02)
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right',down_time=0.02)
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance:
                    if d_y < 0:
                        utils.wait_for_is_standing(300)
                        UpJump('').main()
                    else:
                        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
                            print("down stair")
                            time.sleep(utils.rand_float(0.05, 0.07))
                            press(config.bot.config['Jump'], 1)
                            time.sleep(utils.rand_float(0.08, 0.12))
                            key_up('down')
                        time.sleep(utils.rand_float(0.1, 0.15))
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
        utils.wait_for_is_standing(1000)
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 121:
            time.sleep(utils.rand_float(0.1, 0.3))
            press(Key.BUFF_1, 1)
            time.sleep(utils.rand_float(0.6, 0.8))
            self.cd120_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd150_buff_time > 151:
            time.sleep(utils.rand_float(0.1, 0.3))
            press(Key.BUFF_3, 1)
            time.sleep(utils.rand_float(0.5, 0.7))
            self.cd150_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 181:
            time.sleep(utils.rand_float(0.1, 0.3))
            press(Key.BUFF_2, 1)
            time.sleep(utils.rand_float(0.5, 0.7))
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
            time.sleep(utils.rand_float(0.1, 0.3))
            press(Key.BUFF_4, 1)
            time.sleep(utils.rand_float(0.3, 0.5))
            self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
            self.cd900_buff_time = now
        # if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
        #     for key in buffs:
        #       press(key, 3, up_time=0.3)
        #       self.decent_buff_time = now		


class FlashJump(Command):
    """Performs a flash jump in the given direction."""
    _display_name = '二段跳'

    def __init__(self, direction="",jump='false',combo='',triple_jump="False",fast_jump="false"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.triple_jump = settings.validate_boolean(triple_jump)
        self.fast_jump = settings.validate_boolean(fast_jump)

    def main(self):
        self.player_jump(self.direction)
        if not self.fast_jump:
            time.sleep(utils.rand_float(0.03, 0.06)) # fast flash jump gap
        else:
            time.sleep(utils.rand_float(0.08, 0.12)) # slow flash jump gap
        if self.direction == 'up':
            press(Key.FLASH_JUMP, 1)
        else:
            press(Key.FLASH_JUMP, 1,up_time=0.05)
            if self.triple_jump:
                time.sleep(utils.rand_float(0.05, 0.08))
                press(Key.FLASH_JUMP, 1,down_time=0.07,up_time=0.04) # if this job can do triple jump
        key_up(self.direction,up_time=0.01)
        time.sleep(utils.rand_float(0.03, 0.06))
			

class UpJump(Command):
    """Performs a up jump in the given direction."""
    _display_name = '上跳'

    def __init__(self, direction="", jump='False',combo="false"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.jump:
            self.player_jump(self.direction)
            time.sleep(utils.rand_float(0.03, 0.06)) 
        else:
            key_down(self.direction)
        press(Key.UP_JUMP, 1,up_time=0.05)
        key_up(self.direction)
        if self.combo:
            time.sleep(utils.rand_float(0.04, 0.07))
        else:
            time.sleep(utils.rand_float(0.4, 0.6))

# 三連斬
class MainGroupAttackSkill(Command):
    """Attacks using '三連斬' in a given direction."""
    _display_name = '三連斬'

    def __init__(self, direction="",jump='false', attacks=3, repetitions=1,combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.jump:
            self.player_jump(self.direction)
            time.sleep(utils.rand_float(0.02, 0.05))
        else:
            key_down(self.direction)
        for _ in range(self.repetitions):
            press(Key.MAIN_GROUP_ATTACK_SKILL, self.attacks,down_time=0.08, up_time=0.06)
        # if config.stage_fright and utils.bernoulli(0.7):
        #     time.sleep(utils.rand_float(0.1, 0.2))
        key_up(self.direction,up_time=0.02)
        if self.combo:
            if self.attacks >= 3:
                time.sleep(utils.rand_float(0.1, 0.15))
            else:
                time.sleep(utils.rand_float(0.1, 0.15))
        else:
            if self.attacks == 3:
                time.sleep(utils.rand_float(0.45, 0.48))
            else:
                time.sleep(utils.rand_float(0.45, 0.48))

class Skill_A(Command):
    """Attacks using '連接五影用三連斬' in a given direction."""
    _display_name = '連接五影用三連斬'
    skill_cool_down = 3

    def __init__(self, direction="",jump='false', attacks=2, repetitions=1,combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.jump:
            self.player_jump(self.direction)
            time.sleep(utils.rand_float(0.02, 0.05))
        else:
            key_down(self.direction)
        for _ in range(self.repetitions):
            press(Key.SKILL_A, self.attacks,down_time=0.07, up_time=0.04)
        # if config.stage_fright and utils.bernoulli(0.7):
        #     time.sleep(utils.rand_float(0.1, 0.2))
        self.set_my_last_cooldown(time.time())
        key_up(self.direction,up_time=0.02)
        if self.combo:
            if self.attacks >= 3:
                time.sleep(utils.rand_float(0.02, 0.04))
            else:
                time.sleep(utils.rand_float(0.02, 0.04))
        else:
            if self.attacks == 3:
                time.sleep(utils.rand_float(0.45, 0.48))
            else:
                time.sleep(utils.rand_float(0.45, 0.48))

# 曉月大太刀
class Skill_1(Command):
    """Uses '曉月大太刀' once."""
    _display_name = '曉月大太刀'
    skill_cool_down = 8.2

    def __init__(self, direction='',jump='false',combo="true"):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                self.player_jump(self.direction)
                time.sleep(utils.rand_float(0.02, 0.05))
            else:
                key_down(self.direction)
            press(Key.SKILL_1, 1)
            key_up(self.direction,up_time=0.02)
            self.set_my_last_cooldown(time.time())
            if self.combo:
                time.sleep(utils.rand_float(0.4, 0.6))
            else:
                time.sleep(utils.rand_float(1.5, 1.8))
             
# 剎那斬
class Skill_2(Command):
    """Uses '剎那斬' once."""
    _display_name = '剎那斬'
    skill_cool_down = 8.2
    skill_image = IMAGE_DIR + 'skill_2.png'

    def __init__(self, direction='',jump='false',combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                self.player_jump(self.direction)
                time.sleep(utils.rand_float(0.02, 0.05))
            else:
                key_down(self.direction)
            press(Key.SKILL_2, 1, up_time=0.1)
            key_up(self.direction,up_time=0.02)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(0.3, 0.4))

class Skill_22(BaseSkill):
    _display_name ='幽暗戒指'
    key=Key.SKILL_22
    delay=0.8
    rep_interval=0.25
    skill_cool_down=3
    ground_skill=False
    combo_delay = 0.3

# 指令五影劍
class Skill_3(Command):
    """Attacks using '指令五影劍' in a given direction."""
    _display_name = '指令五影劍'
    skill_cool_down = 8.2

    def __init__(self, direction='',jump='false', attacks=1, repetitions=1,combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        if self.jump:
            self.player_jump(self.direction)
            time.sleep(utils.rand_float(0.02, 0.05))
        else:
            key_down(self.direction)
        press(Key.SKILL_3, self.attacks, up_time=0.05)
        key_up(self.direction,up_time=0.02)
        time.sleep(utils.rand_float(0.25, 0.35))
        self.set_my_last_cooldown(time.time())
		
# 五影劍
class Skill_33(Command):
    """Attacks using '五影劍' in a given direction."""
    _display_name = '五影劍'
    skill_cool_down = 25

    def __init__(self, direction='',jump='false', attacks=1, repetitions=1,combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            self.player_jump(self.direction)
            time.sleep(utils.rand_float(0.02, 0.05))
        else:
            key_down(self.direction)
        press(Key.SKILL_33, self.attacks, up_time=0.05)
        key_up(self.direction,up_time=0.02)
        self.set_my_last_cooldown(time.time())
        time.sleep(utils.rand_float(0.2, 0.25))
        if self.jump:
            time.sleep(utils.rand_float(0.2, 0.3))

# 神速無雙
class Skill_4(Command):
    """Press skill,Uses '神速無雙' once. 可消除上跳延遲"""
    _display_name = '神速無雙'

    def main(self):
        press(Key.SKILL_4, 1)

# 曉月流奧義-劍神
class Skill_5(Command):
    """Press skill,Uses '曉月流奧義-劍神' once. """
    _display_name = '曉月流奧義-劍神'
    skill_cool_down = 120
    skill_image = IMAGE_DIR + 'skill_5.png'
    buff_time=30

    def __init__(self,direction="",jump='false',combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.check_is_skill_ready():
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            press(Key.SKILL_5, 1, up_time=0.05)
            time.sleep(utils.rand_float(0.1, 0.15))
            key_up(self.direction,up_time=0.02)
            time.sleep(utils.rand_float(0.5, 0.6))
            self.set_my_last_cooldown(time.time())

# 集結曉之陣
class Skill_6(BaseSkill):
    """Press skill,Uses '集結曉之陣' once. """
    _display_name = '集結曉之陣'
    skill_cool_down = 120
    skill_image = IMAGE_DIR + 'skill_6.png'
    buff_time=30

    def main(self):
        if not self.check_should_active():
            return
        if self.check_is_skill_ready():
            utils.wait_for_is_standing(2000)
            press(Key.SKILL_6, 1, up_time=0.05)
            time.sleep(utils.rand_float(0.5, 0.6))
            self.set_my_last_cooldown(time.time())

# 嘯月光斬
class Skill_7(Command):
    """Press skill,Uses '嘯月光斬' once. """
    _display_name = '嘯月光斬'
    skill_cool_down = 88
    skill_image = IMAGE_DIR + 'skill_7.png'

    def __init__(self,direction="",jump='false',combo='true'):
        super().__init__(locals())
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.check_is_skill_ready():
            utils.wait_for_is_standing(2000)
            press(Key.SKILL_7, 1,down_time=0.2, up_time=0.1)
            self.set_my_last_cooldown(time.time())
            if self.combo:
                time.sleep(utils.rand_float(0.3, 0.5))
            else:
                time.sleep(utils.rand_float(2.8, 3))

# 百人一閃/疾風五月雨刃
class Skill_8(Command):
    """Press skill,Uses '百人一閃/疾風五月雨刃' once. """
    _display_name = '百人一閃/疾風五月雨刃'
    skill_cool_down = 120
    skill_image = IMAGE_DIR + 'skill_8.png'

    def __init__(self,direction="",jump='false',combo='true'):
        super().__init__(locals())
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.check_is_skill_ready():
          utils.wait_for_is_standing(2000)
          press(Key.SKILL_8, 1)
          self.set_my_last_cooldown(time.time())
          if self.combo:
              time.sleep(utils.rand_float(0.6, 0.8))
          else:
              time.sleep(utils.rand_float(2.5, 3))

# 一閃
class Skill_9(Command):
    """Press skill,Uses '一閃' once. """
    _display_name = '一閃'
    skill_cool_down = 56
    buff_time=54
    skill_image = IMAGE_DIR + 'skill_9.png'

    def __init__(self,direction="",jump='false',combo='true'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.check_is_skill_ready():
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            press(Key.SKILL_9, 1, up_time=0.1)
            key_up(self.direction,up_time=0.02)
            time.sleep(utils.rand_float(1.6, 1.8))
            self.set_my_last_cooldown(time.time())

# 一閃角
class Skill_12(BaseSkill):
    """Press skill,Uses '一閃角' once. """
    _display_name = '一閃角'
    skill_cool_down = 6.2
    active_if_skill_ready = ''
    active_if_skill_cd = ''
    active_if_in_skill_buff = ''
    active_if_not_in_skill_buff = ''

    def main(self):
        self.active_if_skill_cd = 'skill_9'
        if not self.check_should_active():
            return
        if self.check_is_skill_ready():
            if self.jump:
                utils.wait_for_is_standing(2000)
                self.player_jump()
            key_down(self.direction)
            press(Key.SKILL_9, 1, up_time=0.05)
            time.sleep(utils.rand_float(0.1, 0.12))
            key_up(self.direction,up_time=0.02)
            self.set_my_last_cooldown(time.time())
            if self.combo:
                time.sleep(utils.rand_float(0.3, 0.5))
            else:
                time.sleep(utils.rand_float(0.8, 1))

# 斷空閃
class Skill_10(Command):
    """Press skill,Uses '斷空閃' once. """
    _display_name = '斷空閃'
    _distance = 30

    def __init__(self,direction="",jump='false',combo="true"):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.combo = settings.validate_boolean(combo)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            self.player_jump(self.direction)
            time.sleep(utils.rand_float(0.02, 0.05))
        else:
            key_down(self.direction)
        press(Key.SKILL_10, 1, up_time=0.1)
        # time.sleep(utils.rand_float(0.05, 0.07))
        key_up(self.direction,up_time=0.01)
        if self.combo:
            time.sleep(utils.rand_float(0.02, 0.05))
        else:
            time.sleep(utils.rand_float(0.8, 0.9))

# 瞬殺斬
class Skill_11(Command):
    """Press skill,Uses '瞬殺斬' once. """
    _display_name = '瞬殺斬'
    skill_cool_down = 3.2

    def __init__(self, direction='',jump='false',combo="true"):
        super().__init__(locals())
        self.combo = settings.validate_boolean(combo)
        self.jump = settings.validate_boolean(jump)
        self.direction = settings.validate_arrows(direction)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                self.player_jump(self.direction)
                time.sleep(utils.rand_float(0.02, 0.05))
            else:
                key_down(self.direction)
            press(Key.SKILL_11, 1)
            key_up(self.direction,up_time=0.02)
            self.set_my_last_cooldown(time.time())
            if self.combo:
                time.sleep(utils.rand_float(0.1, 0.15))
            else:
                time.sleep(utils.rand_float(1, 1.2))

# 鷹爪閃
class Skill_V(Command):
    """Press skill,Uses '鷹爪閃' once. """
    _display_name = '鷹爪閃'
    _distance = 10

    def __init__(self,direction="",jump='false',combo="true"):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.combo = settings.validate_boolean(combo)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            self.player_jump(self.direction)
            time.sleep(utils.rand_float(0.02, 0.05))
        else:
            key_down(self.direction)
        press(Key.SKILL_V, 1, up_time=0.1)
        time.sleep(utils.rand_float(0.05, 0.07))
        key_up(self.direction,up_time=0.02)
        if self.combo:
            time.sleep(utils.rand_float(0.1, 0.3))
        else:
            time.sleep(utils.rand_float(1.1, 1.3))

# 連刃斬
class Skill_Z(Command):
    """Press skill,Uses '連刃斬' once. """
    _display_name = '連刃斬'
    _distance = 10

    def __init__(self,direction="",jump='false',combo="false"):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        key_down(self.direction)
        press(Key.SKILL_Z, 1, up_time=0.1)
        time.sleep(utils.rand_float(0.05, 0.07))
        key_up(self.direction,up_time=0.02)
        if self.combo:
            time.sleep(utils.rand_float(0.1, 0.3))
        else:
            time.sleep(utils.rand_float(0.3, 0.4))
