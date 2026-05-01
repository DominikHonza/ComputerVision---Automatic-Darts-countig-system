class ScoreBuffer:
    """Stores up to three darts for a single turn and sums their score."""

    def __init__(self):
        """Initialize the turn buffer with three empty dart slots."""
        self.darts = [None, None, None]
        self.index = 0

    def add_dart(self, ring, sector, score):
        """Append one scored dart unless the turn already contains three darts."""

        if self.index >= 3:
            return

        self.darts[self.index] = (ring, sector, score)
        self.index += 1

    def reset(self):
        """Clear the current turn and start writing from the first slot."""

        self.darts = [None, None, None]
        self.index = 0

    def get_darts(self):
        """Return the three dart slots for the current turn."""
        return self.darts

    def get_total(self):
        """Return the sum of all non-empty dart scores in the buffer."""

        total = 0

        for d in self.darts:
            if d is not None:
                total += d[2]

        return total
