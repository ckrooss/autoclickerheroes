#!/usr/bin/env python
from time import sleep

from pynput.keyboard import Controller

from .util import Activator, ActivatorKey

# Defensive Buff (s), Offensive Buff (f), Ultimate Buff (h) -> Mega Buff (v)
KEYBOARD = Controller()
HEALING = ["d", "x"]
ATTACKS = ["z", "y", "t", "e", "w"]
DEFENSE = ["a", "r"]
BUFFING = ["v", "g"]
GLOBAL_COOLDOWN = 0.8
KEYTAP_COOLDOWN = 0.05
ACTIVATOR = Activator(ActivatorKey.Capslock, "NGU")

def execute_all():
    for cmd in HEALING + DEFENSE + BUFFING + ATTACKS:
        # for cmd in BUFFING + ATTACKS:
        # for cmd in ["w"]:
        KEYBOARD.tap(cmd)
        sleep(KEYTAP_COOLDOWN)

def main():
    while True:
        ACTIVATOR.waitForActive()
        print("Starting to fight")

        while ACTIVATOR.active():
            execute_all()
            sleep(KEYTAP_COOLDOWN)


if __name__ == "__main__":
    main()
