#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from time import sleep, time
import traceback
from pynput.keyboard import Controller
import logging
from .util import active, Activator


FORMAT = "%(asctime)-15s [%(name)s] [%(levelname)s] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
log = logging.getLogger("ngu_attacker")

# Defensive Buff (s), Offensive Buff (f), Ultimate Buff (h) -> Mega Buff (v)
KEYBOARD = Controller()
HEALING = ["d", "x"]
ATTACKS = ["z", "y", "t", "e", "w"]
DEFENSE = ["a", "r"]
BUFFING = ["v", "g"]
GLOBAL_COOLDOWN = 0.8
KEYTAP_COOLDOWN = 0.05

def execute_all():
    for cmd in HEALING + DEFENSE + BUFFING + ATTACKS:
        # for cmd in BUFFING + ATTACKS:
        # for cmd in ["w"]:
        KEYBOARD.tap(cmd)
        sleep(KEYTAP_COOLDOWN)

def main():
    activator = Activator.Capslock
    window_name = "NGU"

    while True:
        if not active(activator, window_name):
            log.info("Waiting... Press %s to activate" % activator)

            while not active(activator, window_name):
                sleep(1)

        log.info("Starting to fight")

        while active(activator, window_name):
            execute_all()
            sleep(KEYTAP_COOLDOWN)


if __name__ == "__main__":
    main()