from src.common import config, settings, utils
import time
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, GoToMap, ChangeChannel, Frenzy, Player_jump, WaitStanding, WealthPotion
from src.common.vkeys import press, key_down, key_up
import cv2

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/dawn_warrior/'

# List of key mappings
class Key:
    WORLD_MAP = 'pageup'
    
    # Movement
    FLASH_JUMP = 'shift'
    ROPE = 'v'
    UP_JUMP = 'c'

    # Buffs
    
    # Buffs Toggle

    # Attack Skills
    SKILL_A = 'a' # 精氣散播
    SKILL_S = 's' # 龍脈釋放(L水U日R風)
    SKILL_W = 'w' # 龍脈轉換(L水U日R風)
    SKILL_E = 'e' # 自由龍脈
    SKILL_X = 'x' # 龍脈的痕跡
    SKILL_Q = 'q' # 喚醒
    SKILL_R = 'r' # 大大的舒展
    SKILL_F = 'f' # 翻騰的精氣
    SKILL_3 = '3' # 蜿蜒的山脊
    SKILL_D = 'd' # 山之種子
    SKILL_4 = 'down+4' # 噴泉

    # special Skills
    SP_F12 = 'f12' # 輪迴

def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]
    if config.player_states['is_stuck'] and abs(d_x) < 16:
        print("is stuck")
        time.sleep(utils.rand_float(0.05, 0.08))
        x_arrow = ''
        if direction != 'left' and direction != 'right':
            if abs(d_x) >= 0:
                x_arrow = 'right'
            else:
                x_arrow = 'left'
            press(x_arrow+'+'+config.bot.config['Jump'])
        else:
            press(config.bot.config['Jump'])
        Skill_A(direction='',pre_delay='0.1').execute()
        WaitStanding(duration='3').execute()

    if direction == 'left' or direction == 'right':
        utils.wait_for_is_standing(1000)
        d_y = target[1] - config.player_pos[1]
        d_x = target[0] - config.player_pos[0]
        if abs(d_x) >= 14:
            if abs(d_x) >= 30:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
            elif abs(d_x) >= 26:
                press(config.bot.config['Jump'],up_time=0.08)
                time.sleep(0.3)
                press(Key.FLASH_JUMP,up_time=0.02)
                if d_x < 0:
                    key_up('left')
                    SkillCombination(direction='right',jump='false',target_skills='skill_a').execute()
                else:
                    key_up('right')
                    SkillCombination(direction='left',jump='false',target_skills='skill_a').execute()
            elif abs(d_x) >= 20:
                press(config.bot.config['Jump'],up_time=0.02)
                time.sleep(0.45)
                press(Key.FLASH_JUMP,up_time=0.02)
                if d_x < 0:
                    key_up('left')
                    press('right')
                else:
                    key_up('right')
                    press('left')
                utils.wait_for_is_standing(1500)
            else:
                Skill_A(direction='',jump='true').execute()
                utils.wait_for_is_standing(1500)
            time.sleep(utils.rand_float(0.05, 0.08))
            # if abs(d_x) <= 22:
            #     key_up(direction)
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
                SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
            utils.wait_for_is_standing(1500)
        else:
            time.sleep(utils.rand_float(0.03, 0.05))
            utils.wait_for_is_standing(1500)
    
    if direction == 'up':
        utils.wait_for_is_standing(500)
        if abs(d_x) > settings.move_tolerance:
            return
        if abs(d_y) > 6 :
            if abs(d_y) <= 27:
                UpJump().execute()
                SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
            elif abs(d_y) > 27:
                Rope(jump='true').execute()
                Skill_A().execute()
            else:
                UpJump().execute()
                SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
            utils.wait_for_is_standing(300)
        else:
            press(config.bot.config['Jump'], 1)
            time.sleep(utils.rand_float(0.1, 0.15))

    if direction == 'down':
        if abs(d_x) > settings.move_tolerance:
            return
        down_duration = 0.01
        
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
            print("down stair")
            Fall(direction='',duration=(down_duration)).execute()
            # if abs(d_x) >= 5:
            #     if d_x > 0:
            #         Fall(direction='right',duration=down_duration).execute()
            #     else:
            #         Fall(direction='left',duration=down_duration).execute()
                
            # else:
            #     Fall(direction='',duration=(down_duration+0.1)).execute()
            #     if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING:
            #         print("leave lader")
            #         if d_x > 0:
            #             key_down('left')
            #             press(config.bot.config['Jump'])
            #             key_up('left')
            #         else:
            #             key_down('right')
            #             press(config.bot.config['Jump'])
            #             key_up('right')
            SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
                
        utils.wait_for_is_standing(4000)
        time.sleep(utils.rand_float(0.03, 0.05))

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
                        UpJump().execute()
                        Skill_A().execute()
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
        utils.wait_for_is_standing(1000)
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 121:
            self.cd120_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd150_buff_time > 151:
            self.cd150_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 181:
            # Skill_4().execute()
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
            self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
            self.cd900_buff_time = now

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
        if not self.jump:
            utils.wait_for_is_standing()
            if not self.fast_jump:
                self.player_jump(self.direction)
                time.sleep(utils.rand_float(0.02, 0.04)) # fast flash jump gap
            else:
                key_down(self.direction,down_time=0.05)
                press(config.bot.config['Jump'],down_time=0.06,up_time=0.05)
        else:
            key_down(self.direction,down_time=0.05)
            # press(config.bot.config['Jump'],down_time=0.06,up_time=0.05)
        
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
    delay=0.35
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.35
        
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

