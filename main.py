from dart_detector import DartDetector
from stream_server import start_stream_server, set_frame
from display import display_score, display_calibration
from touch_input import start_touch, check_touch
from score_buffer import ScoreBuffer
import cv2
import time
import numpy as np
import os

# --------------------------------------------------------------
# GAME SETUP
# --------------------------------------------------------------
player1 = 501
player2 = 501
currentPlayer = 1
# --------------------------------------------------------------
# SETUP
# --------------------------------------------------------------
print("Starting camera...")

counter = 0
darts = []

width = 1280
height = 720
cropLeft = 400
cropRight = 120

overlayWidth = width - cropLeft - cropRight
overlayHeight = height

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Waiting for camera auto exposure...")

FRAME_PATH = os.path.join(os.path.dirname(__file__), "frame.jpg")

def nextPlayer ():
    # sub players points
    display_calibration()
    for _ in range(20):
        cap.read()
    
    base_frame = get_stable_frame(cap, 30)
    save_calibration_frame(base_frame)
    return base_frame

def apply_score(darts):

    global player1, player2

    total = 0

    for d in darts:
        total += d[2]

    if currentPlayer == 1:
        player1 -= total
    else:
        player2 -= total

def switch_player():

    global currentPlayer

    if currentPlayer == 1:
        currentPlayer = 2
    else:
        currentPlayer = 1

def get_stable_frame(cap, samples=10):

    frames = []

    for _ in range(samples):

        ret, frame = cap.read()

        if not ret:
            continue

        frame = frame[:, cropLeft:-cropRight]
        frames.append(frame.astype(np.float32))
        time.sleep(0.1)

    avg = np.mean(frames, axis=0)

    return avg.astype(np.uint8)


def save_calibration_frame(frame):
    cv2.imwrite(FRAME_PATH, frame)
    print(f"Saved calibration frame: {FRAME_PATH}")

time.sleep(2)

# --------------------------------------------------------------
# KALIBRACE
# --------------------------------------------------------------
# zahodíme pár frame aby se kamera stabilizovala
for _ in range(30):
    cap.read()

base_frame = get_stable_frame(cap, 30)
save_calibration_frame(base_frame)

detector = DartDetector(base_frame)
#cv2.imwrite("base.jpg", base_frame)

start_stream_server(8888)

buffer = ScoreBuffer()
start_touch()
print("System ready")

# --------------------------------------------------------------
# HLAVNI SMYCKA
# --------------------------------------------------------------

while True:


    if check_touch():

        print("Next player")

        apply_score(darts)

        switch_player()

        darts = []

        base_frame = nextPlayer()

        detector = DartDetector(base_frame)

    frame = get_stable_frame(cap, 10)

    frame, darts = detector.process(frame)

    display_score(darts, player1, player2, currentPlayer)

    set_frame(frame)
