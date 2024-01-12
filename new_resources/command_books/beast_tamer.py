"""A collection of all commands that Adele can use to interact with the game. 	"""

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command, SkillCombination, Fall, BaseSkill, Frenzy
from src.common.vkeys import press, key_down, key_up

### image dir
IMAGE_DIR = config.RESOURCES_DIR + '/command_books/beast_tamer/'
# List of key mappings
class Key:
    WORLD_MAP = 'pageup'
    
    # Movement
    FLASH_JUMP = 'alt'
    UP_JUMP = 'c'
    ROPE = '`'

    # Buffs
    BUFF_1 = '1' # 黃金卡牌
    BUFF_F1 = 'f1' # 全集中守護
    BUFF_F2 = 'f2' # 好戲上場
    BUFF_CTRL = 'CTRL' # 露西妲寶珠

    # Buffs Toggle
    BUFF_6 = '6' # 集中打擊

    # Attack Skills
    SKILL_A = 'a' # 隊伍攻擊
    SKILL_X = 'q' # 艾卡飛行
    SKILL_S = 's' # 隊伍轟炸
    SKILL_W = 'w' # 幻獸師派對時間
    SKILL_D = 'd' # 小動物大進擊
    SKILL_R = 'r' # 蜘蛛之鏡
    SKILL_F = 'f' # 小波波
    SKILL_2 = '2' # 打翻飯桌
    SKILL_3 = '3' # 煙霧放屁
    SKILL_4 = 'down+4' # 噴泉


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
        if abs(d_x) >= 16:
            # if abs(d_x) >= 60:
            #     FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
            #     time.sleep(utils.rand_float(0.7, 0.8))
            if abs(d_x) >= 24:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                time.sleep(utils.rand_float(0.6, 0.7))
            else:
                Skill_A(jump='true').execute()
                time.sleep(utils.rand_float(0.45, 0.55))
            # if abs(d_x) <= 22:
            #     key_up(direction)
            utils.wait_for_is_standing(500)
            time.sleep(utils.rand_float(0.1, 0.12))
        else:
            time.sleep(utils.rand_float(0.05, 0.08))
            utils.wait_for_is_standing(500)
        d_x = target[0] - config.player_pos[0]
        if abs(d_x) <= 6:
            key_up(direction)

    
    if direction == 'up':
        utils.wait_for_is_standing(500)
        if abs(d_x) > settings.move_tolerance:
            return
        if abs(d_y) > 6 :
            if abs(d_y) > 36:
                press(jump, 1)
                time.sleep(utils.rand_float(0.1, 0.15))
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            else:
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            utils.wait_for_is_standing(1000)
            time.sleep(utils.rand_float(0.1, 0.2))
        else:
            press(jump, 1)
            time.sleep(utils.rand_float(0.06, 0.12))
            utils.wait_for_is_standing(1000)
            time.sleep(utils.rand_float(0.1, 0.15))

    if direction == 'down':
        if abs(d_x) > settings.move_tolerance:
            return
        down_duration = 0.04
        if abs(d_y) > 20:
            down_duration = 0.4
        elif abs(d_y) > 13:
            down_duration = 0.22
        
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
            print("down stair")
            if abs(d_x) >= 6:
                if d_x > 0:
                    Fall(direction='right',duration=down_duration).execute()
                else:
                    Fall(direction='left',duration=down_duration).execute()
                
            else:
                Fall(direction='',duration=(down_duration+0.2)).execute()
                if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING:
                    if d_x > 0:
                        key_down('left')
                        press(jump)
                        key_up('left')
                    else:
                        key_down('right')
                        press(jump)
                        key_up('right')
            # SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
        utils.wait_for_is_standing(1800)
        time.sleep(utils.rand_float(0.1, 0.15))
     
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
        jump = config.bot.config['Jump']
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
                        press(jump, 2, down_time=0.1)
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
            # press(Key.BUFF_1, 2)
            # time.sleep(utils.rand_float(0.6, 0.8))
            self.cd120_buff_time = now
        if self.cd150_buff_time == 0 or now - self.cd150_buff_time > 150:
            # press(Key.BUFF_1, 2)
            # time.sleep(utils.rand_float(0.6, 0.8))
            self.cd150_buff_time = now
            Buff_ctrl().execute()
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 180:
            press('shift', 1,up_time=0.2)
            press('down', 1,up_time=0.4)
            Buff_1().execute()
            time.sleep(utils.rand_float(0.1, 0.2))
            press('shift', 1,up_time=0.2)
            press('left', 1,up_time=0.4)
            press(Key.BUFF_6,1,up_time=0.4)
            # Buff_1().execute()
            # time.sleep(utils.rand_float(0.5, 0.6))
            Buff_F2().execute()
            time.sleep(utils.rand_float(0.1, 0.2))
            Buff_F1().execute()
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
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

    def __init__(self, direction="",jump='false',combo='False',triple_jump="False",fast_jump="false",reverse_triple='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.triple_jump = settings.validate_boolean(triple_jump)
        self.fast_jump = settings.validate_boolean(fast_jump)
        self.jump = settings.validate_boolean(jump)
        self.reverse_triple = settings.validate_boolean(reverse_triple)

    def main(self):
        jump = config.bot.config['Jump']

        if not self.jump:
            utils.wait_for_is_standing()
            if not self.fast_jump:
                self.player_jump(self.direction)
                time.sleep(utils.rand_float(0.02, 0.04)) # fast flash jump gap
            else:
                key_down(self.direction,down_time=0.05)
                press(jump,down_time=0.06,up_time=0.05)
        else:
            key_down(self.direction,down_time=0.05)
            press(jump,down_time=0.06,up_time=0.05)
        
        press(Key.FLASH_JUMP, 1,down_time=0.06,up_time=0.01)
        key_up(self.direction,up_time=0.01)
        if self.triple_jump:
            time.sleep(utils.rand_float(0.03, 0.05))
            # reverse_direction
            reverse_direction = ''
            if self.reverse_triple:
                if self.direction == 'left':
                    reverse_direction = 'right'
                elif self.direction == 'right':
                    reverse_direction = 'left'
                print('reverse_direction : ',reverse_direction)
                key_down(reverse_direction,down_time=0.05)
            else:
                time.sleep(utils.rand_float(0.02, 0.03))
            press(Key.FLASH_JUMP, 1,down_time=0.07,up_time=0.04) # if this job can do triple jump
            if self.reverse_triple:
                key_up(reverse_direction,up_time=0.01)
        time.sleep(utils.rand_float(0.01, 0.02))

class UpJump(BaseSkill):
    """Performs a up jump in the given direction."""
    _display_name = '上跳'
    _distance = 27
    key=Key.UP_JUMP
    delay=0.1
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

    # def __init__(self,jump='false', direction='',combo='true'):
    #     super().__init__(locals())
    #     self.direction = settings.validate_arrows(direction)

    def main(self):
        self.jump = True
        super().main()

class Rope(BaseSkill):
    """Performs a up jump in the given direction."""
    _display_name = '連接繩索'
    _distance = 27
    key=Key.ROPE
    delay=1.4
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

# 隊伍攻擊
class Skill_AA(Command):
    """Attacks using '隊伍攻擊' in a given direction."""
    _display_name = '隊伍攻擊'

    def __init__(self, direction, attacks=2, repetitions=1,jump='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        jump = config.bot.config['Jump']
        if self.jump:
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(jump, 1)
        else:
            key_down(self.direction)
        time.sleep(utils.rand_float(0.03, 0.05))
        for _ in range(self.repetitions):
            press(Key.SKILL_A, self.attacks, up_time=0.08)
        # if config.stage_fright and utils.bernoulli(0.7):
        #     time.sleep(utils.rand_float(0.1, 0.2))
        key_up(self.direction)
        if self.combo:
            if self.attacks == 3:
                time.sleep(utils.rand_float(0.1, 0.15))
            else:
                time.sleep(utils.rand_float(0.1, 0.15))
        else:
            if self.attacks == 3:
                time.sleep(utils.rand_float(0.35, 0.45))
            else:
                time.sleep(utils.rand_float(0.3, 0.35))

# 艾卡飛行
class Skill_X(Command):
    """Attacks using '艾卡飛行' in a given direction."""
    _display_name = '艾卡飛行'
    skill_cool_down = 60
    skill_image = IMAGE_DIR + 'skill_x.png'

    def __init__(self):
        super().__init__(locals())

    def main(self):
        if self.check_is_skill_ready():
            press(Key.SKILL_X, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            self.set_my_last_cooldown(time.time())
		
# 隊伍轟炸
class Skill_SS(Command):
    """Attacks using '隊伍轟炸' in a given direction."""
    _display_name = '隊伍轟炸'
    skill_cool_down = 3
    skill_image = IMAGE_DIR + 'skill_s.png'

    def __init__(self):
        super().__init__(locals())

    def main(self):
        if self.check_is_skill_ready():
            press(Key.SKILL_S, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            self.set_my_last_cooldown(time.time())

class Buff_1(BaseSkill):
    _display_name = '黃金卡牌'
    _distance = 0
    key=Key.BUFF_1
    delay=0.7
    rep_interval=0.5
    skill_cool_down=30
    ground_skill=True
    buff_time=180
    combo_delay = 0.25

class Buff_F1(BaseSkill):
    _display_name = '全集中守護'
    _distance = 0
    key=Key.BUFF_F1
    delay=0.7
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=True
    buff_time=60
    combo_delay = 0.25

class Buff_F2(BaseSkill):
    _display_name = '好戲上場'
    _distance = 0
    key=Key.BUFF_F2
    delay=0.3
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=True
    buff_time=30
    combo_delay = 0.25

class Skill_W(BaseSkill):
    _display_name = '幻獸師派對時間'
    _distance = 0
    key=Key.SKILL_W
    delay=1.1
    rep_interval=0.5
    skill_cool_down=30
    ground_skill=False
    buff_time=10
    combo_delay = 0.25

class Skill_D(BaseSkill):
    _display_name = '小動物大進擊'
    _distance = 0
    key=Key.SKILL_D
    delay=0.2
    rep_interval=0.5
    skill_cool_down=30
    ground_skill=True
    buff_time=10
    combo_delay = 0.25

class Skill_F(BaseSkill):
    _display_name = '小波波'
    _distance = 0
    key=Key.SKILL_F
    delay=1
    rep_interval=0.5
    skill_cool_down=30
    ground_skill=True
    buff_time=60
    combo_delay = 0.25

class Skill_R(BaseSkill):
    _display_name ='蜘蛛之鏡'
    key=Key.SKILL_R
    delay=0.6
    rep_interval=0.25
    skill_cool_down=240
    ground_skill=False
    buff_time=0
    combo_delay = 0.4

class Skill_2(BaseSkill):
    _display_name = '打翻飯桌'
    _distance = 0
    key=Key.SKILL_2
    delay=2
    rep_interval=1.9
    skill_cool_down=15
    ground_skill=False
    buff_time=0
    combo_delay = 2

class Skill_3(BaseSkill):
    _display_name = '煙霧放屁'
    _distance = 0
    key=Key.SKILL_3
    delay=1
    rep_interval=0.5
    skill_cool_down=5
    ground_skill=True
    buff_time=15
    combo_delay = 0.25

class Skill_4(BaseSkill):
    _display_name ='噴泉'
    key=Key.SKILL_4
    delay=1
    rep_interval=0.25
    skill_cool_down=60
    ground_skill=True
    buff_time=60
    combo_delay = 0.3

class Skill_A(BaseSkill):
    _display_name = '普攻'
    _distance = 0
    key=Key.SKILL_A
    delay=0.5
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.25

class Buff_ctrl(BaseSkill):
    _display_name = '露西妲寶珠'
    _distance = 0
    key=Key.BUFF_CTRL
    delay=0.8
    rep_interval=0.5
    skill_cool_down=150
    ground_skill=True
    buff_time=120
    combo_delay = 0.25