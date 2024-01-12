from src.common import config, settings, utils
import time
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, GoToMap, ChangeChannel, Frenzy, Player_jump, WaitStanding, WealthPotion
from src.common.vkeys import press, key_down, key_up
import cv2

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/hoyung/'

# List of key mappings
class Key:
    WORLD_MAP = 'pageup'
    
    # Movement
    FLASH_JUMP = 'alt'
    # ROPE = 'c'
    FLY = 'x' # 觔斗雲
    SET_GATE = 'up+v' # 歪曲縮地符
    GATE = 'v' # 歪曲縮地符
    STOMP = 'shift' # 遁甲千斤石

    # UP_JUMP = 'up+alt'

    # Buffs
    BUFF_1 = '1' # 靈藥太乙仙丹
    BUFF_5 = '5' # 幻影分身符
    BUFF_6 = '6' # 蝴蝶之夢
    BUFF_F1 = 'f1' # 天地人幻影
    BUFF_F2 = 'f2' # 極大分身亂舞
    BUFF_F3 = 'f3' # 降臨怪力亂神
    BUFF_F5 = 'f5' # 必死決心

    # Buffs Toggle

    # Attack Skills
    SKILL_A = 'a' # 如意扇
    SKILL_Q = 'q' # 芭蕉風
    SKILL_W = 'w' # 金箍棒
    SKILL_E = 'e' # 滅火炎
    SKILL_C = 'c' # 地震碎
    SKILL_S = 's' # 土波流
    SKILL_D = 'd' # 吸星渦流
    SKILL_F = 'f' # 追擊鬼火符
    SKILL_2 = '2' # 蜘蛛之鏡
    SKILL_3 = '3' # 山靈召喚
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
    jump = config.bot.config['Jump']

    if config.player_states['is_stuck']:
        print("is stuck")
        time.sleep(utils.rand_float(0.05, 0.08))
        x_arrow = ''
        if direction != 'left' and direction != 'right':
            if abs(d_x) >= 0:
                x_arrow = 'right'
            else:
                x_arrow = 'left'
            press(x_arrow+'+'+jump)
        else:
            press(jump)
        Skill_A(direction='',pre_delay='0.1').execute()
        WaitStanding(duration='3').execute()

    if direction == 'left' or direction == 'right':
        utils.wait_for_is_standing(1000)
        d_y = target[1] - config.player_pos[1]
        d_x = target[0] - config.player_pos[0]
        if abs(d_x) >= 10:
            if abs(d_x) >= 60:
                FlashJump(direction='',triple_jump='true',fast_jump='false').execute()
                Fly(pre_delay='0.1',duration='0.9').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_w|skill_a').execute()
            elif abs(d_x) >= 28:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                fly_time = (abs(d_x)-21)*0.027
                fly_time_y = (abs(d_y)-5.8)*0.031
                if fly_time >= 0.93:
                    fly_time = 0.93
                if fly_time <= 0.05:
                    fly_time = 0.05
                if fly_time_y >= fly_time:
                    fly_time_y = fly_time
                if fly_time_y <= 0.05:
                    fly_time_y = 0.05
                print("fly_time",fly_time)
                Fly(jump='false',key_down_skill='true').execute()
                if abs(d_y) >= 7:
                    if d_y < 0 :
                        d = 'up'
                    else:
                        d = 'down'
                    print('second direction : ', d )
                    press(d,down_time=fly_time_y,up_time=0.02)
                    time.sleep(fly_time-fly_time_y+0.02)
                else:
                    time.sleep(utils.rand_float(fly_time*0.94, fly_time+0.03))
                Fly(key_up_skill='true').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_w|skill_a').execute()
            else:
                fly_time = (abs(d_x)-10)*0.027
                fly_time_y = (abs(d_y)-5.8)*0.03
                if fly_time >= 0.92:
                    fly_time = 0.92
                if fly_time <= 0.05:
                    fly_time = 0.05
                if fly_time_y >= fly_time:
                    fly_time_y = fly_time
                if fly_time_y <= 0.05:
                    fly_time_y = 0.05
                print("fly_time",fly_time)
                Skill_QQ(jump='true').execute()
                Fly(jump='false',key_down_skill='true').execute()
                if abs(d_y) >= 7:
                    if d_y < 0 :
                        d = 'up'
                    else:
                        d = 'down'
                    print('second direction : ', d )
                    press(d,down_time=fly_time_y,up_time=0.02)
                    time.sleep(fly_time-fly_time_y)
                else:
                    time.sleep(utils.rand_float(fly_time*0.94, fly_time+0.04))
                Fly(key_up_skill='true').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_w|skill_a').execute()
            # time.sleep(utils.rand_float(0.04, 0.06))
            # if abs(d_x) <= 22:
            #     key_up(direction)
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
                SkillCombination(direction='',jump='false',target_skills='stomp|skill_a').execute()
            utils.wait_for_is_standing(2500)
        else:
            time.sleep(utils.rand_float(0.03, 0.06))
            utils.wait_for_is_standing(2500)
    
    if direction == 'up':
        utils.wait_for_is_standing(500)
        if abs(d_x) > settings.move_tolerance:
            return
        if abs(d_y) > 6 :
            if abs(d_y) >= 30:
                fly_time_y = (abs(d_y)-27)*0.034
                if fly_time_y >= 0.93:
                    fly_time = 0.93
                if fly_time_y <= 0.05:
                    fly_time_y = 0.05
                Skill_QQ().execute()
                Fly(direction='up',duration=str(fly_time_y)).execute()
                Skill_E(direction='up',rep='2').execute()
                SkillCombination(direction='',jump='false',target_skills='stomp').execute()
            # elif abs(d_y) <= 17:
            #     # UpJump().execute()
            #     SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
            else:
                Skill_QQ().execute()
                fly_time_y = (abs(d_y)-4)*0.034
                if fly_time_y >= 0.93:
                    fly_time = 0.93
                if fly_time_y <= 0.05:
                    fly_time_y = 0.05
                print("fly_time",fly_time_y)
                Fly(jump='false',key_down_skill='true').execute()
                press('up',down_time=fly_time_y,up_time=0.03)
                Fly(key_up_skill='true').execute()
                SkillCombination(direction='',jump='false',target_skills='stomp|skill_a').execute()
            utils.wait_for_is_standing(1300)
        else:
            press(jump, 1)
            time.sleep(utils.rand_float(0.1, 0.15))

    if direction == 'down':
        if abs(d_x) > settings.move_tolerance:
            return
        
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
            print("down stair")
            if abs(d_y) >= 7:
                time.sleep(utils.rand_float(0.07, 0.1))
                key_up('down')
                if d_x >= 0:
                    x_direction = 'right'
                else:
                    x_direction = 'left'
                press(x_direction+'+'+jump, 1,up_time=0.12)
                # Skill_Q(combo='true').execute()
                fly_time = (abs(d_y)-4)*0.025
                Fly(direction='down',duration=str(fly_time)).execute()
                Stomp().execute()
            else:
                Fall(duration='0.1').execute() 
                # Stomp().execute()
        utils.wait_for_is_standing(2000)
        time.sleep(utils.rand_float(0.1, 0.12))

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
                        Skill_QQ().execute()
                        fly_time = abs(d_y)-6
                        if fly_time <= 0:
                            fly_time = 0.05
                        Fly(direction='up',duration=str(fly_time*0.028)).execute()
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
            press(config.bot.config['Jump'],down_time=0.06,up_time=0.05)
        
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