class Skill_A(BaseSkill):
    _display_name = '精氣散播'
    _distance = 0
    key=Key.SKILL_A
    delay=0.45
    rep_interval=0.62
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class Skill_S(BaseSkill):
    _display_name = '龍脈釋放(L水U日R風)'
    _distance = 0
    key=Key.SKILL_S
    delay=0.55
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.55
    fast_direction=False

class Skill_W(BaseSkill):
    _display_name = '龍脈轉換(L水U日R風)'
    _distance = 0
    key=Key.SKILL_W
    delay=0.2
    rep_interval=0.1
    skill_cool_down=6.8
    ground_skill=True
    buff_time=0
    combo_delay = 0.1
    fast_direction=False

class Skill_E(BaseSkill):
    _display_name = '自由龍脈'
    _distance = 0
    key=Key.SKILL_E
    delay=0.4
    rep_interval=0.1
    skill_cool_down=1.5
    ground_skill=True
    buff_time=0
    combo_delay = 0.4
    recharge_interval = 10
    max_maintained = 3

class Skill_X(BaseSkill):
    _display_name = '龍脈的痕跡'
    _distance = 0
    key=Key.SKILL_X
    delay=0.25
    rep_interval=0.1
    skill_cool_down=1
    ground_skill=False
    buff_time=0
    combo_delay = 0.1
    recharge_interval = 6
    max_maintained = 3

class Skill_Q(BaseSkill):
    _display_name = '喚醒'
    _distance = 0
    key=Key.SKILL_Q
    delay=0.55
    rep_interval=0.1
    skill_cool_down=7
    ground_skill=True
    buff_time=0
    combo_delay = 0.55

class Skill_R(BaseSkill):
    _display_name = '大大的舒展'
    _distance = 0
    key=Key.SKILL_R
    delay=0.9
    rep_interval=0.1
    skill_cool_down=60
    ground_skill=True
    buff_time=0
    combo_delay = 0.9

class Skill_F(BaseSkill):
    _display_name = '翻騰的精氣'
    _distance = 0
    key=Key.SKILL_F
    delay=0.52
    rep_interval=0.1
    skill_cool_down=20
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class Skill_3(BaseSkill):
    _display_name = '蜿蜒的山脊'
    _distance = 0
    key=Key.SKILL_3
    delay=0.65
    rep_interval=0.1
    skill_cool_down=60
    ground_skill=False
    buff_time=10
    combo_delay = 0.65

