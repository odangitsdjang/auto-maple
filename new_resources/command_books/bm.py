from src.common import config, settings, utils
import time
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, GoToMap, ChangeChannel, Frenzy, Player_jump, WaitStanding, WealthPotion
from src.common.vkeys import press, key_down, key_up
import cv2

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/dawn_warrior/'

# List of key mappings
class Key:
    INTERACT = 'space'

    # Movement
    JUMP = 'alt'
    FLASH_JUMP = 'alt'
    ROPE = 'v'
    UP_JUMP = 'up+alt'
    BLINK_SHOT = "n"

    GRITTY = "q"
    ARROW_BLAST = "d"
    ERDA_FOUNTAIN = "down+7"
    
    # 120s Buffs First Rotation
    QUIVER_BARRAGE = "8"
    INHUMAN_SPEED = "0"
    CONCENTRATION = '='

    # 120s Buff Second Rotation (balance out damage)
    STORM_OF_ARROWS = '9'
    # EPIC_ADVENTURE = '-'
    VICIOUS_SHOT = "o"

    # 3rd rotation
    ARACHNID = "5"
    FURY_OF_THE_WILD = "3"

    # TOTEM = "6"

    # 200s+ Buffs
    PHOENIX = "6"
    
    # Skills
    ARROW_STREAM = "shift"
    HURRICANE = 'a'



    # Buffs
    
    # Buffs Toggle

    # Attack Skills
    ARROW_STREAM = "shift"
    SKILL_HURR = 'a' # Hurricane
    SKILL_1 = '1' # Cosmos (LOTD)
    SKILL_2 = '2' # Rift of damnation/styx
    SKILL_3 = '3' # Soul eclipse
    SKILL_D = 'd' # Equinox slash
    SKILL_DEL = 'delete' # Cosmic Forge
    SKILL_0 = '0' # Cosmic Burst / Note: Turn off auto cast when running bot!
    SKILL_Q = 'q' # Cosmic Shower
    SKILL_F = 'f' # Blazing Assault/Luster Charge
    SKILL_MINUS = '-' # 西格諾斯槍兵陣/Cygnus?

    # special Skills
    SP_F12 = '' # Frenzy

def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]

    if direction == 'left' or direction == 'right':
        utils.wait_for_is_standing(1000)
        d_y = target[1] - config.player_pos[1]
        d_x = target[0] - config.player_pos[0]
        if config.player_states['is_stuck'] and abs(d_x) < 16:
            print("is stuck")
            time.sleep(utils.rand_float(0.1, 0.2))
            press(Key.JUMP)
            Skill_Arrow_Stream(direction='').execute()
            WaitStanding(duration='1').execute()
        if abs(d_x) >= 16:
            if abs(d_x) >= 28:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_gritty|skill_arrow_stream').execute()
            else:
                if d_y == 0:
                    Skill_Arrow_Stream().execute()
                else:
                    Skill_Arrow_Stream(direction='',jump='true').execute()
            time.sleep(utils.rand_float(0.04, 0.06))
            # if abs(d_x) <= 22:
            #     key_up(direction)
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
                SkillCombination(direction='',jump='false',target_skills='skill_gritty|skill_arrow_stream').execute()
            utils.wait_for_is_standing(500)
        else:
            time.sleep(utils.rand_float(0.05, 0.08))
            utils.wait_for_is_standing(500)
    
    if direction == 'up':
        utils.wait_for_is_standing(1500)
        if abs(d_x) > settings.move_tolerance:
            return
        if abs(d_y) > 6 :
            if abs(d_y) > 36:
                press(Key.JUMP, 1)
                time.sleep(utils.rand_float(0.12, 0.18))
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            elif abs(d_y) <= 26:
                UpJump(pre_delay="0.1").execute()
            else:
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            SkillCombination(direction='',jump='false',target_skills='skill_gritty|skill_arrow_stream').execute()
            utils.wait_for_is_standing(1300)
        else:
            press(Key.JUMP, 1)
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
                        press(Key.JUMP)
                        key_up('left')
                    else:
                        key_down('right')
                        press(Key.JUMP)
                        key_up('right')
            SkillCombination(direction='',jump='false',target_skills='skill_gritty|skill_arrow_stream').execute()
                
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
                        press(Key.JUMP, 1, down_time=0.1)
                        key_up('down')
                        time.sleep(utils.rand_float(0.17, 0.25))
                    counter -= 1
            d_x = self.target[0] - config.player_pos[0]
            d_y = self.target[1] - config.player_pos[1]
            toggle = not toggle