class Fly(BaseSkill):
    _display_name = '觔斗雲'
    _distance = 30 # max 1s
    key=Key.FLY
    delay=0.02
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.02
    float_in_air = True
    fast_rep=True

    def main(self):
        if self.duration >= 0.95:
            self.duration = 0.95
        if self.direction.find('up') > -1 and self.direction.find('down') > -1:
            self.direction_after_skill = True
        return super().main()

# class Rope(BaseSkill):
#     """Performs a up jump in the given direction."""
#     _display_name = '連接繩索'
#     _distance = 27
#     key=Key.ROPE
#     delay=1.4
#     rep_interval=0.5
#     skill_cool_down=0
#     ground_skill=False
#     buff_time=0
#     combo_delay = 0.2

class Stomp(BaseSkill):
    _display_name = '遁甲千斤石'
    _distance = 0
    key=Key.STOMP
    delay=0.5
    rep_interval=0.5
    skill_cool_down=0.5
    ground_skill=False
    buff_time=0
    combo_delay = 0.5

class Skill_A(BaseSkill):
    _display_name = '如意扇'
    _distance = 0
    key=Key.SKILL_A
    delay=0.48
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.48

class Skill_Q(BaseSkill):
    _display_name = '芭蕉風'
    _distance = 0
    key=Key.SKILL_Q
    delay=0.45
    rep_interval=0.2
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.45
    float_in_air = True

class Skill_QQ(BaseSkill):
    _display_name = '地板芭蕉風'
    _distance = 0
    key=Key.SKILL_Q
    delay=0.45
    rep_interval=0.2
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.45
    float_in_air = True

class Skill_W(BaseSkill):
    _display_name = '金箍棒'
    _distance = 0
    key=Key.SKILL_W
    delay=0.6
    rep_interval=0.5
    skill_cool_down=11.8
    ground_skill=False
    buff_time=0
    combo_delay = 0.6
    skill_image = IMAGE_DIR + 'skill_w.png'

class Skill_E(BaseSkill):
    _display_name = '滅火炎'
    _distance = 0
    key=Key.SKILL_E
    delay=0.6
    rep_interval=0.15
    skill_cool_down=8.7
    ground_skill=False
    buff_time=0
    combo_delay = 0.35
    float_in_air = True
    skill_image = IMAGE_DIR + 'skill_e.png'

