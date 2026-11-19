#!/usr/bin/env python

from time import sleep
from pynput.mouse import Controller as Mouse, Button
from util import Activator, ActivatorKey

mouse = Mouse()
act = Activator(ActivatorKey.Capslock, "Revolution Idle")

while True:
    if not act.active():
        print(f"Waiting... Press {act.getKey()} to activate")

        while not act.active():
            sleep(1)

    print("Clicking...")

    while act.active():
        mouse.click(Button.left)
        print(f"click {mouse.position}")
        sleep(5)
