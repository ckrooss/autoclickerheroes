import os
from enum import Enum
from time import sleep

if os.name == "nt":
    import ctypes
    import pygetwindow 

    def get_active_window():
        return pygetwindow.getActiveWindow().title
    
    def window_active(name):
        return name in pygetwindow.getActiveWindow().title

    USER32 = ctypes.WinDLL("User32.dll")
    def numlock_active():
        return USER32.GetKeyState(0x90)

    def capslock_active():
        return USER32.GetKeyState(0x14)
elif os.name == "posix":
    import re
    from subprocess import check_output

    led_regex = re.compile("LED mask:\\s+(\\d*)")

    def get_active_window():
        return check_output(["kdotool", "getactivewindow", "getwindowname"])

    def window_active(name):
        return name.encode("utf-8") in check_output(["kdotool", "getactivewindow", "getwindowname"])

    def numlock_active():
        led_bitmap = int(led_regex.search(check_output(["xset", "q"]).decode("utf-8")).group(1))
        return led_bitmap & 2

    def capslock_active():
        led_bitmap = int(led_regex.search(check_output(["xset", "q"]).decode("utf-8")).group(1))
        return led_bitmap & 1
else:
    raise Exception("Unknown OS: %s" % os.name)

class ActivatorKey(Enum):        
    Numlock = 1
    Capslock = 2

class Activator():
    def __init__(self, key: ActivatorKey, name: str = ""):
        self.__key = key
        self.__name = name
        assert key in [ActivatorKey.Numlock, ActivatorKey.Capslock]

    def waitForActive(self):
        if not self.active():
            print(f"Waiting for {self.__key} and Active Window \"{self.__name}\"...")

        while not self.active():
            sleep(0.5)

    def active(self):
        match self.__key:
            case ActivatorKey.Numlock:
                return window_active(self.__name) and numlock_active()
            case ActivatorKey.Capslock:
                return window_active(self.__name) and capslock_active()
            case _:
                raise Exception("Unknown activator: %s" % self.__key)

    def getKey(self):
        return self.__key
