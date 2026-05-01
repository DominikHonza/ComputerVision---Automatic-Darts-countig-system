import math

SECTORS = [
    20,5,12,9,14,11,8,16,7,19,3,17,2,15,10,6,13,4,18,1
]


def get_ring_score(distance, board_radius):
    """Map radial distance from the center to a dartboard ring label."""

    bull_inner = board_radius * 0.05
    bull_outer = board_radius * 0.09

    triple_inner = board_radius * 0.53
    triple_outer = board_radius * 0.59

    double_inner = board_radius * 0.88
    double_outer = board_radius * 0.95

    if distance <= bull_inner:
        return "BULL"

    if distance <= bull_outer:
        return "OUTER_BULL"

    if triple_inner <= distance <= triple_outer:
        return "TRIPLE"

    if double_inner <= distance <= double_outer:
        return "DOUBLE"

    if distance > double_outer:
        return "MISS"

    return "SINGLE"

ROTATION_OFFSET = 3
def get_sector(dx, dy, angleOffset):
    """Convert a hit vector into the corresponding dartboard sector number."""

    angle = math.degrees(math.atan2(-dy, dx))

    if angle < 0:
        angle += 360

    angle = (angle + angleOffset) % 360

    sector_index = int(angle // 18)

    sector_index = (sector_index + ROTATION_OFFSET) % 20

    return SECTORS[sector_index]

def calculate_score(ring, sector):
    """Convert a ring label and sector number into a numeric score."""

    if ring == "BULL":
        return 50

    if ring == "OUTER_BULL":
        return 25

    if ring == "TRIPLE":
        return sector * 3

    if ring == "DOUBLE":
        return sector * 2

    if ring == "SINGLE":
        return sector

    if ring == "MISS":
        return 0

    return 0
