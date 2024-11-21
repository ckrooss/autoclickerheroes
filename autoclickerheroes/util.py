import os
from enum import Enum

if os.name == "nt":
    import ctypes
    import pygetwindow 
    
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

    def window_active(name):
        return name in check_output(["kdotool", "getactivewindow", "getwindowname"])

    def numlock_active():
        led_bitmap = int(led_regex.search(check_output(["xset", "q"]).decode("utf-8")).group(1))
        return led_bitmap & 2

    def capslock_active():
        led_bitmap = int(led_regex.search(check_output(["xset", "q"]).decode("utf-8")).group(1))
        return led_bitmap & 1
else:
    raise Exception("Unknown OS: %s" % os.name)


class Activator(Enum):
    Numlock = 1
    Capslock = 2

def active(activator, name):
    if activator == Activator.Numlock:
        return window_active(name) and numlock_active()
    elif activator == Activator.Capslock:
        return window_active(name) and capslock_active()
    else:
        raise Exception("Unknown activator: %s" % activator)
