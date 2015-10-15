import win32api
import win32con
from itertools import cycle
from time import sleep
import PIL.ImageGrab as pg
import numpy as np
import cv2

FISH = cv2.imread("fish.png")

# LEFT SCREEN
ATTACK = (-642, 566)
BUY = (-1488, 834)
POWERS = (-914, 360)

# RIGHT SCREEN
ATTACK = (1296, 558)
BUY = (432, 819)
POWERS = (1001, 360)


def find_fish():
    """
    Find the fish-object and return it's x and y coordinates
    Only works on the primary monitor at 1920x1080!
    """
    img = np.array(pg.grab())
    img = img[:, :, ::-1].copy()
    result = cv2.matchTemplate(img, FISH, method=cv2.TM_CCOEFF_NORMED)
    _, result = cv2.threshold(result.copy(), 0.9, 1, cv2.THRESH_BINARY)

    _, maxVal, _, maxLoc = cv2.minMaxLoc(result)

    if maxVal:
        # Add dirty offsets because result.shape != img.shape
        x, y = maxLoc
        y = 1080 - y
        x += 10
        y += 160

        return x, y
    else:
        return 0, 0


def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def active():
    """True if click should be continued"""
    return win32api.GetKeyState(win32con.VK_NUMLOCK)


def do_attack():
    """Attack once"""
    click(*ATTACK)
    sleep(1.0 / 50.0)


def do_buy():
    """Buy a single upgrade for the highest tier hero"""
    click(*BUY)
    sleep(1.0 / 60.0)


def do_powers():
    """Activate default maximum combo once"""
    for i in [1, 2, 3, 4, 5, 7, 8, 6, 9]:
        x, y = POWERS
        click(x, y + 55 * (i - 1))
        sleep(0.05)


def click_fish():
    """Find and click the fish-clickable"""
    x, y = find_fish()
    if x and y:
        print("Caught a fish at %s:%s" % (x, y))
        click(x, y)
        sleep(1)

# TODO: Create timer based events
for i in cycle(range(1, 1000)):
    if active():
        for _ in range(10):
            do_attack()

        if i % 99 == 0:
            click_fish()
            for _ in range(10):
                do_buy()

        if i % 999 == 0:
            do_powers()
    else:
        print("Standby...")
        sleep(0.5)
