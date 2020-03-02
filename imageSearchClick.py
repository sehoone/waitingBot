import cv2
import numpy as np
import pyautogui
import random
import time
import platform
import subprocess
import schedule

is_retina = False
if platform.system() == "Darwin":
    is_retina = subprocess.call("system_profiler SPDisplaysDataType | grep 'retina'", shell=True)

def r(num, rand):
    return num + rand * random.random()
    
def imagesearch(image, precision=0.8):
    im = pyautogui.screenshot()
    if is_retina:
        im.thumbnail((round(im.size[0] * 0.5), round(im.size[1] * 0.5)))
    # im.save('testarea.png') useful for debugging purposes, this will save the captured region as "testarea.png"
    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return max_loc

def click_image(image, pos, action, timestamp, offset=5):
    img = cv2.imread(image)
    height, width, channels = img.shape
    pyautogui.moveTo(pos[0] + r(width / 2, offset), pos[1] + r(height / 2, offset),
                     timestamp)
    pyautogui.click(button=action)

def job():
    try:
        pos = imagesearch("d:/dev/pythonWorkspace/waitingBot/selectServer.png")
        if pos[0] != -1:
            print("position : ", pos[0], pos[1])
            pyautogui.moveTo(pos[0], pos[1])
        else:
            print("image not found")    

        if pos[0] != -1:
            click_image("d:/dev/pythonWorkspace/waitingBot/selectServer.png", pos, "left", 0.2, offset=5)    
    except:
        print('exception')


schedule.every(3).seconds.do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)