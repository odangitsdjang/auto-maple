"""A collection of classes used to execute a Routine."""

import math
from pickle import FALSE
import time
from src.common import config, settings, utils, remote_info
from src.common.vkeys import click, key_down, key_up, press
from src.routine.maps import WorldMap
from src.modules.listener import Listener
import cv2
from random import randint

#################################
#       Routine Components      #
#################################
class Component:
    id = 'Routine Component'
    PRIMITIVES = {int, str, bool, float}

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('Component superclass __init__ only accepts 1 (optional) argument: LOCALS')
        if len(kwargs) != 0:
            raise TypeError('Component superclass __init__ does not accept any keyword arguments')
        if len(args) == 0:
            self.kwargs = {}
        elif type(args[0]) != dict:
            raise TypeError("Component superclass __init__ only accepts arguments of type 'dict'.")
        else:
            self.kwargs = args[0].copy()
            if '__class__' in self.kwargs:
                self.kwargs.pop('__class__')
            if 'self' in self.kwargs:
                self.kwargs.pop('self')
            # if not 'active_if_skill_ready' in self.kwargs:
            #     self.kwargs['active_if_skill_ready'] = ""

    @utils.run_if_enabled
    def execute(self):
        self.main()

    def main(self):
        pass

    def update(self, *args, **kwargs):
        """Updates this Component's constructor arguments with new arguments."""

        self.__class__(*args, **kwargs)     # Validate arguments before actually updating values
        self.__init__(*args, **kwargs)

    def info(self):
        """Returns a dictionary of useful information about this Component."""

        return {
            'name': self.__class__.__name__,
            'vars': self.kwargs.copy()
        }

    def encode(self):
        """Encodes an object using its ID and its __init__ arguments."""

        arr = [self.id]
        for key, value in self.kwargs.items():
            if key != 'id' and type(self.kwargs[key]) in Component.PRIMITIVES:
                arr.append(f'{key}={value}')
        return ', '.join(arr)

    def check_should_active(self):
        '''
            check should active command if pass all conditions
        '''
        if self.active_if_skill_ready:
            if not utils.get_if_skill_ready(self.active_if_skill_ready.lower()):
                return False
        if self.active_if_skill_cd:
            if utils.get_if_skill_ready(self.active_if_skill_cd.lower()):
                return False
        if self.active_if_in_skill_buff:
            if not utils.get_is_in_skill_buff(self.active_if_in_skill_buff.lower()):
                return False
        if self.active_if_not_in_skill_buff:
            if utils.get_is_in_skill_buff(self.active_if_not_in_skill_buff.lower()):
                return False
        return True

class Point(Component):
    """Represents a location in a user-defined routine."""

    id = '*'

    def __init__(self, x, y, frequency=1, skip='False', adjust='False'\
        , active_if_in_x_range='', active_if_in_y_range='', active_if_not_in_x_range='', active_if_not_in_y_range=''\
        , active_if_skill_ready = '', active_if_skill_cd='',active_if_in_skill_buff='',active_if_not_in_skill_buff=""):
        super().__init__(locals())
        self.x = float(x)
        self.y = float(y)
        self.location = (self.x, self.y)
        self.frequency = settings.validate_nonnegative_int(frequency)
        self.counter = int(settings.validate_boolean(skip))
        self.adjust = settings.validate_boolean(adjust)
        self.is_conditional_point = False
        if active_if_in_x_range != '':
            self.active_if_in_x_range = float(active_if_in_x_range)
            self.is_conditional_point = True
        if active_if_in_y_range != '':
            self.active_if_in_y_range = float(active_if_in_y_range)
            self.is_conditional_point = True
        if active_if_not_in_x_range != '':
            self.active_if_not_in_x_range = float(active_if_not_in_x_range)
            self.is_conditional_point = True
        if active_if_not_in_y_range != '':
            self.active_if_not_in_y_range = float(active_if_not_in_y_range)
            self.is_conditional_point = True
        self.active_if_skill_ready = active_if_skill_ready
        self.active_if_skill_cd = active_if_skill_cd
        if not hasattr(self, 'commands'):       # Updating Point should not clear commands
            self.commands = []
        self.active_if_in_skill_buff = active_if_in_skill_buff
        self.active_if_not_in_skill_buff = active_if_not_in_skill_buff

    def main(self):
        if not self.check_should_active():
            return
        if not self.check_is_player_in_xy_range():
            return
        if settings.auto_change_channel and \
            (config.should_change_channel or \
            config.should_solve_rune or config.enabled == False):
            return
        """Executes the set of actions associated with this Point."""
        if self.counter == 0:
            if self.location != (-1,-1) and not self.is_conditional_point:
                move = config.bot.command_book['move']
                move(*self.location).execute()
                if self.adjust:
                    adjust = config.bot.command_book['adjust']      # TODO: adjust using step('up')?
                    adjust(*self.location).execute()
            for command in self.commands:
                if settings.auto_change_channel and \
                    (config.should_change_channel or \
                    config.should_solve_rune or config.enabled == False):
                    break
                command.execute()
        time.sleep(utils.rand_float(0.02, 0.04))
        self._increment_counter()

    @utils.run_if_enabled
    def _increment_counter(self):
        """Increments this Point's counter, wrapping back to 0 at the upper bound."""

        self.counter = (self.counter + 1) % self.frequency

    def check_is_player_in_xy_range(self):
        if hasattr(self, 'active_if_in_x_range'):
            if abs(self.x - config.player_pos[0]) <= self.active_if_in_x_range:
                pass
            else:
                return False
        if hasattr(self, 'active_if_in_y_range'):
            if abs(self.y - config.player_pos[1]) <= self.active_if_in_y_range:
                pass
            else:
                return False

        if hasattr(self, 'active_if_not_in_x_range') or hasattr(self, 'active_if_not_in_y_range'):
            if hasattr(self, 'active_if_not_in_x_range'):
                if abs(self.x - config.player_pos[0]) >= self.active_if_not_in_x_range:
                    print("active_if_not_in_x_range >=",self.active_if_not_in_x_range)
                    # self.location = (-1,-1)
                    return True
                else:
                    pass
            if hasattr(self, 'active_if_not_in_y_range'):
                if abs(self.y - config.player_pos[1]) >= self.active_if_not_in_y_range:
                    print("active_if_not_in_y_range >=",self.active_if_not_in_y_range)
                    # self.location = (-1,-1)
                    return True
                else:
                    pass
            return False
        
        return True

    def info(self):
        curr = super().info()
        curr['vars'].pop('location', None)
        curr['vars']['commands'] = ', '.join([c.id for c in self.commands])
        return curr

    def __str__(self):
        return f'  * {self.location}'

