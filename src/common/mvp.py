import cv2
# import utils 
import requests
import os
from dotenv import load_dotenv
from src.common import utils
import json 

load_dotenv()

# TEST_PIC = cv2.imread('r_50.png', 0)
MVP_TEMPLATE_1 = cv2.imread('assets/mvp_common_atmospheric_effect.png', 0)

FILTER_HEIGHT_START = 650 # 650 -> 768
FILTER_WIDTH_START = 13
FILTER_WIDTH_END = 555 # 13 -> 588
TEXT_LINE_DEPTH = 13

# hard coded pixel values relative to 768 x 1366 resolution
# TODO: needs to be adjusted during resolution fix or find the top left/bottom right pixel position of the chat box with cv2
def get_mvp_announced_pixel_location(frame):
    return utils.multi_match(frame[FILTER_HEIGHT_START:, FILTER_WIDTH_START:FILTER_WIDTH_END],
        MVP_TEMPLATE_1,
        threshold=0.93)

def get_cropped_img(frame, mvp_img_point):
    h, w, _ = frame.shape

    height_min = (FILTER_HEIGHT_START + mvp_img_point[1] - (TEXT_LINE_DEPTH//2) - 1)
    height_end = height_min + (2 * TEXT_LINE_DEPTH) 

    return frame[height_min:height_end, FILTER_WIDTH_START:FILTER_WIDTH_END]
      
def send_mvp_notif_to_discord(img):
    imencoded  = cv2.imencode(".jpg", img)[1]

    url = f'https://discord.com/api/v10/channels/{os.getenv("CHANNEL_ID")}/messages'
    headers= {
        'Accept': 'application/json',
        'Authorization': f'Bot {os.getenv("DISCORD_TOKEN")}'
    }

    files = {
        'image.jpg': imencoded.tobytes()
    }

    data = {
        'content': f'<@&{os.getenv("MVP_NOTIFICATION_ROLE_ID")}>', # ping specific role
    }

    files["payload_json"] = (None, json.dumps(data))

    # response = requests.post(url, headers=headers, json=data) # send string only, header may need to add Content-Type
    response = requests.post(url, headers=headers, files=files)

    if response.ok: 
        print("discord notification sent ok")

    else:
        response.raise_for_status()
