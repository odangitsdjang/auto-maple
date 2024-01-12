from src.common import config, settings, utils
import time
import cv2
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, GoToMap, ChangeChannel, WaitStanding
from src.common.vkeys import press, key_down, key_up

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/ice_lightning/'

# List of key mappings
class Key:
    WORLD_MAP = 'pageup'
    
    # Movement
    TELEPORT = '`' # 瞬移
    UPJUMP = 'shift' # 上跳
    # Buffs
    BUFF_5 = '5' # 鬼夜叉:大鬼封魂陣
    BUFF_6 = '6' # 影朋花狐2
    BUFF_7 = '7' # 曉之陣:集結
    # Buffs Toggle

    # Attack Skills
    SKILL_Q = 'q' # 鬼夜叉老大
    SKILL_S = 's'# 紫光白狐
    SKILL_A = 'a' # 陰陽除靈符
    SKILL_D = 'd' # 妖繪釋放
    SKILL_1 = '1' # 紫扇仰波
    SKILL_W = 'w' # 鬼神召喚
    SKILL_E = 'e' # 雪女召喚
    SKILL_R = 'r' # 靈石召喚
    SKILL_Z = 'z' # 恢復靈力
    SKILL_T = 't' # 幽暗
    SKILL_2 = '2' # 雙天狗
    SKILL_3 = '3' # 破邪連擊符
    SKILL_4 = '4' # 一鬼踐踏

    # special Skills
    SP_F12 = 'f12' # 輪迴

def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]

    # if not check_current_tag('alpha'):
    #     utils.wait_for_is_standing(1000)
    #     Skill_A().execute()
    if config.player_states['is_stuck'] and abs(d_x) >= 17:
        print("is stuck")
        time.sleep(utils.rand_float(0.2, 0.3))
        Skill_1(direction=direction,jump='true',combo='true').execute()
        # if d_x <= 0:
        #     Fall(direction='left',duration='0.3')
        # else:
        #     Fall(direction='right',duration='0.3')
        config.player_states['is_stuck'] = False
    if direction == 'left' or direction == 'right':
        if not config.player_states['is_keydown_skill']:
            if abs(d_x) >= 23:
                Skill_1x3(jump='true',combo='true').execute()
            if abs(d_x) >= 17:
                Teleport(direction=direction,combo='true').execute()
            elif abs(d_x) > 10:
                Skill_1x3(jump='true',combo='true').execute()
                WaitStanding(duration='0.8').execute()
            else:
                time.sleep(utils.rand_float(0.03, 0.05))
        else:
            time.sleep(utils.rand_float(0.07, 0.09))
        # utils.wait_for_is_standing(200)
        # d_x = target[0] - config.player_pos[0]
        # if abs(d_x) >= settings.move_tolerance and config.player_states['in_bottom_platform'] == False and len(settings.platforms) > 0:
        #     print('back to ground')
        #     key_up(direction)
        #     time.sleep(utils.rand_float(0.3, 0.4))
        #     Fall(duration='0.2').execute()
        #     Teleport(direction='down').execute()
        #     Skill_A(combo='True').execute()
    
    if direction == 'up':
        if abs(d_x) <= settings.move_tolerance and not config.player_states['is_keydown_skill']:
            key_up('left')
            key_up('right')
            time.sleep(utils.rand_float(0.2, 0.25))
            if abs(d_y) > 3 :
                if abs(d_y) >= 40:
                    UpJump().execute()
                    Teleport(direction=direction,combo='true').execute()
                elif abs(d_y) >= 25:
                    Teleport(direction=direction,jump='true',combo='true').execute()
                else:
                    Teleport(direction=direction,combo='true').execute()
                Skill_1(combo='false').execute()
            else:
                Skill_1(jump='true',combo='false').execute()
            WaitStanding('1').execute()
    if direction == 'down':
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
            print("down stair")
            if not config.player_states['is_keydown_skill']:
                if abs(d_y) >= 27 :
                    time.sleep(utils.rand_float(0.2, 0.3))
                    Fall(duration='0.1').execute()
                if abs(d_y) > 10:
                    time.sleep(utils.rand_float(0.2, 0.3))
                    Teleport(direction=direction,combo='false').execute()
                    # Skill_1(combo='false').execute()
                else:
                    time.sleep(utils.rand_float(0.2, 0.3))
                    Fall(duration='0.2').execute()
                Skill_1(combo='false').execute()
            else:
                time.sleep(utils.rand_float(0.05, 0.08))
                Fall(duration='0.2').execute()
        time.sleep(utils.rand_float(0.05, 0.08))
        WaitStanding('1').execute()

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
                threshold = settings.adjust_tolerance
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left',down_time=0.02)
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            walk_counter += 1
                            time.sleep(0.01)
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right',down_time=0.02)
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            walk_counter += 1
                            time.sleep(0.01)
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance:
                    if d_y < 0:
                        Teleport(direction='up').execute()
                    else:
                        Fall(duration=0.2).execute()
                        time.sleep(utils.rand_float(0.05, 0.1))
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
            # time.sleep(utils.rand_float(0.1, 0.2))
            # Skill_D().execute()
            self.cd120_buff_time = now
        if self.cd150_buff_time == 0 or now - self.cd150_buff_time > 151:
            self.cd150_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 181:
            # time.sleep(utils.rand_float(0.3, 0.4))
            # press(Key.SKILL_F1, 1,up_time=0.2)
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
            time.sleep(utils.rand_float(0.1, 0.2))
            Buff_6().execute()
            # press(Key.BUFF_5, 1,up_time=0.3)
            self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
            # time.sleep(utils.rand_float(0.1, 0.3))
            # press(Key.BUFF_5, 1)
            self.cd900_buff_time = now
        # if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
        #     for key in buffs:
        #       press(key, 3, up_time=0.3)
        #       self.decent_buff_time = now	

