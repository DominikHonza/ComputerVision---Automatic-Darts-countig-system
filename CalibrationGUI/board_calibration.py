class BoardCalibration:
    def __init__(self, points):
        """
        points = [top_left, top_right, bottom_right, bottom_left]
        každý bod: (x, y)
        """
        self.points = points