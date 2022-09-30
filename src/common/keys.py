import time
from random import random
from interception import *
from src.common import utils


SC_DECIMAL_ARROW = {
    "LEFT": 75, "RIGHT": 77, "DOWN": 80, "UP": 72,
}

SC_DECIMAL = {
    "ALT": 56, "SPACE": 57, "CTRL": 29, "SHIFT": 42,
    "A": 30, "S": 31, "D": 32, "F": 33,
    "Q": 16, "W": 17, "E": 18, "R": 19,
    "0": 1, "1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7
}

# Change these to your own settings.
JUMP_KEY = "ALT"
ATTACK_KEY = "SHIFT"
ROPE_LIFT_KEY = "D"

class Keys:
    def __init__(self):
        context = interception() 
        context.set_filter(interception.is_keyboard, interception_filter_key_state.INTERCEPTION_FILTER_KEY_ALL.value)
        print("Click any key on your keyboard.")
        while True:
            device = context.wait()
            if interception.is_keyboard(device):
                print(f"Bound to keyboard: {context.get_HWID(device)}.")
                c.set_filter(interception.is_keyboard, 0)
                break
        self.device = device
        self.context = context

    def release_all(self):
        key = key.upper()
        for key in SC_DECIMAL_ARROW:
            self.context.send(self.device, key_stroke(SC_DECIMAL_ARROW[key], 3, 0))
        for key in SC_DECIMAL:
            self.context.send(self.device, key_stroke(SC_DECIMAL[key], 1, 0))

    def release(self, key):
        key = key.upper()
        if key in SC_DECIMAL_ARROW:
            self.context.send(self.device, key_stroke(SC_DECIMAL_ARROW[key], 3, 0))
        else:
            self.context.send(self.device, key_stroke(SC_DECIMAL[key], 1, 0))

    @utils.run_if_enabled
    def key_down(self, key):
        key = key.upper()
        if key in SC_DECIMAL_ARROW:
            self.context.send(self.device, key_stroke(SC_DECIMAL_ARROW[key], 2, 0))
        else:
            self.context.send(self.device, key_stroke(SC_DECIMAL[key], 0, 0))

    def key_up(self, key):
        key = key.upper()
        if key in SC_DECIMAL_ARROW:
            self.context.send(self.device, key_stroke(SC_DECIMAL_ARROW[key], 3, 0))
        else:
            self.context.send(self.device, key_stroke(SC_DECIMAL[key], 1, 0))

    @utils.run_if_enabled
    def press(self, key, n, down_time=0.05, up_time=0.1):
        """
        Presses KEY N times, holding it for DOWN_TIME seconds, and releasing for UP_TIME seconds.
        :param key:         The keyboard input to press.
        :param n:           Number of times to press KEY.
        :param down_time:   Duration of down-press (in seconds).
        :param up_time:     Duration of release (in seconds).
        :return:            None
        """
        key = key.upper()

        for _ in range(n):
            if key in SC_DECIMAL_ARROW:
                self.context.send(self.device, key_stroke(SC_DECIMAL_ARROW[key], 2, 0))
                time.sleep(down_time * (0.8 + 0.4 * random()))
                self.context.send(self.device, key_stroke(SC_DECIMAL_ARROW[key], 3, 0))
            else:
                self.context.send(self.device, key_stroke(SC_DECIMAL[key], 0, 0))
                time.sleep(down_time * (0.8 + 0.4 * random()))
                self.context.send(self.device, key_stroke(SC_DECIMAL[key], 1, 0))
            time.sleep(up_time * (0.8 + 0.4 * random()))

    @utils.run_if_enabled
    def click(position, button='left'):
        pass
