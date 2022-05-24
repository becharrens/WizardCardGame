import unittest

from WizardGame.Card import build_deck, Card, CardType, Suit
from WizardGame.ProbailisticAIPlayer import ProbabilisticAIPlayer


class MyTestCase(unittest.TestCase):
    def test_build_deck_contains_all_cards(self):
        expected_deck = [
            Card(CardType.ONE, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.TWO, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.THREE, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.FOUR, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.FIVE, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.SIX, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.SEVEN, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.EIGHT, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.NINE, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.TEN, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.ELEVEN, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.TWELVE, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.THIRTEEN, Suit.BLUE, wizard_index=0, jester_index=0),
            Card(CardType.ONE, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.TWO, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.THREE, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.FOUR, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.FIVE, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.SIX, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.SEVEN, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.EIGHT, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.NINE, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.TEN, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.ELEVEN, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.TWELVE, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.THIRTEEN, Suit.GREEN, wizard_index=0, jester_index=0),
            Card(CardType.ONE, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.TWO, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.THREE, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.FOUR, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.FIVE, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.SIX, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.SEVEN, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.EIGHT, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.NINE, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.TEN, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.ELEVEN, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.TWELVE, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.THIRTEEN, Suit.RED, wizard_index=0, jester_index=0),
            Card(CardType.ONE, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.TWO, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.THREE, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.FOUR, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.FIVE, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.SIX, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.SEVEN, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.EIGHT, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.NINE, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.TEN, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.ELEVEN, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.TWELVE, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.THIRTEEN, Suit.YELLOW, wizard_index=0, jester_index=0),
            Card(CardType.WIZARD, Suit.NONE, wizard_index=0, jester_index=0),
            Card(CardType.JESTER, Suit.NONE, wizard_index=0, jester_index=0),
            Card(CardType.WIZARD, Suit.NONE, wizard_index=1, jester_index=0),
            Card(CardType.JESTER, Suit.NONE, wizard_index=0, jester_index=1),
            Card(CardType.WIZARD, Suit.NONE, wizard_index=2, jester_index=0),
            Card(CardType.JESTER, Suit.NONE, wizard_index=0, jester_index=2),
            Card(CardType.WIZARD, Suit.NONE, wizard_index=3, jester_index=0),
            Card(CardType.JESTER, Suit.NONE, wizard_index=0, jester_index=3),
        ]

        deck = build_deck()

        self.assertEqual(expected_deck, deck, "decks are not equal")

    def test_hashes_of_cards_in_deck(self):
        hashes = [hash(card) for card in build_deck()]
        special_card_hashes = [57, 53, 58, 54, 59, 55, 60, 56]
        number_card_hashes = list(range(1, 53))
        expected_hashes = number_card_hashes + special_card_hashes
        self.assertEqual(list(expected_hashes), hashes, "hashes of cards do not match expected values")

    def test_probability(self):
        # Z,1R,5Y  12Y
        cards_seen = {Card(CardType.FIVE, Suit.YELLOW), Card(CardType.TWELVE, Suit.YELLOW),
                      Card(CardType.ONE, Suit.RED), Card(CardType.WIZARD, Suit.NONE)}
        cards_seen_hashes = {hash(card) for card in cards_seen}
        player = ProbabilisticAIPlayer('CPU4', 4)
        print(player.uniform_probability_of_card_winning(Card(CardType.FIVE, Suit.YELLOW), Suit.YELLOW, Suit.YELLOW,
                                                         cards_seen_hashes, 0, False))


if __name__ == '__main__':
    unittest.main()
