import cv2
# import utils 
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def send_img_msg_to_discord(img, mention=True):
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

    if mention: files["payload_json"] = (None, json.dumps(data))

    # response = requests.post(url, headers=headers, json=data) # send string only, header may need to add Content-Type
    response = requests.post(url, headers=headers, files=files)

    if response.ok: 
        print("discord notification sent ok")

    else:
        response.raise_for_status()

def send_msg_to_discord(msg):
    url = f'https://discord.com/api/v10/channels/{os.getenv("CHANNEL_ID")}/messages'
    
    headers= {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bot {os.getenv("DISCORD_TOKEN")}'
    }

    data = {
        'content': f'{msg}>'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.ok: 
        print("discord notification sent ok")

    else:
        response.raise_for_status()