class Label(Component):
    id = '@'

    def __init__(self, label):
        super().__init__(locals())
        self.label = str(label)
        if self.label in config.routine.labels:
            raise ValueError
        self.links = set()
        self.index = None

    def set_index(self, i):
        self.index = i

    def encode(self):
        return '\n' + super().encode()

    def info(self):
        curr = super().info()
        curr['vars']['index'] = self.index
        return curr

    def __delete__(self, instance):
        del self.links
        config.routine.labels.pop(self.label)

    def __str__(self):
        return f'{self.label}:'

class Jump(Component):
    """Jumps to the given Label."""

    id = '>'

    def __init__(self, label, frequency=1, skip='False'\
        ,frequency_to_loop='False', active_if_skill_ready = '', active_if_skill_cd='',active_if_in_skill_buff='',active_if_not_in_skill_buff=''):
        super().__init__(locals())
        self.label = str(label)
        self.frequency = settings.validate_nonnegative_int(frequency)
        self.counter = int(settings.validate_boolean(skip))
        self.link = None
        self.frequency_to_loop = settings.validate_boolean(frequency_to_loop)
        if self.frequency_to_loop:
            self.counter = 1
        self.active_if_skill_ready = active_if_skill_ready
        self.active_if_skill_cd = active_if_skill_cd
        self.active_if_in_skill_buff = active_if_in_skill_buff
        self.active_if_not_in_skill_buff = active_if_not_in_skill_buff

    def main(self):
        if self.link is None:
            print(f"\n[!] Label '{self.label}' does not exist.")
        else:
            if not self.check_should_active():
                return

            if self.counter == 0 and not self.frequency_to_loop:
                config.routine.index = self.link.index
            elif self.counter != 0 and self.frequency_to_loop:
                config.routine.index = self.link.index
            self._increment_counter()

    @utils.run_if_enabled
    def _increment_counter(self):
        self.counter = (self.counter + 1) % self.frequency

    def bind(self):
        """
        Binds this Goto to its corresponding Label. If the Label's index changes, this Goto
        instance will automatically be able to access the updated value.
        :return:    Whether the binding was successful
        """

        if self.label in config.routine.labels:
            self.link = config.routine.labels[self.label]
            self.link.links.add(self)
            return True
        return False

    def __delete__(self, instance):
        if self.link is not None:
            self.link.links.remove(self)

    def __str__(self):
        return f'  > {self.label}'

class Setting(Component):
    """Changes the value of the given setting variable."""

    id = '$'

    def __init__(self, target, value):
        super().__init__(locals())
        self.key = str(target)
        if self.key not in settings.SETTING_VALIDATORS:
            raise ValueError(f"Setting '{target}' does not exist")
        self.value = settings.SETTING_VALIDATORS[self.key](value)

    def main(self):
        setattr(settings, self.key, self.value)

    def __str__(self):
        return f'  $ {self.key} = {self.value}'

SYMBOLS = {
    '*': Point,
    '@': Label,
    '>': Jump,
    '$': Setting
}