class Skill_C(BaseSkill):
    _display_name = '地震碎'
    _distance = 0
    key=Key.SKILL_C
    delay=0.62
    rep_interval=0.2
    skill_cool_down=6
    ground_skill=True
    buff_time=0
    combo_delay = 0.48

class Skill_S(BaseSkill):
    _display_name = '土波流'
    _distance = 0
    key=Key.SKILL_S
    delay=0.7
    rep_interval=0.2
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.5

class Skill_D(BaseSkill):
    _display_name = '吸星渦流'
    _distance = 0
    key=Key.SKILL_D
    delay=0.65
    rep_interval=0.3
    skill_cool_down=3
    ground_skill=True
    buff_time=44
    combo_delay = 0.65

    def main(self):
        if utils.get_is_in_skill_buff('skill_d'):
            self.rep = 2
        return super().main()

class Skill_F(BaseSkill):
    _display_name = '追擊鬼火符'
    _distance = 0
    key=Key.SKILL_F
    delay=0.5
    rep_interval=0.5
    skill_cool_down=3
    ground_skill=False
    buff_time=44
    combo_delay = 0.5

class Skill_3(BaseSkill):
    _display_name = '山靈召喚'
    _distance = 0
    key=Key.SKILL_3
    delay=0.6
    rep_interval=0.5
    skill_cool_down=200
    ground_skill=True
    buff_time=60
    combo_delay = 0.6

class Buff_1(BaseSkill):
    _display_name = '靈藥太乙仙丹'
    _distance = 0
    key=Key.BUFF_1
    delay=0.55
    rep_interval=0.5
    skill_cool_down=100
    ground_skill=False
    buff_time=10
    combo_delay = 0.55

class Buff_5(BaseSkill):
    _display_name = '幻影分身符'
    _distance = 0
    key=Key.BUFF_5
    delay=0.65
    rep_interval=0.5
    skill_cool_down=3
    ground_skill=False
    buff_time=180
    combo_delay = 0.65

class Buff_6(BaseSkill):
    _display_name = '蝴蝶之夢'
    _distance = 0
    key=Key.BUFF_6
    delay=0.4
    rep_interval=0.5
    skill_cool_down=3
    ground_skill=False
    buff_time=100
    combo_delay = 0.4

class Buff_F1(BaseSkill):
    _display_name = '天地人幻影'
    _distance = 0
    key=Key.BUFF_F1
    delay=0.4
    rep_interval=0.5
    skill_cool_down=100
    ground_skill=False
    buff_time=30
    combo_delay = 0.4

class Buff_F2(BaseSkill):
    _display_name = '極大分身亂舞'
    _distance = 0
    key=Key.BUFF_F2
    delay=0.65
    rep_interval=0.5
    skill_cool_down=200
    ground_skill=False
    buff_time=30
    combo_delay = 0.65

class Buff_F3(BaseSkill):
    _display_name = '降臨怪力亂神'
    _distance = 0
    key=Key.BUFF_F3
    delay=0.6
    rep_interval=0.6
    skill_cool_down=200
    ground_skill=True
    buff_time=30
    combo_delay = 0.6

class Gate(BaseSkill):
    _display_name = '歪曲縮地符'
    _distance = 0
    key=Key.SET_GATE
    delay=0.55
    rep_interval=0.5
    skill_cool_down=5
    ground_skill=True
    buff_time=100
    combo_delay = 0.55

    def main(self):
        self.active_if_skill_ready = 'returntogate'
        if super().main():
            ReturnToGate.set_my_last_cooldown(time.time())
            return True
        else:
            return False

class ReturnToGate(BaseSkill):
    _display_name = '回歸歪曲縮地符'
    _distance = 0
    key=Key.GATE
    delay=0.1
    rep_interval=0.5
    skill_cool_down=5
    ground_skill=True
    buff_time=5
    combo_delay = 0.1

    def main(self):
        self.active_if_in_skill_buff = 'gate'
        self.active_if_skill_ready = 'gate'
        return super().main()

class Skill_4(BaseSkill):
    _display_name ='噴泉'
    key=Key.SKILL_4
    delay=0.8
    rep_interval=0.25
    skill_cool_down=60
    ground_skill=True
    buff_time=60
    combo_delay = 0.3

class Skill_2(BaseSkill):
    _display_name ='蜘蛛之鏡'
    key=Key.SKILL_2
    delay=0.6
    rep_interval=0.25
    skill_cool_down=250
    ground_skill=False
    buff_time=0
    combo_delay = 0.6

class Buff_F5(BaseSkill):
    _display_name ='必死決心'
    key=Key.BUFF_F5
    delay=0.7
    rep_interval=0.25
    skill_cool_down=85
    ground_skill=True
    buff_time=30
    combo_delay = 0.7

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
#         SkillCombination(direction='',target_skills='skill_as').execute()
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
