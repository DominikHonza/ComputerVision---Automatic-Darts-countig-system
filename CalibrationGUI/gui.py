import cv2
from board_calibration import BoardCalibration
from warp import normalize_board
import json
import os
import random
import math

CONFIG_FILE = "calibration.json"
IMAGE_PATH = "frame.jpg"

OFFSET = 1000
TRACKBAR_PADDING = 500


def nothing(_):
    pass


def get_val(name):
    return cv2.getTrackbarPos(name, "Controls") - OFFSET


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def build_config(tl, tr, br, bl, center, angle):
    return {
        "tl": list(tl),
        "tr": list(tr),
        "br": list(br),
        "bl": list(bl),
        "center": list(center),
        "angle": angle,
    }


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


img = cv2.imread(IMAGE_PATH)

if img is None:
    print("Image not found!")
    exit()

h, w = img.shape[:2]
x_max = w + OFFSET + TRACKBAR_PADDING
y_max = h + OFFSET + TRACKBAR_PADDING

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

default_config = {
    "tl": [100, 100],
    "tr": [w - 100, 100],
    "br": [w - 100, h - 100],
    "bl": [100, h - 100],
    "center": [w // 2, h // 2],
    "angle": 64
}

hit_points = [
    (random.randint(0, w), random.randint(0, h))
    for _ in range(5)
]

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        print("Loaded config")
else:
    config = default_config

if "tr" not in config:
    mirrored_tr_x = config["center"][0] + (config["center"][0] - config["tl"][0])
    config["tr"] = [mirrored_tr_x, config["tl"][1]]

if "br" not in config:
    mirrored_br_x = config["center"][0] + (config["center"][0] - config["bl"][0])
    config["br"] = [mirrored_br_x, config["bl"][1]]

# --------------------------------------------------
# WINDOWS
# --------------------------------------------------

cv2.namedWindow("Controls", cv2.WINDOW_NORMAL)
cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
cv2.namedWindow("Warped", cv2.WINDOW_NORMAL)

cv2.resizeWindow("Controls", 950, 400)

# --------------------------------------------------
# TRACKBARS
# --------------------------------------------------

cv2.createTrackbar("tl_x", "Controls", clamp(config["tl"][0] + OFFSET, 0, x_max), x_max, nothing)
cv2.createTrackbar("tl_y", "Controls", clamp(config["tl"][1] + OFFSET, 0, y_max), y_max, nothing)

cv2.createTrackbar("tr_x", "Controls", clamp(config["tr"][0] + OFFSET, 0, x_max), x_max, nothing)
cv2.createTrackbar("tr_y", "Controls", clamp(config["tr"][1] + OFFSET, 0, y_max), y_max, nothing)

cv2.createTrackbar("bl_x", "Controls", clamp(config["bl"][0] + OFFSET, 0, x_max), x_max, nothing)
cv2.createTrackbar("bl_y", "Controls", clamp(config["bl"][1] + OFFSET, 0, y_max), y_max, nothing)

cv2.createTrackbar("br_x", "Controls", clamp(config["br"][0] + OFFSET, 0, x_max), x_max, nothing)
cv2.createTrackbar("br_y", "Controls", clamp(config["br"][1] + OFFSET, 0, y_max), y_max, nothing)

cv2.createTrackbar("center_x", "Controls", clamp(config["center"][0] + OFFSET, 0, x_max), x_max, nothing)
cv2.createTrackbar("center_y", "Controls", clamp(config["center"][1] + OFFSET, 0, y_max), y_max, nothing)

cv2.createTrackbar("angle", "Controls", config.get("angle", 64), 360, nothing)

cv2.createTrackbar("hit_x", "Controls", clamp(config.get("hit", [w//2, h//2])[0] + OFFSET, 0, x_max), x_max, nothing)
cv2.createTrackbar("hit_y", "Controls", clamp(config.get("hit", [w//2, h//2])[1] + OFFSET, 0, y_max), y_max, nothing)


# --------------------------------------------------
# ACTIVE POINT
# --------------------------------------------------

active = "tl"
last_saved_config = None
dragging_point = None


def set_point(name, x, y):
    cv2.setTrackbarPos(
        f"{name}_x",
        "Controls",
        clamp(x + OFFSET, 0, x_max),
    )
    cv2.setTrackbarPos(
        f"{name}_y",
        "Controls",
        clamp(y + OFFSET, 0, y_max),
    )


def get_current_points():
    return {
        "tl": (get_val("tl_x"), get_val("tl_y")),
        "tr": (get_val("tr_x"), get_val("tr_y")),
        "br": (get_val("br_x"), get_val("br_y")),
        "bl": (get_val("bl_x"), get_val("bl_y")),
        "center": (get_val("center_x"), get_val("center_y")),
    }


def find_nearest_point(x, y, max_distance=25):
    nearest_name = None
    nearest_distance = max_distance

    for name, point in get_current_points().items():
        distance = math.hypot(point[0] - x, point[1] - y)
        if distance <= nearest_distance:
            nearest_name = name
            nearest_distance = distance

    return nearest_name


def on_original_mouse(event, x, y, flags, param):
    global active, dragging_point

    if event == cv2.EVENT_LBUTTONDOWN:
        selected = find_nearest_point(x, y)
        if selected is not None:
            active = selected
            dragging_point = selected
            set_point(selected, x, y)
    elif event == cv2.EVENT_MOUSEMOVE and dragging_point is not None:
        set_point(dragging_point, x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        dragging_point = None

def move_point(name, dx, dy):
    current_x = cv2.getTrackbarPos(f"{name}_x", "Controls")
    current_y = cv2.getTrackbarPos(f"{name}_y", "Controls")

    cv2.setTrackbarPos(
        f"{name}_x",
        "Controls",
        clamp(current_x + dx, 0, x_max),
    )

    cv2.setTrackbarPos(
        f"{name}_y",
        "Controls",
        clamp(current_y + dy, 0, y_max),
    )


cv2.setMouseCallback("Original", on_original_mouse)

# --------------------------------------------------
# LOOP
# --------------------------------------------------

while True:

    tl = (get_val("tl_x"), get_val("tl_y"))
    tr = (get_val("tr_x"), get_val("tr_y"))
    bl = (get_val("bl_x"), get_val("bl_y"))
    br = (get_val("br_x"), get_val("br_y"))
    center = (get_val("center_x"), get_val("center_y"))
    
    angle = cv2.getTrackbarPos("angle", "Controls")

    hit = (get_val("hit_x"), get_val("hit_y"))
    current_config = build_config(tl, tr, br, bl, center, angle)

    calibration = BoardCalibration([tl, tr, br, bl])

    try:
        original, warped, results = normalize_board(img, calibration, angle_offset=angle, hit_points=hit_points)
    except Exception as e:
        original = img.copy()
        warped = img.copy()
        cv2.putText(warped, str(e), (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    preview = original.copy()

    #for r in results:
        #print(r)

    # center
    cv2.circle(preview, center, 8, (0,0,255), -1)
    cv2.line(preview, center, (center[0], center[1] + 500), (0,255,255), 2)

    # body
    point_colors = {
        "tl": (255, 0, 0),
        "tr": (255, 0, 0),
        "br": (255, 0, 0),
        "bl": (255, 0, 0),
        "center": (0, 0, 255),
    }
    points = {
        "tl": tl,
        "tr": tr,
        "br": br,
        "bl": bl,
        "center": center,
    }

    for name, point in points.items():
        radius = 10 if name == active else 6
        thickness = 2 if name == active else -1
        cv2.circle(preview, point, radius, point_colors[name], thickness)
        cv2.putText(preview, name, (point[0] + 8, point[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    # highlight active
    cv2.putText(preview, f"ACTIVE: {active}", (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.putText(preview, "1=tl 2=tr 3=br 4=bl 5=center", (10, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1)
    cv2.putText(preview, "drag points with left mouse button", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1)
    
    # Hitpoint
    for p in hit_points:
        cv2.circle(preview, p, 5, (0,255,255), -1)

    cv2.imshow("Original", preview)
    cv2.imshow("Warped", warped)

    key = cv2.waitKeyEx(30)

    # --------------------------------------------------
    # SWITCH ACTIVE
    # --------------------------------------------------

    if key == ord('1'): active = "tl"
    if key == ord('2'): active = "tr"
    if key == ord('3'): active = "br"
    if key == ord('4'): active = "bl"
    if key == ord('5'): active = "center"

    # --------------------------------------------------
    # ARROWS (1px)
    # --------------------------------------------------

    step = 1

    if key == 2490368:   # UP
        move_point(active, 0, -step)
    elif key == 2621440: # DOWN
        move_point(active, 0, step)
    elif key == 2424832: # LEFT
        move_point(active, -step, 0)
    elif key == 2555904: # RIGHT
        move_point(active, step, 0)

    # --------------------------------------------------
    # SHIFT + ARROWS (rychlé)
    # --------------------------------------------------

    fast = 5

    if key == (2490368 + 0x10000):
        move_point(active, 0, -fast)
    elif key == (2621440 + 0x10000):
        move_point(active, 0, fast)
    elif key == (2424832 + 0x10000):
        move_point(active, -fast, 0)
    elif key == (2555904 + 0x10000):
        move_point(active, fast, 0)

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    if key == ord('s'):
        save_config(current_config)
        last_saved_config = current_config
        print("Saved config")

    if current_config != last_saved_config:
        save_config(current_config)
        last_saved_config = current_config

    # EXIT
    if key == ord('q') or key == 27:
        break

cv2.destroyAllWindows()
