from src.common import config, settings, utils
import time
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, GoToMap, ChangeChannel, WaitStanding, WealthPotion
from src.common.vkeys import press, key_down, key_up
import cv2

# List of key mappings
class Key:
    WORLD_MAP = 'w'

    # Movement
    FLASH_JUMP = 'alt'
    ROPE = 'v'
    UP_JUMP = 'up+alt'
    BLINK_SHOT = 'n'
    BLINK_SHOT_RESUMMON = 'down+n'
    COVERING_FIRE = 'r'

    GRITTY = 'q'
    ARROW_BLAST = 'd'
    ERDA_FOUNTAIN = '7'
    
    # 120s Buff First Rotation 
    STORM_OF_ARROWS = '9'
    VICIOUS_SHOT = 'o'
    INHUMAN_SPEED = '0'
    CONCENTRATION = '='

    # 120s Buffs Second Rotation (balance out damage)
    MAPLE_GODDESS_BLESSING = '6'
    QUIVER_BARRAGE = '8'
    FURY_OF_THE_WILD = '3'

    # 3rd rotation
    ARACHNID = '5'

    # Other Buffs
    PHOENIX = '1'
    MAPLE_WARRIOR = '' # Auto Buffed
    EPIC_ADVENTURE = '' # Auto Buffed
    
    # Skills
    ARROW_STREAM = 'shift'
    HURRICANE = 'a'

    # Buffs
    GUILD_DAMAGE = 'insert'
    GUILD_CRIT_DAMAGE = 'pageup'
    
    # special Skills
    SP_F12 = '' # Frenzy

def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]
    jump = config.bot.config['Jump']

    if direction == 'left' or direction == 'right':
        utils.wait_for_is_standing(1500)
        d_y = target[1] - config.player_pos[1]
        d_x = target[0] - config.player_pos[0]
        if config.player_states['is_stuck'] and abs(d_x) < 16:
            print("is stuck")
            time.sleep(utils.rand_float(0.1, 0.2))
            press(jump)
            Skill_Arrow_Stream(direction='').execute()
            WaitStanding(duration='1').execute()
        if abs(d_x) >= 16:
            if abs(d_x) >= 28:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_gritty|skill_arrow_stream').execute()
            else:
                if d_y == 0:
                    pass
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
        if abs(d_y) > 6:
            print(f"dy is {d_y}")
            if (abs(d_y) > 42):
                UpJump(pre_delay="0.1", jump='true').execute()
                time.sleep(utils.rand_float(0.10, 0.15))
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            elif abs(d_y) > 36:
                press(jump, 1)
                time.sleep(utils.rand_float(0.12, 0.18))
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            elif abs(d_y) <= 16:
                UpJump_Slow().execute()
            elif abs(d_y) <= 26:
                UpJump(pre_delay="0.1", jump='true').execute()
            else:
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            SkillCombination(direction='',jump='false',target_skills='skill_gritty|skill_arrow_stream').execute()
            utils.wait_for_is_standing(1300)
        else:
            press(jump, 1)
            time.sleep(utils.rand_float(0.1, 0.15))

    if direction == 'down':
        if abs(d_x) > settings.move_tolerance:
            return
        down_duration = 0.04
        if abs(d_y) > 27:
            down_duration = 0.6
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
                        press(jump)
                        key_up('left')
                    else:
                        key_down('right')
                        press(jump)
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
                        utils.wait_for_is_standing(1500)
                        UpJump(jump='true').execute()
                    else:
                        utils.wait_for_is_standing(1500)
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
    def __init__(self):
        super().__init__(locals())
          
    # bm is a 2 min dpm class, separate burst skills into two timers to elongate burst / mob more effectively
    def main(self):
        Skill_Phoenix().execute()
        Skill_Arachnid().execute()
        Buff_Rotation_1().execute()
        Buff_Rotation_2().execute()

