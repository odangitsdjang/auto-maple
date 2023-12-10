import cv2
# import utils 
import requests
import os
from dotenv import load_dotenv
from src.common import utils

load_dotenv()

TEST_PIC = cv2.imread('src/common/a.png', 1)
# TEST_PIC = cv2.imread('r_50.png', 0)
MVP_TEMPLATE_1 = cv2.imread('src/common/mvp/mvp_atmospheric.png', 0)

frame = TEST_PIC

FILTER_HEIGHT_START = 650 # 650 -> 768
FILTER_WIDTH_END = 580 # 0 -> 588
TEXT_LINE_DEPTH = 12

# hard coded pixel values relative to 768 x 1366 resolution
# TODO: needs to be adjusted during resolution fix or find the top left/bottom right pixel position of the chat box with cv2
def get_mvp_announced_pixel_location(frame):
    return utils.multi_match(frame[FILTER_HEIGHT_START:, :FILTER_WIDTH_END],
        MVP_TEMPLATE_1,
        threshold=0.93, save_result=True)
    
def send_mvp_notif_to_discord(frame, mvp_img_point):
    h, w, _ = frame.shape

    top_left = (0, FILTER_HEIGHT_START + mvp_img_point[1])
    top_right = (FILTER_WIDTH_END, FILTER_HEIGHT_START + mvp_img_point[1])
    bot_left = (0, FILTER_HEIGHT_START + mvp_img_point[1]+ (2 * TEXT_LINE_DEPTH))
    bot_right = (FILTER_WIDTH_END, + FILTER_HEIGHT_START + mvp_img_point[1] + (2 * TEXT_LINE_DEPTH))

    cropped = frame[top_left:top_right, bot_left: bot_right]
    imgencoded = cv2.imencode('.jpg', cropped)[1]
    
    url = f'https://discord.com/api/v10/channels/{os.getenv("CHANNEL_ID")}/messages'
    headers= {
        # 'Content-Type': 'application/json',
        'Content-Type': 'multipart/form-data',
        'Content-Disposition': 'form-data',
        'Accept': 'application/json',
        'Authorization': f'Bot {os.getenv("DISCORD_TOKEN")}'
    }

    files = {
        'file' : ('image.jpg', imgencoded.tobytes(), 'image/jpeg')
    }

    data = {
        'content': f'<@&{os.getenv("MVP_NOTIFICATION_ROLE_ID")}>', # ping specific role
    }

    response = requests.request('POST', url, headers=headers, data=data, files=files)

    if response.ok: 
        print("discord notification sent ok")

    else:
        print(response)