#############################
#       Shared Commands     #
#############################
class Command(Component):
    id = 'Command Superclass'
    _display_name = ""
    _custom_id = ""
    skill_cool_down = 0
    last_cool_down = 0

    def __init__(self, *args):
        super().__init__(*args)
        self.id = self.__class__.__name__
        self._custom_id = self.id
        # self.set_my_last_cooldown(0)

    def __str__(self):
        variables = self.__dict__
        result = '    ' + self.id
        if len(variables) - 1 > 0:
            result += ':'
        for key, value in variables.items():
            if key != 'id':
                result += f'\n        {key}={value}'
        return result

    def player_jump(self,direction="",ground_skill=True):
        print("player jumping")
        if ground_skill:
            utils.wait_for_is_standing(1500)
        key_down(direction)
        press(config.bot.config['Jump'], 1,up_time=0.05)
        for i in range(100): # maximum time : 2s
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_JUMPING \
                or config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
                time.sleep(utils.rand_float(0.01, 0.03))
                break
            if i % 10 == 9:
                press(config.bot.config['Jump'], 1,up_time=0.05)
            else:
                time.sleep(0.02)
        key_up(direction)
            
    def check_should_active(self):
        '''
            check should active command if pass all conditions
        '''
        if hasattr(self,'active_if_skill_ready'):
            if self.active_if_skill_ready and not utils.get_if_skill_ready(self.active_if_skill_ready.lower()):
                return False
        if hasattr(self,'active_if_skill_cd'):
            if self.active_if_skill_cd and utils.get_if_skill_ready(self.active_if_skill_cd.lower()):
                return False
        if hasattr(self,'active_if_in_skill_buff'):
            if self.active_if_in_skill_buff and not utils.get_is_in_skill_buff(self.active_if_in_skill_buff.lower()):
                return False
        if hasattr(self,'active_if_not_in_skill_buff'):
            if self.active_if_not_in_skill_buff and utils.get_is_in_skill_buff(self.active_if_not_in_skill_buff.lower()):
                return False
        return True

    def get_my_last_cooldown(self,id=''):
        if id == '':
            id = self._custom_id
        if id in config.skill_cd_timer:
            return config.skill_cd_timer[id]
        else: 
            return 0

    def set_my_last_cooldown(self,last_time=time.time()):
        config.skill_cd_timer[self._custom_id] = last_time
        if self.skill_cool_down != 0:
            config.is_skill_ready_collector[self._custom_id] = False

    @classmethod
    def set_is_skill_ready(cls,is_ready):
        config.is_skill_ready_collector[cls.__name__] = is_ready

    @classmethod
    def get_should_active(cls):
        if hasattr(cls,'active_if_skill_ready'):
            if cls.active_if_skill_ready and not utils.get_if_skill_ready(cls.active_if_skill_ready.lower()):
                return False
        if hasattr(cls,'active_if_skill_cd'):
            if cls.active_if_skill_cd and utils.get_if_skill_ready(cls.active_if_skill_cd.lower()):
                return False
        if hasattr(cls,'active_if_in_skill_buff'):
            if cls.active_if_in_skill_buff and not utils.get_is_in_skill_buff(cls.active_if_in_skill_buff.lower()):
                return False
        if hasattr(cls,'active_if_not_in_skill_buff'):
            if cls.active_if_not_in_skill_buff and utils.get_is_in_skill_buff(cls.active_if_not_in_skill_buff.lower()):
                return False
        return True

    @classmethod
    def get_is_skill_ready(cls,bias=0):
        skill_cool_down =  cls.skill_cool_down
        if skill_cool_down > 5 and settings.cd_value != '':
            cd_percent_and_sec = settings.cd_value.split('%')
            skill_cool_down = skill_cool_down * (1-0.01*float(cd_percent_and_sec[0]))
            if len(cd_percent_and_sec) > 1 and cd_percent_and_sec[1] != '':
                cd_minus_sec = abs(int(cd_percent_and_sec[1]))
                for i in range(7):
                    if cd_minus_sec == 0:
                        break
                    if skill_cool_down <= 10:
                        skill_cool_down = skill_cool_down * (1 - (cd_minus_sec * 0.05))
                        break
                    else:
                        skill_cool_down = skill_cool_down - 1
                        cd_minus_sec = cd_minus_sec - 1
            if skill_cool_down < 5:
                skill_cool_down = 5
            
        if not cls.__name__ in config.is_skill_ready_collector:
            config.is_skill_ready_collector[cls.__name__] = False

        if not cls.__name__ in config.skill_cd_timer:
            config.skill_cd_timer[cls.__name__] = 0

        if config.is_skill_ready_collector[cls.__name__] == True:
            return True

        last_cool_down = cls.get_my_last_cooldown(cls,cls.__name__)
        now = time.time()
        if now - last_cool_down > skill_cool_down:
            config.is_skill_ready_collector[cls.__name__] = True
            return True
        else:
            if (now + bias) - last_cool_down > skill_cool_down: 
                return True
            config.is_skill_ready_collector[cls.__name__] = False
            return False

    def check_is_skill_ready(self,bias=0):
        if config.is_skill_ready_collector[self._custom_id] == True:
            return True

        last_cool_down = self.get_my_last_cooldown(self._custom_id)
        now = time.time()
        if now - last_cool_down > self.skill_cool_down:
            config.is_skill_ready_collector[self._custom_id] = True
            # print(self._custom_id,self._display_name," is ready to use")
            return True
        else:
            if (now + bias) - last_cool_down > self.skill_cool_down: 
                return True
            config.is_skill_ready_collector[self._custom_id] = False
            return False

class Move(Command):
    """Moves to a given position using the shortest path based on the current Layout."""

    def __init__(self, x, y, move_tolerance='', max_steps=15):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)
        self.prev_direction = ''
        if move_tolerance != '':
            self.move_tolerance = float(move_tolerance)
        else:
            self.move_tolerance = settings.move_tolerance

    def _new_direction(self, new):
        key_down(new,down_time=0.04)
        if self.prev_direction and self.prev_direction != new:
            key_up(self.prev_direction,up_time=0.04)
        self.prev_direction = new

    def _new_move_method(self,target):
        pass

    def main(self):
        counter = self.max_steps
        path = config.layout.shortest_path(config.player_pos, self.target)
        stuck_count = 0
        for i, point in enumerate(path):
            toggle = True
            self.prev_direction = ''
            # local_error = utils.distance(config.player_pos, point)
            # global_error = utils.distance(config.player_pos, self.target)
            d_x = point[0] - config.player_pos[0]
            d_y = point[1] - config.player_pos[1]
            
            # prevent change map error
            if config.player_pos[0] == 0 and config.player_pos[1] == 0:
                step("left", (-30,30))
            while config.enabled and counter > 0 and \
                    (abs(d_x) > self.move_tolerance or \
                    abs(d_y) > self.move_tolerance / 2):
                # stop if other move trigger
                if (settings.auto_change_channel and (config.should_change_channel)) or config.enabled == False:
                    self._new_direction('')
                    break
                last_player_pos = config.player_pos
                if toggle:
                    d_x = point[0] - config.player_pos[0]
                    d_y = point[1] - config.player_pos[1]
                    if abs(d_x) > self.move_tolerance :
                        if d_x < 0:
                            key = 'left'
                        else:
                            key = 'right'
                        self._new_direction(key)
                        step(key, point)
                        if settings.record_layout:
                            config.layout.add(*config.player_pos)
                        counter -= 1
                        time.sleep(0.02)
                        if last_player_pos[0] == config.player_pos[0] and last_player_pos[1] == config.player_pos[1]:
                            if stuck_count >= 2:
                                config.player_states['is_stuck'] = True
                            else:
                                stuck_count = stuck_count + 1
                        else:
                            stuck_count = 0
                            config.player_states['is_stuck'] = False
                    else:
                        # pass
                        if d_x < 0:
                            key = 'left'
                        else:
                            key = 'right'
                        self._new_direction(key)
                        time.sleep(0.1*abs(d_x)/self.move_tolerance)
                        self._new_direction('')
                else:
                    d_x = point[0] - config.player_pos[0]
                    d_y = point[1] - config.player_pos[1]
                    # if abs(d_y) > self.move_tolerance / 2:
                    if abs(d_y) >= 2:
                        if d_y < 0:
                            key = 'up' # if direction=up dont press up to avoid transporter
                            # if abs(d_x) <= self.move_tolerance: # key up horizontal arrow if inside move_tolerance 
                            self._new_direction('')
                        else:
                            key = 'down'
                            # if not config.player_states['in_bottom_platform']:
                            #     self._new_direction(key)
                            # if abs(d_x) <= self.move_tolerance: # key up horizontal arrow if inside move_tolerance 
                            self._new_direction('')
                        step(key, point)
                        if settings.record_layout:
                            config.layout.add(*config.player_pos)
                        counter -= 1
                        time.sleep(0.02)
                        if last_player_pos[0] == config.player_pos[0] and last_player_pos[1] == config.player_pos[1]:
                            if stuck_count >= 2:
                                config.player_states['is_stuck'] = True
                            else:
                                stuck_count = stuck_count + 1
                        else:
                            stuck_count = 0
                            config.player_states['is_stuck'] = False
                # local_error = utils.distance(config.player_pos, point)
                # global_error = utils.distance(config.player_pos, self.target)
                toggle = not toggle
            if self.prev_direction:
                key_up(self.prev_direction)

