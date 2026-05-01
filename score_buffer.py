"""Turn-local storage for scored darts in the legacy darts application.

Author:
    xhonza04 Dominik Honza

Description:
    This module provides a simple fixed-size container for up to three darts
    thrown during one turn and offers convenience methods for reset and score
    summation.
"""

class ScoreBuffer:
    """Stores up to three darts for a single turn and sums their score."""

    def __init__(self):
        """Initialize the turn buffer with three empty dart slots."""
        self.darts = [None, None, None]
        self.index = 0

    def add_dart(self, ring, sector, score):
        """Append one scored dart unless the buffer is already full.

        Args:
            ring: Ring label of the detected hit.
            sector: Sector number of the detected hit.
            score: Numeric score assigned to the hit.
        """

        if self.index >= 3:
            return

        self.darts[self.index] = (ring, sector, score)
        self.index += 1

    def reset(self):
        """Clear the current turn and start writing from the first slot."""

        self.darts = [None, None, None]
        self.index = 0

    def get_darts(self):
        """Return the three dart slots for the current turn.

        Returns:
            list: List of up to three dart tuples or ``None`` placeholders.
        """
        return self.darts

    def get_total(self):
        """Return the sum of all non-empty dart scores in the buffer.

        Returns:
            int: Total score accumulated in the current turn buffer.
        """

        total = 0

        for d in self.darts:
            if d is not None:
                total += d[2]

        return total
