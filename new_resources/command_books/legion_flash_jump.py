from src.common import config, settings, utils
import time
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, GoToMap, ChangeChannel, Frenzy, Player_jump, WaitStanding, WealthPotion
from src.common.vkeys import press, key_down, key_up
import cv2

# List of key mappings
class Key:
    INTERACT = 'space'

    # Movement
    JUMP = 'alt'
    FLASH_JUMP = 'alt'
    ROPE = 'v'
    UP_JUMP = 'up+alt'
    
    MAPLE_WARRIOR = "6" 
    EPIC_ADVENTURE = "8"
    
    # Skills
    ATTACK = "shift"
    GRITTY = "q"

    # Buffs
    SKILL_DECENT_HOLY_SYMBOL = "f5"
    BUFF_1 = "9"
    BUFF_2 = "0"
    BUFF_3 = "-"
    BUFF_4 = "="

    MAPLE_GODDESS_BLESSING = ""
    GUILD_DAMAGE = 'insert'
    GUILD_CRIT_DAMAGE = 'pageup'
    ERDA_FOUNTAIN = "7"


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
            Skill_Attack(direction='').execute()
            WaitStanding(duration='1').execute()
        if abs(d_x) >= 16:
            if abs(d_x) >= 28:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_gritty|skill_attack').execute()
            else:
                if d_y == 0:
                    pass
                else:
                    Skill_Attack(direction='',jump='true').execute()
            time.sleep(utils.rand_float(0.04, 0.06))
            # if abs(d_x) <= 22:
            #     key_up(direction)
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
                SkillCombination(direction='',jump='false',target_skills='skill_gritty|skill_attack').execute()
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
            SkillCombination(direction='',jump='false',target_skills='skill_gritty|skill_attack').execute()
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
            SkillCombination(direction='',jump='false',target_skills='skill_gritty|skill_attack').execute()
                
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
    def __init__(self):
        super().__init__(locals())
          
    # bm is a 2 min dpm class, separate burst skills into two timers to elongate burst / mob more effectively
    def main(self):
        Skill_Maple_Warrior().execute()
        Skill_Decent_Holy_Symbol(pre_delay="0.5").execute()

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

class Skill_Attack(BaseSkill):
    _display_name = 'Basic Attack'
    _distance = 0
    key=Key.ATTACK
    delay=0.3 
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.05

class Skill_Attack_Slow(BaseSkill):
    _display_name = 'Basic Attack Slow AS7'
    _distance = 0
    key=Key.ATTACK
    delay=0.5
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.05

class Skill_Gritty(BaseSkill):
    _display_name = 'Gritty-like AOE jump skill'
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

class Skill_Maple_Warrior(BaseSkill):
    _display_name = 'Maple Warrior'
    _distance = 0
    key=Key.MAPLE_WARRIOR
    delay=0.3
    rep_interval=0.5
    skill_cool_down=600
    ground_skill=True
    buff_time=0
    combo_delay = 0.2

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

class Skill_Buff_1(BaseSkill):
    _display_name = 'Buff 1'
    _distance = 0
    key=Key.BUFF_1
    delay=0.3
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=True
    buff_time=0
    combo_delay = 0.2
    
class Skill_Buff_2(BaseSkill):
    _display_name = 'Buff 2'
    _distance = 0
    key=Key.BUFF_2
    delay=0.3
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=True
    buff_time=0
    combo_delay = 0.2

class Skill_Buff_3(BaseSkill):
    _display_name = 'Buff 3'
    _distance = 0
    key=Key.BUFF_3
    delay=0.3
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=True
    buff_time=0
    combo_delay = 0.2

class Skill_Buff_4(BaseSkill):
    _display_name = 'Buff 4'
    _distance = 0
    key=Key.BUFF_4
    delay=0.3
    rep_interval=0.5
    skill_cool_down=120
    ground_skill=True
    buff_time=0
    combo_delay = 0.2

class Skill_Maple_Goddess_Blessing(BaseSkill):
    _display_name = 'Maple Goddess Blessing'
    _distance = 0
    key=Key.MAPLE_GODDESS_BLESSING
    delay=0.3
    rep_interval=0.5
    skill_cool_down=180
    ground_skill=True
    buff_time=60
    combo_delay = 0.2

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
        SkillCombination(direction='',target_skills='skill_attack').execute()
        minimap = config.capture.minimap['minimap']
        height, width, _n = minimap.shape
        bottom_y = height - 30
        # bottom_y = config.player_pos[1]
        settings.platforms = 'b' + str(int(bottom_y))
        while True:
            if settings.auto_change_channel and config.should_solve_rune:
                Skill_Attack().execute()
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_Attack().execute()
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
                SkillCombination(direction='left',target_skills='skill_erda_fountain|skill_0|skill_attack').execute()
                UpJump(direction='left').execute()
                SkillCombination(direction='left',target_skills='skill_q|skill_0|skill_f|skill_d|skill_attack').execute()
            else:
                # left side
                move(20,bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                FlashJump(direction='right').execute()
                SkillCombination(direction='right',target_skills='skill_erda_fountain|skill_0|skill_attack').execute()
                UpJump(direction='right').execute()
                SkillCombination(direction='right',target_skills='skill_q|skill_0|skill_f|skill_d|skill_attack').execute()
            
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_Attack().execute()
                continue
            move(width//2,bottom_y).execute()
            UpJump(jump='true').execute()
            SkillCombination(direction='left',target_skills='skill_3|skill_2|skill_1|skill_del|skill_0|skill_attack').execute()
            toggle = not toggle

        if settings.home_scroll_key:
            config.map_changing = True
            press(settings.home_scroll_key)
            time.sleep(5)
            config.map_changing = False
        return
