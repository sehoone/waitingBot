import pyautogui as pyautogui
while True:
    x, y = pyautogui.position()
    print('x: %s, y: %s' % (x, y))