class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

class Player_jump(Command):
    def __init__(self, direction='',ground_skill="True"):
        super().__init__(locals())
        self.direction = direction
        self.ground_skill = settings.validate_boolean(ground_skill)

    def main(self):
        print(f"Player_jump with direction{self.direction} groundSkill {self.ground_skill}")
        self.player_jump(direction=self.direction, ground_skill=self.ground_skill)
        return super().main()

def step(direction, target):
    """
    The default 'step' function. If not overridden, immediately stops the bot.
    :param direction:   The direction in which to move.
    :param target:      The target location to step towards.
    :return:            None
    """

    print("\n[!] Function 'step' not implemented in current command book, aborting process.")
    config.enabled = False

class Wait(Command):
    """Waits for a set amount of time."""

    def __init__(self, duration):
        super().__init__(locals())
        self.duration = float(duration)

    def main(self):
        time.sleep(utils.rand_float(self.duration*0.95, self.duration*1.05))
        
class Walk(Command):
    """Walks in the given direction for a set amount of time."""

    def __init__(self, direction, duration):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.duration = float(duration)

    def main(self):
        key_down(self.direction)
        time.sleep(utils.rand_float(self.duration*0.95, self.duration*1.1))
        key_up(self.direction)

class Fall(Command):
    """
    Performs a down-jump and then free-falls until the player exceeds a given distance
    from their starting position.
    """

    def __init__(self, direction='', duration='0.1'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.duration = float(duration)

    def main(self):
        WaitStanding(duration='2').execute()
        time.sleep(utils.rand_float(0.02, 0.05))
        fall_successful = False
        for i in range(3):
            cur_y = config.player_pos[1]
            key_down('down',down_time=0.04)
            press(config.bot.config['Jump'], 1, down_time=0.05,up_time=0.05)
            key_up('down',up_time=0.08)
            cur_y2 = config.player_pos[1]
            for j in range(50):
                if config.player_pos[1]-cur_y2 >= 1:
                    print("fall successful!")
                    fall_successful = True
                    break
                time.sleep(0.01)
            if not fall_successful:
                if cur_y != cur_y2:
                    print("in ladder")
                    press("left+"+config.bot.config['Jump'], 1, down_time=0.08,up_time=0.05)
                else:
                    time.sleep(utils.rand_float(0.1, 0.15))
                    continue
            time.sleep(utils.rand_float(self.duration*1, self.duration*1.05))
            if self.direction == '':
                pass
            elif self.direction != '':
                key_down(self.direction)
                press(config.bot.config['Jump'], 2, down_time=0.05,up_time=0.05)
                key_up(self.direction,up_time=0.02)
            # time.sleep(utils.rand_float(0.15, 0.17))
            if config.player_pos[1]-cur_y >= 1:
                break
        
class Buff(Command):
    """Undefined 'buff' command for the default command book."""

    def main(self):
        print("\n[!] 'Buff' command not implemented in current command book, aborting process.")
        config.enabled = False

class CustomKey(Command):
    """users define their custom function of target key """
    _display_name = '自定義按鍵'
    # skill_cool_down = 0

    def __init__(self,name='',key='', direction='',jump='false',delay='0.5',rep='1',rep_interval='0.3',rep_interval_increase='0',duration='0',cool_down='0',ground_skill='true',buff_time='',active_if_skill_ready='',active_if_skill_cd='',active_if_in_skill_buff='',active_if_not_in_skill_buff=''):
        super().__init__(locals())
        self._display_name = name
        self.key = key
        self._custom_id = 'custom_key_' + key
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.delay = float(delay)
        self.rep = settings.validate_nonnegative_int(rep)
        self.rep_interval = float(rep_interval)
        self.rep_interval_increase = float(rep_interval_increase)
        self.duration = float(duration)
        self.skill_cool_down = float(cool_down)
        self.ground_skill = settings.validate_boolean(ground_skill)
        config.is_skill_ready_collector[self._custom_id] = True
        self.buff_time = buff_time
        self.active_if_skill_ready = active_if_skill_ready
        self.active_if_skill_cd = active_if_skill_cd
        self.active_if_in_skill_buff = active_if_in_skill_buff
        self.active_if_not_in_skill_buff = active_if_not_in_skill_buff

    def main(self):
        if not self.check_should_active():
            return
        if self.skill_cool_down == 0 or self.check_is_skill_ready():
            if self.ground_skill:
                utils.wait_for_is_standing(1000)

            if self.jump:
                self.player_jump(direction=self.direction,ground_skill=self.ground_skill)
                # time.sleep(utils.rand_float(0.02, 0.05))
            else:
                key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.07))
            for i in range(self.rep):
                key_down(self.key,down_time=0.07)
                if self.duration != 0:
                    time.sleep(utils.rand_float(self.duration*0.9, self.duration*1.1))
                key_up(self.key,up_time=0.05)
                if i != (self.rep-1):
                    ret_interval = self.rep_interval+self.rep_interval_increase*i
                    time.sleep(utils.rand_float(ret_interval*0.92, ret_interval*1.08))
            key_up(self.direction,up_time=0.01)
            # if self.skill_cool_down != 0:
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(self.delay*0.8, self.delay*1.2))

class WaitStanding(Command):
    """wait user standing """
    _display_name = ""
    def __init__(self,duration='0'):
        super().__init__(locals())
        self.duration = float(duration)

    def main(self):
        utils.wait_for_is_standing(self.duration*1000)

