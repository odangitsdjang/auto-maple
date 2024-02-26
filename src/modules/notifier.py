"""A module for detecting and notifying the user of dangerous in-game events."""

from src.common import config, utils, settings, mvp, discord
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

MINIMAP_EXP_PORTAL_RANGES = (
    ((5, 150, 200),  (10, 255, 255)),
)
minimap_exp_portal_filtered = utils.filter_color(cv2.imread('assets/minimap_exp_portal_template.png'), MINIMAP_EXP_PORTAL_RANGES)
EXP_PORTAL_TEMPLATE = cv2.cvtColor(minimap_exp_portal_filtered, cv2.COLOR_BGR2GRAY)

ESPECIA_PORTAL_RANGE = (
    ((125, 30, 230), (151, 90, 255)),
)
especia_filtered = utils.filter_color(cv2.imread('assets/especia_template.png'), ESPECIA_PORTAL_RANGE)
ESPECIA_TEMPLATE = cv2.cvtColor(especia_filtered, cv2.COLOR_BGR2GRAY)

# The Elite Boss's warning sign
ELITE_TEMPLATE = cv2.imread('assets/elite_template.jpg', 0)

# check for unexpected conversation
STOP_CONVERSATION_TEMPLATE = cv2.imread('assets/stop_conversation.png', 0)
STOP_BUFF_STACKING_CONVERSATION_TEMPLATE = cv2.imread('assets/buff_stack_cancel.png', 0)

