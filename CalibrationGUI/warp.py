import cv2
import numpy as np
from board_calibration import BoardCalibration
import math

SECTORS = [
    1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5,20
]


def normalize_board(frame, calibration: BoardCalibration, size=800, angle_offset=0, hit_points=None):

    img = frame.copy()

    dst = np.array([
        [size/2, 0],
        [size, size/2],
        [size/2, size],
        [0, size/2]
    ], dtype=np.float32)

    points = np.array(calibration.points, dtype=np.float32)

    # DEBUG body
    for p in points:
        cv2.circle(img, tuple(map(int, p)), 8, (0, 0, 255), -1)

    cv2.line(img, tuple(points[0].astype(int)), tuple(points[1].astype(int)), (0,255,255), 2)
    cv2.line(img, tuple(points[1].astype(int)), tuple(points[2].astype(int)), (0,255,255), 2)
    cv2.line(img, tuple(points[2].astype(int)), tuple(points[3].astype(int)), (0,255,255), 2)
    cv2.line(img, tuple(points[3].astype(int)), tuple(points[0].astype(int)), (0,255,255), 2)

    # WARP
    M = cv2.getPerspectiveTransform(points, dst)
    warped = cv2.warpPerspective(frame, M, (size, size))

    center = (size // 2, size // 2)
    board_radius = size // 2 - 100

    # KRUHY
    cv2.circle(warped, center, int(board_radius * 0.05), (0,255,0), 2)
    cv2.circle(warped, center, int(board_radius * 0.09), (0,255,0), 2)

    cv2.circle(warped, center, int(board_radius * 0.53), (255,0,0), 2)
    cv2.circle(warped, center, int(board_radius * 0.59), (255,0,0), 2)

    cv2.circle(warped, center, int(board_radius * 0.88), (0,0,255), 2)
    cv2.circle(warped, center, int(board_radius * 0.95), (0,0,255), 2)

    # --------------------------------------------------
    # HIT POINTS → DISTANCE + ANGLE
    # --------------------------------------------------

    results = []

    if hit_points is not None and len(hit_points) > 0:

        pts = np.array(hit_points, dtype=np.float32).reshape(-1, 1, 2)
        transformed = cv2.perspectiveTransform(pts, M)

        for p in transformed:
            x = int(p[0][0])
            y = int(p[0][1])

            dx = x - center[0]
            dy = y - center[1]

            distance = math.sqrt(dx*dx + dy*dy)

            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0:
                angle += 360

            # 🔥 NORMALIZACE podle offsetu
            norm_angle = (angle - angle_offset) % 360

            results.append({
                "point": (x, y),
                "distance": distance,
                "angle": norm_angle
            })

            # ---- RINGY ----
            cv2.circle(warped, center, int(board_radius * 0.05), (0,255,0), 2)
            cv2.circle(warped, center, int(board_radius * 0.09), (0,255,0), 2)

            cv2.circle(warped, center, int(board_radius * 0.53), (255,0,0), 2)
            cv2.circle(warped, center, int(board_radius * 0.59), (255,0,0), 2)

            cv2.circle(warped, center, int(board_radius * 0.88), (0,0,255), 2)
            cv2.circle(warped, center, int(board_radius * 0.95), (0,0,255), 2)

            # ---- SEKTORY ----
            for i in range(20):

                angle = np.deg2rad(i * 18 + angle_offset)

                sx = int(center[0] + board_radius * np.cos(angle))
                sy = int(center[1] + board_radius * np.sin(angle))

                cv2.line(warped, center, (sx, sy), (255,255,0), 1)

                # čísla sektorů (bonus 🔥)
                mid_angle = np.deg2rad(i * 18 + 9 + angle_offset)

                tx = int(center[0] + board_radius * 0.6 * np.cos(mid_angle))
                ty = int(center[1] + board_radius * 0.6 * np.sin(mid_angle))

                cv2.putText(
                    warped,
                    str(SECTORS[i]),
                    (tx, ty),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255,255,255),
                    1,
                    cv2.LINE_AA
                )

            # střed
            cv2.circle(warped, center, 5, (0,255,255), -1)

            # kreslení
            cv2.circle(warped, (x, y), 6, (0,255,255), -1)

            label = f"d:{int(distance)} a:{int(norm_angle)}"

            text_x = x + 8
            text_y = y - 8

            # background box
            (text_w, text_h), _ = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                1
            )

            cv2.rectangle(
                warped,
                (text_x, text_y - text_h - 4),
                (text_x + text_w, text_y),
                (0, 0, 0),
                -1
            )

            # text
            cv2.putText(
                warped,
                label,
                (text_x, text_y - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0,255,255),
                1,
                cv2.LINE_AA
            )

    cv2.circle(warped, center, 5, (0,255,255), -1)

    return img, warped, results