"""Touch input handling for player switching in the legacy darts system.

Author:
    xhonza04 Dominik Honza

Description:
    This module listens to the touchscreen input device and exposes a simple
    edge-triggered flag so the main loop can react to player changes.
"""

from evdev import InputDevice, ecodes
import threading

DEVICE_PATH = "/dev/input/event0"

device = InputDevice(DEVICE_PATH)

touch_detected = False


def touch_thread():
    """Listen for touch events and mark when the screen is pressed."""

    global touch_detected

    for event in device.read_loop():

        # dotyk prstem
        if event.type == ecodes.EV_KEY:
            if event.code == ecodes.BTN_TOUCH and event.value == 1:
                touch_detected = True


def start_touch():
    """Start background monitoring of the touchscreen input device."""

    thread = threading.Thread(target=touch_thread, daemon=True)
    thread.start()


def check_touch():
    """Return and clear the touch flag so one tap is handled only once.

    Returns:
        bool: ``True`` if a new touch event was detected since the last check.
    """

    global touch_detected

    if touch_detected:
        touch_detected = False
        return True

    return False