class BaseSkill(Command):
    """pre define base skill class """
    _display_name = ""
    key=''
    delay=0.5
    rep_interval=0.3
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.1
    rep_interval_increase = 0
    fast_rep=False
    fast_direction=True
    float_in_air=False
    recharge_interval=0
    max_maintained=0
    key_down_skill=False
    key_up_skill=False

    def __init__(self, direction='',jump='false',rep='1',pre_delay='0',duration='0',\
            combo='false',wait_until_ready='false',direction_after_skill='false',\
            active_if_skill_ready='',active_if_skill_cd='',active_if_in_skill_buff='',active_if_not_in_skill_buff='',\
            key_down_direction='false', skill_hold_duration='0'\
            ):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.rep = settings.validate_nonnegative_int(rep)
        self.duration = float(duration)
        self.pre_delay = float(pre_delay)
        self.skill_hold_duration = float(skill_hold_duration)
        if not self._custom_id in config.is_skill_ready_collector:
            config.is_skill_ready_collector[self._custom_id] = True
            config.skill_cd_timer[self._custom_id] = 0
        self.combo = settings.validate_boolean(combo)
        self.wait_until_ready = settings.validate_boolean(wait_until_ready)
        self.direction_after_skill = settings.validate_boolean(direction_after_skill)
        self.key_down_direction = settings.validate_boolean(key_down_direction)
        if self.skill_cool_down > 5 and settings.cd_value != '':
            cd_percent_and_sec = settings.cd_value.split('%')
            self.skill_cool_down = self.skill_cool_down * (1-0.01*float(cd_percent_and_sec[0]))
            if len(cd_percent_and_sec) > 1 and cd_percent_and_sec[1] != '':
                cd_minus_sec = abs(int(cd_percent_and_sec[1]))
                for i in range(7):
                    if cd_minus_sec == 0:
                        break
                    if self.skill_cool_down <= 10:
                        self.skill_cool_down = self.skill_cool_down * (1 - (cd_minus_sec * 0.05))
                        break
                    else:
                        self.skill_cool_down = self.skill_cool_down - 1
                        cd_minus_sec = cd_minus_sec - 1
            if self.skill_cool_down < 5:
                self.skill_cool_down = 5
            print(self._custom_id," : ",self.skill_cool_down,'s')
                        
        if active_if_skill_ready:
            self.active_if_skill_ready = active_if_skill_ready
        if active_if_skill_cd:
            self.active_if_skill_cd = active_if_skill_cd
        if active_if_in_skill_buff:
            self.active_if_in_skill_buff = active_if_in_skill_buff
        if active_if_not_in_skill_buff:
            self.active_if_not_in_skill_buff = active_if_not_in_skill_buff

    def check_maintained(self):
        if self.max_maintained > 0:
            if not self._custom_id in config.skill_cd_timer:
                config.skill_cd_timer[self._custom_id] = 0
                config.is_skill_ready_collector[self._custom_id] = True
            if not self._custom_id in config.skill_maintained_count:
                config.skill_maintained_count[self._custom_id] = 0
            passed_time = time.time() - config.skill_cd_timer[self._custom_id] 
            temp_maintained = config.skill_maintained_count[self._custom_id] + float(passed_time / self.recharge_interval)
            return temp_maintained
        else:
            return 1

    def consume_maintained(self):
        if self.max_maintained > 0:
            passed_time = time.time() - config.skill_cd_timer[self._custom_id] 
            config.skill_maintained_count[self._custom_id] = config.skill_maintained_count[self._custom_id] + float(passed_time / self.recharge_interval)
            if config.skill_maintained_count[self._custom_id] > self.max_maintained:
                config.skill_maintained_count[self._custom_id] = self.max_maintained
            config.skill_maintained_count[self._custom_id] = config.skill_maintained_count[self._custom_id] - 1
            print(self._custom_id,' skill_maintained_count : ', config.skill_maintained_count[self._custom_id])

    def main(self):
        if not self.check_should_active() and not self.key_up_skill:
            return False
        if self.wait_until_ready:
            if self.max_maintained > 0:
                temp_maintained = self.check_maintained()
                if temp_maintained < 1:
                    time.sleep(0.2+self.recharge_interval*(1-temp_maintained))
            cd_passed = time.time() - float(self.get_my_last_cooldown())
            if cd_passed < self.skill_cool_down:
                wait_time = self.skill_cool_down - cd_passed + 0.2
                print('wait_time : ',wait_time)
                time.sleep(wait_time)
        if self.key_up_skill or (self.check_maintained() >= 1 and (self.skill_cool_down == 0 or self.check_is_skill_ready())):
            if self.ground_skill:
                utils.wait_for_is_standing(2000)
            if self.pre_delay > 0:
                time.sleep(utils.rand_float(self.pre_delay*0.95, self.pre_delay*1.05))

            if not self.direction_after_skill:
                if self.jump and not self.ground_skill:
                    self.player_jump(direction=self.direction, ground_skill=self.ground_skill)
                    time.sleep(utils.rand_float(0.02, 0.04))
                else:
                    if not self.key_up_skill:
                        key_down(self.direction,down_time=0.05)
                        time.sleep(utils.rand_float(0.02, 0.03))
            else:
                if self.jump and not self.ground_skill:
                    self.player_jump(direction=self.direction, ground_skill=self.ground_skill)
                    time.sleep(utils.rand_float(0.02, 0.04))

            for i in range(self.rep):
                if not self.key_up_skill:
                    if self.fast_rep:
                        key_down(self.key,down_time=0.045)
                    else:
                        key_down(self.key,down_time=0.07)
                if self.direction_after_skill:
                    if self.fast_direction:
                        key_down(self.direction,down_time=0.06)
                if self.duration != 0:
                    time.sleep(utils.rand_float(self.duration*0.97, self.duration*1.03))
                if i == (self.rep-1):
                    if not self.key_down_direction and self.fast_direction:
                        key_up(self.direction,up_time=0.05)
                if not self.key_down_skill:
                    key_up(self.key,up_time=0.02)
                if self.direction_after_skill:
                    if not self.fast_direction:
                        time.sleep(utils.rand_float(0.25, 0.3))
                    press(self.direction,down_time=0.05)
                if i != (self.rep-1):
                    rep_interval = self.rep_interval+self.rep_interval_increase*i
                    time.sleep(utils.rand_float(rep_interval*0.95, rep_interval*1.05))
            # if self.skill_cool_down != 0:
            if self.key_down_skill and self.skill_hold_duration:
                time.sleep(utils.rand_float(self.skill_hold_duration*0.99, self.skill_hold_duration*1.02)) 
            self.consume_maintained()
            self.set_my_last_cooldown(time.time())
            if self.combo:
                time.sleep(utils.rand_float(self.combo_delay*0.97, self.combo_delay*1.1))
            else:
                time.sleep(utils.rand_float(self.delay*0.97, self.delay*1.1))
            # if self.key_up_skill:
            config.player_states['is_keydown_skill'] = False
            if self.float_in_air:
                config.player_states['is_standing'] = False
                config.player_states['movement_state'] = config.MOVEMENT_STATE_FALLING
                config.capture.check_is_standing_count = -7
            return True
        else:
            if self.key_down_skill:
                config.player_states['is_keydown_skill'] = True
            return False
            
