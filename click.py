#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The ClickerHeroesAutoclicker plays CLickerHeroes (https://www.clickerheroes.com) for you.
It attacks at maximum speed, buys hero upgrades, activates your powers and even clicks the collectable fish.

Usage:
    Activate the NUMLOCK LED on your keyboard to activate the bot. Deactive it to pause the bot.

Requirements:
    Windows
    pywin32
    opencv3
    numpy
    Pillow
"""

try:
    import win32api
    import win32con
    print("Windows Mode")
except ImportError:
    pass

from pykeyboard import PyKeyboard
from time import sleep, time
import PIL.ImageGrab as pg
import numpy as np
import cv2
from threading import Timer, RLock
import logging
from datetime import datetime
from os import listdir, mkdir
from os.path import exists
from shutil import move


def clean_logfiles():
    allfiles = listdir(".")
    logfiles = [f for f in allfiles if f.endswith("_log.txt")]

    if not exists("log"):
        mkdir("log")

    for f in logfiles:
        move(f, "log")


def setup_logger():
    clean_logfiles()

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # STDOUT
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.set_name("screen")
    ch.setLevel(logging.DEBUG)

    # LOGFILE
    fh = logging.FileHandler(datetime.fromtimestamp(time()).strftime('%Y-%m-%d_%H-%M-%S') + "_log.txt")
    fh.setFormatter(formatter)
    fh.set_name("file")
    fh.setLevel(logging.INFO)

    log.addHandler(ch)
    log.addHandler(fh)

    return log

FISH = cv2.imread("templates/candy.png")
BANANA = cv2.imread("templates/banana.png")
LILIN = cv2.imread("templates/lilin.png")
BEE = cv2.imread("templates/bee.png")
POWERUP = cv2.imread("templates/powerup.png")
SKULL = cv2.imread("templates/skull.png")
DOWN = cv2.imread("templates/down.png")
UP = cv2.imread("templates/up.png")
GILD = cv2.imread("templates/gild.png")
SHOP = cv2.imread("templates/shop.png")
UPGRADE = cv2.imread("templates/upgrade.png")

CLICK_PERIOD = 1.0 / 50.0
BUY_PERIOD = 10
POWERS_PERIOD = 150
FISH_PERIOD = 60
UPGRADE_PERIOD = 300
SEASONAL_PERIOD = 10

COORDINATES = dict()

scroll_lock = RLock()


def logit(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            import traceback
            log.error("Unknown error: %s", traceback.format_exc())

    return inner


def init_coords():
    x, y = find_object(SHOP, "shop")
    COORDINATES["attack"] = (x, y - 200)

    x, y = find_object(UP, "up-arrow")
    COORDINATES["up"] = (x, y)
    COORDINATES["powerups"] = (x + 65, y - 20)

    x, y = find_object(DOWN, "down-arrow")
    COORDINATES["down"] = (x, y)

    for name, (x, y) in COORDINATES.items():
        if not (x and y):
            log.error("Could not find Game-Window")
            exit(0)


def find_object(template, name=""):
    """
    Find the object in template and return it's x and y coordinates
    Only works on the primary monitor!
    """
    img = np.array(pg.grab())
    img = img[:, :, ::-1].copy()
    result = cv2.matchTemplate(img, template, method=cv2.TM_CCOEFF_NORMED)
    _, result = cv2.threshold(result.copy(), 0.8, 1, cv2.THRESH_BINARY)

    _, maxVal, _, maxLoc = cv2.minMaxLoc(result)

    if maxVal:
        x, y = maxLoc

        x_center = (2*x + template.shape[1]) / 2
        y_center = (2*y + template.shape[0]) / 2

        # Debug: View rectangle around template + center circle
        if name == "debug":
            cv2.rectangle(img, (x, y), (x + template.shape[1], y + template.shape[0]), (0, 0, 255), 1)
            cv2.circle(img, (x_center, y_center), 22, (0, 255, 0), 1)
            cv2.imshow("asd", img)
            cv2.waitKey(0)

        log.debug("Found {name} at {x} {y}".format(name=name, x=x, y=y))

        return x_center, y_center
    else:
        log.debug("Can't find {name}".format(name=name))
        return 0, 0


def get_pixel_values(x, y):
    img = np.array(pg.grab())
    img = img[:, :, ::-1].copy()
    return img[y, x]


def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def active():
    return win32api.GetKeyState(win32con.VK_NUMLOCK)


def do_attack():
    """Attack once"""
    click(*COORDINATES["attack"])
    sleep(CLICK_PERIOD)


def do_buy(hero_coords):
    """Buy a single upgrade for the highest tier hero"""

    x, y = hero_coords

    if x and y:
        click(*hero_coords)
        sleep(CLICK_PERIOD)


def do_powers():
    """Activate default maximum combo once"""
    for i in [1, 2, 3, 4, 5, 7, 8, 6, 9]:
        x, y = COORDINATES["powerups"]
        click(x, y + 55 * (i - 1))
        sleep(CLICK_PERIOD)


def click_fish():
    """Find and click the fish-clickable"""
    x, y = find_object(FISH, "fish")

    if x and y:
        click(x, y)
        sleep(CLICK_PERIOD)


def click_bee():
    x, y = find_object(BEE, "bee")

    if x and y:
        for _ in range(60):
            click(x, y)
            sleep(CLICK_PERIOD)


def scroll_up(n=1):
    scroll_lock.acquire()
    up = COORDINATES["up"]
    if n > 0:

        for _ in range(n):
            click(*up)
            sleep(CLICK_PERIOD)

        sleep(0.01 * n)

    else:
        up = up[0], up[1] + 50
        click(*up)
        sleep(0.3)

    scroll_lock.release()


def scroll_down(n=1):
    scroll_lock.acquire()
    down = COORDINATES["down"]
    if n > 0:
        for _ in range(n):
            click(*down)
            sleep(CLICK_PERIOD)

        sleep(0.01 * n)

    else:
        down = down[0], down[1] - 50
        click(*down)
        sleep(0.3)

    scroll_lock.release()


def button_is_active(x, y):
    # ON ~ [254 250 214]
    # OFF ~ [0 99 69]
    r, g, b = get_pixel_values(x, y)
    if (r > 100 and g > 150 and b > 100):
        return True
    else:
        log.debug("Button at %s/%s is deactivated (%s, %s, %s)" % (x, y, r, g, b))
        return True


def search_hero(hero, deep=False):
    COORDINATES["hero"] = None

    if not deep:
        x, y = find_object(hero, "hero")

        if x and y:
            COORDINATES["hero"] = (x - 400, y)
    else:
        scroll_lock.acquire()

        scroll_up(n=-1)

        while True:
            scroll_down(n=3)

            x, y = find_object(hero, "hero")

            if x and y:
                COORDINATES["hero"] = (x - 400, y)
                break

            x, y = find_object(GILD, "gild")

            if x and y:
                log.info("No hero yet")
                break

        scroll_lock.release()


def get_best_hero():
    scroll_lock.acquire()

    scroll_up(n=-1)
    scroll_down(n=-1)
    sleep(0.5)
    x, y = find_object(GILD, "GILD")

    scroll_lock.release()

    if x and y:
        return (x - 20, y - 200)
    else:
        return (0, 0)


def upgrade_all():
    scroll_lock.acquire()

    scroll_up(n=-1)
    scroll_down(n=-1)

    x, y = find_object(UPGRADE, "upgrade all")

    if x and y:
        click(x, y)

    scroll_lock.release()


@logit
def attack_timer():
    while active():
        do_attack()
    else:
        return


@logit
def buy_timer():
    log.info("buy timer ticking")
    search_hero(LILIN)

    if COORDINATES.get("hero"):
        if button_is_active(*COORDINATES["hero"]):
            target = COORDINATES["hero"]
        else:
            log.debug("Not buying, not enough money")
            target = [0, 0]
    else:
        target = get_best_hero()

    if all(target):
        kbd = PyKeyboard()
        kbd.press_key("q")
        do_buy(target)
        kbd.release_key("q")

    if active():
        timers["buy"] = Timer(BUY_PERIOD, buy_timer)
        timers["buy"].start()


@logit
def powers_timer():
    log.info("powers timer ticking")
    do_powers()

    if active():
        timers["powers"] = Timer(POWERS_PERIOD, powers_timer)
        timers["powers"].start()


@logit
def fish_timer():
    log.info("fish timer ticking")
    click_fish()

    if active():
        timers["fish"] = Timer(FISH_PERIOD, fish_timer)
        timers["fish"].start()


@logit
def upgrade_timer():
    log.info("Upgrade timer ticking")

    upgrade_all()

    if active():
        timers["upgrade"] = Timer(UPGRADE_PERIOD, upgrade_timer)
        timers["upgrade"].start()


@logit
def seasonal_timer():
    log.info("Seasonal timer ticking")

    click_bee()

    if active():
        timers["seasonal"] = Timer(SEASONAL_PERIOD, seasonal_timer)
        timers["seasonal"].start()


if __name__ == '__main__':
    log = setup_logger()

    init_coords()

    while True:
        while not active():
            log.debug("Stand by...")
            sleep(0.5)

        timers = {"attack": Timer(CLICK_PERIOD, attack_timer),
                  "buy": Timer(BUY_PERIOD, buy_timer),
                  "powers": Timer(POWERS_PERIOD, powers_timer),
                  "fish": Timer(3, fish_timer),
                  "upgrade": Timer(5, lambda: None),
                  "seasonal": Timer(10, seasonal_timer)}

        [t.start() for t in timers.values()]

        timers["attack"].join()

        log.info("Canceling timers")

        while any([t.is_alive() for t in timers.values()]):
            [t.cancel() for t in timers.values()]

    log.info("Exiting")
