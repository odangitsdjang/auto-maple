"""A collection of functions and classes used across multiple modules."""

import math
import queue
import cv2
import time
import threading
import numpy as np
import matplotlib.pyplot as plt
from src.common import config, settings
from random import random
from ctypes import windll
from ctypes.wintypes import RECT, HWND


def move_window(handle: HWND, x: int, y: int):
    """移動視窗到座標(x, y)

    Args:
        handle (HWND): 窗口句柄
        x (int): 横座標
        y (int): 綜座標
    """
    #test move
    SetWindowPos = windll.user32.SetWindowPos
    # GetClientRect = windll.user32.GetClientRect
    # GetWindowRect = windll.user32.GetWindowRect
    # EnableWindow = windll.user32.EnableWindow

    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0X0002
    SWP_NOZORDER = 0x0004
    SetWindowPos(handle, 0, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER)


def run_if_enabled(function):
    """
    Decorator for functions that should only run if the bot is enabled.
    :param function:    The function to decorate.
    :return:            The decorated function.
    """

    def helper(*args, **kwargs):
        if config.enabled:
            return function(*args, **kwargs)
    return helper


def run_if_disabled(message=''):
    """
    Decorator for functions that should only run while the bot is disabled. If MESSAGE
    is not empty, it will also print that message if its function attempts to run when
    it is not supposed to.
    """

    def decorator(function):
        def helper(*args, **kwargs):
            if not config.enabled:
                return function(*args, **kwargs)
            elif message:
                print(message)
        return helper
    return decorator


def distance(a, b):
    """
    Applies the distance formula to two points.
    :param a:   The first point.
    :param b:   The second point.
    :return:    The distance between the two points.
    """

    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def game_window_click(point=(0,0),button='left',click_time=1,delay=0.4):
    from src.common.vkeys import click
    if not config.enabled:
        return
        
    target = (
        round(point[0] + config.capture.window['left']),
        round(point[1] + config.capture.window['top'])
    )
    # print(target)
    click(target, button=button,click_time=click_time)
    time.sleep(rand_float(delay,delay*1.5))

def wait_for_is_standing(ms=2000):
    """
    Wait until player stand on the ground 
    :param ms:   The maximun waiting time
    :return:    is_standing or not
    """
    for i in range(int(ms / 10)): # maximum time : 2s
        if config.player_states['is_standing']:
            return True
        time.sleep(0.01)
    return False

def wait_for_is_jumping(ms=2000):
    """
    Wait until player stand on the ground 
    :param ms:   The maximun waiting time
    :return:    is_standing or not
    """
    for i in range(int(ms / 10)): # maximum time : 2s
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_JUMPING:
            return True
        time.sleep(0.01)
    return False

def wait_for_is_falling(ms=2000):
    """
    Wait until player stand on the ground 
    :param ms:   The maximun waiting time
    :return:    is_standing or not
    """
    for i in range(int(ms / 10)): # maximum time : 2s
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
            return True
        time.sleep(0.01)
    return False

def check_is_jumping():
    """
    check if player state is not standing
    :return:    is jumping or not
    """
    return not config.player_states['is_standing']

def get_if_skill_ready(skill:str,bias=0):
    """
    check if skill is ready
    :return: True or False
    """
    command_book = config.bot.command_book
    target_skill_name = None
    skills = skill.split("|")
    for key in command_book:
        for s in skills:
            skill_and_bias = s.split('-')
            if len(skill_and_bias) == 1:
                bias = 0
            else:
                bias = float(skill_and_bias[1])
            if key.lower() == skill_and_bias[0]:
                target_skill_name = command_book[key].__name__
                if command_book[key].get_is_skill_ready(bias):
                    break
                else:
                    target_skill_name = None
        if target_skill_name:
            break

    if target_skill_name:
        return True
    else:
        return False

def get_is_in_skill_buff(skill):
    """
    check if in skill buff time
    :return: True or False
    """
    command_book = config.bot.command_book
    target_skill_name = None
    skills = skill.split("|")
    for key in command_book:
        for s in skills:
            skill_and_bias = s.split('-')
            if str(s).find('+') >= 0:
                skill_and_bias = s.split('+')
                skill_and_bias[1] = float(skill_and_bias[1]) * -1
            if len(skill_and_bias) == 1:
                bias = 0
            else:
                bias = float(skill_and_bias[1])
            if key.lower() == skill_and_bias[0]:
                target_skill_name = command_book[key].__name__
                if not config.skill_cd_timer[target_skill_name]:
                    config.skill_cd_timer[target_skill_name] = 0
                if (time.time() + bias) - float(config.skill_cd_timer[target_skill_name]) < int(command_book[target_skill_name.lower()].buff_time):
                    # print("in skill buff : ",target_skill_name, ", bias : ",bias)
                    break
                else:
                    target_skill_name = None
        if target_skill_name:
            break

    if target_skill_name:
        # print("in skill buff : ",skills)
        return True
    else:
        # print("not in skill buff : ",skills)
        return False

