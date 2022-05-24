class PlayerBid:
    def __init__(self, expected_wins: int) -> None:
        super().__init__()
        self.expected_wins: int = expected_wins
        self.wins: int = 0

    def trick_won(self):
        self.wins += 1

    def score_for_round(self):
        if self.expected_wins == self.wins:
            return 20 + 10 * self.wins

        return -10 * abs(self.expected_wins - self.wins)

    def __str__(self) -> str:
        return f"expected={self.expected_wins}, actual={self.wins}"

    def __repr__(self) -> str:
        return str(self)

