from typing import Optional

from WizardGame.Card import Card, CardType, Suit, compare_cards


class Trick:
    def __init__(self, trump: Suit) -> None:
        super().__init__()
        self.trump: Suit = trump
        self.suit_to_follow: Optional[Suit] = None
        self.winner_card: Optional[Card] = None
        self.winner_player: str = ""
        self.cards: dict[str, Card] = dict()
        self.is_wizard_played: bool = False

    def play_card(self, player: str, card: Card):
        if not self.is_wizard_played:
            if self.winner_card is None:
                self.winner_card = card
                self.winner_player = player
                self.is_wizard_played = card.card_type == CardType.WIZARD
                if not self.is_wizard_played:
                    self.suit_to_follow = card.suit

            else:
                if compare_cards(self.winner_card, card, self.trump) < 0:
                    if card.card_type == CardType.WIZARD:
                        self.is_wizard_played = True
                        if self.suit_to_follow == Suit.NONE:
                            self.suit_to_follow = None
                    elif self.suit_to_follow == Suit.NONE:
                        self.suit_to_follow = card.suit
                    self.winner_card = card
                    self.winner_player = player

        self.cards[player] = card

    def __str__(self):
        trick_info = f"Trick - trump: '{self.trump}', suit to follow: {self.suit_to_follow}, winning player: {self.winner_player}, winning card: {self.winner_card}"
        played_cards = ", ".join(
            [f"{player}: {card}" for player, card in self.cards.items()]
        )
        return "\n".join([trick_info, played_cards]) + "\n\n"
