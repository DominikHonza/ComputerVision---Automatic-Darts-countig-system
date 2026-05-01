"""Perspective normalization and scoring projection for dart hits.

Author:
    xhonza04 Dominik Honza

Description:
    This module loads calibration data, computes the perspective transform from
    camera space into normalized board space, and evaluates the transformed hit
    position using the scoring rules defined in ``enumerate_score.py``.
"""

import cv2
import numpy as np
from enumerate_score import get_ring_score, get_sector, calculate_score
import math
import json
import os

ANGLEOFFSET = 64
ANGLEOFFSET_SCORE = 0
CALIBRATION_FILE = os.path.join(os.path.dirname(__file__), "calibration.json")

SECTORS = [
    1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5,20
]


def load_calibration():
    """Load board calibration data from disk or use built-in defaults.

    Returns:
        dict: Calibration dictionary containing board corner coordinates and
        angular offsets.
    """

    default_config = {
        "tl": [5, 62],
        "tr": [1160, -44],
        "br": [1160, 767],
        "bl": [5, 667],
        "angle": ANGLEOFFSET,
        "score_angle": ANGLEOFFSET_SCORE,
    }

    if not os.path.exists(CALIBRATION_FILE):
        return default_config

    with open(CALIBRATION_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    config = default_config.copy()
    config.update(loaded)
    return config

def line_intersection(p1, p2, p3, p4):
    """Return the intersection point of two lines defined by point pairs.

    Args:
        p1: First point of line one.
        p2: Second point of line one.
        p3: First point of line two.
        p4: Second point of line two.

    Returns:
        list: Intersection coordinates in the form ``[x, y]``.
    """

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)

    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / denom

    return [px, py]

def normalize_board(frame, hit_point):
    """Project a detected hit into normalized board space and score it.

    Args:
        frame: Current BGR image of the dartboard.
        hit_point: Detected hit location in source image coordinates.

    Returns:
        tuple: Scored dart in the form ``(ring, sector, score)``.
    """
    img = frame.copy()
    calibration = load_calibration()

    # ===== NORMALIZACE =====

    size = 800

    # cílové body (ideální kruh)
    dst = np.array([
        [size/2, 0],        # top
        [size, size/2],     # right
        [size/2, size],     # bottom
        [0, size/2]         # left
    ], dtype=np.float32)

    # ===== TEČNY =====

    top_left = calibration["tl"]
    top_right = calibration["tr"]
    bottom_right = calibration["br"]
    bottom_left = calibration["bl"]

    points = np.array([
        top_left,
        top_right,
        bottom_right,
        bottom_left
    ], dtype=np.float32)

    cv2.circle(img, tuple(np.int32(top_left)), 8, (0,0,255), -1)
    cv2.circle(img, tuple(np.int32(top_right)), 8, (0,0,255), -1)
    cv2.circle(img, tuple(np.int32(bottom_right)), 8, (0,0,255), -1)
    cv2.circle(img, tuple(np.int32(bottom_left)), 8, (0,0,255), -1)

    #cv2.imshow("tangents", img)

    # ===== PERSPEKTIVNÍ TRANSFORMACE =====

    # Map the calibrated board outline into a fixed top-down coordinate system.
    M = cv2.getPerspectiveTransform(points, dst)

    warped = cv2.warpPerspective(img, M, (size, size))

    # ===== STŘED =====

    center = (size//2-2, size//2)
    board_radius = size//2 - 100

    # ===== TRANSFORMACE BODU =====

    point = np.array([[hit_point]], dtype=np.float32)
    transformed_point = cv2.perspectiveTransform(point, M)

    x = int(transformed_point[0][0][0])
    y = int(transformed_point[0][0][1])

    # vykreslení bodu
    cv2.circle(warped, (x, y), 8, (0,255,255), -1)

    # Score is derived from radial distance for the ring and angle for the sector.
    dx = x - center[0]
    dy = y - center[1]

    distance = np.sqrt(dx*dx + dy*dy)

    ring = get_ring_score(distance, board_radius)
    sector = get_sector(dx, dy, calibration.get("score_angle", ANGLEOFFSET_SCORE))

    print("Ring:", ring)
    print("Sector:", sector)

    # ===== RINGY =====

    bull_inner = board_radius * 0.05
    bull_outer = board_radius * 0.09

    triple_inner = board_radius * 0.53
    triple_outer = board_radius * 0.59

    double_inner = board_radius * 0.88
    double_outer = board_radius * 0.95

    cv2.circle(warped, center, int(bull_inner), (0,255,0), 2)
    cv2.circle(warped, center, int(bull_outer), (0,255,0), 2)

    cv2.circle(warped, center, int(triple_inner), (255,0,0), 2)
    cv2.circle(warped, center, int(triple_outer), (255,0,0), 2)

    cv2.circle(warped, center, int(double_inner), (0,0,255), 2)
    cv2.circle(warped, center, int(double_outer), (0,0,255), 2)

    # ===== SEKTORY =====

    for i in range(20):

        # hraniční čára sektoru
        angle = np.deg2rad(i * 18 + calibration.get("angle", ANGLEOFFSET))

        x = int(center[0] + board_radius * np.cos(angle))
        y = int(center[1] + board_radius * np.sin(angle))

        cv2.line(warped, center, (x,y), (255,255,0), 1)

        # ===== STŘED SEKTORU =====
        mid_angle = np.deg2rad(i * 18 + 9 + calibration.get("angle", ANGLEOFFSET))

        tx = int(center[0] + board_radius * 0.55 * np.cos(mid_angle))
        ty = int(center[1] + board_radius * 0.55 * np.sin(mid_angle))

        sector_number = SECTORS[i]

        label = f"{sector_number}"

        cv2.putText(
            warped,
            label,
            (tx, ty),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2,
            cv2.LINE_AA
        )


    cv2.circle(warped, center, 5, (0,255,255), -1)
    return ring, sector, calculate_score(ring, sector)
    #cv2.imshow("corrected board", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#normalize_board("base.png",hit_point=(850, 350))
