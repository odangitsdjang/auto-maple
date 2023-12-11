import cv2
from src.common import utils

# TEST_PIC = cv2.imread('r_50.png', 0)
MVP_TEMPLATE_1 = cv2.imread('assets/mvp_common_atmospheric_effect.png', 0)

FILTER_HEIGHT_START = 650 # 650 -> 768
FILTER_WIDTH_START = 13
FILTER_WIDTH_END = 558 # 13 -> 588
TEXT_LINE_DEPTH = 13

# hard coded pixel values relative to 768 x 1366 resolution
# TODO: needs to be adjusted during resolution fix or find the top left/bottom right pixel position of the chat box with cv2
def get_mvp_announced_pixel_location(frame):
    return utils.multi_match(frame[FILTER_HEIGHT_START:, FILTER_WIDTH_START:FILTER_WIDTH_END],
        MVP_TEMPLATE_1,
        threshold=0.93)

# reducing threshold for situations:
# a. same message but on one line image vs 2 line image (needs to be the same message) (can be actually fixed by only grabbing the correct number of lines of message)
# b. same message but different background due to player movement causing bot to think they're different messages
def is_same_message(frame, template):
    return len(utils.multi_match(frame, template, threshold=0.47)) > 0 

def get_cropped_img(frame, mvp_img_point):
    h, w, _ = frame.shape

    height_min = (FILTER_HEIGHT_START + mvp_img_point[1] - (TEXT_LINE_DEPTH//2) - 1)
    height_end = height_min + (2 * TEXT_LINE_DEPTH)
    height_end_max =  h - TEXT_LINE_DEPTH # prevent showing exp bar

    return frame[height_min:min(height_end, height_end_max), FILTER_WIDTH_START:FILTER_WIDTH_END]

#TODO
def should_grab_mvp():
    return

#TODO
def get_channel(frame):
    return

#TODO
def get_map(frame):
    return

#TODO
def parse_map(frame):
    return