def separate_args(arguments):
    """
    Separates a given array ARGUMENTS into an array of normal arguments and a
    dictionary of keyword arguments.
    :param arguments:    The array of arguments to separate.
    :return:             An array of normal arguments and a dictionary of keyword arguments.
    """

    args = []
    kwargs = {}
    for a in arguments:
        a = a.strip()
        index = a.find('=')
        if index > -1:
            key = a[:index].strip()
            value = a[index+1:].strip()
            kwargs[key] = value
        else:
            args.append(a)
    return args, kwargs


def single_match(frame, template):
    """
    Finds the best match within FRAME.
    :param frame:       The image in which to search for TEMPLATE.
    :param template:    The template to match with.
    :return:            The top-left and bottom-right positions of the best match.
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF)
    _, _, _, top_left = cv2.minMaxLoc(result)
    w, h = template.shape[::-1]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    return top_left, bottom_right

def multi_match(frame, template, threshold=0.95, centered=True, save_result = False):
    """
    Finds all matches in FRAME that are similar to TEMPLATE by at least THRESHOLD.
    :param frame:       The image in which to search.
    :param template:    The template to match with.
    :param threshold:   The minimum percentage of TEMPLATE that each result must match.
    :return:            An array of matches that exceed THRESHOLD.
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))
    results = []

    if save_result:
        img_disp = gray.copy()
    for p in locations:
        if centered:
            x = int(round(p[0] + template.shape[1] / 2))
            y = int(round(p[1] + template.shape[0] / 2))
        else:
            x = p[0]
            y =  p[1]
        results.append((x, y))
        if save_result:
            right_bottom = (p[0] + template.shape[1], p[1] + template.shape[0])
            cv2.rectangle(img_disp, p,right_bottom, (0,255,0), 5, 8, 0 )
    if save_result:
        fig,ax = plt.subplots(3,1)
        fig.suptitle('match_template')
        ax[0].set_title('img_src')
        ax[0].imshow(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)) 
        ax[1].set_title('img_templ')
        ax[1].imshow(template,'gray') 
        ax[2].set_title('img_disp')
        ax[2].imshow(cv2.cvtColor(img_disp,cv2.COLOR_BGR2RGB)) 
        plt.savefig('plot.png') 
        plt.show()   
    return results

def single_match_with_threshold(frame, template, threshold=0.95):
    """
    Finds max match in FRAME that are similar to TEMPLATE by at least THRESHOLD.
    :param frame:       The image in which to search.
    :param template:    The template to match with.
    :param threshold:   The minimum percentage of TEMPLATE that each result must match.
    :return:            An array of matches that exceed THRESHOLD.
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    results = []
    _, score, _, top_left = cv2.minMaxLoc(result)
    print("score : ",score)
    if score >= threshold:
        x = int(round(top_left[0] + template.shape[1] / 2))
        y = int(round(top_left[1] + template.shape[0] / 2))
        results.append((x, y))
    return results

def single_match_with_digit(frame, template, threshold=0.95):
    """
    Finds max match in FRAME that are similar to TEMPLATE by at least THRESHOLD.
    :param frame:       The image in which to search.
    :param template:    The template to match with.
    :param threshold:   The minimum percentage of TEMPLATE that each result must match.
    :return:            An array of matches that exceed THRESHOLD.
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    results = []
    _, score, _, top_left = cv2.minMaxLoc(result)
    # print("score : ",score)
    if score >= threshold:
        x = round(top_left[0] + template.shape[1] / 2,1)
        y = round(top_left[1] + template.shape[0] / 2,1)
        results.append((x, y))
    return results

def convert_to_roundint(point):
    """
    Converts POINT into roundint coordinates in the range [0, 1] based on FRAME.
    Normalizes the units of the vertical axis to equal those of the horizontal
    axis by using config.mm_ratio.
    :param point:   The point in absolute coordinates.
    :param frame:   The image to use as a reference.
    :return:        The given point in roundint coordinates.
    """

    # x = point[0] / frame.shape[1]
    # y = point[1] / config.capture.minimap_ratio / frame.shape[0]
    x = int(round(point[0]))
    y = int(round(point[1])) 
    return x, y

def convert_to_relative(point, frame):
    """
    Converts POINT into relative coordinates in the range [0, 1] based on FRAME.
    Normalizes the units of the vertical axis to equal those of the horizontal
    axis by using config.mm_ratio.
    :param point:   The point in absolute coordinates.
    :param frame:   The image to use as a reference.
    :return:        The given point in relative coordinates.
    """

    # x = point[0] / frame.shape[1]
    # y = point[1] / config.capture.minimap_ratio / frame.shape[0]
    x = point[0] 
    y = point[1] 
    return x, y


