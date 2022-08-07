from abc import ABC, abstractmethod
from typing import Optional

from WizardAI.Board import Board
from WizardAI.Card import Card, Suit, playable_cards
from WizardAI.Trick import Trick


class Player(ABC):
    def __init__(self, name: str, num_players: int) -> None:
        super().__init__()
        self.hand: list[Card] = []
        self.board: Optional[Board] = None
        self.name: str = name
        self.num_players: int = num_players

    @abstractmethod
    def select_card(
        self,
        trick: Trick,
        cards_to_play: list[Card],
    ) -> Card:
        raise Exception("Unimplemented")

    @abstractmethod
    def choose_trump(self) -> Suit:
        raise Exception("Unimplemented")

    @abstractmethod
    def select_bid(self, bids: dict[str, int]) -> int:
        raise Exception("Unimplemented")

    @abstractmethod
    def trick_outcome(self, trick: Trick) -> None:
        raise Exception("Unimplemented")

    def deal_hand(self, hand: list[Card]) -> None:
        self.hand = hand

    def set_board(self, board: Board) -> None:
        self.board = board

    def choose_card(self, trick: Trick) -> Card:
        valid_cards: list[Card] = playable_cards(self.hand, trick.suit_to_follow)

        card: Card = self.select_card(trick, valid_cards)
        self.hand = [c for c in self.hand if card != c]
        return card

    def calculate_bid(self, bids: dict[str, int]) -> int:
        return self.select_bid(bids)

    def __str__(self) -> str:
        return self.name
