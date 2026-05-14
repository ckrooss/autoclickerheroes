#!/usr/bin/env python
"""The ClickerHeroesAutoclicker plays ClickerHeroes (https://www.clickerheroes.com) for you.

It attacks at maximum speed, buys hero upgrades, activates your powers
and even clicks the collectable fish.

Installation:
    use `uv sync` and `uv run`

Usage:
    Activate the NUMLOCK LED on your keyboard to activate the bot. Deactive it to pause the bot.
"""

import sys
import traceback
from threading import RLock, Timer
from time import sleep

import cv2
import numpy as np
import pyscreenshot as pg
from pynput.keyboard import Controller as Keyboard
from pynput.mouse import Button as MouseButton
from pynput.mouse import Controller as Mouse
from util import Activator, ActivatorKey

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

COORDINATES = {}

SCROLL_LOCK = RLock()

MOUSE = Mouse()
KEYBOARD = Keyboard()
ACTIVATOR = Activator(ActivatorKey.Numlock, "NGU")


class CyclicTimer(object):
    """Repeated timer that runs in a fixed interval and swallows exceptions.

    All timers are running as daemons, so the threads doesn't prevent python from exiting!
    """

    def __init__(self, delay, f):
        self.f = f
        self.timer = Timer(delay, self.wrap_f)
        self.timer.daemon = True
        self.delay = delay

    def wrap_f(self):
        try:
            self.f()
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Prevented timer from crashing - Exception was: {e}")
            print(traceback.format_exc())

        self.timer = Timer(self.delay, self.wrap_f)
        self.timer.daemon = True
        self.timer.start()

    def start(self):
        """Start the timer."""
        return self.timer.start()


def init_coords():
    """Find required coords, exit if game window is not found."""
    x, y = find_object(SHOP)
    COORDINATES["attack"] = (x, y - 200)

    x, y = find_object(UP)
    COORDINATES["up"] = (x, y)
    COORDINATES["powerups"] = (x + 65, y - 20)

    x, y = find_object(DOWN)
    COORDINATES["down"] = (x, y)

    for (x, y) in COORDINATES.values():
        if not (x and y):
            print("Could not find Game-Window")
            sys.exit(0)


def find_object(template, debug=True):
    """Find the object in template and return it's x and y coordinates.

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
            cv2.rectangle(
                img=img, pt1=(x, y), pt2=(x + template.shape[1], y + template.shape[0]), color=(0, 0, 255), thickness=1
            )

            cv2.circle(img, (x_center, y_center), 22, (0, 255, 0), 1)
            cv2.imshow("asd", img)
            print(f"Found {name} at {x} {y}")
            cv2.waitKey(0)

        return x_center, y_center

    print(f"Can't find {name}")
    return 0, 0


def get_pixel_values(x, y):
    """Return RGB Values for a pixel at x/y."""
    img = np.array(pg.grab())
    img = img[:, :, ::-1].copy()
    return img[y, x]


def click(x, y):
    """Single left click at x/y."""
    if not ACTIVATOR.active():
        return

    MOUSE.position = (x, y)
    MOUSE.click(MouseButton.left)


def do_attack():
    """Attack the enemy once."""
    click(*COORDINATES["attack"])
    sleep(CLICK_PERIOD)


def do_buy(hero_coords):
    """Buy a single upgrade for the highest tier hero."""
    x, y = hero_coords

    if x and y:
        click(*hero_coords)
        sleep(CLICK_PERIOD)


def do_powers():
    """Activate default maximum combo once."""
    for i in [1, 2, 3, 4, 5, 7, 8, 6, 9]:
        x, y = COORDINATES["powerups"]
        click(x, y + 55 * (i - 1))
        sleep(CLICK_PERIOD)


def click_seasonal():
    """Find and click the seasonally changing clickable."""
    x, y = find_object(SEASONAL)

    if x and y:
        click(x, y)
        sleep(CLICK_PERIOD)


def click_bee():
    """Find and click the bee flying across the screen."""
    x, y = find_object(BEE)

    if x and y:
        for _ in range(60):
            click(x, y)
            sleep(CLICK_PERIOD)


def scroll(direction, n=1):
    """Scroll n times."""
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
    """Return True if the button at x/y is clickable."""
    # ON ~ [254 250 214]
    # OFF ~ [0 99 69]
    r, g, b = get_pixel_values(x, y)
    if r > 100 and g > 150 and b > 100:
        return True

    print("Button at {x}/{y} is deactivated ({r}, {g}, {b})".format(**locals()))
    return True


def search_hero(hero):
    """Search specified hero and set coordinates in COORDINATES["hero"]."""
    COORDINATES["hero"] = None

    x, y = find_object(hero)

    if x and y:
        # offset -400 is the x-distance between hero portrait and upgrade button
        COORDINATES["hero"] = (x - 400, y)


def get_best_hero():
    """Search for the best available hero (bottom hero)."""
    with SCROLL_LOCK:
        scroll("up", n=-1)
        scroll("down", n=-1)
        sleep(0.5)
        x, y = find_object(GILD)

    if x and y:
        return x - 20, y - 200

    return 0, 0


def upgrade_all():
    """Click the upgrade all button once."""
    with SCROLL_LOCK:
        scroll("up", n=-1)
        scroll("down", n=-1)

        x, y = find_object(UPGRADE)

        if x and y:
            click(x, y)


def buy_timer():
    """Upgrade the curqrent hero and re-schedule self."""
    search_hero(ACTIVE_HERO)

    if COORDINATES.get("hero"):
        if button_is_active(*COORDINATES["hero"]):
            target = COORDINATES["hero"]
        else:
            print("Not buying, not enough money")
            target = (0, 0)
    else:
        target = get_best_hero()

    if all(target):
        KEYBOARD.press("q")
        do_buy(target)
        KEYBOARD.release("q")


def enable_autoprogress():
    x, y = find_object(NOAUTO)

    if x and y:
        click(x, y)


if __name__ == "__main__":
    init_coords()
    ACTIVATOR.waitForActive()

    CyclicTimer(CLICK_PERIOD, do_attack).start()
    CyclicTimer(BUY_PERIOD, buy_timer).start()
    CyclicTimer(POWERS_PERIOD, do_powers).start()
    CyclicTimer(SEASONAL_PERIOD, click_seasonal).start()
    CyclicTimer(UPGRADE_PERIOD, upgrade_all).start()
    CyclicTimer(BEE_PERIOD, click_bee).start()
    CyclicTimer(PROGRESS_PERIOD, enable_autoprogress).start()

    while ACTIVATOR.active():
        sleep(0.5)
