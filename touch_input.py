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
    """Return and clear the touch flag so one tap is handled only once."""

    global touch_detected

    if touch_detected:
        touch_detected = False
        return True

    return False