class Teleport(BaseSkill):
    _display_name ='瞬移'
    _distance = 27
    key=Key.TELEPORT
    delay=0.53
    rep_interval=0.3
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.12

class UpJump(Command):
    """Performs a up jump in the given direction."""
    _display_name = '上跳'
    skill_cool_down = 6

    def __init__(self, direction="", jump='False',combo="false"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if not self.check_is_skill_ready():
            return
        self.player_jump(self.direction)
        time.sleep(utils.rand_float(0.03, 0.06)) 
        press(Key.UPJUMP, 1,up_time=0.05)
        key_up(self.direction)
        if self.combo:
            time.sleep(utils.rand_float(0.05, 0.1))
        else:
            time.sleep(utils.rand_float(0.4, 0.6))

class Skill_A(BaseSkill):
    _display_name ='陰陽除靈符'
    key=Key.SKILL_A
    delay=0.85
    rep_interval=0.15
    skill_cool_down=3
    ground_skill=False
    buff_time=0
    combo_delay = 0.4
    
class TeleportCombination(Command):
    """teleport with other skill."""
    _display_name = '瞬移組合'

    def __init__(self, direction="left",combo_skill='',combo_direction='', jump='False',combo2="true"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo_skill = combo_skill.lower()
        self.combo2 = combo2
        self.combo_direction = settings.validate_arrows(combo_direction)

    def main(self):
        Teleport(direction=self.direction,combo="true",jump=str(self.jump)).execute()
        skills_array = self.combo_skill.split("|")
        for skill in skills_array:
            skill = skill.lower()
            s = config.bot.command_book[skill]
            if not s.get_is_skill_ready():
                continue
            else:
                print(skill)
                s(direction=self.combo_direction,combo=self.combo2).execute()
                break

class Skill_S(BaseSkill):
    _display_name ='紫光白狐'
    key=Key.SKILL_S
    delay=1.5
    rep_interval=0.2
    skill_cool_down=180
    ground_skill=True
    buff_time=0
    combo_delay = 0.3

class Skill_D(BaseSkill):
    _display_name ='妖繪釋放'
    key=Key.SKILL_D
    delay=1
    rep_interval=0.2
    skill_cool_down=90
    ground_skill=False
    buff_time=0
    combo_delay = 0.7

    def main(self):
        self.duration = 2
        return super().main()

class Skill_Q(BaseSkill):
    _display_name ='鬼夜叉老大'
    key=Key.SKILL_Q
    delay=0.4
    rep_interval=0.2
    skill_cool_down=3
    ground_skill=True
    buff_time=34
    combo_delay = 0.25

class Skill_W(BaseSkill):
    _display_name ='鬼神召喚'
    key=Key.SKILL_W
    delay=0.3
    rep_interval=0.2
    skill_cool_down=58
    ground_skill=True
    buff_time=30
    combo_delay = 0.2

class Skill_E(BaseSkill):
    _display_name ='雪女召喚'
    key=Key.SKILL_E
    delay=0.3
    rep_interval=0.2
    skill_cool_down=73
    ground_skill=True
    buff_time=50
    combo_delay = 0.2

class Skill_1(BaseSkill):
    _display_name ='紫扇仰波'
    key=Key.SKILL_1
    delay=0.5
    rep_interval=0.12
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.22

class Skill_1x3(BaseSkill):
    _display_name ='紫扇仰波'
    key=Key.SKILL_1
    delay=0.1
    rep_interval=0.001
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.05
    fast_rep=True

    def main(self):
        self.rep = 3
        return super().main()

class Skill_T(BaseSkill):
    _display_name ='幽暗'
    key=Key.SKILL_T
    delay=0.8
    rep_interval=0.12
    skill_cool_down=3
    ground_skill=False
    buff_time=0
    combo_delay = 0.05

class Skill_Z(BaseSkill):
    _display_name ='恢復靈力'
    key=Key.SKILL_Z
    delay=0.15
    rep_interval=0.12
    skill_cool_down=14
    ground_skill=False
    buff_time=0
    combo_delay = 0.15

class Skill_2(BaseSkill):
    _display_name ='雙天狗'
    key=Key.SKILL_2
    delay=0.1
    rep_interval=0.1
    skill_cool_down=1
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

class Skill_3(BaseSkill):
    _display_name ='破邪連擊符'
    key=Key.SKILL_3
    delay=0.5
    rep_interval=0.1
    skill_cool_down=60
    ground_skill=True
    buff_time=0
    combo_delay = 0.1

class Buff_5(BaseSkill):
    _display_name ='鬼夜叉:大鬼封魂陣'
    key=Key.BUFF_5
    delay=0.2
    rep_interval=0.1
    skill_cool_down=235
    ground_skill=True
    buff_time=60
    combo_delay = 0.2

class Buff_6(BaseSkill):
    _display_name ='影朋花狐2'
    key=Key.BUFF_6
    delay=0.5
    rep_interval=0.1
    skill_cool_down=3
    ground_skill=True
    buff_time=500
    combo_delay = 0.2

class Buff_7(BaseSkill):
    _display_name ='曉之陣:集結'
    key=Key.BUFF_7
    delay=0.5
    rep_interval=0.1
    skill_cool_down=115
    ground_skill=True
    buff_time=45
    combo_delay = 0.2

class skill_4(BaseSkill):
    _display_name ='一鬼踐踏'
    key=Key.SKILL_4
    delay=2.2
    rep_interval=0.1
    skill_cool_down=120
    ground_skill=True
    buff_time=0
    combo_delay = 0.3

class Skill_R(BaseSkill):
    _display_name ='靈石召喚'
    key=Key.SKILL_R
    delay=0.4
    rep_interval=0.1
    skill_cool_down=188
    ground_skill=True
    buff_time=74
    combo_delay = 0.25
    
class Sp_F12(BaseSkill):
    _display_name ='輪迴'
    key=Key.SP_F12
    delay=0.5
    rep_interval=0.2
    skill_cool_down=60
    ground_skill=True
    buff_time=600
    combo_delay = 0.2

    def main(self):
        time.sleep(0.4)
        return super().main()

class AutoHunting(Command):
    _display_name ='自動走位狩獵'

    def __init__(self,duration='180',map=''):
        super().__init__(locals())
        self.duration = float(duration)
        self.map = map

    def main(self):
        daily_complete_template = cv2.imread('assets/daily_complete.png', 0)
        start_time = time.time()
        toggle = True
        move = config.bot.command_book['move']
        GoToMap(target_map=self.map).execute()
        Skill_D().execute()
        minimap = config.capture.minimap['minimap']
        height, width, _n = minimap.shape
        bottom_y = height - 30
        # bottom_y = config.player_pos[1]
        settings.platforms = 'b' + str(int(bottom_y))
        while True:
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                continue
            Sp_F12().execute()
            frame = config.capture.frame
            point = utils.single_match_with_threshold(frame,daily_complete_template,0.9)
            if len(point) > 0:
                print("one daily end")
                break
            minimap = config.capture.minimap['minimap']
            height, width, _n = minimap.shape
            if time.time() - start_time >= self.duration:
                break
            if not config.enabled:
                break
            
            if toggle:
                # right side
                move((width-30),bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    print('new bottom')
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                print("current bottom : ", settings.platforms)
                print("current player : ", str(config.player_pos[1]))
                SkillCombination(direction='right',target_skills='skill_e|skill_s|buff_7|buff_5|skill_t|skill_a',combo='true',jump='true').execute()
                Skill_2().execute()
                Teleport(direction='left').execute()
                UpJump(combo='true',direction='left').execute()
                SkillCombination(direction='left',target_skills='skill_e|skill_s|buff_7|buff_5|skill_t|skill_a',combo='true',jump='true').execute()
                Skill_2().execute()
            else:
                # left side
                move(30,bottom_y).execute()
                Teleport(direction='down').execute()
                if config.player_pos[1] >= bottom_y:
                    print('new bottom')
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                print("current bottom : ", settings.platforms)
                SkillCombination(direction='left',target_skills='skill_e|skill_s|buff_7|buff_5|skill_t|skill_a',combo='true',jump='true').execute()
                Skill_2().execute()
                Teleport(direction='right').execute()
                UpJump(combo='true',direction='right').execute()
                SkillCombination(direction='right',target_skills='skill_e|skill_s|buff_7|buff_5|skill_t|skill_a',combo='true',jump='true').execute()
                Skill_2().execute()
            
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                continue
            move(width//2,bottom_y).execute()
            time.sleep(0.4)
            SkillCombination(direction='',target_skills='skill_r|skill_w|skill_q|skill_4',combo='true').execute()
            Skill_2().execute()
            toggle = not toggle
            

        if settings.home_scroll_key:
            config.map_changing = True
            press(settings.home_scroll_key)
            time.sleep(5)
            config.map_changing = False
        return
