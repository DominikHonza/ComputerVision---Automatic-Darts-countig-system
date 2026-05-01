class ScoreBuffer:

    def __init__(self):
        self.darts = [None, None, None]
        self.index = 0

    def add_dart(self, ring, sector, score):

        if self.index >= 3:
            return

        self.darts[self.index] = (ring, sector, score)
        self.index += 1

    def reset(self):

        self.darts = [None, None, None]
        self.index = 0

    def get_darts(self):
        return self.darts

    def get_total(self):

        total = 0

        for d in self.darts:
            if d is not None:
                total += d[2]

        return total