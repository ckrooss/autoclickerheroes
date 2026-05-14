#!/usr/bin/env python
from time import sleep
from pynput.keyboard import Key, Controller
from util import Activator, ActivatorKey

activator = Activator(ActivatorKey.Numlock, "Slayer")

# Defensive Buff (s), Offensive Buff (f), Ultimate Buff (h) -> Mega Buff (v)
KEYBOARD = Controller()
SPRINT_COOLDOWN = 1.0
JUMP_BURST = 2
JUMP_PAUSE = 0.5

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
    sleep(0.18)
    shoot()


while True:
    if not activator.active():
        print("Waiting... Press %s to activate" % activator)

        while not activator.active():
            sleep(1)

    print("Starting to fight")

    while activator.active():
        sprint()
        jump_cycle()
        sleep(SPRINT_COOLDOWN)
