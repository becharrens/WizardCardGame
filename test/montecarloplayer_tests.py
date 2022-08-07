import unittest

from WizardAI.Card import Card, CardType, Suit
from WizardAI.MonteCarloPlayer import MonteCarloPlayer, MonteCarloSimulator


class MonteCarloTests(unittest.TestCase):
    def test_bid_estimates(self):
        # 4Y, Z, 3Y, Trump = 10B
        simulator: MonteCarloSimulator = MonteCarloSimulator(
            "CPU4",
            [
                Card(CardType.FOUR, Suit.YELLOW),
                Card(CardType.WIZARD, Suit.NONE, wizard_index=0),
                Card(CardType.THREE, Suit.YELLOW),
            ],
            dict(),
            Suit.BLUE,
            Card(CardType.TEN, Suit.BLUE),
            None,
            None,
            None,
            "CPU2",
            dict(),
            dict(),
            {"CPU2": "CPU3", "CPU3": "CPU4", "CPU4": "P1", "P1": "CPU2"},
            5,
            5,
            None,
        )
        for i in range(5):
            estimate: int = simulator.estimate_winnings()
            print(estimate)
            if estimate > 0:
                return
        assert (
            False
        ), "estimate was false 5 times in a row. This should be very unlikely"
