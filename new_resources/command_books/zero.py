from src.common import config, settings, utils
import time
import cv2
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, ChangeChannel, GoToMap, Frenzy
from src.common.vkeys import press, key_down, key_up

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/zero/'

# List of key mappings
class Key:
    WORLD_MAP = 'pageup'
    
    # Movement
    FLASH_JUMP = 'alt'
    TELEPORT = 'x' # 爆裂衝刺

    # Buffs
    BUFF_8 = '8' # 集中時間
    BUFF_F1 = 'f1' # 武公寶珠
    BUFF_PAGEUP = 'pageup' # 掌握時間
    BUFF_F5 = 'f5' # 優伊娜的心願
    BUFF_5 = '5' # 幻靈武具
    
    # Buffs Toggle

    # Attack Skills
    SKILL_Q = 'q' # 狂風千刃(a4)
    SKILL_S = 's'# 瞬閃斬擊(a2)
    SKILL_A = 'a' # 月之降臨(a1)
    SKILL_D = 'd' # 旋風急轉彎(a3)
    SKILL_R = 'r' # 巨力重擊(b4)
    SKILL_W = 'w' # 趨前砍擊(b2)
    SKILL_E = 'e' # 迴旋突進(b3)
    SKILL_F = 'f' # 暗影瞬閃
    SKILL_F2 = 'f2' # 終焉之時
    SKILL_2 = '2' # 蜘蛛之鏡
    SKILL_3 = '3' # 暗影之雨

    # special Skills
    SP_F12 = 'f12' # 輪迴

def check_current_tag(tag):
    if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
        if config.player_states['current_tag'] == tag:
            return True
        else:
            return False
    else:
        config.player_states['beta_tag'] = time.time()-3
        config.player_states['alpha_tag'] = time.time()
        config.player_states['current_tag'] = 'alpha'
    return False

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

    if direction == 'left' or direction == 'right':
        if abs(d_x) > 20:
            if abs(d_x) >= 40:
                if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
                    if config.player_states['current_tag'] == 'alpha':
                        Skill_S(rep='2').execute()
                        Teleport(direction=direction).execute()
                    else:
                        Teleport(direction=direction).execute()
                        FlashJump(direction=direction).execute()
                        Skill_W(rep='2').execute()
                else:
                    Teleport(direction=direction).execute()
                    FlashJump(direction=direction).execute()
            else:
                if utils.bernoulli(0.3+0.4*(abs(d_x)-10)/100):
                    FlashJump(direction=direction).execute()
                    if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
                        if config.player_states['current_tag'] == 'alpha':
                            Skill_A(rep='2').execute()
                        else:
                            Skill_W(rep='2').execute()
                else:
                    Teleport(direction=direction).execute()
        elif abs(d_x) > 10:
            time.sleep(utils.rand_float(0.1, 0.15))
        utils.wait_for_is_standing(1000)
    
    if direction == 'up':
        if abs(d_y) > 4 :
            if abs(d_y) >= 22:
                Teleport(direction=direction,jump='true').execute()
            else:
                Teleport(direction=direction).execute()
            utils.wait_for_is_standing(300)
        else:
            press(config.bot.config['Jump'], 1)
            time.sleep(utils.rand_float(0.2, 0.25))
    if direction == 'down':
        # if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
        print("down stair")
        # if abs(d_y) > 3 :
        Teleport(direction=direction).execute()
        # if abs(d_x) > 3:
        #     if d_x > 0:
        #         key_down('right')
        #         press(config.bot.config['Jump'], 1)
        #         key_up('right')
        #     else:
        #         key_down('left')
        #         press(config.bot.config['Jump'], 1)
        #         key_up('left')
        time.sleep(utils.rand_float(0.05, 0.08))
        # utils.wait_for_is_standing(300)

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
                # if abs(d_x) > threshold:
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
                if abs(d_y) > settings.adjust_tolerance:
                    if d_y < 0:
                        Teleport(direction='up').execute()
                    else:
                        Teleport(direction='down').execute()
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
            time.sleep(utils.rand_float(0.1, 0.3))
            press(Key.BUFF_8, 1)
            self.cd900_buff_time = now
        # if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
        #     for key in buffs:
        #       press(key, 3, up_time=0.3)
        #       self.decent_buff_time = now	