class Skill_D(BaseSkill):
    _display_name = '山之種子'
    _distance = 0
    key=Key.SKILL_D
    delay=0.5
    rep_interval=0.1
    skill_cool_down=0.5
    ground_skill=True
    buff_time=20
    combo_delay = 0.5
    recharge_interval = 7
    max_maintained = 4

class Skill_4(BaseSkill):
    _display_name ='噴泉'
    key=Key.SKILL_4
    delay=0.6
    rep_interval=0.25
    skill_cool_down=60
    ground_skill=True
    buff_time=60
    combo_delay = 0.3

# class AutoHunting(Command):
#     _display_name ='自動走位狩獵'

#     def __init__(self,duration='180',map=''):
#         super().__init__(locals())
#         self.duration = float(duration)
#         self.map = map

#     def main(self):
#         daily_complete_template = cv2.imread('assets/daily_complete.png', 0)
#         start_time = time.time()
#         toggle = True
#         move = config.bot.command_book['move']
#         GoToMap(target_map=self.map).execute()
#         SkillCombination(direction='',target_skills='skill_a').execute()
#         minimap = config.capture.minimap['minimap']
#         height, width, _n = minimap.shape
#         bottom_y = height - 30
#         # bottom_y = config.player_pos[1]
#         settings.platforms = 'b' + str(int(bottom_y))
#         while True:
#             if settings.auto_change_channel and config.should_solve_rune:
#                 Skill_AS().execute()
#                 config.bot._solve_rune()
#                 continue
#             if settings.auto_change_channel and config.should_change_channel:
#                 ChangeChannel(max_rand=40).execute()
#                 Skill_AS().execute()
#                 continue
#             Frenzy().execute()
#             frame = config.capture.frame
#             point = utils.single_match_with_threshold(frame,daily_complete_template,0.9)
#             if len(point) > 0:
#                 print("one daily end")
#                 break
#             minimap = config.capture.minimap['minimap']
#             height, width, _n = minimap.shape
#             if time.time() - start_time >= self.duration:
#                 break
#             if not config.enabled:
#                 break
            
#             if toggle:
#                 # right side
#                 move((width-20),bottom_y).execute()
#                 if config.player_pos[1] >= bottom_y:
#                     bottom_y = config.player_pos[1]
#                     settings.platforms = 'b' + str(int(bottom_y))
#                 FlashJump(direction='left').execute()
#                 Skill_X(direction='left+up').execute()
#                 Skill_S().execute()
#                 FlashJump(direction='left').execute()
#                 SkillCombination(direction='left',target_skills='skill_w|skill_e|skill_as').execute()
#             else:
#                 # left side
#                 move(20,bottom_y).execute()
#                 if config.player_pos[1] >= bottom_y:
#                     bottom_y = config.player_pos[1]
#                     settings.platforms = 'b' + str(int(bottom_y))
#                 FlashJump(direction='right').execute()
#                 Skill_X(direction='right+up').execute()
#                 Skill_S().execute()
#                 FlashJump(direction='right').execute()
#                 SkillCombination(direction='right',target_skills='skill_w|skill_e|skill_as').execute()
            
#             if settings.auto_change_channel and config.should_solve_rune:
#                 config.bot._solve_rune()
#                 continue
#             if settings.auto_change_channel and config.should_change_channel:
#                 ChangeChannel(max_rand=40).execute()
#                 Skill_AS().execute()
#                 continue
#             move(width//2,bottom_y).execute()
#             UpJump(jump='true').execute()
#             SkillCombination(direction='left',target_skills='skill_w|skill_e|skill_as').execute()
#             SkillCombination(direction='right',target_skills='skill_1|skill_d|skill_as').execute()
#             toggle = not toggle
            

#         if settings.home_scroll_key:
#             config.map_changing = True
#             press(settings.home_scroll_key)
#             time.sleep(5)
#             config.map_changing = False
#         return
