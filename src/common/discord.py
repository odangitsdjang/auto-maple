import cv2
# import utils 
import requests
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

def send_img_msg_to_discord(img, channel=os.getenv("MVP_CHANNEL_ID"), bot_token=os.getenv("DISCORD_MVP_TOKEN"), mention=True):
    imencoded  = cv2.imencode(".jpg", img)[1]

    url = f'https://discord.com/api/v10/channels/{channel}/messages'
    headers= {
        'Accept': 'application/json',
        'Authorization': f'Bot {bot_token}'
    }

    files = {
        'image.jpg': imencoded.tobytes()
    }

    data = {
        'content': f'<@&{os.getenv("MVP_NOTIFICATION_ROLE_ID")}>', # ping specific role
    }

    if mention: files["payload_json"] = (None, json.dumps(data))

    # response = requests.post(url, headers=headers, json=data) # send string only, header may need to add Content-Type
    response = requests.post(url, headers=headers, files=files)

    if response.ok: 
        print("discord notification sent ok")

    else:
        response.raise_for_status()

def send_msg_to_discord(msg, channel=os.getenv("ESPECIA_CHANNEL_ID"), bot_token=os.getenv("DISCORD_ESPECIA_TOKEN"), include_time=True):
    url = f'https://discord.com/api/v10/channels/{channel}/messages'
    
    headers= {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bot {bot_token}'
    }

    
    local_time = datetime.now(timezone.utc).astimezone().strftime("%I:%M:%S.%f")
    print(local_time)

    print(datetime.now(timezone.utc).astimezone().tzinfo)

    data = {
        'content': f'<@&{os.getenv("MVP_NOTIFICATION_ROLE_ID")}> {include_time and local_time} {msg}'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.ok: 
        print("discord notification sent ok")

    else:
        response.raise_for_status()
