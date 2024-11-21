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
        return "Idle Slayer" in GetWindowText(GetForegroundWindow())

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

FORMAT = '%(asctime)-15s [%(name)s] [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
log = logging.getLogger("idle_slayer")


def active(activator):
    if activator == "numlock":
        return window_active() and numlock_active()
    elif activator == "capslock":
        return window_active() and capslock_active()
    else:
        raise Exception("Unknown activator: %s" % activator)


# Defensive Buff (s), Offensive Buff (f), Ultimate Buff (h) -> Mega Buff (v)
KEYBOARD = Controller()
SPRINT_COOLDOWN = 1.0
JUMP_BURST = 2
JUMP_PAUSE = 0.5
       
activator = "numlock"

def tap(key):
    KEYBOARD.press(key)
    sleep(0.01)
    KEYBOARD.release(key)
    sleep(0.01)    


def sprint():
    tap(Key.shift_l)


def jump_high():
    KEYBOARD.press(Key.space)
    sleep(0.15)
    KEYBOARD.release(Key.space)
    sleep(0.01)    

def jump_low():
    tap(Key.space)

def shoot():
    tap(Key.space)

def jump_cycle():
    jump_high()
    shoot()
    sleep(0.35)
    shoot()
    # sleep(0.20)
    sleep(0.18)
    shoot()

while True:
    if not active(activator):
        log.info("Waiting... Press %s to activate" % activator)

        while not active(activator):
            sleep(1)

    log.info("Starting to fight")


    while active(activator):
        sprint()
        jump_cycle()
        sleep(SPRINT_COOLDOWN)
