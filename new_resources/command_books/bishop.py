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
    TELEPORT = 'd' # 瞬移
    UPJUMP = 'alt' # 上跳
    # Buffs
    INFINITY = '9' # Infinity
    INFINITY2 = '0' # Infinity 2
    
    # FMAs / semi FMAs
    SKILL_Q = 'q' # Genesis
    SKILL_F2 = 'f2'
    SKILL_W = 'w' # Peacemaker

    # Attack Skills
    SKILL_BB = 'shift' # Big bang
    SKILL_E = 'e' # Triumph Feather
    SKILL_R = 'r' # Blood of the Divine
    SKILL_A = 'a' # Angel Ray

    # Summons
    SKILL_FOUNTAIN = '1'
    SKILL_ERDA_FOUNTAIN = '7'
    SKILL_BAHAMUT = '8'
    SKILL_ADVANCED_BLESSING = '='
    SKILL_DECENT_SHARP_EYES = '-'
    
    SKILL_R = 'r' # 持續制裁者
    SKILL_S = 's'# 末日烈焰
    SKILL_BB = 'shift' # 火焰之襲
    SKILL_D = 'd' # 藍焰斬
    SKILL_1 = '1' # 劇毒領域
    SKILL_F3 = 'f3' # 火炎神之怒號
    SKILL_E = 'e' # 火流星
    SKILL_F = 'f' # 劇毒新星
    SKILL_F1 = 'f1' # 魔力無限
    SKILL_F2 = 'f2' # 波動記憶
    SKILL_2 = '2' # 蜘蛛之鏡
    SKILL_3 = '3' # 劇毒連鎖

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
    # if not check_current_tag('alpha'):
    #     utils.wait_for_is_standing(1000)
    #     Skill_BB().execute()
    if config.player_states['is_stuck'] and abs(d_x) >= 17:
        print("is stuck")
        time.sleep(utils.rand_float(0.2, 0.3))
        press(jump,up_time=0.4)
        WaitStanding(duration='1').execute()
        # if d_x <= 0:
        #     Fall(direction='left',duration='0.3')
        # else:
        #     Fall(direction='right',duration='0.3')
        config.player_states['is_stuck'] = False
    if direction == 'left' or direction == 'right':
        if abs(d_x) >= 16:
            TeleportCombination(combo_skill='skill_bb',direction=direction,combo2='true').execute()
        elif abs(d_x) > 10:
            time.sleep(utils.rand_float(0.25, 0.35))
        else:
            time.sleep(utils.rand_float(0.01, 0.015))
        utils.wait_for_is_standing(200)
        # d_x = target[0] - config.player_pos[0]
        # if abs(d_x) >= settings.move_tolerance and config.player_states['in_bottom_platform'] == False and len(settings.platforms) > 0:
        #     print('back to ground')
        #     key_up(direction)
        #     time.sleep(utils.rand_float(0.3, 0.4))
        #     Fall(duration='0.2').execute()
        #     Teleport(direction='down').execute()
        #     Skill_BB(combo='True').execute()
    
    if direction == 'up':
        
        if abs(d_x) <= settings.move_tolerance and not config.player_states['is_keydown_skill']:
            time.sleep(utils.rand_float(0.2, 0.25))
            key_up('left')
            key_up('right')
            if abs(d_y) > 3 :
                if abs(d_y) >= 35:
                    UpJump().execute()
                    TeleportCombination(combo_skill='skill_bb',direction=direction,combo2='true').execute()
                elif abs(d_y) >= 20:
                    TeleportCombination(combo_skill='skill_bb',direction=direction,combo2='true').execute()
                else:
                    TeleportCombination(combo_skill='skill_bb',direction=direction,combo2='true').execute()
                utils.wait_for_is_standing(300)
            else:
                press(jump, 1)
                time.sleep(utils.rand_float(0.1, 0.15))
    if direction == 'down':
        if abs(d_x) <= settings.move_tolerance:
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
                print("down stair")
                if abs(d_y) >= 20 :
                    time.sleep(utils.rand_float(0.2, 0.3))
                    Fall(duration='0.3').execute()
                if abs(d_y) > 10 and utils.bernoulli(0.8):
                    TeleportCombination(combo_skill='skill_bb',direction=direction,combo2='true').execute()
                else:
                    time.sleep(utils.rand_float(0.2, 0.3))
                    Fall(duration='0.2').execute()
        time.sleep(utils.rand_float(0.05, 0.08))
        utils.wait_for_is_standing(800)

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
    def __init__(self):
        super().__init__(locals())

    def main(self):
        Buff_Rotation_1(pre_delay=0.7).execute()
        Buff_Rotation_2(pre_delay=0.7).execute()
        Skill_Advanced_Blessing(pre_delay=0.7).execute()
        Skill_Decent_Sharp_Eyes(pre_delay=0.7).execute()
        

