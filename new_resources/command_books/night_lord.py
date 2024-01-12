from src.common import config, settings, utils
import time
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, GoToMap, ChangeChannel, Frenzy, WaitStanding, WealthPotion
from src.common.vkeys import press, key_down, key_up
import cv2

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/night_lord/'

# List of key mappings
class Key:
    WORLD_MAP = 'pageup'
    
    # Movement
    FLASH_JUMP = 'v'
    ROPE = '`'
    UP_JUMP = 'c'
    DASH = 'x' # 暗影衝刺

    # Buffs
    BUFF_F1 = 'f1' # 出血毒素
    BUFF_F2 = 'f2' # 楓之谷世界女神的祝福
    BUFF_F3 = 'f3' # 飛閃起爆符
    BUFF_5 = '5' # 終極隱身術
    BUFF_F5 = 'f5' # 必死決心
    BUFF_3 = '3' # 無雙之力

    # Buffs Toggle

    # Attack Skills
    SKILL_A = 'a' # 挑釁契約
    SKILL_1 = '1' # 達克魯的秘傳
    SKILL_D = 'd' # 絕殺領域
    SKILL_S = 's'# 風魔手裏劍
    SKILL_W = 'w' # 穢土轉生
    SKILL_E = 'e' # 四星鏢雨
    SKILL_F = 'f' # 
    SKILL_2 = '2' # 蜘蛛之鏡
    SKILL_4 = 'down+4' # 噴泉

    # special Skills
    SP_F12 = 'f12' # 輪迴
    DARK_EMBRACE = 'shift'

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
        utils.wait_for_is_standing(2000)
        d_y = target[1] - config.player_pos[1]
        d_x = target[0] - config.player_pos[0]
        
        if abs(d_x) >= 16:
            if abs(d_x) >= 60:
                FlashJump(direction='',triple_jump='true',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
            elif abs(d_x) >= 28:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
            else:
                if d_y == 0 and Dash().execute():
                    pass
                else:
                    Skill_A(direction='',jump='true').execute()
            time.sleep(utils.rand_float(0.03, 0.05))
            if abs(d_x) <= 22:
                key_up(direction)
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
                SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
            utils.wait_for_is_standing(2500)
        else:
            time.sleep(utils.rand_float(0.1, 0.15))
            utils.wait_for_is_standing(2500)
    
    if direction == 'up':
        if abs(d_x) > settings.move_tolerance:
            return
        utils.wait_for_is_standing(1500)
        if abs(d_y) > 6 :
            if abs(d_y) < 15:
                UpJump(pre_delay='0.1').execute()
            elif abs(d_y) <= 18:
                UpJump(pre_delay='0.1',jump='true').execute()
            else:
                Rope(jump='true').execute()
            SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
            time.sleep(utils.rand_float(0.2, 0.3))
            WaitStanding(duration='3300').execute()
        else:
            press(config.bot.config['Jump'], 1)
            time.sleep(utils.rand_float(0.1, 0.15))

    if direction == 'down':
        if abs(d_x) > settings.move_tolerance:
            return
        down_duration = 0.2
        if abs(d_y) > 20:
            down_duration = 0.5
        elif abs(d_y) > 13:
            down_duration = 0.3
        
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
            print("down stair")
            if abs(d_x) >= 15:
                if d_x > 0:
                    Fall(direction='right',duration=down_duration).execute()
                else:
                    Fall(direction='left',duration=down_duration).execute()
                
            else:
                Fall(direction='',duration=(down_duration+0.1)).execute()
                if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING:
                    print("leave lader")
                    if d_x > 0:
                        key_down('left')
                        press(config.bot.config['Jump'])
                        key_up('left')
                    else:
                        key_down('right')
                        press(config.bot.config['Jump'])
                        key_up('right')
            SkillCombination(direction='',jump='false',target_skills='skill_a').execute()
                
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
        utils.wait_for_is_standing(1000)
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 121:
            self.cd120_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd150_buff_time > 151:
            self.cd150_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 181:
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
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

class UpJump(BaseSkill):
    """Performs a up jump in the given direction."""
    _display_name = '上跳'
    _distance = 27
    key=Key.UP_JUMP
    delay=0.45
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.45

    # def __init__(self,jump='false', direction='',combo='true'):
    #     super().__init__(locals())
    #     self.direction = settings.validate_arrows(direction)

    # def main(self):
    #     utils.wait_for_is_standing(500)
    #     press(Key.UP_JUMP, 1)
    #     key_down(self.direction)
    #     time.sleep(utils.rand_float(0.35, 0.4))
    #     if 'left' in self.direction or 'right' in self.direction:
    #         press(config.bot.config['Jump'], 1)
    #     key_up(self.direction)
        
class Rope(BaseSkill):
    """Performs a up jump in the given direction."""
    _display_name = '連接繩索'
    _distance = 27
    key=Key.ROPE
    delay=1.4
    rep_interval=0.5
    skill_cool_down=3
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class Dash(BaseSkill):
    """Performs a dash in the given direction."""
    _display_name = '暗影衝刺'
    _distance = 10
    key=Key.DASH
    delay=0.25
    rep_interval=0.5
    skill_cool_down=5
    ground_skill=False
    buff_time=0
    combo_delay = 0.25

class Skill_A(BaseSkill):
    _display_name = '挑釁契約'
    _distance = 27
    key=Key.SKILL_A
    delay=0.52
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class Skill_1(BaseSkill):
    _display_name = '達克魯的秘傳'
    _distance = 27
    key=Key.SKILL_1
    delay=0.55
    rep_interval=0.5
    skill_cool_down=57
    ground_skill=True
    buff_time=12
    combo_delay = 0.5

class Skill_D(BaseSkill):
    _display_name = '絕殺領域'
    _distance = 27
    key=Key.SKILL_D
    delay=0.55
    rep_interval=0.5
    skill_cool_down=57
    ground_skill=True
    buff_time=60
    combo_delay = 0.5

class Skill_S(BaseSkill):
    _display_name = '風魔手裏劍'
    _distance = 50
    key=Key.SKILL_S
    delay=0.58
    rep_interval=0.5
    skill_cool_down=24
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class Skill_W(BaseSkill):
    _display_name = '穢土轉生'
    _distance = 50
    key=Key.SKILL_W
    delay=0.65
    rep_interval=0.5
    skill_cool_down=29
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class Skill_E(BaseSkill):
    _display_name = '四星鏢雨'
    _distance = 50
    key=Key.SKILL_E
    delay=0.94
    rep_interval=0.5
    skill_cool_down=14
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class Skill_2(BaseSkill):
    _display_name ='蜘蛛之鏡'
    key=Key.SKILL_2
    delay=0.75
    rep_interval=0.25
    skill_cool_down=240
    ground_skill=False
    buff_time=0
    combo_delay = 0.4

class Buff_F1(BaseSkill):
    _display_name ='出血毒素'
    key=Key.BUFF_F1
    delay=0.85
    rep_interval=0.25
    skill_cool_down=171
    ground_skill=True
    buff_time=80
    combo_delay = 0.8

class Buff_F2(BaseSkill):
    _display_name ='楓之谷世界女神的祝福'
    key=Key.BUFF_F2
    delay=0.85
    rep_interval=0.25
    skill_cool_down=180
    ground_skill=True
    buff_time=60
    combo_delay = 0.85

class Buff_F3(BaseSkill):
    _display_name ='飛閃起爆符'
    key=Key.BUFF_F3
    delay=0.9
    rep_interval=0.25
    skill_cool_down=171
    ground_skill=True
    buff_time=90
    combo_delay = 0.4

class Buff_5(BaseSkill):
    _display_name ='終極隱身術'
    key=Key.BUFF_5
    delay=0.7
    rep_interval=0.25
    skill_cool_down=192
    ground_skill=True
    buff_time=30
    combo_delay = 0.6

class Buff_F5(BaseSkill):
    _display_name ='必死決心'
    key=Key.BUFF_F5
    delay=0.7
    rep_interval=0.25
    skill_cool_down=77
    ground_skill=True
    buff_time=30
    combo_delay = 0.7

class Buff_3(BaseSkill):
    _display_name ='武公寶珠'
    key=Key.BUFF_3
    delay=1.45
    rep_interval=0.25
    skill_cool_down=143
    ground_skill=True
    buff_time=60
    combo_delay = 0.2
    skill_image = IMAGE_DIR + 'buff_3.png'
    active_if_not_in_skill_buff = 'buff_3'

class Skill_4(BaseSkill):
    _display_name ='噴泉'
    key=Key.SKILL_4
    delay=0.6
    rep_interval=0.25
    skill_cool_down=57
    ground_skill=True
    buff_time=60
    combo_delay = 0.3

class DarkEmbrace(BaseSkill):
    _display_name ='幽暗'
    key=Key.DARK_EMBRACE
    delay=1
    rep_interval=0.12
    skill_cool_down=3
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

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
        SkillCombination(direction='',target_skills='skill_a').execute()
        minimap = config.capture.minimap['minimap']
        height, width, _n = minimap.shape
        bottom_y = height - 30
        # bottom_y = config.player_pos[1]
        settings.platforms = 'b' + str(int(bottom_y))
        while True:
            if settings.auto_change_channel and config.should_solve_rune:
                Skill_A().execute()
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_A().execute()
                continue
            
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
            
            Frenzy().execute()
            SkillCombination(target_skills='buff_f3|buff_3|buff_f2').execute()
            if toggle:
                # right side
                move((width-20),bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    print('new bottom')
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                print("current bottom : ", settings.platforms)
                print("current player : ", str(config.player_pos[1]))
                FlashJump(direction='left').execute()
                Rope(rep='2',combo='True').execute()
                SkillCombination(direction='left',target_skills='skill_w|skill_s|skill_e|skill_a').execute()
            else:
                # left side
                move(20,bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    print('new bottom')
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                print("current bottom : ", settings.platforms)
                FlashJump(direction='right').execute()
                Rope(rep='2',combo='True').execute()
                SkillCombination(direction='right',target_skills='skill_2|skill_4|skill_w|skill_s|skill_e|skill_a').execute()
            
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_A().execute()
                continue
            move(width//2,bottom_y).execute()
            UpJump(jump='true').execute()
            SkillCombination(direction='left',target_skills='skill_w|skill_s|skill_e|skill_a').execute()
            SkillCombination(direction='right',target_skills='skill_1|skill_d|skill_a').execute()
            toggle = not toggle
            

        if settings.home_scroll_key:
            config.map_changing = True
            press(settings.home_scroll_key)
            time.sleep(5)
            config.map_changing = False
        return