class Frenzy(BaseSkill):
    _display_name ='輪迴'
    key="f12"
    delay=0.8
    rep_interval=0.2
    skill_cool_down=60
    ground_skill=True
    buff_time=600
    combo_delay = 0.2

    def main(self):
        if settings.frenzy_key:
            self.key = settings.frenzy_key
        return super().main()

class WealthPotion (BaseSkill):
    _display_name ='財物密藥'
    key="f10"
    delay=0.2
    rep_interval=0.2
    skill_cool_down=7260
    ground_skill=False
    buff_time=7260
    combo_delay = 0.2

    def main(self):
        self.active_if_not_in_skill_buff = 'wealthpotion'
        return super().main()

class SkillCombination(Command):
    """auto select skill in this combination"""
    _display_name = '技能組合'

    def __init__(self, direction='',jump='false',target_skills='',combo='false',wait='0',active_if_skill_ready='',active_if_skill_cd='',active_if_in_skill_buff='',active_if_not_in_skill_buff=''):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = jump
        self.target_skills = target_skills
        self.combo = combo
        self.wait = float(wait)
        self.active_if_skill_ready = active_if_skill_ready
        self.active_if_skill_cd = active_if_skill_cd
        self.active_if_in_skill_buff = active_if_in_skill_buff
        self.active_if_not_in_skill_buff = active_if_not_in_skill_buff
        
    def main(self):
        if not self.check_should_active():
            return
        skills_array = self.target_skills.split("|")
        for skill in skills_array:
            skill = skill.lower()
            if "+" in skill:
                combo_skills = skill.split('+')
                s = config.bot.command_book[combo_skills[0]]
                if not s.get_is_skill_ready() or not s.get_should_active():
                    continue
                if self.wait > 0:
                    time.sleep(utils.rand_float(self.wait,self.wait*1.1))
                s(direction=self.direction,jump=self.jump,combo="true").execute()
                s = config.bot.command_book[combo_skills[1]]
                s(direction=self.direction,jump="false",combo=self.combo).execute()
                break
            else:
                s = config.bot.command_book[skill]
                if not s.get_is_skill_ready() or not s.get_should_active():
                    continue
                else:
                    if self.wait > 0:
                        time.sleep(utils.rand_float(self.wait,self.wait*1.1))
                    s(direction=self.direction,jump=self.jump,combo=self.combo).execute()
                    break

class GoToMap(Command):
    """ go to target map """
    _display_name = 'Map Change'
    # skill_cool_down = 0

    def __init__(self,target_map=''):
        super().__init__(locals())
        self.target_map = target_map

    def main(self):
        if settings.id:
            remote_info.get_remote_async(settings.id)
        # wm = WorldMap()
        # if wm.check_if_in_correct_map(self.target_map):
        #     return
        press(config.world_map_button)
        time.sleep(utils.rand_float(2*0.9, 2*1.2))
        wm = WorldMap()
        config.map_changing = True
        if self.target_map in wm.maps_info:
            target_map_info = wm.maps_info[self.target_map]
            utils.game_window_click(wm.WORLD_MENU)
            utils.game_window_click(target_map_info['world_selection_point'])
            utils.game_window_click(wm.AREA_MENU)
            utils.game_window_click(target_map_info['area_selection_point'])
            time.sleep(utils.rand_float(0.3*0.8, 0.3*1.2))
            utils.game_window_click(target_map_info['point'],click_time=2)
        else:
            if wm.search_map(self.target_map):
                pass

        press('enter')
        config.should_change_channel = False
        config.bot.map_rune_active = False
        config.latest_change_channel_or_map = time.time()
        time.sleep(2.5)
        # for _ in range(10):
        #     if wm.check_if_in_correct_map(self.target_map):
        #         break
        #     time.sleep(0.3)
        Listener.recalibrate_minimap()
        if settings.id:
            # if len(config.my_remote_info) == 0:
            remote_info.wait_for_get(settings.id)
            config.remote_infos[str(settings.id)][1] = self.target_map
            remote_info.update_remote_async(settings.id,config.remote_infos[str(settings.id)])
            time.sleep(1)        
        else:
            time.sleep(2.2)
        config.map_changing = False

# TODO
# In order to save operation, have the desired target map saved as "favorite" in the guide menu
class GoToGuideMap(Command):
    """ go to target map via guide """
    _display_name = 'Map Change via Guide'
    def __init__(self,target_map=''):
        super().__init__(locals())
        self.target_map = target_map

    def main(self):
        return


