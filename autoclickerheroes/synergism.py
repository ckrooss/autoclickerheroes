#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from time import sleep, time
import traceback
from pynput.keyboard import Key, Controller
import logging
import re
from subprocess import check_output, CalledProcessError
import os

if os.name == "nt":
    import ctypes
    from win32gui import GetWindowText, GetForegroundWindow

    USER32 = ctypes.WinDLL("User32.dll")

    def window_active():
        return "Synergism" in GetWindowText(GetForegroundWindow())

    def numlock_active():
        return USER32.GetKeyState(0x90)

    def capslock_active():
        return USER32.GetKeyState(0x14)

elif os.name == "posix":
    led_regex = re.compile("LED mask:\\s+(\\d*)")

    def window_active():
        try:
            return b"Idle Slayer" in check_output(["xdotool", "getactivewindow", "getwindowname"])
        except CalledProcessError:
            return False

    def numlock_active():
        led_bitmap = int(led_regex.search(check_output(["xset", "q"]).decode("utf-8")).group(1))
        return led_bitmap & 2

    def capslock_active():
        led_bitmap = int(led_regex.search(check_output(["xset", "q"]).decode("utf-8")).group(1))
        return led_bitmap & 1
else:
    raise Exception("Unknown OS: %s" % os.name)

FORMAT = "%(asctime)-15s [%(name)s] [%(levelname)s] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
log = logging.getLogger("synergism")


def active(activator):
    if activator == "numlock":
        return window_active() and numlock_active()
    elif activator == "capslock":
        return window_active() and capslock_active()
    elif activator == "none":
        return window_active()
    else:
        raise Exception("Unknown activator: %s" % activator)


# Defensive Buff (s), Offensive Buff (f), Ultimate Buff (h) -> Mega Buff (v)
KEYBOARD = Controller()
SHORT_SLEEP = 1.0
MEDIUM_SLEEP = 5.0

activator = "none"


def enter(key):
    if active(activator):
        KEYBOARD.tap(key)


def wait(length):
    if active(activator):
        sleep(length)


TRANS_FIRST = ["1", "2"]
TRANS = ["1", "2", "3", "4", "5"]
REINC = ["6", "7", "8", "9", "e"]


def transcension_cycle():
    enter("1")
    wait(SHORT_SLEEP)
    enter("2")
    wait(SHORT_SLEEP)
    enter("3")
    wait(SHORT_SLEEP)
    enter("4")
    wait(SHORT_SLEEP)
    enter("5")
    wait(SHORT_SLEEP)
    enter("e")
    wait(SHORT_SLEEP)


def first_reincarnation_cycle():
    enter("6")
    wait(SHORT_SLEEP)
    enter("7")
    wait(SHORT_SLEEP)
    enter("e")
    wait(SHORT_SLEEP)


def reincarnation_cycle():
    enter("6")
    wait(SHORT_SLEEP)
    enter("7")
    wait(SHORT_SLEEP)
    enter("8")
    wait(MEDIUM_SLEEP)
    enter("9")
    wait(MEDIUM_SLEEP)
    enter("e")
    wait(MEDIUM_SLEEP)
    enter("0")
    wait(MEDIUM_SLEEP)
    wait(MEDIUM_SLEEP)


def fulll_cycle():
    t1 = time()

    transcension_cycle()
    if not active(activator):
        return

    first_reincarnation_cycle()

    while active(activator):
        transcension_cycle()
        if not active(activator):
            break
        reincarnation_cycle()


while True:
    if not active(activator):
        log.info("Waiting... Press %s to activate" % activator)

        while not active(activator):
            sleep(1)

    log.info("Starting Challenges")

    while active(activator):
        fulll_cycle()
        wait(MEDIUM_SLEEP)
