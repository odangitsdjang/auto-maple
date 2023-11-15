
import time
import cv2
import threading
import ctypes
import mss
import mss.windows
import numpy as np
from src.common import config, utils, settings
from ctypes import wintypes
from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
from ctypes import windll, pointer, wintypes
from src.common import utils
from src.modules.capture import Capture
import cv2

window = {'left': 0,'top': 0,'width': 1366, 'height': 768}
default_window_resolution = {'1366x768':(1366,768),'2560x1440':(2560,1440)}

# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 9

PLAYER_TEMPLATE = cv2.imread('assets/player_template.png', 0)
PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape

MM_TL_TEMPLATE = cv2.imread('assets/minimap_tl_template.png', 0)
MM_BR_TEMPLATE = cv2.imread('assets/minimap_br_template.png', 0)

MMT_HEIGHT = max(MM_TL_TEMPLATE.shape[0], MM_BR_TEMPLATE.shape[0])
MMT_WIDTH = max(MM_TL_TEMPLATE.shape[1], MM_BR_TEMPLATE.shape[1])

user32 = windll.user32
handle = user32.FindWindowW(None, "MapleStory")
rect = wintypes.RECT()

GetDC = windll.user32.GetDC
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
GetClientRect = windll.user32.GetClientRect
CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
SelectObject = windll.gdi32.SelectObject
BitBlt = windll.gdi32.BitBlt
SRCCOPY = 0x00CC0020
GetBitmapBits = windll.gdi32.GetBitmapBits
DeleteObject = windll.gdi32.DeleteObject
ReleaseDC = windll.user32.ReleaseDC

user32.GetWindowRect(handle, pointer(rect)) # output: 1
# pixel location of each, e.g. (78, 78, 1460, 885) which happens to be (78 + 1382, 78 + 807)
# this example is with 1366 x 768, but the extra 16x39 pixels is made up by the borders
rect = (rect.left, rect.top, rect.right, rect.bottom) 

window['left'] = rect[0]
window['top'] = rect[1]
window['width'] = max(rect[2] - rect[0], MMT_WIDTH)
window['height'] = max(rect[3] - rect[1], MMT_HEIGHT)

# get the proper pixel location of top without the borders, set proper width and height
window['top'] = rect[1] + abs(default_window_resolution['2560x1440'][1] - window['height'])
window['width'] = default_window_resolution['2560x1440'][0]
window['height'] = default_window_resolution['2560x1440'][1]

# Calibrate by finding the bottom right corner of the minimap

def screenshot_in_bg(self,handle: HWND, tl_x = 0, tl_y = 0, width=0, height=0):        
    if width == 0 or height == 0:
        # get target window size
        r = RECT()
        GetClientRect(handle, byref(r))
        width, height = r.right, r.bottom

        # 开始截图
        dc = GetDC(handle)
        cdc = CreateCompatibleDC(dc)
        bitmap = CreateCompatibleBitmap(dc, width, height)
        SelectObject(cdc, bitmap)
        BitBlt(cdc, 0, 0, width, height, dc, tl_x, tl_y, SRCCOPY)
        # 截图是BGRA排列，因此总元素个数需要乘以4
        total_bytes = width*height*4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte*total_bytes
        GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
        DeleteObject(bitmap)
        DeleteObject(cdc)
        ReleaseDC(handle, dc)
        # 返回截图数据为numpy.ndarray
        return np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)

frame = Capture.screenshot_in_bg(handle,0,0,window['width'],window['height'])

tl, _ = utils.single_match(frame, MM_TL_TEMPLATE)
_, br = utils.single_match(frame, MM_BR_TEMPLATE)
mm_tl = (
    tl[0] + MINIMAP_BOTTOM_BORDER,
    tl[1] + MINIMAP_TOP_BORDER
)
mm_br = (
    max(mm_tl[0] + PT_WIDTH, br[0] - MINIMAP_BOTTOM_BORDER),
    max(mm_tl[1] + PT_HEIGHT, br[1] - MINIMAP_BOTTOM_BORDER)
)

minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
minimap_sample = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]

minimap = Capture.screenshot_in_bg(handle,mm_tl[0],mm_tl[1],mm_br[0]-mm_tl[0],mm_br[1]-mm_tl[1])
# cv2.imshow('image',img)
# cv2.waitKey(0)