class ChangeChannel(Command):
    """ go to target channel """
    _display_name = '換頻'
    # skill_cool_down = 0

    def __init__(self,target_channel='',max_rand='0',delay='5'):
        super().__init__(locals())
        self.delay = float(delay)
        self.max_rand = int(max_rand)
        if int(max_rand) > 0:
            self.max_rand = int(max_rand)
            self.next_line = False
        elif target_channel == '':
            self.next_line = True
            self.target_channel = int(config.current_channel) + 1
        else:
            self.next_line = False
            self.target_channel = int(target_channel)

    def main(self):
        if settings.id:
            remote_info.get_remote_async(settings.id)
        time.sleep(self.delay)
        if int(self.max_rand) > 0:
            while True:
                self.target_channel = randint(1,int(self.max_rand))
                if self.target_channel != config.current_channel:
                    break
        for _ in range(8):
            press('esc') # menu key
            press('enter',n=2) # select channel change key
            time.sleep(utils.rand_float(0.3*0.8, 0.3*1.2))
            frame = config.capture.frame
            title_template = cv2.imread('assets/channel_change.png', 0)
            ok_template = cv2.imread('assets/ok1.png', 0)
            points = utils.multi_match(frame, title_template, threshold=0.9)
            if len(points) > 0:
                config.map_changing = True
                p = (points[0][0],points[0][1])
                base_point = (-142,51)
                block_size = (70,20)
                if self.next_line == False:
                    target_point = (p[0]+base_point[0]+block_size[0] * ((self.target_channel - 1) % 5),p[1]+base_point[1]+block_size[1] * ((self.target_channel - 1) // 5))
                    utils.game_window_click(target_point,click_time=2)
                    print("change to channel: ",self.target_channel)
                else:
                    press('right',up_time=0.2) 
                    press('enter')
                time.sleep(1)
                # check if menu is opened
                change_channel_failed = False
                for iii in range(2):
                    frame = config.capture.frame
                    check_points = utils.multi_match(frame, title_template, threshold=0.9)
                    if len(check_points) > 0:
                        press('esc') 
                        change_channel_failed = True
                        time.sleep(0.5)
                    frame = config.capture.frame
                    check_points = utils.single_match_with_threshold(frame, ok_template, threshold=0.9)
                    if len(check_points) > 0:
                        press('esc') 
                        change_channel_failed = True
                        time.sleep(0.5)
                    time.sleep(0.5)
                if change_channel_failed == True:
                    ChangeChannel(max_rand=30,delay='1').execute()
                    break
                # Listener.recalibrate_minimap()
                config.current_channel = self.target_channel
                config.latest_change_channel_or_map = time.time()
                config.should_change_channel = False
                config.bot.map_rune_active = False
                time.sleep(3)
                config.map_changing = False
                if config.should_change_channel and settings.auto_change_channel:
                    ChangeChannel(max_rand=30,delay='1').execute()
                    break
                if settings.id:
                    # if len(config.my_remote_info) == 0:
                    remote_info.wait_for_get(settings.id)
                    config.remote_infos[str(settings.id)][2] = self.target_channel
                    remote_info.update_remote_async(settings.id,config.remote_infos[str(settings.id)])
                break

class EndScript(Command):
    """ End Script at given military time: e.g. '19:20' (7:20 PM) """
    _display_name = 'End Script'

    def __init__(self,should_back_home='true',home_scroll_key='f9',end_time=''):
        super().__init__(locals())
        self.should_back_home = settings.validate_boolean(should_back_home)
        self.home_scroll_key = home_scroll_key
        self.end_time = end_time

    def main(self):
        if self.end_time != '':
            hour_min = self.end_time.split(':')
            cur_time = time.localtime()   
            if int(cur_time.tm_hour) == int(hour_min[0]) and (int(cur_time.tm_min) - int(hour_min[1])) >= 0 and (int(cur_time.tm_min) - int(hour_min[1])) <= 3:
                pass
            else:
                return
                
        time.sleep(1)
        if self.should_back_home:
            if self.home_scroll_key:
                press(self.home_scroll_key)
            elif settings.home_scroll_key:
                press(settings.home_scroll_key)
            else:
                pass
        if config.enabled:
            Listener.toggle_enabled()

class DailyCombination(Command):
    """ go to target channel """
    _display_name = '每日任務組合包'

    def __init__(self,maps='',remote='false'):
        super().__init__(locals())
        self.maps = maps
        self.remote = settings.validate_boolean(remote)

    def main(self):
        if self.remote:
            info = remote_info.get_user_info(settings.id) 
            # daily column
            self.maps = info[4]
        map_list = self.maps.split('|')
        auto_hunting = config.bot.command_book['autohunting']
        for t_map in map_list:
            auto_hunting('300',t_map).execute()
            if not config.enabled:
                break

class FollowPartner(Command):
    """ follow partner's map and channel """
    _display_name = '跟隨夥伴'

    def __init__(self,partner='',from_remote='true'):
        super().__init__(locals())
        self.partner = partner
        self.from_remote = settings.validate_boolean(from_remote)

    def main(self):
        if settings.id:
            remote_info.get_remote_async(settings.id)
            my_info = remote_info.wait_for_get(settings.id)
            my_map = my_info[1]
            my_channel = int(my_info[2])
            if self.from_remote:
                self.partner = my_info[5]
        else:
            my_map = ''
            my_channel = 0
        if not self.partner:
            return
        partner_info = remote_info.get_user_info(self.partner) 
        partner_map = partner_info[1]
        partner_channel = int(partner_info[2])
        if my_channel != partner_channel:
            ChangeChannel(target_channel=str(partner_channel)).execute()
        if my_map != partner_map:
            GoToMap(partner_map).execute()

class StoryAssistant(Command):
    """ story assistant """
    _display_name = '主線助手'

    def __init__(self):
        super().__init__(locals())
        self.BULB_TEMPLATE = cv2.imread('assets/bulb.png', 0)
        self.COMPLETE_TEMPLATE = cv2.imread('assets/story_complete.png', 0)
        self.NEXT_TEMPLATE = cv2.imread('assets/story_next.png', 0)
        self.ACCEPT_TEMPLATE = cv2.imread('assets/story_accept.png', 0)
        self.CONVERSATION_TEMPLATE = cv2.imread('assets/stop_conversation.jpg', 0)
        self.HPMP_TEMPLATE = cv2.imread('assets/hpmp.png', 0)

    def main(self):
        settings.story_mode = True
        config.map_changing = True
        find_conversation = False

        # find NEXT_TEMPLATE
        points = utils.multi_match(config.capture.frame, self.NEXT_TEMPLATE, threshold=0.9)
        if len(points) > 0:
            print("find NEXT_TEMPLATE")
            press('space')
            find_conversation = True
        
        # find ACCEPT_TEMPLATE
        points = utils.multi_match(config.capture.frame, self.ACCEPT_TEMPLATE, threshold=0.9)
        if len(points) > 0:
            print("find ACCEPT_TEMPLATE")
            press('enter')
            find_conversation = True

        # find CONVERSATION_TEMPLATE
        points = utils.multi_match(config.capture.frame, self.CONVERSATION_TEMPLATE, threshold=0.9)
        if len(points) > 0:
            print("find CONVERSATION_TEMPLATE")
            time.sleep(0.1)
            press('space')
            find_conversation = True

        # find HPMP_TEMPLATE
        points = utils.multi_match(config.capture.frame, self.HPMP_TEMPLATE, threshold=0.9)
        if len(points) == 0:
            print("no HPMP_TEMPLATE")
            press('space')

        if not find_conversation:
            # find COMPLETE_TEMPLATE
            points = utils.multi_match(config.capture.frame, self.COMPLETE_TEMPLATE, threshold=0.9)
            if len(points) > 0:
                p = (points[0][0],points[0][1])
                print("find COMPLETE_TEMPLATE")
                utils.game_window_click(p,delay=0.1)
                time.sleep(0.3)
                utils.game_window_click((700,100), button='right',delay=0.1)

            # # find bulb
            # points = utils.multi_match(config.capture.frame, self.BULB_TEMPLATE, threshold=0.9)
            # if len(points) > 0:
            #     p = (points[0][0],points[0][1])
            #     print("find bulb")
            #     utils.game_window_click(p)
            #     time.sleep(0.3)
            #     utils.game_window_click((700,100), button='right')

        time.sleep(utils.rand_float(0.2, 0.4))

### Flow:
### a. Start at San Commerci Trading Post map
### b. Click on Maestra Flametta NPC
### c_1. If there is a quest with Maestra, choice between quest / "Start Trade"
### c_2. No quest - no dialogue
### d . Click on "Enter Trade" or Interact button
### e_1. did not claim reward before ->   
###     click next -> click Yes -> click next (or Interact -> Y -> Interact)
### e_2. already claimed reward ->  move on to next step
### f. Click on middle Scale image (Dolce)
### g. Click on OK (Proceeding to Dolce) or Enter button
### h. Fill items for the voyage,  Commerci soap (6x)
### i. Click "SHIP"
### j. Click "OK" or Enter button
### k. Click depart
### l. Click "OK" or Enter button
### m. Auto hunt for ~22 seconds, (flash jump right twice and platter left)
### n. Click Brown ok button or wait a few more seconds to leave
class Commerci(Command):
    _display_name ='Commerci Solo Voyage'

    # number of Dolce Voyages that can be run, # of items that ship can bring
    def __init__(self,voyages='12',items='6'):
        super().__init__(locals())
        self.voyages = float(voyages)
        self.items = int(items)

    def main(self):
        settings.story_mode = True
        maestra_template = cv2.imread('assets/commerci/maestra_template.png', 0)
        start_trade_template = cv2.imread('assets/commerci/start_trade.png', 0)
        next_template = cv2.imread('assets/commerci/commerci_next.png', 0)
        dolce_template = cv2.imread('assets/commerci/dolce.png', 0)
        add_item_template = cv2.imread('assets/commerci/commerci_add_item.png', 0)
        ship_template = cv2.imread('assets/commerci/commerci_ship.png', 0)
        depart_template = cv2.imread('assets/commerci/commerci_depart.png', 0)

        # GoToGuideMap(target_map="commerci_solo").execute()
        bot = config.bot
        time.sleep(0.3)
        # TODO: determine automatically how many voyages left 
        while self.voyages > 0:
            points = utils.multi_match(config.capture.frame, maestra_template, threshold=0.95)
            if len(points) > 0:
                p = (points[0][0],points[0][1])
                print("clicking Maestra")
                utils.game_window_click(p,delay=0.1)
                time.sleep(0.5)
                # utils.game_window_click((700,100), button='right',delay=0.1)
            
            # if start trade button exists, there is an extra dialogue box
            points = utils.multi_match(config.capture.frame, start_trade_template, threshold=0.95)
            if len(points) > 0:
                press("down")
                press(bot.config['Interact'], up_time=0.3)
                print("click start trade")
                utils.game_window_click((700,100), button='right',delay=0.1)

            press(bot.config['Interact'], up_time=0.3)

            # if next button exists, need to claim
            points = utils.multi_match(config.capture.frame, next_template, threshold=0.95)
            if len(points) > 0:
                press(bot.config['Interact'])
                press("y")
                press(bot.config['Interact'])
                print("claimed voyage rewards")
                time.sleep(0.3)

            points = utils.multi_match(config.capture.frame, dolce_template, threshold=0.95)
            if len(points) > 0:
                p = (points[0][0],points[0][1])
                print("clicking Dolce")
                utils.game_window_click(p,delay=0.1)
                time.sleep(0.3)
                utils.game_window_click((700,100), button='right',delay=0.1)        

            press("enter", up_time=0.3)

            points = utils.multi_match(config.capture.frame, add_item_template, threshold=0.95)
            if len(points) > 0:
                p = (points[0][0]+2,points[0][1]-6)
                print("adding items")
                for _ in range(self.items):
                    utils.game_window_click(p,delay=0.15)
                time.sleep(0.1)
                utils.game_window_click((700,100), button='right',delay=0.1)    

            points = utils.multi_match(config.capture.frame, ship_template, threshold=0.95)
            if len(points) > 0:
                p = (points[0][0],points[0][1]-2)
                print("ship")
                utils.game_window_click(p,delay=0.1)
                utils.game_window_click((700,100), button='right',delay=0.1)  
                time.sleep(0.15)
            
            press("enter", up_time=0.4)

            points = utils.multi_match(config.capture.frame, depart_template, threshold=0.95)
            if len(points) > 0:
                p = (points[0][0],points[0][1]-2)
                print("depart")
                utils.game_window_click(p,delay=0.1)
                utils.game_window_click((700,100), button='right',delay=0.1)  
                time.sleep(0.15)

            press("enter", up_time=0.3)

            config.map_changing = True
            auto_hunting = config.bot.command_book['commercidolceautohunt']
            completed_correctly = auto_hunting().execute()

            if completed_correctly:
                self.voyages = self.voyages - 1
        settings.story_mode = False
        