class FlashJump(Command):
    """Performs a flash jump in the given direction."""
    _display_name = '二段跳'

    def __init__(self, direction="",jump='false',combo='False',triple_jump="False",fast_jump="false"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.triple_jump = settings.validate_boolean(triple_jump)
        self.fast_jump = settings.validate_boolean(fast_jump)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if not self.jump:
            self.player_jump(self.direction)
        else:
            key_down(self.direction,down_time=0.05)
            press(config.bot.config['Jump'],down_time=0.04,up_time=0.05)
        if not self.fast_jump:
            time.sleep(utils.rand_float(0.02, 0.04)) # fast flash jump gap
        else:
            time.sleep(utils.rand_float(0.08, 0.12)) # slow flash jump gap
        if self.direction == 'up':
            press(Key.FLASH_JUMP, 1)
        else:
            press(Key.FLASH_JUMP, 1,down_time=0.06,up_time=0.05)
            if self.triple_jump:
                time.sleep(utils.rand_float(0.05, 0.08))
                press(Key.FLASH_JUMP, 1,down_time=0.07,up_time=0.04) # if this job can do triple jump
        key_up(self.direction,up_time=0.01)
        time.sleep(utils.rand_float(0.02, 0.04))

class Teleport(BaseSkill):
    _display_name ='爆裂衝刺'
    _distance = 27
    key=Key.TELEPORT
    delay=0.16
    rep_interval=0.3
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

    # def main(self):
    #     CustomKey(name=self._display_name,key=Key.TELEPORT,direction=self.direction,jump=self.jump,delay=0.095).execute()

class Skill_Q(BaseSkill):
    _display_name ='狂風千刃(a4)'
    key=Key.SKILL_Q
    delay=0.75
    rep_interval=0.23
    skill_cool_down=3
    ground_skill=False
    buff_time=0
    combo_delay = 0.25
    rep_interval_increase = 0.05
    skill_image = IMAGE_DIR + 'skill_q.png'
    
    def main(self):
        if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
            if config.player_states['current_tag'] == 'beta':
                utils.wait_for_is_standing(800)
            latest_beta_tag_duration = time.time() - config.player_states['beta_tag']
            if latest_beta_tag_duration > 3.33 and config.player_states['current_tag'] == 'beta':
                config.player_states['alpha_tag'] = time.time()
            elif latest_beta_tag_duration <= 3.33 and config.player_states['current_tag'] == 'beta':
                time.sleep(3.33-(time.time() - config.player_states['beta_tag']))
                config.player_states['alpha_tag'] = time.time()
            config.player_states['current_tag'] = 'alpha'
        else:
            config.player_states['beta_tag'] = time.time()-3
            config.player_states['alpha_tag'] = time.time()
            config.player_states['current_tag'] = 'alpha'
        super().main()

class Skill_A(BaseSkill):
    _display_name ='月之降臨(a1)'
    key=Key.SKILL_A
    delay=0.3
    rep_interval=0.1
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.2
    
    def main(self):
        if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
            if config.player_states['current_tag'] == 'beta':
                utils.wait_for_is_standing(800)
            latest_beta_tag_duration = time.time() - config.player_states['beta_tag']
            if latest_beta_tag_duration > 3.33 and config.player_states['current_tag'] == 'beta':
                config.player_states['alpha_tag'] = time.time()
            elif latest_beta_tag_duration <= 3.33 and config.player_states['current_tag'] == 'beta':
                time.sleep(3.33-(time.time() - config.player_states['beta_tag']))
                config.player_states['alpha_tag'] = time.time()
            config.player_states['current_tag'] = 'alpha'
        else:
            config.player_states['beta_tag'] = time.time()-3
            config.player_states['alpha_tag'] = time.time()
            config.player_states['current_tag'] = 'alpha'
        super().main()

class Skill_S(BaseSkill):
    _display_name ='瞬閃斬擊(a2)'
    key=Key.SKILL_S
    delay=0.4
    rep_interval=0.12
    skill_cool_down=1
    ground_skill=False
    buff_time=0
    combo_delay = 0.2
    # skill_image = IMAGE_DIR + 'skill_s.png'

    def main(self):
        if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
            if config.player_states['current_tag'] == 'beta':
                utils.wait_for_is_standing(800)
            latest_beta_tag_duration = time.time() - config.player_states['beta_tag']
            if latest_beta_tag_duration > 3.33 and config.player_states['current_tag'] == 'beta':
                config.player_states['alpha_tag'] = time.time()
            elif latest_beta_tag_duration <= 3.33 and config.player_states['current_tag'] == 'beta':
                time.sleep(3.33-(time.time() - config.player_states['beta_tag']))
                config.player_states['alpha_tag'] = time.time()
            config.player_states['current_tag'] = 'alpha'
        else:
            config.player_states['beta_tag'] = time.time()-3
            config.player_states['alpha_tag'] = time.time()
            config.player_states['current_tag'] = 'alpha'
        super().main()

class Skill_D(BaseSkill):
    _display_name ='旋風急轉彎(a3)'
    key=Key.SKILL_D
    delay=0.9
    rep_interval=0.9
    skill_cool_down=2
    ground_skill=False
    buff_time=0
    combo_delay = 0.5

    def main(self):
        if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
            if config.player_states['current_tag'] == 'beta':
                utils.wait_for_is_standing(800)
            latest_beta_tag_duration = time.time() - config.player_states['beta_tag']
            if latest_beta_tag_duration > 3.33 and config.player_states['current_tag'] == 'beta':
                config.player_states['alpha_tag'] = time.time()
            elif latest_beta_tag_duration <= 3.33 and config.player_states['current_tag'] == 'beta':
                time.sleep(3.33-(time.time() - config.player_states['beta_tag']))
                config.player_states['alpha_tag'] = time.time()
            config.player_states['current_tag'] = 'alpha'
        else:
            config.player_states['beta_tag'] = time.time()-3
            config.player_states['alpha_tag'] = time.time()
            config.player_states['current_tag'] = 'alpha'
        super().main()

class Skill_R(BaseSkill):
    _display_name ='巨力重擊(b4)'
    key=Key.SKILL_R
    delay=1.22
    rep_interval=0.22
    rep_interval_increase = 0.28
    skill_cool_down=3
    ground_skill=True
    buff_time=0
    combo_delay = 1

    def main(self):
        if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
            if config.player_states['current_tag'] == 'alpha':
                utils.wait_for_is_standing(800)
            latest_alpha_tag_duration = time.time() - config.player_states['alpha_tag']
            if latest_alpha_tag_duration > 3.33 and config.player_states['current_tag'] == 'alpha':
                config.player_states['beta_tag'] = time.time()
            elif latest_alpha_tag_duration <= 3.33 and config.player_states['current_tag'] == 'alpha':
                time.sleep(3.33-(time.time() - config.player_states['alpha_tag']))
                config.player_states['beta_tag'] = time.time()
            config.player_states['current_tag'] = 'beta'
        else:
            config.player_states['beta_tag'] = time.time()
            config.player_states['alpha_tag'] = time.time()-3
            config.player_states['current_tag'] = 'beta'
        super().main()

class Skill_W(BaseSkill):
    _display_name ='趨前砍擊'
    key=Key.SKILL_W
    delay=0.5
    rep_interval=0.23
    skill_cool_down=0.5
    ground_skill=False
    buff_time=0
    combo_delay = 0.3

    def main(self):
        if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
            if config.player_states['current_tag'] == 'alpha':
                utils.wait_for_is_standing(800)
            latest_alpha_tag_duration = time.time() - config.player_states['alpha_tag']
            if latest_alpha_tag_duration > 3.33 and config.player_states['current_tag'] == 'alpha':
                config.player_states['beta_tag'] = time.time()
            elif latest_alpha_tag_duration <= 3.33 and config.player_states['current_tag'] == 'alpha':
                time.sleep(3.33-(time.time() - config.player_states['alpha_tag']))
                config.player_states['beta_tag'] = time.time()
            config.player_states['current_tag'] = 'beta'
        else:
            config.player_states['beta_tag'] = time.time()
            config.player_states['alpha_tag'] = time.time()-3
            config.player_states['current_tag'] = 'beta'
        super().main()

class Skill_E(BaseSkill):
    _display_name ='迴旋突進'
    key=Key.SKILL_E
    delay=0.3
    rep_interval=0.1
    skill_cool_down=0.5
    ground_skill=False
    buff_time=0
    combo_delay = 0.12

    def main(self):
        if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
            if config.player_states['current_tag'] == 'alpha':
                utils.wait_for_is_standing(800)
            latest_alpha_tag_duration = time.time() - config.player_states['alpha_tag']
            if latest_alpha_tag_duration > 3.33 and config.player_states['current_tag'] == 'alpha':
                config.player_states['beta_tag'] = time.time()
            elif latest_alpha_tag_duration <= 3.33 and config.player_states['current_tag'] == 'alpha':
                time.sleep(3.33-(time.time() - config.player_states['alpha_tag']))
                config.player_states['beta_tag'] = time.time()
            config.player_states['current_tag'] = 'beta'
        else:
            config.player_states['beta_tag'] = time.time()
            config.player_states['alpha_tag'] = time.time()-3
            config.player_states['current_tag'] = 'beta'
        super().main()

class Skill_E1(BaseSkill):
    _display_name ='迴旋突進收尾用1段'
    key=Key.SKILL_E
    delay=1.05
    rep_interval=0.15
    skill_cool_down=0.5
    ground_skill=False
    buff_time=0
    combo_delay = 1.05

    def main(self):
        if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
            if config.player_states['current_tag'] == 'alpha':
                utils.wait_for_is_standing(800)
            latest_alpha_tag_duration = time.time() - config.player_states['alpha_tag']
            if latest_alpha_tag_duration > 3.33 and config.player_states['current_tag'] == 'alpha':
                config.player_states['beta_tag'] = time.time()
            elif latest_alpha_tag_duration <= 3.33 and config.player_states['current_tag'] == 'alpha':
                time.sleep(3.33-(time.time() - config.player_states['alpha_tag']))
                config.player_states['beta_tag'] = time.time()
            config.player_states['current_tag'] = 'beta'
        else:
            config.player_states['beta_tag'] = time.time()
            config.player_states['alpha_tag'] = time.time()-3
            config.player_states['current_tag'] = 'beta'
        super().main()

class Buff_F1(BaseSkill):
    _display_name ='武公寶珠'
    key=Key.BUFF_F1
    delay=0.8
    rep_interval=0.25
    skill_cool_down=143
    ground_skill=True
    buff_time=60
    combo_delay = 0.2
    skill_image = IMAGE_DIR + 'buff_f1.png'
    active_if_not_in_skill_buff = 'buff_f1'

class Skill_FA1(BaseSkill):
    _display_name ='暗影瞬閃a1'
    key=Key.SKILL_F
    delay=0.5
    rep_interval=0.25
    skill_cool_down=40
    ground_skill=False
    buff_time=0
    combo_delay = 0.2
    skill_image = IMAGE_DIR + 'skill_fa.png'

    def main(self):
        if not 'current_tag' in config.player_states and config.player_states['current_tag'] != 'alpha':
            return
        super().main()

class Skill_FA2(BaseSkill):
    _display_name ='暗影瞬閃a2'
    key=Key.SKILL_F
    delay=0.5
    rep_interval=0.25
    skill_cool_down=3
    ground_skill=False
    buff_time=0
    combo_delay = 0.2
    active_if_skill_cd = 'skill_fa1'

    def main(self):
        if not 'current_tag' in config.player_states and config.player_states['current_tag'] != 'alpha':
            return
        super().main()

class Skill_FB1(BaseSkill):
    _display_name ='暗影瞬閃b1'
    key=Key.SKILL_F
    delay=0.5
    rep_interval=0.25
    skill_cool_down=40
    ground_skill=False
    buff_time=0
    combo_delay = 0.2
    skill_image = IMAGE_DIR + 'skill_fb.png'

    def main(self):
        if not 'current_tag' in config.player_states and config.player_states['current_tag'] != 'beta':
            return
        super().main()

class Skill_FB2(BaseSkill):
    _display_name ='暗影瞬閃b2'
    key=Key.SKILL_F
    delay=0.6
    rep_interval=0.25
    skill_cool_down=3
    ground_skill=False
    buff_time=0
    combo_delay = 0.42
    active_if_skill_cd = 'skill_fb1'

    def main(self):
        if not 'current_tag' in config.player_states and config.player_states['current_tag'] != 'beta':
            return
        super().main()

class Skill_F2(BaseSkill):
    _display_name ='終焉之時'
    key=Key.SKILL_F2
    delay=0.55
    rep_interval=0.25
    skill_cool_down=230
    buff_time=45
    ground_skill=False
    combo_delay = 0.2

class Skill_F22(BaseSkill):
    _display_name ='終焉之時引爆'
    key=Key.SKILL_F2
    delay=0.55
    rep_interval=0.25
    skill_cool_down=45
    buff_time=0
    ground_skill=False
    combo_delay = 0.03
    active_if_in_skill_buff = 'skill_f2'

class Skill_2(BaseSkill):
    _display_name ='蜘蛛之鏡'
    key=Key.SKILL_2
    delay=0.8
    rep_interval=0.25
    skill_cool_down=240
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class Skill_3(BaseSkill):
    _display_name ='暗影之雨'
    key=Key.SKILL_3
    delay=4.3
    rep_interval=0.25
    skill_cool_down=300
    ground_skill=True
    buff_time=0
    combo_delay = 0.2
    skill_image = IMAGE_DIR + 'skill_3.png'

    def main(self):
        if 'beta_tag' in config.player_states and 'alpha_tag' in config.player_states and 'current_tag' in config.player_states:
            latest_alpha_tag_duration = time.time() - config.player_states['alpha_tag']
            latest_beta_tag_duration = time.time() - config.player_states['beta_tag']
            if latest_alpha_tag_duration < 3.1 or latest_beta_tag_duration < 3.1 :
                super().main()

class Buff_Pageup(BaseSkill):
    _display_name ='掌握時間'
    key=Key.BUFF_PAGEUP
    delay=1
    rep_interval=0.25
    skill_cool_down=180
    ground_skill=False
    buff_time=0
    combo_delay = 0.2
    skill_image = IMAGE_DIR + 'buff_pageup.png'
    active_if_skill_cd = 'buff_f1'
    active_if_not_in_skill_buff = 'skill_f2'

    def main(self):
        if super().main():
            config.is_skill_ready_collector['Buff_F1'] = True
            config.is_skill_ready_collector['Skill_3'] = True

class Buff_F5(BaseSkill):
    _display_name ='優伊娜的心願'
    key=Key.BUFF_F5
    delay=0.45
    rep_interval=0.25
    skill_cool_down=230
    ground_skill=False
    buff_time=0
    combo_delay = 0.3
    active_if_skill_cd = 'buff_f1'
    active_if_not_in_skill_buff = 'skill_f2'

    def main(self):
        if super().main():
            config.is_skill_ready_collector['Buff_F1'] = True
            config.is_skill_ready_collector['Skill_3'] = True

class Buff_5(BaseSkill):
    _display_name ='幻靈武具'
    key=Key.BUFF_5
    delay=0.45
    rep_interval=0.25
    skill_cool_down=172
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

class SP_F12(BaseSkill):
    _display_name ='輪迴'
    key=Key.SP_F12
    delay=0.5
    rep_interval=0.25
    skill_cool_down=60
    ground_skill=True
    buff_time=600
    combo_delay = 0.2

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
        Skill_A(rep='3').execute()
        minimap = config.capture.minimap['minimap']
        height, width, _n = minimap.shape
        bottom_y = height - 30
        # bottom_y = config.player_pos[1]
        settings.platforms = 'b' + str(int(bottom_y))
        while True:
            if settings.auto_change_channel and config.should_solve_rune:
                Skill_A(rep='3').execute()
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40,delay='4').execute()
                Skill_A(rep='3').execute()
                continue
            Frenzy().execute()
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
                move((width-20),bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    print('new bottom')
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                FlashJump(direction='right').execute()
                Skill_Q(rep='3',direction='left').execute()
                Teleport(direction='left').execute()
                Skill_E(rep='2').execute()
                Teleport(direction='up').execute()
                FlashJump(direction='left',jump='true').execute()
                Skill_W(rep='2').execute() 
                SkillCombination(direction='',combo='true',target_skills='skill_3|Skill_FB1|skill_f2|skill_2|buff_f1|buff_f5|buff_pageup|skill_f22|Skill_FB2|Skill_E1').execute()
                time.sleep(0.2)
                Skill_S(rep='2',direction='left').execute()
                FlashJump(direction='left').execute()
                Skill_D(direction='left',rep='2').execute()
                SkillCombination(direction='',target_skills='skill_f2|skill_2|Skill_FA1|Skill_FA2|skill_f22').execute()
            else:
                # left side
                move(20,bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    print('new bottom')
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                FlashJump(direction='left').execute()
                Skill_Q(rep='3',direction='right').execute()
                Teleport(direction='right').execute()
                Skill_E(rep='2').execute()
                Teleport(direction='up').execute()
                FlashJump(direction='right',jump='true').execute()
                Skill_W(rep='2').execute()
                SkillCombination(direction='',combo='true',target_skills='skill_3|Skill_FB1|skill_f2|skill_2|buff_f1|buff_f5|buff_pageup|skill_f22|Skill_FB2|Skill_E1').execute()
                time.sleep(0.2)
                Skill_S(rep='2',direction='right').execute()
                FlashJump(direction='right').execute()
                Skill_D(direction='right',rep='2').execute()
                SkillCombination(direction='',target_skills='skill_f2|skill_2|Skill_FA1|Skill_FA2|skill_f22').execute()
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_A(rep='3').execute()
                continue
            toggle = not toggle
            

        if settings.home_scroll_key:
            config.map_changing = True
            press(settings.home_scroll_key)
            time.sleep(5)
            config.map_changing = False
        return
