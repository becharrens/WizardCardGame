from WizardAI.Card import (
    Suit,
    Card,
    InvalidCardException,
    card_from_string,
    suit_from_string,
    InvalidSuitException,
)
from WizardAI.Player import Player
from WizardAI.Trick import Trick


class HumanPlayer(Player):
    def select_card(self, trick: Trick, cards_to_play: list[Card]) -> Card:
        while True:
            print(
                f"Player {self.name} hand: {self.hand}, playable cards: {cards_to_play}"
            )
            card_str: str = input(
                f"{self.name}, please select a playable card to play: "
            )

            try:
                card: Card = card_from_string(card_str)
            except InvalidCardException:
                print(f"'{card_str}' is not a valid card string!")
                continue

            if card.suit != Suit.NONE and card in cards_to_play:
                return card

            for hand_card in cards_to_play:
                if hand_card.card_type == card.card_type:
                    return hand_card

            print(f"'{card_str}' is not a valid card from your hand to play!")

    def choose_trump(self) -> Suit:
        while True:
            print(f"Player {self.name} hand: {self.hand}")
            trump_suit_str: str = input(f"{self.name}, please select a trump suit: ")

            try:
                return suit_from_string(trump_suit_str)
            except InvalidSuitException:
                print(f"'{trump_suit_str}' is not a valid suit!")

    def select_bid(self, bids: dict[str, int]) -> int:
        while True:
            print(f"Player {self.name} hand: {self.hand}, bids so far: {bids}")
            bid_str: str = input(
                f"{self.name}, please estimate the number of tricks you will win this round: "
            )

            try:
                bid: int = int(bid_str)
                if bid < 0:
                    print(f"'{bid}' is an invalid bid, bid must be an integer >= 0!")
                return bid
            except ValueError:
                print(f"'{bid_str}' is not a valid bid, your bid must be an integer!")

    def trick_outcome(self, trick: Trick) -> None:
        print(f"Player {self.name} - the trick ended with {trick}")
        print(f"Player {self.name} - current state: {self.board.player_tricks_won}")
        input("Press enter to continue")
