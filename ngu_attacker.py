#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from time import sleep, time
import traceback
from pynput.keyboard import Key, Controller
import logging
import re
from subprocess import check_output
import os

if os.name == "nt":
    import ctypes
    from win32gui import GetWindowText, GetForegroundWindow
    USER32 = ctypes.WinDLL("User32.dll")

    def window_active():
        return "NGU Idle" in GetWindowText(GetForegroundWindow())

    def numlock_active():
        return USER32.GetKeyState(0x90)

    def capslock_active():
        return USER32.GetKeyState(0x14)

elif os.name == "posix":

    led_regex = re.compile("LED mask:\\s+(\\d*)")

    def window_active():
        return b"NGU Idle" in check_output(["xdotool", "getactivewindow", "getwindowname"])

    def numlock_active():
        led_bitmap = int(led_regex.search(check_output(["xset", "q"]).decode("utf-8")).group(1))
        return led_bitmap & 2

    def capslock_active():
        led_bitmap = int(led_regex.search(check_output(["xset", "q"]).decode("utf-8")).group(1))
        return led_bitmap & 1
else:
    raise Exception("Unknown OS: %s" % os.name)

FORMAT = '%(asctime)-15s [%(name)s] [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
log = logging.getLogger("ngu_attacker")


def active(activator):
    if activator == "numlock":
        return window_active() and numlock_active()
    elif activator == "capslock":
        return window_active() and capslock_active()
    else:
        raise Exception("Unknown activator: %s" % activator)


# Defensive Buff (s), Offensive Buff (f), Ultimate Buff (h) -> Mega Buff (v)
KEYBOARD = Controller()
HEALING = ["d", "x"]
ATTACKS = ["z", "y", "t", "e", "w"]
DEFENSE = ["a",  "r"]
BUFFING = ["v", "g"]
GLOBAL_COOLDOWN = 0.8
KEYTAP_COOLDOWN = 0.05

def execute_all():
    for cmd in HEALING + DEFENSE + BUFFING + ATTACKS:
    # for cmd in BUFFING + ATTACKS:
    # for cmd in ["w"]:
        KEYBOARD.tap(cmd)
        sleep(KEYTAP_COOLDOWN)

last_click = 0
activator = "capslock"

while True:
    if not active(activator):
        log.info("Waiting... Press %s to activate" % activator)

        while not active(activator):
            sleep(1)

    log.info("Starting to fight")


    while active(activator):
        execute_all()
        sleep(KEYTAP_COOLDOWN)