class Buff(Command):
    def __init__(self, BlinkShot=False):
        super().__init__(locals())
        # bm is a 2 min dpm class, separate burst skills into two timers to elongate burst / mob more effectively
        self.reset_timers(BlinkShot) 

    def reset_timers(self, BlinkShot):
        self.cd120_first_rotation = 0 # Burst 1
        # Burst 2
        self.cd120_second_rotation = time.time() - 40 # always use 80 seconds after first rotation (quiver barrage lasts 40 sec)
        # Supplemental damage after Burst 1
        self.cd120_third_rotation = time.time() - 90 # use 30 seconds after first rotation
        self.cd200_buff_time = 0
        self.cd60_blinkshot = 0
        self.blink_shot_on = BlinkShot  

    def main(self):
        now = time.time()
        is_buff_cast = 0

        # resetting rotation timers if bot was off for a while (reloading does not reset time without this code - BUG?)
        if now - self.cd120_first_rotation > 180:
            self.reset_timers(BlinkShot=self.blink_shot_on)

        # print("Time into first rotation timer: ", now - self.cd120_first_rotation)
        # print("Time into second rotation timer: ", now - self.cd120_second_rotation)
        if self.cd120_first_rotation == 0 or now - self.cd120_first_rotation > 120:
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.STORM_OF_ARROWS, 1)
            time.sleep(utils.rand_float(0.25, 0.28))
            press(Key.INHUMAN_SPEED, 1)
            time.sleep(utils.rand_float(0.21, 0.25))
            # press(Key.EPIC_ADVENTURE, 1)
            # time.sleep(utils.rand_float(0.15, 0.2))
            self.cd120_first_rotation = now
            is_buff_cast = 1
        if now - self.cd120_second_rotation > 120:
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.QUIVER_BARRAGE, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.VICIOUS_SHOT, 1)
            time.sleep(utils.rand_float(0.21, 0.25))
            press(Key.CONCENTRATION, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            
            self.cd120_second_rotation = now
            is_buff_cast = 1
        if now - self.cd120_third_rotation > 120: 
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.ARACHNID, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.FURY_OF_THE_WILD, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            
            self.cd120_third_rotation = now
            is_buff_cast = 1
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.PHOENIX, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            self.cd200_buff_time = now
            is_buff_cast = 1
        if self.blink_shot_on == "True" and (self.cd60_blinkshot == 0 or now - self.cd60_blinkshot > 60):
            time.sleep(utils.rand_float(0.15, 0.2))
            SkillCombination(direction='up',jump='false',target_skills='skill_blinkshot').execute()
            SkillCombination(direction='down',jump='false',target_skills='skill_blinkshot').execute()
            time.sleep(utils.rand_float(0.1, 0.15))
            self.cd60_blinkshot = now
        
        if is_buff_cast:
            time.sleep(utils.rand_float(0.1, 0.12))

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
                press(Key.JUMP,down_time=0.06,up_time=0.05)
        else:
            key_down(self.direction,down_time=0.05)
            press(Key.JUMP,down_time=0.06,up_time=0.05)
        
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
    _display_name = 'Rope lift'
    _distance = 27
    key=Key.ROPE
    delay=1.4
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class Skill_Arrow_Stream(BaseSkill):
    _display_name = 'Arrow Stream'
    _distance = 20
    key=Key.ARROW_STREAM
    delay=0.3 # with decent speed infusion, needs test
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.05

class Skill_Arrow_Blast(BaseSkill):
    _display_name = 'Arrow Blast/Platter'
    _distance = 20
    key=Key.ARROW_BLAST
    key_down_skill=True
    delay=0.5
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.05

class Skill_Arrow_Blast_Up(BaseSkill):
    _display_name = 'Arrow Blast/Platter Up'
    _distance = 20
    key=Key.ARROW_BLAST
    key_up_skill=True
    delay=0.5
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.05


class Skill_Arrow_Blast_Summon(BaseSkill):
    _display_name = 'Arrow Blast/Platter Summon'
    _distance = 20
    key=Key.ARROW_BLAST
    key_down_skill=True
    delay=0.5
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.05

    def main(self):
        super().main()
        time.sleep(utils.rand_float(0.1, 0.15))
        key_up(Key.ARROW_BLAST)
        config.player_states['is_keydown_skill'] = False
        
        press(Key.INTERACT, 1, down_time=.03)
        

class Skill_Hurricane(BaseSkill):
    _display_name = 'Hurricane'
    _distance = 20
    key=Key.HURRICANE
    key_down_skill=True
    delay=0.5
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.05

class Skill_Hurricane_Up(BaseSkill):
    _display_name = 'Hurricane Up'
    _distance = 20
    key=Key.HURRICANE
    key_up_skill=True
    delay=0.5
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.05

class Skill_Gritty(BaseSkill):
    _display_name = 'Gritty Gust'
    _distance = 22
    key=Key.GRITTY
    delay=0.45
    rep_interval=0.5
    skill_cool_down=15
    ground_skill=False
    buff_time=0
    combo_delay = 0.4


class Skill_Erda_Fountain(BaseSkill):
    _display_name = 'Erda Fountain'
    _distance = 0
    key=Key.ERDA_FOUNTAIN
    delay=0.9
    rep_interval=0.5
    skill_cool_down=57
    ground_skill=True
    buff_time=60
    combo_delay = 0.9

class Skill_BlinkShot(BaseSkill):
    _display_name = 'Blink Shot'
    _distance = 0
    key=Key.BLINK_SHOT
    delay=0.3
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.2

class AutoHunting(Command):
    _display_name ='自動走位狩獵/AutoHunting'

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
        SkillCombination(direction='',target_skills='skill_arrow_stream').execute()
        minimap = config.capture.minimap['minimap']
        height, width, _n = minimap.shape
        bottom_y = height - 30
        # bottom_y = config.player_pos[1]
        settings.platforms = 'b' + str(int(bottom_y))
        while True:
            if settings.auto_change_channel and config.should_solve_rune:
                Skill_Arrow_Stream().execute()
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_Arrow_Stream().execute()
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
                SkillCombination(direction='left',target_skills='skill_erda_fountain|skill_0|skill_arrow_stream').execute()
                UpJump(direction='left').execute()
                SkillCombination(direction='left',target_skills='skill_q|skill_0|skill_f|skill_d|skill_arrow_stream').execute()
            else:
                # left side
                move(20,bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                FlashJump(direction='right').execute()
                SkillCombination(direction='right',target_skills='skill_erda_fountain|skill_0|skill_arrow_stream').execute()
                UpJump(direction='right').execute()
                SkillCombination(direction='right',target_skills='skill_q|skill_0|skill_f|skill_d|skill_arrow_stream').execute()
            
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_Arrow_Stream().execute()
                continue
            move(width//2,bottom_y).execute()
            UpJump(jump='true').execute()
            SkillCombination(direction='left',target_skills='skill_3|skill_2|skill_1|skill_del|skill_0|skill_arrow_stream').execute()
            toggle = not toggle

        if settings.home_scroll_key:
            config.map_changing = True
            press(settings.home_scroll_key)
            time.sleep(5)
            config.map_changing = False
        return
