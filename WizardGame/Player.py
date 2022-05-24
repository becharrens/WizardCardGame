from abc import ABC, abstractmethod
from typing import Optional

from WizardGame.Board import Board
from WizardGame.Card import Card, Suit
from WizardGame.PlayerBid import PlayerBid
from WizardGame.Trick import Trick


class Player(ABC):
    def __init__(self, name: str, num_players: int) -> None:
        super().__init__()
        self.hand: set[Card] = set()
        self.board: Optional[Board] = None
        self.name: str = name
        self.num_players: int = num_players

    @abstractmethod
    def select_card(self, trick: Trick, cards_to_play: set[Card]) -> Card:
        raise Exception("Unimplemented")

    @abstractmethod
    def choose_trump(self) -> Suit:
        raise Exception("Unimplemented")

    @abstractmethod
    def select_bid(self, bids: dict[str, PlayerBid]) -> int:
        raise Exception("Unimplemented")

    def deal_hand(self, hand: set[Card]) -> None:
        self.hand = hand

    def set_board(self, board: Board) -> None:
        self.board = board

    def choose_card(self, trick: Trick) -> Card:
        if trick.suit_to_follow is None:
            valid_cards: set[Card] = self.hand
        else:
            valid_cards: set[Card] = set()
            can_only_play_special: bool = True

            for card in self.hand:
                if card.suit == Suit.NONE:
                    valid_cards.add(card)
                elif card.suit == trick.suit_to_follow:
                    valid_cards.add(card)
                    can_only_play_special = False

            if can_only_play_special:
                valid_cards = self.hand

        card: Card = self.select_card(trick, valid_cards)
        self.hand.remove(card)
        return card

    def calculate_bid(self, bids: dict[str, PlayerBid]) -> PlayerBid:
        return PlayerBid(self.select_bid(bids))

    def __str__(self) -> str:
        return self.name
