"""A module for detecting and notifying the user of dangerous in-game events."""

from src.common import config, utils, settings
import time
import os
import cv2
import pygame
import threading
import numpy as np
import keyboard as kb
import requests
from src.common.vkeys import key_down, key_up, press, click
from src.routine.components import Point
from src.common.vkeys import release_unreleased_key

# A rune's symbol on the minimap
RUNE_RANGES = (
    ((141, 148, 245), (146, 158, 255)),
)
rune_filtered = utils.filter_color(cv2.imread('assets/rune_template.png'), RUNE_RANGES)
RUNE_TEMPLATE = cv2.cvtColor(rune_filtered, cv2.COLOR_BGR2GRAY)

# Other players' symbols on the minimap
OTHER_RANGES = (
    ((0, 245, 215), (10, 255, 255)),
)
other_filtered = utils.filter_color(cv2.imread('assets/other_template.png'), OTHER_RANGES)
OTHER_TEMPLATE = cv2.cvtColor(other_filtered, cv2.COLOR_BGR2GRAY)

# The Elite Boss's warning sign
ELITE_TEMPLATE = cv2.imread('assets/elite_template2.jpg', 0)

# check for unexpected conversation
STOP_CONVERSTION_TEMPLATE = cv2.imread('assets/stop_conversation.jpg', 0)

# check for unexpected conversation
REVIVE_CONFIRM_TEMPLATE = cv2.imread('assets/revive_confirm.png', 0)

# fiona_lie_detector image
FIONA_LIE_DETECTOR_TEMPLATE = cv2.imread('assets/fiona_lie_detector.png',0)

# rune curse image
RUNE_CURSE_TEMPLATE = cv2.imread('assets/rune_curse.png',0)

# The rune's buff icon
RUNE_BUFF_TEMPLATE = cv2.imread('assets/rune_buff_template.jpg', 0)
RUNE_BUFF_TEMPLATE_BOTTOM = cv2.imread('assets/rune_buff_template_bottom.jpg', 0)

def get_alert_path(name):
    return os.path.join(Notifier.ALERTS_DIR, f'{name}.mp3')


