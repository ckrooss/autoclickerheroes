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
from time import sleep
from threading import Timer, RLock
import ctypes
import traceback
from win32gui import GetWindowText, GetForegroundWindow
from pykeyboard import PyKeyboard
from pymouse import PyMouse
import pyscreenshot as pg
import numpy as np
import cv2
import logging
USER32 = ctypes.WinDLL("User32.dll")
FORMAT = '%(asctime)-15s [%(name)s] [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARN)
log = logging.getLogger(__name__)


# Templates
# Seasonal Items
PIE = cv2.imread("templates/pie.png")
SACK = cv2.imread("templates/sack.png")
CANDY = cv2.imread("templates/candy.png")
CHRISTMASCANDY = cv2.imread("templates/christmas_candy.png")

# Heroes
BANANA = ("Banana", cv2.imread("templates/banana.png"))
ALABASTER = ("Alabaster", cv2.imread("templates/alabaster.png"))
CADMIA = ("Cadmia", cv2.imread("templates/cadmia.png"))
LILIN = ("Lilin", cv2.imread("templates/lilin.png"))
BETTY = ("Betty", cv2.imread("templates/betty.png"))
BEE = ("Bee", cv2.imread("templates/bee.png"))
MAX = ("Bomber Max", cv2.imread("templates/max.png"))
MOLOCH = ("Moloch", cv2.imread("templates/moloch.png"))
GOG = ("Gog", cv2.imread("templates/gog.png"))
MIDAS = ("Midas", cv2.imread("templates/midas.png"))

# Misc
FISH = ("Fish", cv2.imread("templates/fish.png"))
NOAUTO = ("No automatic progress", cv2.imread("templates/noauto.png"))
GILD = ("Gild", cv2.imread("templates/gild.png"))
SHOP = ("Shop", cv2.imread("templates/shop.png"))
UPGRADE = ("Upgrade", cv2.imread("templates/upgrade.png"))
POWERUP = ("Powerup", cv2.imread("templates/powerup.png"))
SKULL = ("Skull", cv2.imread("templates/skull.png"))
DOWN = ("Down", cv2.imread("templates/down.png"))
UP = ("Up", cv2.imread("templates/up.png"))

# Config
ACTIVE_HERO = MIDAS
SEASONAL = FISH
CLICK_PERIOD = 1.0 / 50.0
BUY_PERIOD = 10
POWERS_PERIOD = 150
SEASONAL_PERIOD = 5
UPGRADE_PERIOD = 300
BEE_PERIOD = 5
PROGRESS_PERIOD = 600

COORDINATES = dict()

SCROLL_LOCK = RLock()


class CyclicTimer(object):
    """
    Repeated timer that runs in a fixed interval and swallows exceptions

    All timers are running as daemons, so the threads doesn't prevent python from exiting!
    """

    def __init__(self, delay, f):
        self.f = f
        self.timer = Timer(delay, self.wrap_f)
        self.timer.setDaemon(True)
        self.delay = delay

    def wrap_f(self):
        try:
            self.f()
        except KeyboardInterrupt:
            exit()
        except Exception:
            log.warn("Prevented timer from crashing - Exception was:")
            log.warn(traceback.format_exc())

        self.timer = Timer(self.delay, self.wrap_f)
        self.timer.setDaemon(True)
        self.timer.start()

    def start(self):
        return self.timer.start()


def init_coords():
    """Find required coords, exit if game window is not found"""
    x, y = find_object(SHOP)
    COORDINATES["attack"] = (x, y - 200)

    x, y = find_object(UP)
    COORDINATES["up"] = (x, y)
    COORDINATES["powerups"] = (x + 65, y - 20)

    x, y = find_object(DOWN)
    COORDINATES["down"] = (x, y)

    for name, (x, y) in COORDINATES.items():
        if not (x and y):
            log.error("Could not find Game-Window")
            exit(0)


