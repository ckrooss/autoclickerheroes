#!/usr/bin/env python
from time import sleep, time

from pynput.keyboard import Controller
from util import Activator, ActivatorKey

# Defensive Buff (s), Offensive Buff (f), Ultimate Buff (h) -> Mega Buff (v)
KEYBOARD = Controller()
SHORT_SLEEP = 1.0
MEDIUM_SLEEP = 5.0
ACTIVATOR = Activator(ActivatorKey.Capslock)

def enter(key):
    if ACTIVATOR.active():
        KEYBOARD.tap(key)


def wait(length):
    if ACTIVATOR.active():
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
    if not ACTIVATOR.active():
        return

    first_reincarnation_cycle()

    while ACTIVATOR.active():
        transcension_cycle()
        if not ACTIVATOR.active():
            break
        reincarnation_cycle()


while True:
    ACTIVATOR.waitForActive()
    print("Starting Challenges")

    while ACTIVATOR.active():
        fulll_cycle()
        wait(MEDIUM_SLEEP)
