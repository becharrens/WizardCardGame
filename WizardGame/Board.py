from typing import Optional

from WizardGame.Card import Card, Suit
from WizardGame.PlayerBid import PlayerBid


class Board:
    """Contains information about the board and the state of the players for a given round"""

    def __init__(
            self,
            trump_card: Optional[Card],
            trump: Suit,
            player_bids: dict[str, PlayerBid],
            player_scores: dict[str, int],
            next_player_lookup: dict[str, str],
            starting_player: str,
    ) -> None:
        super().__init__()
        self.played_cards: set[int] = set() if trump_card is None else {hash(trump_card)}
        self.player_played_cards: dict[str, set[Card]] = dict()
        self.player_bids: dict[str, PlayerBid] = player_bids
        self.player_scores: dict[str, int] = player_scores
        self.trump_card: Card = trump_card
        self.turn: str = starting_player
        self.next_player_lookup: dict[str, str] = next_player_lookup
        self.trump = trump
        self.num_players = len(self.player_scores)

    def card_played(self, player: str, card: Card) -> None:
        self.played_cards.add(hash(card))
        invalid_cards = [c for c in self.played_cards if c > 60]
        if len(invalid_cards):
            print("error!!")
        self.player_played_cards.setdefault(player, set()).add(card)
        self.turn = self.next_player_lookup[player]

    def trick_won(self, player: str) -> None:
        self.player_bids[player].trick_won()
        self.turn = player

    def update_scores(self) -> None:
        for player in self.player_scores:
            self.player_scores[player] += self.player_bids[player].score_for_round()
