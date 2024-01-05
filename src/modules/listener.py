"""A keyboard listener to track user inputs."""

import time
import threading
import keyboard as kb
from src.common.interfaces import Configurable
from src.common import config, utils, settings
from src.common.vkeys import release_unreleased_key
from datetime import datetime
import win32gui

class Listener(Configurable):
    DEFAULT_CONFIG = {
        'Start/stop': 'insert',
        'Reload routine': 'f6',
        'Record position': 'f7'
    }
    BLOCK_DELAY = 1         # Delay after blocking restricted button press

    def __init__(self):
        """Initializes this Listener object's main thread."""

        super().__init__('controls')
        config.listener = self

        self.enabled = False
        self.ready = False
        self.block_time = 0
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts listening to user inputs.
        :return:    None
        """

        print('\n[~] Started keyboard listener')
        self.thread.start()

    def _main(self):
        """
        Constantly listens for user inputs and updates variables in config accordingly.
        :return:    None
        """

        self.ready = True
        while True:
            if self.enabled:
                if kb.is_pressed(self.config['Start/stop']):
                    Listener.toggle_enabled()
                elif kb.is_pressed(self.config['Reload routine']):
                    Listener.reload_routine()
                elif self.restricted_pressed('Record position'):
                    Listener.record_position()
            time.sleep(0.01)

    def restricted_pressed(self, action):
        """Returns whether the key bound to ACTION is pressed only if the bot is disabled."""

        if kb.is_pressed(self.config[action]):
            if not config.enabled:
                return True
            now = time.time()
            if now - self.block_time > Listener.BLOCK_DELAY:
                print(f"\n[!] Cannot use '{action}' while Auto Maple is enabled")
                self.block_time = now
        return False

    @staticmethod
    def toggle_enabled():
        """Resumes or pauses the current routine. Plays a sound to notify the user."""

        config.bot.map_rune_active = False
        config.should_solve_rune = False
        
        if not config.enabled:
            Listener.recalibrate_minimap()      # Recalibrate only when being enabled.
            print('dk : ', settings.driver_key)
            time.sleep(1)

        config.enabled = not config.enabled
        utils.print_state()

        if config.enabled:
            config.gui.view.status.set_start_btn('stop')
            config.notifier._ping('start')
        else:
            config.gui.view.status.set_start_btn('start')
            config.notifier._ping('end')
            release_unreleased_key()
        time.sleep(0.267)

    @staticmethod
    def reload_routine():
        Listener.recalibrate_minimap()

        config.routine.load(config.routine.path)
        config.notifier._ping('reload')

    @staticmethod
    def recalibrate_minimap():
        window_name = "MapleStory"
        # hwnd = win32gui.FindWindow(None, window_name)
        # win32gui.SetForegroundWindow(hwnd)
        config.capture.calibrated = False
        while not config.capture.calibrated:
            time.sleep(0.01)
        config.gui.edit.minimap.redraw()

    @staticmethod
    def record_position():
        pos = tuple('{:.3f}'.format(round(i, 3)) for i in config.player_pos)
        now = datetime.now().strftime('%I:%M:%S %p')
        config.gui.edit.record.add_entry(now, pos)
        print(f'\n[~] Recorded position ({pos[0]}, {pos[1]}) at {now}')
        time.sleep(0.6)
