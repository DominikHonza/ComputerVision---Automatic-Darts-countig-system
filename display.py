import cv2
import numpy as np

FB_PATH = "/dev/fb1"

WIDTH = 480
HEIGHT = 320


def format_dart(d):
    """Convert an internal dart tuple into the short label shown on the LCD."""

    if d is None:
        return "X"

    ring, sector, score = d

    if ring == "TRIPLE":
        return f"T{sector}"

    if ring == "DOUBLE":
        return f"D{sector}"

    if ring == "SINGLE":
        return f"{sector}"

    if ring == "OUTER_BULL":
        return "25"

    if ring == "BULL":
        return "50"

    return "MISS"


def display_score(darts, player1, player2, currentPlayer):
    """Render current scores and turn darts, then write the image to fb1."""

    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    # -------------------------
    # PLAYER SCORES
    # -------------------------

    color1 = (0,255,0) if currentPlayer == 1 else (255,255,255)
    color2 = (0,255,0) if currentPlayer == 2 else (255,255,255)

    cv2.putText(img, f"P1: {player1}", (20,40),
        cv2.FONT_HERSHEY_SIMPLEX, 1, color1, 2)

    cv2.putText(img, f"P2: {player2}", (300,40),
        cv2.FONT_HERSHEY_SIMPLEX, 1, color2, 2)

    # -------------------------
    # DARTS
    # -------------------------

    slots = [None, None, None]

    for i in range(min(len(darts),3)):
        slots[i] = darts[i]

    y = 120
    total = 0

    for i,d in enumerate(slots):

        text = format_dart(d)

        if d is not None:
            total += d[2]

        cv2.putText(
            img,
            f"{i+1}: {text}",
            (120,y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (255,255,255),
            2
        )

        y += 50

    # -------------------------
    # TURN SCORE
    # -------------------------

    cv2.putText(
        img,
        f"TURN: {total}",
        (140,280),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.4,
        (0,255,0),
        3
    )

    # -------------------------
    # FRAMEBUFFER OUTPUT
    # -------------------------

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    r = (img[:,:,0] >> 3).astype(np.uint16)
    g = (img[:,:,1] >> 2).astype(np.uint16)
    b = (img[:,:,2] >> 3).astype(np.uint16)

    rgb565 = (r << 11) | (g << 5) | b

    with open(FB_PATH, "wb") as f:
        f.write(rgb565.tobytes())


def display_calibration():
    """Show the transition screen while a new reference frame is captured."""

    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    # velký text
    cv2.putText(
        img,
        "NEXT PLAYER",
        (70,120),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (255,255,255),
        3,
        cv2.LINE_AA
    )

    # instrukce
    cv2.putText(
        img,
        "Calibrating please wait...",
        (90,180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (200,200,200),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        img,
        "Do not throw darts...",
        (95,220),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (200,200,200),
        2,
        cv2.LINE_AA
    )

    # převod framebuffer
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    r = (img[:,:,0] >> 3).astype(np.uint16)
    g = (img[:,:,1] >> 2).astype(np.uint16)
    b = (img[:,:,2] >> 3).astype(np.uint16)

    rgb565 = (r << 11) | (g << 5) | b

    with open(FB_PATH, "wb") as f:
        f.write(rgb565.tobytes())
