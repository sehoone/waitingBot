import cv2
import numpy as np
import pyautogui
import random
import time
import platform
import subprocess
import schedule
import serial
from PIL import ImageGrab

ser = serial.Serial('COM7', 9600)
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
    searchX = pos[0] + round(r(width / 2, 5))
    searchY = pos[1] + round(r(height / 2, 5))
    print("searchX : ",searchX)
    print("searchY : ",searchY)
    pyautogui.moveTo(searchX, searchY,
                     timestamp)
    pyautogui.click(button=action)

def selectImage(image):
    pos = imagesearch(image)
    if pos[0] != -1:
        img2 = cv2.imread(image)
        height, width, channels = img2.shape
        searchX = pos[0] + round(r(width / 2, 5))
        searchY = pos[1] + round(r(height / 2, 5))
        print("searchX : ",searchX)
        print("searchY : ",searchY)
        sumXY = str(searchX) + "," + str(searchY) + ";"
        print("sumXY : ",sumXY)
        ser.write(str.encode(sumXY))
        #pyautogui.click("LEFT")
        #ser.write(b'Click')
    else:
        print("image not found") 

def screenCapture():
    captureImg = ImageGrab.grab()
    captureImg.save("D:/dev/pythonWorkspace/waitingBot/serialComunity/image/captureImg.png")

def job():
        selectImage("D:/dev/pythonWorkspace/waitingBot/serialComunity/image/selectServerJuJak.png")
        time.sleep(2)
        selectImage("D:/dev/pythonWorkspace/waitingBot/serialComunity/image/loginBtn.png") 
        time.sleep(2)
        screenCapture()

schedule.every(8).seconds.do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)