# check for unexpected conversation
REVIVE_CONFIRM_TEMPLATE = cv2.imread('assets/dead_ok.png', 0)

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
        config.notifier = self
        pygame.mixer.init()
        self.mixer = pygame.mixer.music

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

        self.room_change_threshold = 0.9
        self.notifier_delay = 0.1
        self.rune_ready_offset_seconds = 1
        self.skill_template_cd_set = {}
        self.lastest_skill_cd_check_time = 0

    def start(self):
        """Starts this Notifier's thread."""

        print('\n[~] Started notifier')
        self.thread.start()

    def _main(self):
        self.ready = True
        prev_others = 0
        detection_i = 0
        rune_check_count = 0

        prev_mvp = []
        prev_mvp_timer = 0
        mvp_ping_interval = 60 # seconds
        
        prev_especia_timer = 0
        especia_ping_interval = 91 # seconds

        while True:
            if config.enabled:
                now = time.time()

                frame = config.capture.frame
                height, width, _ = frame.shape
                minimap = config.capture.minimap['minimap']

                # Check for unexpected black screen
                if not config.map_changing and not settings.story_mode:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    if np.count_nonzero(gray < 15) / height / width > self.room_change_threshold:
                        if settings.rent_frenzy == False:
                            discord.send_msg_to_discord("black screen", critical=True)
                            self._alert('siren')

                # Check for elite warning
                elite_frame = frame[height // 4:3 * height // 4, width // 4:3 * width // 4]
                elite = utils.multi_match(elite_frame, ELITE_TEMPLATE, threshold=0.9)
                if len(elite) > 0:
                    if settings.rent_frenzy == False and not settings.auto_change_channel:
                        self._ping('mando_this_is_the_way')
                    elif settings.auto_change_channel:
                        pass
                        # config.should_change_channel = True
                
                # Check for mvp every x frames, if found post discord message with a limit of every 1 minute,
                mvp_img_point = mvp.get_mvp_announced_pixel_location(frame)
                if len(mvp_img_point) > 0:
                    mvp_img_point = mvp_img_point[0]
                    cropped_img = mvp.get_cropped_img(frame, mvp_img_point)
                    # template should be the smaller sized of the two, set the vars appropriately
                    if (len(prev_mvp) > len(cropped_img)):
                        template = cropped_img
                        frame_cp = prev_mvp
                    else:
                        template = prev_mvp
                        frame_cp = cropped_img
                    if len(prev_mvp) == 0 or (not mvp.is_same_message(frame_cp, cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)) and now > prev_mvp_timer + mvp_ping_interval):
                        discord.send_img_msg_to_discord(cropped_img)
                        prev_mvp = cropped_img
                        prev_mvp_timer = now 

                # Check for Especia portal
                if now == 0 or now > prev_especia_timer + especia_ping_interval:
                    does_portal_exist = []
                    # check minimap for red/orange portal first (starforce(?) maps have orange portal all the time though)
                    filtered = utils.filter_color(minimap, MINIMAP_EXP_PORTAL_RANGES)
                    if (len(filtered) > len(EXP_PORTAL_TEMPLATE)): 
                        does_portal_exist = utils.multi_match(filtered, EXP_PORTAL_TEMPLATE, threshold=0.9)

                    if len(does_portal_exist) > 0:
                        filtered_frame = utils.filter_color(frame, ESPECIA_PORTAL_RANGE)
                        matches = utils.multi_match(filtered_frame, ESPECIA_TEMPLATE, threshold=0.4)

                        if len(matches) > 0:
                            discord.send_msg_to_discord("especia", include_time=True, nice_to_have=True)
                            prev_especia_timer = now

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
                    
                # not urgen detection 
                if detection_i % 5==0:
                    # check for rune curse
                    # if settings.rent_frenzy == False and settings.story_mode == False:
                    #     curse_frame = frame[0:height // 2, 0:width//2]
                    #     rune_curse_detector = utils.multi_match(curse_frame, RUNE_CURSE_TEMPLATE, threshold=0.9)
                    #     if len(rune_curse_detector) > 0:
                    #         print("find rune_curse_detector")
                    #         if settings.auto_change_channel:
                    #             if config.should_change_channel == False and config.should_solve_rune == False:
                    #                 if time.time() - config.latest_change_channel_or_map <= 60:
                    #                     config.should_solve_rune = True
                    #                 else:
                    #                     config.should_change_channel = True
                    #                 self._ping('rune_appeared', volume=0.75)
                    #         else:
                    #             # self._send_msg_to_line_notify("輪之詛咒")
                    #             self._alert('siren')

                    # check for unexpected conversation
                    if not settings.story_mode:
                        conversation_frame = frame[height//2-250:height//2+250, width //2-250:width//2+250]

                        generic_conversation = utils.multi_match(conversation_frame, STOP_CONVERSATION_TEMPLATE, threshold=0.9)
                        buff_stacking_conversation = utils.multi_match(conversation_frame, STOP_BUFF_STACKING_CONVERSATION_TEMPLATE, threshold=0.9)
                        
                        matched = (len(generic_conversation) > 0 and generic_conversation) or \
                            (len(buff_stacking_conversation) > 0 and buff_stacking_conversation)
                        if matched:
                            print("stop conversation")
                            conversation_pos = min(matched, key=lambda p: p[0])
                            target = (
                                round(conversation_pos[0] +(width //2-250)),
                                round(conversation_pos[1] +(height//2-250) - 2)
                            )
                            utils.game_window_click(target)
                            time.sleep(1)

                    # check for unexpected death
                    revive_frame = frame[height//2-100:height//2+200, width //2-150:width//2+150]
                    revive_confirm = utils.multi_match(revive_frame, REVIVE_CONFIRM_TEMPLATE, threshold=0.9)
                    if len(revive_confirm) > 0:
                        if settings.rent_frenzy == False:
                            discord.send_msg_to_discord("died", critical=True)
                        revive_confirm_pos = min(revive_confirm, key=lambda p: p[0])
                        target = (
                            round(revive_confirm_pos[0] +(width //2-150)),
                            round(revive_confirm_pos[1] +(height//2-100))
                        )
                        utils.game_window_click(target)
                        time.sleep(1)
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
                # Add logic that adds coupling to rune cd which adds overhead of having correct rune cd in the routine but reduces operations and chance of triggering false rune alerts
                # especially on shared (instanced) maps
                time_since_last_solved_rune = now - config.latest_solved_rune

                if settings.rent_frenzy == False and settings.story_mode == False:                    
                    if not config.bot.map_rune_active:
                        if (time_since_last_solved_rune >= (60 * int(settings.rune_cd_min) - self.rune_ready_offset_seconds)) and (
                            not self.has_rune_buff(frame)
                        ):
                            # look for rune on minimap 
                            filtered = utils.filter_color(minimap, RUNE_RANGES)
                            matches = utils.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)
                            rune_start_time = now
                            # if rune is on minimap, find closest position and ping the user
                            if matches and config.routine.sequence:
                                abs_rune_pos = (matches[0][0], matches[0][1])
                                config.bot.rune_pos = utils.convert_to_relative(abs_rune_pos, minimap)
                                print('rune pos : ',config.bot.rune_pos)
                                distances = list(map(distance_to_rune, config.routine.sequence))
                                index = np.argmin(distances)
                                config.bot.rune_closest_pos = config.routine[index].location
                                print('rune_closest_pos : ',config.bot.rune_closest_pos)
                                config.bot.map_rune_active = True
                                rune_check_count = 0
                                self._ping('rune_appeared')
                    elif config.bot.solve_rune_fail_count >= 3 and not settings.auto_change_channel:
                        discord.send_msg_to_discord("Rune Fail", critical=True)
                        config.bot.map_rune_active = False
                        self._alert('siren')
                    else:
                        # Rune was active on map, bot.py should have solved it and rune should no longer be active on map after a while
                        if detection_i % 10 == 0:
                            filtered = utils.filter_color(minimap, RUNE_RANGES)
                            matches = utils.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)
                            if len(matches) == 0:
                                if rune_check_count >= 50:
                                    rune_check_count = 0
                                    config.bot.map_rune_active = False
                                else:
                                    rune_check_count = rune_check_count + 1
                            else:
                                rune_check_count = 0
                        
                            # check in rune buff
                            if self.has_rune_buff(frame):
                                config.bot.in_rune_buff = True # not necessary here?
                                rune_start_time = now
                                print('in rune buff/cd, turning off map_rune_active')
                                config.bot.map_rune_active = False
                            else:
                                config.bot.in_rune_buff = False

                detection_i = detection_i + 1
            time.sleep(self.notifier_delay)
    
    def has_rune_buff(self, frame):
        rune_buff = utils.multi_match(frame[:65, :],
            RUNE_BUFF_TEMPLATE,
            threshold=0.93)
        rune_buff_bottom = utils.multi_match(frame[:95, :],
            RUNE_BUFF_TEMPLATE_BOTTOM,
            threshold=0.93)
        return (len(rune_buff) > 0 or len(rune_buff_bottom) > 0)

    def _alert(self, name, volume=0.33):
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

    def _ping(self, name, volume=0.25):
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
