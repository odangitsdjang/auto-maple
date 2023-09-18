"""The central program that ties all the modules together."""

import time
from src.modules.bot import Bot
from src.modules.capture import Capture
from src.modules.notifier import Notifier
from src.modules.listener import Listener
from src.modules.gui import GUI
from src.common import settings, config
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full_screen', action='store_true')
    # parser.add_argument('-cb', type=str, default="")
    # parser.add_argument('-rt', type=str, default="")
    # parser.add_argument('--rent', action='store_true')
    # parser.add_argument('-dk', action='store_true')
    args = parser.parse_args()
    print(args)
    if args.full_screen:
        settings.full_screen = True
    # if args.rent:
    #     settings.rent_frenzy = True
    # if args.dk:
    #     settings.driver_key = True
        
bot = Bot()
capture = Capture()
notifier = Notifier()
listener = Listener()

bot.start()
while not bot.ready:
    time.sleep(0.01)

capture.start()
while not capture.ready:
    time.sleep(0.01)

notifier.start()
while not notifier.ready:
    time.sleep(0.01)

listener.start()
while not listener.ready:
    time.sleep(0.01)

print('\n[~] Successfully initialized Auto Maple')

gui = GUI()
gui.start()