def find_object(template, debug=True):
    """
    Find the object in template and return it's x and y coordinates
    Only works on the primary monitor!
    """
    name, template = template
    img = np.array(pg.grab())

    img = img[:, :, ::-1].copy()

    if img.shape[0] != 1080:
        img = cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_AREA)

    if img.shape[2] != 3:
        a, b, g, r = cv2.split(img)
        img = cv2.merge([b, g, r])

    result = cv2.matchTemplate(img, template, method=cv2.TM_CCOEFF_NORMED)
    _, result = cv2.threshold(result.copy(), 0.9, 1, cv2.THRESH_BINARY)

    _, max_value, _, max_location = cv2.minMaxLoc(result)

    if max_value:
        x, y = max_location

        x_center = (2 * x + template.shape[1]) / 2
        y_center = (2 * y + template.shape[0]) / 2

        # Debug: View rectangle around template + center circle
        if debug:
            cv2.rectangle(img=img,
                          pt1=(x, y),
                          pt2=(x + template.shape[1], y + template.shape[0]),
                          color=(0, 0, 255),
                          thickness=1)

            cv2.circle(img, (x_center, y_center), 22, (0, 255, 0), 1)
            cv2.imshow("asd", img)
            log.debug("Found {name} at {x} {y}".format(name=name, x=x, y=y))
            cv2.waitKey(0)

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
    try:
        if "Clicker Heroes" not in GetWindowText(GetForegroundWindow()).encode("utf-8"):
            return
    except UnicodeDecodeError:
        return

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


def click_seasonal():
    """Find and click the seasonally changing clickable"""
    x, y = find_object(SEASONAL)

    if x and y:
        click(x, y)
        sleep(CLICK_PERIOD)


def click_bee():
    """Find and click the bee flying across the screen"""
    x, y = find_object(BEE)

    if x and y:
        for _ in range(60):
            click(x, y)
            sleep(CLICK_PERIOD)


def scroll(direction, n=1):
    """Scroll n times"""
    with SCROLL_LOCK:
        target = COORDINATES[direction]

        if n > 0:
            for _ in range(n):
                click(*target)
                sleep(CLICK_PERIOD)

            sleep(0.01 * n)

        else:
            # 50 offset to scroll all the way up/down in one click
            offset = 50 if direction == "up" else -50
            click(target[0], target[1] + offset)
            sleep(0.3)


def button_is_active(x, y):
    """True if the button at x/y is clickable"""
    # ON ~ [254 250 214]
    # OFF ~ [0 99 69]
    r, g, b = get_pixel_values(x, y)
    if r > 100 and g > 150 and b > 100:
        return True
    else:
        log.debug("Button at {x}/{y} is deactivated ({r}, {g}, {b})".format(**locals()))
        return True


def search_hero(hero):
    """
    Search specified hero and set coordinates in COORDINATES["hero"]
    """

    COORDINATES["hero"] = None

    x, y = find_object(hero)

    if x and y:
        # offset -400 is the x-distance between hero portrait and upgrade button
        COORDINATES["hero"] = (x - 400, y)

    return


def get_best_hero():
    """Search for the best available hero (bottom hero)"""
    with SCROLL_LOCK:
        scroll("up", n=-1)
        scroll("down", n=-1)
        sleep(0.5)
        x, y = find_object(GILD)

    if x and y:
        return x - 20, y - 200
    else:
        return 0, 0


def upgrade_all():
    """Click the upgrade all button once"""
    with SCROLL_LOCK:
        scroll("up", n=-1)
        scroll("down", n=-1)

        x, y = find_object(UPGRADE)

        if x and y:
            click(x, y)


def buy_timer():
    """Upgrade the curqrent hero and re-schedule self"""
    search_hero(ACTIVE_HERO)

    if COORDINATES.get("hero"):
        if button_is_active(*COORDINATES["hero"]):
            target = COORDINATES["hero"]
        else:
            log.debug("Not buying, not enough money")
            target = (0, 0)
    else:
        target = get_best_hero()

    if all(target):
        kbd = PyKeyboard()
        kbd.press_key("q")
        do_buy(target)
        kbd.release_key("q")


def enable_autoprogress():
    x, y = find_object(NOAUTO)

    if x and y:
        click(x, y)


if __name__ == '__main__':
    init_coords()
    log.setLevel(logging.DEBUG)

    if not active():
        log.debug("Stand by...")
        while not active():
            sleep(0.5)

    CyclicTimer(CLICK_PERIOD, do_attack).start()
    CyclicTimer(BUY_PERIOD, buy_timer).start()
    CyclicTimer(POWERS_PERIOD, do_powers).start()
    CyclicTimer(SEASONAL_PERIOD, click_seasonal).start()
    CyclicTimer(UPGRADE_PERIOD, upgrade_all).start()
    CyclicTimer(BEE_PERIOD, click_bee).start()
    CyclicTimer(PROGRESS_PERIOD, enable_autoprogress).start()

    while active():
        sleep(0.5)
