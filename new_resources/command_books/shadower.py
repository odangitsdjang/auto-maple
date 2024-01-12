from src.common import config, settings, utils
import time
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, GoToMap, ChangeChannel, Frenzy, Player_jump, WaitStanding, WealthPotion
from src.common.vkeys import press, key_down, key_up
import cv2

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/shadower/'

# List of key mappings
class Key:
    WORLD_MAP = 'pageup'
    
    # Movement
    FLASH_JUMP = 'alt'
    ROPE = 'v'
    UP_JUMP = 'up+alt'

    # Buffs
    SKILL_DECENT_HOLY_SYMBOL = "6"
    SKILL_DECENT_SHARP_EYES = "8"
    SKILL_DECENT_SPEED_INFUSION = "f6"
    SKILL_DECENT_ADVANCED_BLESSING = "f12"
    
    SKILL_MAPLE_WARRIOR = "5"
    SHADOW_PARTNER = ""

    # Attack Skills
    SKILL_A = 'shift' # cruel step
    SKILL_1 = 'e' # Veil of Shadow
    SKILL_D = 'q' # Dark Flare
    SKILL_S = 'delete' # Meso Explosion
    SKILL_W = 'w' # Sudden Raid
    SKILL_E = 'insert' # Trick blade
    SKILL_X = 'd' # Shadow Assault 
    SKILL_C = '' # Phase dash ??
    SKILL_2 = "" 
    SKILL_3 = '1' # Slash Shadow Formation
    SKILL_4 = '7' # Erda Fountain

    # special Skills
    SP_F12 = '' # frenzy totem

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
        Skill_AS(direction='',pre_delay='0.1').execute()
        WaitStanding(duration='3').execute()

    if direction == 'left' or direction == 'right':
        utils.wait_for_is_standing(1000)
        d_y = target[1] - config.player_pos[1]
        d_x = target[0] - config.player_pos[0]
        if abs(d_x) >= 16:
            if abs(d_x) >= 60:
                FlashJump(direction='',triple_jump='true',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_as').execute()
            elif abs(d_x) >= 28:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_as').execute()
            else:
                if d_y == 0:
                    # Skill_C().execute()
                    Skill_S().execute()
                else:
                    Skill_AS(direction='',jump='true').execute()
            time.sleep(utils.rand_float(0.04, 0.06))
            # if abs(d_x) <= 22:
            #     key_up(direction)
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
                SkillCombination(direction='',jump='false',target_skills='skill_as').execute()
            utils.wait_for_is_standing(500)
        else:
            time.sleep(utils.rand_float(0.05, 0.08))
            utils.wait_for_is_standing(500)
    
    if direction == 'up':
        utils.wait_for_is_standing(500)
        if abs(d_x) > settings.move_tolerance:
            return
        if abs(d_y) > 6 :
            if abs(d_y) > 36:
                press(config.bot.config['Jump'], 1)
                time.sleep(utils.rand_float(0.1, 0.15))
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            elif abs(d_y) <= 17:
                UpJump().execute()
                SkillCombination(direction='',jump='false',target_skills='skill_as').execute()
            else:
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
                SkillCombination(direction='',jump='false',target_skills='skill_as').execute()
            utils.wait_for_is_standing(300)
        else:
            press(config.bot.config['Jump'], 1)
            time.sleep(utils.rand_float(0.1, 0.15))

    if direction == 'down':
        if abs(d_x) > settings.move_tolerance:
            return
        down_duration = 0.15
        if abs(d_y) > 20:
            down_duration = 0.55
        elif abs(d_y) > 13:
            down_duration = 0.35
        
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
            print("down stair")
            if abs(d_x) >= 5:
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
            SkillCombination(direction='',jump='false',target_skills='skill_as').execute()
                
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
                        UpJump().main()
                    else:
                        utils.wait_for_is_standing(1000)
                        key_down('down')
                        time.sleep(utils.rand_float(0.05, 0.07))
                        press(config.bot.config['Jump'], 1, down_time=0.1)
                        key_up('down')
                        time.sleep(utils.rand_float(0.17, 0.25))
                    counter -= 1
            d_x = self.target[0] - config.player_pos[0]
            d_y = self.target[1] - config.player_pos[1]
            toggle = not toggle

class Buff(Command):
    """Uses each of Shadower's buffs once."""

    def __init__(self):
        super().__init__(locals())

    def main(self):
        Skill_Decent_Sharp_Eyes().execute() 
        Skill_Decent_Holy_Symbol().execute()
        # No need for the other buffs rn
        # Skill_Decent_Advanced_Blessing().execute()
        # Skill_Decent_Speed_Infusion().execute() # autobuffed
        # Skill_Maple_Warrior().execute()
        

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

class Skill_A(BaseSkill):
    _display_name = 'Cruel Step'
    _distance = 27
    key=Key.SKILL_A
    delay=0.30
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.05

class Skill_1(BaseSkill):
    _display_name = 'Veil of Shadow'
    _distance = 27
    key=Key.SKILL_1
    delay=0.9
    rep_interval=0.5
    skill_cool_down=60
    ground_skill=False
    buff_time=12
    combo_delay = 0.9

class Skill_D(BaseSkill):
    _display_name = 'Dark Flare'
    _distance = 27
    key=Key.SKILL_D
    delay=0.45
    rep_interval=0.5
    skill_cool_down=56
    ground_skill=True
    buff_time=57
    combo_delay = 0.5

class Skill_S(BaseSkill):
    _display_name = 'Meso Explosion'
    _distance = 50
    key=Key.SKILL_S
    delay=0.05
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.05

class Skill_AS(BaseSkill):
    _display_name = 'Cruel Step + Meso'
    _distance = 27
    key=Skill_A.key
    delay=0.06
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = Skill_A.combo_delay
    fast_rep=True

    def main(self):
        super().main()
        Skill_S().execute()
        # time.sleep(utils.rand_float(0.11*0.95, 0.11*1.1)) # Note: this can probably be faster but leaving it slow to cover more cases for now

class Skill_W(BaseSkill):
    _display_name = 'Sudden Raid'
    _distance = 50
    key=Key.SKILL_W
    delay=0.63
    rep_interval=0.55
    skill_cool_down=29
    ground_skill=False
    buff_time=0
    combo_delay = 0.53

class Skill_E(BaseSkill):
    _display_name = 'Trick blade'
    _distance = 50
    key=Key.SKILL_E
    delay=0.4
    rep_interval=0.5
    skill_cool_down=14
    ground_skill=False
    buff_time=0
    combo_delay = 0.3

class Skill_2(BaseSkill):
    _display_name ='蜘蛛之鏡'
    key=Key.SKILL_2
    delay=0.6
    rep_interval=0.25
    skill_cool_down=240
    ground_skill=False
    buff_time=0
    combo_delay = 0.4

class Skill_3(BaseSkill):
    _display_name ='Slash Shadow Formation'
    key=Key.SKILL_3
    delay=0.4
    rep_interval=0.25
    skill_cool_down=90
    ground_skill=False
    buff_time=5
    combo_delay = 0.3

class Skill_4(BaseSkill):
    _display_name ='Erda fountain'
    key=Key.SKILL_4
    delay=0.9
    rep_interval=0.25
    skill_cool_down=57
    ground_skill=True
    buff_time=60
    combo_delay = 0.3

class Skill_X(BaseSkill):
    _display_name ='Shadow Assault'
    key=Key.SKILL_X
    delay=0.3
    rep_interval=0.25
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

class Skill_C(BaseSkill):
    _display_name ='瞬影殺'
    key=Key.SKILL_C
    delay=0.5
    rep_interval=0.25
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.3

class Skill_Decent_Advanced_Blessing(BaseSkill):
    _display_name = 'Decent Advanced Blessing'
    _distance = 0
    key=Key.SKILL_DECENT_ADVANCED_BLESSING
    delay=0.9
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=True
    buff_time=215
    combo_delay = 0.9

class Skill_Decent_Holy_Symbol(BaseSkill):
    _display_name = 'Decent HS'
    _distance = 0
    key=Key.SKILL_DECENT_HOLY_SYMBOL
    delay=0.9
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=True
    buff_time=220
    combo_delay = 0.9

class Skill_Decent_Sharp_Eyes(BaseSkill):
    _display_name = 'Decent Sharp Eyes'
    _distance = 0
    key=Key.SKILL_DECENT_SHARP_EYES
    delay=0.9
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=True
    buff_time=220
    combo_delay = 0.9

class Skill_Maple_Warrior(BaseSkill):
    _display_name = 'Maple Warrior'
    _distance = 0
    key=Key.SKILL_MAPLE_WARRIOR
    delay=0.9
    rep_interval=0.5
    skill_cool_down=500
    ground_skill=True
    buff_time=1080
    combo_delay = 0.9

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
        SkillCombination(direction='',target_skills='skill_as').execute()
        minimap = config.capture.minimap['minimap']
        height, width, _n = minimap.shape
        bottom_y = height - 30
        # bottom_y = config.player_pos[1]
        settings.platforms = 'b' + str(int(bottom_y))
        while True:
            if settings.auto_change_channel and config.should_solve_rune:
                Skill_AS().execute()
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_AS().execute()
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
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                FlashJump(direction='left').execute()
                Skill_X(direction='left+up').execute()
                Skill_S().execute()
                FlashJump(direction='left').execute()
                SkillCombination(direction='left',target_skills='skill_w|skill_e|skill_as').execute()
            else:
                # left side
                move(20,bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                FlashJump(direction='right').execute()
                Skill_X(direction='right+up').execute()
                Skill_S().execute()
                FlashJump(direction='right').execute()
                SkillCombination(direction='right',target_skills='skill_w|skill_e|skill_as').execute()
            
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_AS().execute()
                continue
            move(width//2,bottom_y).execute()
            UpJump(jump='true').execute()
            SkillCombination(direction='left',target_skills='skill_w|skill_e|skill_as').execute()
            SkillCombination(direction='right',target_skills='skill_1|skill_d|skill_as').execute()
            toggle = not toggle
            

        if settings.home_scroll_key:
            config.map_changing = True
            press(settings.home_scroll_key)
            time.sleep(5)
            config.map_changing = False
        return