class FlashJump(Command):
    """Performs a flash jump in the given direction."""
    _display_name = '二段跳'

    def __init__(self, direction="",jump='false',combo='False',triple_jump="False",fast_jump="false",reverse_triple=""):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.triple_jump = settings.validate_boolean(triple_jump)
        self.fast_jump = settings.validate_boolean(fast_jump)
        self.jump = settings.validate_boolean(jump)
        if self.triple_jump:
            settings.validate_required(self.direction) # direction is required since opposite direction is required for triple 

    def main(self):
        jump = config.bot.config['Jump']
        if not self.jump:
            utils.wait_for_is_standing()
            if not self.fast_jump:
                self.player_jump(direction=self.direction)
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
            self.direction = settings.validate_horizontal_arrows(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            # reverse_direction
            reverse_direction = ''
            if self.direction == 'left':
                reverse_direction = 'right'
            elif self.direction == 'right':
                reverse_direction = 'left'
            key_down(reverse_direction, down_time=0.10)
            press('r', 1) # Key.COVERING_FIRE doesnt work for some reason
            key_up(reverse_direction,up_time=0.01)
            time.sleep(utils.rand_float(0.5, 0.55))
        time.sleep(utils.rand_float(0.01, 0.02))

class UpJump(BaseSkill):
    """Performs a up jump."""
    _display_name = '上跳'
    _distance = 27
    key=Key.UP_JUMP
    delay=0.1
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

    # def __init__(self, pre_delay='0'):
    #     super().__init__(locals())
    #     self.pre_delay = float(pre_delay)
    # def main(self):
    #     # press(config.bot.config['Jump'])
    #     # press(self.key)
    #     self.jump = True
    #     super().main()

class UpJump_Slow(Command):
    """Performs a slow up jump."""

    def main(self):
        jump = jump = config.bot.config['Jump']
        press(jump)
        print('resting')
        time.sleep(utils.rand_float(0.3, 0.35))
        press(Key.UP_JUMP)
        
class Rope(BaseSkill):
    """Performs rope lift in the given direction."""
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
    _distance = 0
    key=Key.ARROW_STREAM
    delay=0.3 # with decent speed infusion, needs test
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.05

class Skill_Arrow_Blast(BaseSkill):
    _display_name = 'Arrow Blast/Platter'
    _distance = 0
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

class Skill_Arrow_Blast_Up(BaseSkill):
    _display_name = 'Arrow Blast/Platter Up'
    _distance = 0
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
    _distance = 0
    key=Key.ARROW_BLAST
    key_down_skill=True
    delay=0.5
    rep_interval=0.5
    skill_cool_down=5
    ground_skill=True
    buff_time=60
    combo_delay = 0.05

    def main(self):
        super().main()
        time.sleep(utils.rand_float(0.1, 0.15))
        press(config.bot.config['Interact'], 1, down_time=.03)
        key_up(Key.ARROW_BLAST)
        config.player_states['is_keydown_skill'] = False

class Skill_Hurricane(BaseSkill):
    _display_name = 'Hurricane'
    _distance = 0
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
    _distance = 0
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
    _distance = 0
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

class Skill_Blink_Shot(BaseSkill):
    _display_name = 'Blink Shot'
    _distance = 0
    key=Key.BLINK_SHOT
    delay=0.3
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=True
    combo_delay = 0.2

class Skill_Blink_Shot_Summon(BaseSkill):
    _display_name = 'Blink Shot Summon'
    _distance = 0
    key=Key.BLINK_SHOT_RESUMMON
    delay=0.3
    rep_interval=0.5
    skill_cool_down=1
    ground_skill=True
    buff_time=120
    combo_delay = 0.2

class Skill_Storm_Of_Arrows(BaseSkill):
    _display_name = 'Storm of Arrows'
    _distance = 0
    key=Key.STORM_OF_ARROWS
    delay=0.45
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=True
    buff_time=65
    combo_delay = 0.5

class Skill_Inhuman_Speed(BaseSkill):
    _display_name = 'Inhuman Speed'
    _distance = 0
    key=Key.INHUMAN_SPEED
    delay=0.45
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=True
    buff_time=30
    combo_delay = 0.5
    
class Skill_Quiver_Barrage(BaseSkill):
    _display_name = 'Quiver Barrage'
    _distance = 0
    key=Key.QUIVER_BARRAGE
    delay=0.45
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=True
    buff_time=40
    combo_delay = 0.5

class Skill_Vicious_Shot(BaseSkill):
    _display_name = 'Vicious Shot'
    _distance = 0
    key=Key.VICIOUS_SHOT
    delay=0.45
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=True
    buff_time=30
    combo_delay = 0.5

class Skill_Concentration(BaseSkill):
    _display_name = 'Concentration'
    _distance = 0
    key=Key.CONCENTRATION
    delay=0.45
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=True
    buff_time=40
    combo_delay = 0.5

class Skill_Arachnid(BaseSkill):
    _display_name = 'Arachnid'
    _distance = 0
    key=Key.ARACHNID
    delay=0.45
    rep_interval=0.5
    skill_cool_down=250
    ground_skill=True
    buff_time=50
    combo_delay = 0.5
    
class Skill_Phoenix(BaseSkill):
    _display_name = 'Phoenix'
    _distance = 0
    key=Key.PHOENIX
    delay=0.45
    rep_interval=0.5
    skill_cool_down=160
    ground_skill=True
    buff_time=0
    combo_delay = 0.5

class Skill_Maple_Goddess_Blessing(BaseSkill):
    _display_name = 'Maple Goddess Blessing'
    _distance = 0
    key=Key.MAPLE_GODDESS_BLESSING
    delay=0.45
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=True
    buff_time=60
    combo_delay = 0.5

class Skill_Fury_Of_The_Wild(BaseSkill):
    _display_name = 'Fury of the Wild'
    _distance = 0
    key=Key.FURY_OF_THE_WILD
    delay=0.45
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=True
    buff_time=40
    combo_delay = 0.5

class Buff_Rotation_1(BaseSkill):
    _display_name ='Buff First Rotation'
    key=Key.STORM_OF_ARROWS
    delay=0.45
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=False
    buff_time=60
    combo_delay = 0.5
    pre_delay = 0.5

    def main(self):
        self.active_if_not_in_skill_buff = 'buff_rotation_2' # only affects main super().main()
        self.active_if_skill_ready = 'skill_storm_of_arrows' # only affects main super().main()
        # if not utils.get_is_in_skill_buff('buff_rotation_2') and utils.get_if_skill_ready('skill_storm_of_arrows'):
        if super().main():
            Skill_Vicious_Shot().execute()
            Skill_Inhuman_Speed().execute()
            Skill_Concentration().execute()
            return True
        return False


class Buff_Rotation_2(BaseSkill):
    _display_name ='Buff Second Rotation'
    key=Key.QUIVER_BARRAGE
    delay=0.45
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=False
    buff_time=60
    combo_delay = 0.5
    pre_delay = 0.5

    def main(self):
        self.active_if_not_in_skill_buff = 'buff_rotation_1' # only affects main super().main()
        self.active_if_skill_ready = 'skill_quiver_barrage' # only affects main super().main()
        # if not utils.get_is_in_skill_buff('buff_rotation_1') and utils.get_if_skill_ready('skill_quiver_barrage'):
        if super().main():
            Skill_Maple_Goddess_Blessing().execute()
            Skill_Fury_Of_The_Wild().execute()
            return True
        return False

class GSkill_Damage (BaseSkill):
    _display_name ='Guild Skill Damage'
    key=Key.GUILD_DAMAGE
    delay=0.2
    rep_interval=0.2
    skill_cool_down=3600
    ground_skill=False
    buff_time=1800
    combo_delay = 0.2

    def main(self):
        self.active_if_not_in_skill_buff = 'gskill_crit_damage'
        self.active_if_skill_ready = 'gskill_damage'
        return super().main()

class GSkill_Crit_Damage (BaseSkill):
    _display_name ='Guild Skill Crit Damage'
    key=Key.GUILD_CRIT_DAMAGE
    delay=0.2
    rep_interval=0.2
    skill_cool_down=3600
    ground_skill=False
    buff_time=1800
    combo_delay = 0.2

    def main(self):
        self.active_if_not_in_skill_buff = 'gskill_damage'
        self.active_if_skill_ready = 'gskill_crit_damage'
        return super().main()
    
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
                UpJump(jump='true').execute()
                SkillCombination(direction='left',target_skills='skill_q|skill_0|skill_f|skill_d|skill_arrow_stream').execute()
            else:
                # left side
                move(20,bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                FlashJump(direction='right').execute()
                SkillCombination(direction='right',target_skills='skill_erda_fountain|skill_0|skill_arrow_stream').execute()
                UpJump(jump='true').execute()
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

# TODO: Add break if already outside from the voyage
class CommerciDolceAutoHunt(Command): 
    _display_name ='Commerci Dolce Auto Hunt'

    def __init__(self,duration='30'):
        super().__init__(locals())
        self.duration = int(duration)

    def main(self):
        # Changing into the voyage
        config.map_changing = True
        time.sleep(utils.rand_float(2.4,2.6)) # wait for map to load

        end_ok_template = cv2.imread('assets/commerci/commerci_end_ok.png', 0)
        trading_post_template = cv2.imread('assets/commerci/trading_post.png', 0)
        start_time = time.time()

        points = utils.multi_match(config.capture.frame, trading_post_template, threshold=0.95)
        if len(points) > 0:
            print("Trading post text found; did not depart on voyage correctly")
            return False
        
        config.map_changing = False
        jump = config.bot.config['Jump']
        while True:
            points = utils.multi_match(config.capture.frame, end_ok_template, threshold=0.95)

            if len(points) > 0:
                p = (points[0][0],points[0][1]-2)
                print("end")
                utils.game_window_click(p,delay=0.1)
                utils.game_window_click((700,100), button='right',delay=0.1)  
                time.sleep(0.15)
                break
            
            if time.time() - start_time >= self.duration:
                break
            # no minimap so manually flash jump
            key_down("right",down_time=0.05)
            press(jump,down_time=0.06,up_time=0.05)
        
            press(jump, 1,down_time=0.06,up_time=0.01)
            time.sleep(0.8)
            
            press(jump,down_time=0.06,up_time=0.05)
            press(jump, 1,down_time=0.06,up_time=0.01)
            key_up("right",up_time=0.01)
            time.sleep(0.6)
            Skill_Arrow_Blast_Summon(direction='left').execute()

            key_down("left",down_time=1.2)
            key_up("left")
            print("holding hurricane")
            Skill_Hurricane(skill_hold_duration=24.5).execute()
            Skill_Hurricane_Up().execute()
            print("releasing hurricane")
        
        config.map_changing = True
        time.sleep(2.5)
        config.map_changing = False
        return True

        