#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The ClickerHeroesAutoclicker plays CLickerHeroes (https://www.clickerheroes.com) for you.
It attacks at maximum speed, buys hero upgrades, activates your powers
and even clicks the collectable fish.

Installation:
    use pip install -r requirements.txt to install dependencies

Usage:
    Activate the NUMLOCK LED on your keyboard to activate the bot. Deactive it to pause the bot.
"""
from __future__ import unicode_literals, print_function
from time import sleep, time
from threading import Timer, RLock
import logging
from datetime import datetime
from os import listdir, mkdir
from os.path import exists
from shutil import move
import ctypes

try:
    USER32 = ctypes.WinDLL ("User32.dll")
    print("Running on win32")
except ImportError:
    print("Not running on win32")

from pykeyboard import PyKeyboard
from pymouse import PyMouse
import PIL.ImageGrab as pg
import numpy as np
import cv2


def clean_logfiles():
    """Move old logfiles into "log" directiory"""
    allfiles = listdir(".")
    logfiles = [f for f in allfiles if f.endswith("_log.txt")]

    if not exists("log"):
        mkdir("log")

    for logfile in logfiles:
        move(logfile, "log")


def setup_logger():
    """Create logger with default loglevels and file + stdout handler"""
    clean_logfiles()

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # STDOUT
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    stdout_handler.set_name("screen")
    stdout_handler.setLevel(logging.DEBUG)

    # LOGFILE
    file_handler = logging.FileHandler(datetime.fromtimestamp(time()).strftime('%Y-%m-%d_%H-%M-%S') + "_log.txt")
    file_handler.setFormatter(formatter)
    file_handler.set_name("file")
    file_handler.setLevel(logging.INFO)

    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    return logger

FISH = cv2.imread("templates/fish.png")
BANANA = cv2.imread("templates/banana.png")
PIE = cv2.imread("templates/pie.png")
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

SCROLL_LOCK = RLock()


def logit(func, **kwargs):
    """
    Decorator to wrap a function into a logging try-catch block
    You can use it to prevent timers from dying
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            import traceback
            log.error("Unknown error: %s", traceback.format_exc())

    return inner


def init_coords():
    """Find required coords, exit if game window is not found"""
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
    
    if img.shape != (1080, 1920):
        img = cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_AREA)

    result = cv2.matchTemplate(img, template, method=cv2.TM_CCOEFF_NORMED)
    _, result = cv2.threshold(result.copy(), 0.9, 1, cv2.THRESH_BINARY)

    _, max_value, _, max_location = cv2.minMaxLoc(result)

    if max_value:
        x, y = max_location

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
    """Returns RGB Values for a pixel at x/y"""
    img = np.array(pg.grab())
    img = img[:, :, ::-1].copy()
    return img[y, x]


def click(x, y):
    """Single left click at x/y"""
    m = PyMouse()
    m.click(x, y, 1)


def active():
    """True if numlock is on"""
    # VK_NUMLOCK is 0x90
    return USER32.GetKeyState(0x90)


def do_attack():
    """Attack the enemy once"""
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
    x, y = find_object(PIE, "pie")

    if x and y:
        click(x, y)
        sleep(CLICK_PERIOD)


def click_bee():
    """Find and click the (seasonal) bee flying across the screen"""
    x, y = find_object(BEE, "bee")

    if x and y:
        for _ in range(60):
            click(x, y)
            sleep(CLICK_PERIOD)


def scroll_up(n=1):
    """Scroll up n times"""
    SCROLL_LOCK.acquire()
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

    SCROLL_LOCK.release()


def scroll_down(n=1):
    """Scroll up n times"""
    SCROLL_LOCK.acquire()
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

    SCROLL_LOCK.release()


def button_is_active(x, y):
    """True if the button at x/y is clickable"""
    # ON ~ [254 250 214]
    # OFF ~ [0 99 69]
    r, g, b = get_pixel_values(x, y)
    if r > 100 and g > 150 and b > 100:
        return True
    else:
        log.debug("Button at {x}/{y} is deactivated ({r}, {g}, {b})".format(x=x, y=y, r=r, g=g, b=b))
        return True


def search_hero(hero, deep=False):
    """
    Search specified hero and set coordinates in COORDINATES["hero"]
    if deep, search the complete list of heroes, else only the visible part
    """

    COORDINATES["hero"] = None

    if not deep:
        x, y = find_object(hero, "hero")

        if x and y:
            COORDINATES["hero"] = (x - 400, y)
    else:
        SCROLL_LOCK.acquire()

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

        SCROLL_LOCK.release()


def get_best_hero():
    """Search for the best available hero (bottom hero)"""
    SCROLL_LOCK.acquire()

    scroll_up(n=-1)
    scroll_down(n=-1)
    sleep(0.5)
    x, y = find_object(GILD, "GILD")

    SCROLL_LOCK.release()

    if x and y:
        return (x - 20, y - 200)
    else:
        return (0, 0)


def upgrade_all():
    """Click the upgrade all button once"""
    SCROLL_LOCK.acquire()

    scroll_up(n=-1)
    scroll_down(n=-1)

    x, y = find_object(UPGRADE, "upgrade all")

    if x and y:
        click(x, y)

    SCROLL_LOCK.release()


@logit
def attack_timer():
    """Endlessly attack, does not return until exit"""
    while active():
        do_attack()
    else:
        return


@logit
def buy_timer():
    """Upgrade the current hero and re-schedule self"""
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
    """Activate powers and re-schedule self"""
    log.info("powers timer ticking")
    do_powers()

    if active():
        timers["powers"] = Timer(POWERS_PERIOD, powers_timer)
        timers["powers"].start()


@logit
def fish_timer():
    """Search + click fish and re-schedule self"""
    log.info("fish timer ticking")
    click_fish()

    if active():
        timers["fish"] = Timer(FISH_PERIOD, fish_timer)
        timers["fish"].start()


@logit
def upgrade_timer():
    """Click upgrade button and re-schedule self"""
    log.info("Upgrade timer ticking")

    upgrade_all()

    if active():
        timers["upgrade"] = Timer(UPGRADE_PERIOD, upgrade_timer)
        timers["upgrade"].start()


@logit
def seasonal_timer():
    """Search + click seasonal clickable and re-schedule self"""
    log.info("Seasonal timer ticking")

    click_bee()

    if active():
        timers["seasonal"] = Timer(SEASONAL_PERIOD, seasonal_timer)
        timers["seasonal"].start()


if __name__ == '__main__':
    log = setup_logger()

    raw_input()
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
