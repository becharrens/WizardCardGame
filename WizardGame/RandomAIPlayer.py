import random

from WizardGame.Card import Suit, Card
from WizardGame.Player import Player
from WizardGame.PlayerBid import PlayerBid
from WizardGame.Trick import Trick


class RandomAIPlayer(Player):
    def select_card(self, trick: Trick, cards_to_play: set[Card]) -> Card:
        return random.choice(list(cards_to_play))

    def choose_trump(self) -> Suit:
        return random.choice([Suit.RED, Suit.BLUE, Suit.GREEN, Suit.YELLOW])

    def select_bid(self, bids: dict[str, PlayerBid]) -> int:
        return random.randint(0, (len(self.hand) // 2) + 1)