class Teleport(BaseSkill):
    _display_name ='瞬移'
    _distance = 27
    key=Key.TELEPORT
    delay=0.53
    rep_interval=0.3
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.16

class UpJump(Command):
    """Performs a up jump in the given direction."""
    _display_name = '上跳'

    def __init__(self, direction="", jump='False',combo="false"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        self.player_jump(self.direction)
        time.sleep(utils.rand_float(0.03, 0.06)) 
        press(Key.UPJUMP, 1,up_time=0.05)
        key_up(self.direction)
        if self.combo:
            time.sleep(utils.rand_float(0.05, 0.1))
        else:
            time.sleep(utils.rand_float(0.4, 0.6))

class Skill_BB(BaseSkill):
    _display_name ='Big Bang'
    key=Key.SKILL_BB
    delay=0.4
    rep_interval=0.2
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

class Skill_Infinity(BaseSkill):
    _display_name ='Infinity'
    key=Key.INFINITY
    delay=0.45
    rep_interval=0.5
    skill_cool_down=90
    ground_skill=False
    buff_time=90
    combo_delay = 0.5

class Skill_Infinity2(BaseSkill):
    _display_name ='Infinity2'
    key=Key.INFINITY2
    delay=0.45
    rep_interval=0.5
    skill_cool_down=90
    ground_skill=False
    buff_time=90
    combo_delay = 0.5

class Buff_Rotation_1(BaseSkill):
    _display_name ='Buff First Rotation'
    key=Key.INFINITY
    delay=0.45
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=False
    buff_time=90
    combo_delay = 0.5

    def main(self):
        self.active_if_not_in_skill_buff = 'buff_rotation_2' # only affects main super().main()
        self.active_if_skill_ready = 'skill_infinity' # only affects main super().main()
        # if not utils.get_is_in_skill_buff('buff_rotation_2') and utils.get_if_skill_ready('skill_storm_of_arrows'):
        if super().main():
            return True
        return False

class Buff_Rotation_2(BaseSkill):
    _display_name ='Buff Second Rotation'
    key=Key.INFINITY2
    delay=0.45
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=False
    buff_time=90
    combo_delay = 0.5

    def main(self):
        self.active_if_not_in_skill_buff = 'buff_rotation_1' # only affects main super().main()
        self.active_if_skill_ready = 'skill_infinity2' # only affects main super().main()
        # if not utils.get_is_in_skill_buff('buff_rotation_1') and utils.get_if_skill_ready('skill_quiver_barrage'):
        if super().main():
            return True
        return False

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

class Skill_Q(BaseSkill):
    _display_name ='Genesis'
    key=Key.SKILL_Q
    delay=0.65
    rep_interval=0.2
    skill_cool_down=30
    ground_skill=True
    buff_time=0
    combo_delay = 0.5

class Skill_W(BaseSkill):
    _display_name ='Peacemaker'
    key=Key.SKILL_W
    delay=0.8
    rep_interval=0.2
    skill_cool_down=10
    ground_skill=True
    combo_delay = 0.28

class Skill_E(BaseSkill):
    _display_name ='Triumph Feather'
    key=Key.SKILL_E
    delay=0.7
    rep_interval=0.2
    skill_cool_down=25
    ground_skill=True
    combo_delay = 0.28

class Skill_R(BaseSkill):
    _display_name ='Blood of the Divine'
    key=Key.SKILL_R
    delay=0.6
    rep_interval=0.2
    skill_cool_down=25
    ground_skill=True
    buff_time=0
    combo_delay = 0.3

class Skill_A(BaseSkill):
    _display_name ='Angel Ray'
    key=Key.SKILL_A
    delay=0.6
    rep_interval=0.2
    skill_cool_down=25
    ground_skill=True
    buff_time=0
    combo_delay = 0.3
    # skill_image = IMAGE_DIR + 'skill_q.png'

class Skill_Erda_Fountain(BaseSkill):
    _display_name = 'Erda Fountain'
    _distance = 0
    key=Key.SKILL_ERDA_FOUNTAIN
    delay=0.9
    rep_interval=0.5
    skill_cool_down=57
    ground_skill=True
    buff_time=60
    combo_delay = 0.9

class Skill_Fountain(BaseSkill):
    _display_name = 'Fountain'
    _distance = 0
    key=Key.SKILL_FOUNTAIN
    delay=0.9
    rep_interval=0.5
    skill_cool_down=55
    ground_skill=True
    buff_time=60
    combo_delay = 0.9

class Skill_Advanced_Blessing(BaseSkill):
    _display_name = 'Advanced Blessing'
    _distance = 0
    key=Key.SKILL_ADVANCED_BLESSING
    delay=0.9
    rep_interval=0.5
    skill_cool_down=55
    ground_skill=True
    buff_time=300
    combo_delay = 0.9

class Skill_Decent_Sharp_Eyes(BaseSkill):
    _display_name = 'Decent Sharp Eyes'
    _distance = 0
    key=Key.SKILL_DECENT_SHARP_EYES
    delay=0.9
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=True
    buff_time=195
    combo_delay = 0.9

## NOT USED  ##
class Skill_3(BaseSkill):
    _display_name ='劇毒連鎖'
    key=Key.SKILL_3
    delay=0.6
    rep_interval=0.2
    skill_cool_down=25
    ground_skill=True
    combo_delay = 0.3
    # skill_image = IMAGE_DIR + 'skill_w.png'

class Skill_1(BaseSkill):
    _display_name ='劇毒領域'
    key=Key.SKILL_1
    delay=0.5
    rep_interval=0.2
    skill_cool_down=30
    ground_skill=True
    buff_time=55
    combo_delay = 0.35
    # skill_image = IMAGE_DIR + 'skill_1.png'

class Skill_F3(BaseSkill):
    _display_name ='火炎神之怒號'
    key=Key.SKILL_F3
    delay=0.55
    rep_interval=0.2
    skill_cool_down=75
    ground_skill=True
    buff_time=3
    combo_delay = 0.4
    # skill_image = IMAGE_DIR + 'skill_3.png'

class Skill_F1(BaseSkill):
    _display_name ='魔力無限'
    key=Key.SKILL_F1
    delay=0.5
    rep_interval=0.2
    skill_cool_down=180
    ground_skill=True
    buff_time=80
    combo_delay = 0.2

class Skill_F2(BaseSkill):
    _display_name ='魔力無限2'
    key=Key.SKILL_F2
    delay=0.8
    rep_interval=0.2
    skill_cool_down=180
    ground_skill=True
    buff_time=78
    combo_delay = 0.6

class Skill_2(BaseSkill):
    _display_name ='蜘蛛之鏡'
    key=Key.SKILL_2
    delay=0.8
    rep_interval=0.25
    skill_cool_down=240
    ground_skill=False
    buff_time=0
    combo_delay = 0.45

class Sp_F12(BaseSkill):
    _display_name ='輪迴'
    key=Key.SP_F12
    delay=0.5
    rep_interval=0.2
    skill_cool_down=60
    ground_skill=True
    buff_time=600
    combo_delay = 0.3

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
        # Skill_S().execute()
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
                move((width-35),bottom_y).execute()
                # Teleport(direction='down').execute()
                if config.player_pos[1] >= bottom_y:
                    print('new bottom')
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                print("current bottom : ", settings.platforms)
                print("current player : ", str(config.player_pos[1]))
                time.sleep(0.2)
                TeleportCombination(direction='right',combo_skill='skill_r|skill_3|skill_f3|skill_s',combo_direction='left').execute()
                TeleportCombination(direction='left',combo_skill='skill_2|skill_s',combo2='false').execute()
                UpJump(combo='true',direction='left').execute()
                TeleportCombination(direction='up',combo_skill='skill_bb').execute()
            else:
                # left side
                move(35,bottom_y).execute()
                # Teleport(direction='down').execute()
                if config.player_pos[1] >= bottom_y:
                    print('new bottom')
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                print("current bottom : ", settings.platforms)
                time.sleep(0.2)
                TeleportCombination(direction='left',combo_skill='skill_r|skill_3|skill_f3|skill_s',combo_direction='right').execute()
                TeleportCombination(direction='right',combo_skill='skill_2|skill_s',combo2='false').execute()
                UpJump(combo='true',direction='right').execute()
                TeleportCombination(direction='up',combo_skill='skill_s').execute()
            
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                continue
            move(width//2,bottom_y).execute()
            # time.sleep(0.5)
            SkillCombination(target_skills='skill_1|skill_d|skill_f|skill_s').execute()
            # TeleportCombination(direction='up',combo_skill='skill_bb',jump='true').execute()
            toggle = not toggle
            

        if settings.home_scroll_key:
            config.map_changing = True
            press(settings.home_scroll_key)
            time.sleep(5)
            config.map_changing = False
        return