class Notifier:
    ALERTS_DIR = os.path.join('assets', 'alerts')

    def __init__(self):
        """Initializes this Notifier object's main thread."""

        pygame.mixer.init()
        self.mixer = pygame.mixer.music

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

        self.room_change_threshold = 0.9
        self.rune_alert_delay = 270         # 4.5 minutes
        self.notifier_delay = 0.1
        self.skill_template_cd_set = {}
        self.lastest_skill_cd_check_time = 0

    def start(self):
        """Starts this Notifier's thread."""

        print('\n[~] Started notifier')
        self.thread.start()

    def _main(self):
        self.ready = True
        prev_others = 0
        rune_start_time = time.time()
        detection_i = 0
        rune_check_count = 0

        while True:
            if config.enabled:
                frame = config.capture.frame
                height, width, _ = frame.shape
                minimap = config.capture.minimap['minimap']

                # Check for unexpected black screen
                if not config.map_changing and not settings.story_mode:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    if np.count_nonzero(gray < 15) / height / width > self.room_change_threshold:
                        if settings.rent_frenzy == False:
                            # self._send_msg_to_line_notify("畫面黑屏")
                            self._alert('siren')

                # Check for elite warning
                elite_frame = frame[height // 4:3 * height // 4, width // 4:3 * width // 4]
                elite = utils.multi_match(elite_frame, ELITE_TEMPLATE, threshold=0.9)
                if len(elite) > 0:
                    # self._send_msg_to_line_notify("黑王出沒")
                    if settings.rent_frenzy == False and not settings.auto_change_channel:
                        self._ping('mando_this_is_the_way')
                    elif settings.auto_change_channel:
                        pass
                        # config.should_change_channel = True

                if settings.rent_frenzy == False and not settings.story_mode:
                    # Check for other players entering the map
                    filtered = utils.filter_color(minimap, OTHER_RANGES)
                    others = len(utils.multi_match(filtered, OTHER_TEMPLATE, threshold=0.5))
                    config.stage_fright = others > 1
                    if time.time() - config.latest_change_channel_or_map <= 60 and config.stage_fright:
                        config.should_change_channel = True # if find other in 1 min between change channel, change again
                    if others != prev_others:
                        if others > 2:
                            self._ping('ding')
                        prev_others = others

                # check for fiona_lie_detector
                fiona_frame = frame[height-400:height, width - 300:width]
                fiona_lie_detector = utils.multi_match(fiona_frame, FIONA_LIE_DETECTOR_TEMPLATE, threshold=0.9)
                if len(fiona_lie_detector) > 0:
                    print("find fiona_lie_detector")
                    # self._send_msg_to_line_notify("菲歐娜測謊")
                    # if settings.rent_frenzy == False:
                    self._alert('siren')
                    time.sleep(0.1)
                    
                # not urgen detection 
                if detection_i % 5==0:
                    # check for rune curse
                    if settings.rent_frenzy == False and settings.story_mode == False:
                        curse_frame = frame[0:height // 2, 0:width//2]
                        rune_curse_detector = utils.multi_match(curse_frame, RUNE_CURSE_TEMPLATE, threshold=0.9)
                        if len(rune_curse_detector) > 0:
                            print("find rune_curse_detector")
                            if settings.auto_change_channel:
                                if config.should_change_channel == False and config.should_solve_rune == False:
                                    if time.time() - config.latest_change_channel_or_map <= 60:
                                        config.should_solve_rune = True
                                    else:
                                        config.should_change_channel = True
                                    self._ping('rune_appeared', volume=0.75)
                            else:
                                # self._send_msg_to_line_notify("輪之詛咒")
                                self._alert('siren')

                    # check for unexpected conversation
                    if not settings.story_mode:
                        conversation_frame = frame[height//2-250:height//2+250, width //2-250:width//2+250]
                        conversation = utils.multi_match(conversation_frame, STOP_CONVERSTION_TEMPLATE, threshold=0.9)
                        if len(conversation) > 0:
                            print("stop conversation")
                            conversation_pos = min(conversation, key=lambda p: p[0])
                            target = (
                                round(conversation_pos[0] +(width //2-250)),
                                round(conversation_pos[1] +(height//2-250))
                            )
                            utils.game_window_click(target)
                            time.sleep(1)
                            utils.game_window_click((700,100), button='right')

                    # check for unexpected dead
                    revive_frame = frame[height//2-100:height//2+200, width //2-150:width//2+150]
                    revive_confirm = utils.multi_match(revive_frame, REVIVE_CONFIRM_TEMPLATE, threshold=0.9)
                    if len(revive_confirm) > 0:
                        # if settings.rent_frenzy == False:
                            # self._send_msg_to_line_notify("角色死亡")
                        revive_confirm_pos = min(revive_confirm, key=lambda p: p[0])
                        target = (
                            round(revive_confirm_pos[0] +(width //2-150)),
                            round(revive_confirm_pos[1] +(height//2-100))
                        )
                        utils.game_window_click(target)
                        time.sleep(1)
                        utils.game_window_click((700,100), button='right')
                        if not settings.auto_revive:
                            self._alert('siren')

                
                # Check for skill cd
                if time.time() - self.lastest_skill_cd_check_time >= 1.5:
                    command_book = config.bot.command_book
                    image_matched = False
                    match_list = []
                    for key in command_book:
                        if hasattr(command_book[key],"skill_cool_down"):
                            command_book[key].get_is_skill_ready()
                        if hasattr(command_book[key],"skill_image") and image_matched == False and not command_book[key].get_is_skill_ready():
                            if not key in self.skill_template_cd_set:
                                skill_template = cv2.imread(command_book[key].skill_image, 0)
                                self.skill_template_cd_set[key] = skill_template
                            else:
                                skill_template = self.skill_template_cd_set[key]
                            is_ready_region = frame[height-500:height-90, width-182:width-126]
                            skill_match = utils.multi_match(is_ready_region, skill_template, threshold=0.9)
                            if len(skill_match) > 0:
                                print(command_book[key]._display_name , " skill_match")
                                match_list.append(key)
                                # image_matched = True
                    for key in match_list:
                        command_book[key].set_is_skill_ready(True)
                    self.lastest_skill_cd_check_time = time.time()

                # Check for rune
                now = time.time()
                if settings.rent_frenzy == False and settings.story_mode == False:
                    if not config.bot.rune_active:
                        filtered = utils.filter_color(minimap, RUNE_RANGES)
                        matches = utils.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)
                        rune_start_time = now
                        if matches and config.routine.sequence:
                            abs_rune_pos = (matches[0][0], matches[0][1])
                            config.bot.rune_pos = utils.convert_to_relative(abs_rune_pos, minimap)
                            print('rune pos : ',config.bot.rune_pos)
                            distances = list(map(distance_to_rune, config.routine.sequence))
                            index = np.argmin(distances)
                            config.bot.rune_closest_pos = config.routine[index].location
                            print('rune_closest_pos : ',config.bot.rune_closest_pos)
                            config.bot.rune_active = True
                            rune_check_count = 0
                            self._ping('rune_appeared', volume=0.75)
                    elif now - rune_start_time > self.rune_alert_delay and now - config.latest_solved_rune >= (60 * int(settings.rune_cd_min) + self.rune_alert_delay):     # Alert if rune hasn't been solved
                        config.bot.rune_active = False
                        # self._send_msg_to_line_notify("解輪耗時過久")
                        if settings.auto_change_channel:
                            config.should_change_channel = True
                        else:
                            self._alert('siren')
                    elif config.bot.solve_rune_fail_count >= 3 and not settings.auto_change_channel:
                        # self._send_msg_to_line_notify("多次解輪失敗")
                        self._alert('siren')
                    else:
                        # check for rune is actually existing
                        if detection_i % 50 == 0:
                            filtered = utils.filter_color(minimap, RUNE_RANGES)
                            matches = utils.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)
                            if len(matches) == 0:
                                if rune_check_count >= 10:
                                    rune_check_count = 0
                                    config.bot.rune_active = False
                                else:
                                    rune_check_count = rune_check_count + 1
                            else:
                                rune_check_count = 0
                        
                            # check in rune buff
                            rune_buff = utils.multi_match(frame[:65, :],
                                            RUNE_BUFF_TEMPLATE,
                                            threshold=0.93)
                            rune_buff_bottom = utils.multi_match(frame[:95, :],
                                            RUNE_BUFF_TEMPLATE_BOTTOM,
                                            threshold=0.93)
                            if len(rune_buff) > 0 or len(rune_buff_bottom) > 0:
                                config.bot.in_rune_buff = True
                                rune_start_time = now
                                print('in rune buff')
                            else:
                                config.bot.in_rune_buff = False

                detection_i = detection_i + 1
            time.sleep(self.notifier_delay)

    # def _send_msg_to_line_notify(self,msg,file=None):
    #     url = "https://notify-api.line.me/api/notify"
    #     if settings.id == "veg":
    #         token = "ezvoLebyYzo6yYlh1BbcF0pab4gU2pWBBG8S0QzkysA"
    #     else:
    #         token = "gOgNCkc4PLinHFzJSbqQZHQyLotFuu0skBCFmHicKoZ"
    #     my_headers = {'Authorization': 'Bearer ' + token }
    #     data = {"message" : msg }
    #     if file:
    #         image = open(file, 'rb')    # 以二進位方式開啟圖片
    #         imageFile = {'imageFile' : image}   # 設定圖片資訊
    #         r = requests.post(url,headers = my_headers, data = data, files=imageFile)
    #     else:
    #         r = requests.post(url,headers = my_headers, data = data)

    def _alert(self, name, volume=0.6):
        """
        Plays an alert to notify user of a dangerous event. Stops the alert
        once the key bound to 'Start/stop' is pressed.
        """

        config.enabled = False
        config.listener.enabled = False
        config.bot.solve_rune_fail_count = 0
        self.mixer.load(get_alert_path(name))
        self.mixer.set_volume(volume)
        self.mixer.play()
        # use go home scroll
        # kb.press("f9")

        while not kb.is_pressed(config.listener.config['Start/stop']):
            time.sleep(0.1)
            if config.enabled:
                break
        self.mixer.stop()
        time.sleep(1)
        config.listener.enabled = True

    def _ping(self, name, volume=0.50):
        """A quick notification for non-dangerous events."""

        self.mixer.load(get_alert_path(name))
        self.mixer.set_volume(volume)
        self.mixer.play()


#################################
#       Helper Functions        #
#################################
def distance_to_rune(point):
    """
    Calculates the distance from POINT to the rune.
    :param point:   The position to check.
    :return:        The distance from POINT to the rune, infinity if it is not a Point object.
    """

    if isinstance(point, Point):
        return utils.distance(config.bot.rune_pos, point.location)
    return float('inf')