def convert_to_absolute(point, frame):
    """
    Converts POINT into absolute coordinates (in pixels) based on FRAME.
    Normalizes the units of the vertical axis to equal those of the horizontal
    axis by using config.mm_ratio.
    :param point:   The point in relative coordinates.
    :param frame:   The image to use as a reference.
    :return:        The given point in absolute coordinates.
    """
    if point[0] < 1 and point[1] < 1:
        x = int(round(point[0] * frame.shape[1]))
        y = int(round(point[1] * config.capture.minimap_ratio * frame.shape[0]))
    else:
        x = int(round(point[0]))
        y = int(round(point[1]))
    return x, y


def filter_color(img, ranges):
    """
    Returns a filtered copy of IMG that only contains pixels within the given RANGES.
    on the HSV scale.
    :param img:     The image to filter.
    :param ranges:  A list of tuples, each of which is a pair upper and lower HSV bounds.
    :return:        A filtered copy of IMG.
    """

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, ranges[0][0], ranges[0][1])
    for i in range(1, len(ranges)):
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, ranges[i][0], ranges[i][1]))

    # Mask the image
    color_mask = mask > 0
    result = np.zeros_like(img, np.uint8)
    result[color_mask] = img[color_mask]
    return result

# Use SSIM to filter out differences in same sized images https://stackoverflow.com/questions/56183201/detect-and-visualize-differences-between-two-images-with-opencv-python


def remove_from_frame(frame, template, save_result = False):
    """
    Returns a filtered copy of frame that removes all parts matching part with the template
    on the HSV scale.
    :param frame:      The frame in question to remove template's colors.
    :param template:   The template, which should be same in size to frame, to base as the original image.
    :return:        A filtered copy of frame.
    """
    combo_orbs_coord = multi_match(frame, template, centered=False, threshold=0.8)
    if (len(combo_orbs_coord) == 0): return frame
    x, y = template.shape
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    coords = [(x, y) for y, x in combo_orbs_coord]
    for coordx, coordy in coords:
        frame[coordx:coordx+x, coordy:coordy+y] = (0, 0, 0)
    result =  cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    if save_result:
        fig,ax = plt.subplots(2,1)
        fig.suptitle('match_template')
        ax[0].set_title('frame')
        ax[0].imshow(frame) 
        ax[1].set_title('result')
        ax[1].imshow(result)  
        plt.savefig('plot.png') 
        plt.show()

    return result

def draw_location(minimap, pos, color):
    """
    Draws a visual representation of POINT onto MINIMAP. The radius of the circle represents
    the allowed error when moving towards POINT.
    :param minimap:     The image on which to draw.
    :param pos:         The location (as a tuple) to depict.
    :param color:       The color of the circle.
    :return:            None
    """

    center = convert_to_absolute(pos, minimap)
    # center = pos
    if settings.move_tolerance < 1:
        radius = round(minimap.shape[1] * settings.move_tolerance)
    else:
        radius = round(settings.move_tolerance)
    cv2.circle(minimap,
               center,
               radius,
               color,
               1)


def print_separator():
    """Prints a 3 blank lines for visual clarity."""

    print('\n\n')


def print_state():
    """Prints whether Auto Maple is currently enabled or disabled."""

    print_separator()
    print('#' * 18)
    print(f"#    {'ENABLED ' if config.enabled else 'DISABLED'}    #")
    print('#' * 18)


def closest_point(points, target):
    """
    Returns the point in POINTS that is closest to TARGET.
    :param points:      A list of points to check.
    :param target:      The point to check against.
    :return:            The point closest to TARGET, otherwise None if POINTS is empty.
    """

    if points:
        points.sort(key=lambda p: distance(p, target))
        return points[0]


def bernoulli(p):
    """
    Returns the value of a Bernoulli random variable with probability P.
    :param p:   The random variable's probability of being True.
    :return:    True or False.
    """

    return random() < p


def rand_float(start, end):
    """Returns a random float value in the interval [START, END)."""

    assert start < end, 'START must be less than END'
    return (end - start) * random() + start


##########################
#       Threading        #
##########################
class Async(threading.Thread):
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.queue = queue.Queue()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.function(*self.args, **self.kwargs)
        self.queue.put('x')

    def process_queue(self, root):
        def f():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                root.after(100, self.process_queue(root))
        return f


def async_callback(context, function, *args, **kwargs):
    """Returns a callback function that can be run asynchronously by the GUI."""

    def f():
        task = Async(function, *args, **kwargs)
        task.start()
        context.after(100, task.process_queue(context))
    return f
