from typing import Optional

from WizardGame.Card import Card, Suit
from WizardGame.PlayerBid import PlayerBid


class Board:
    """Contains information about the board and the state of the players for a given round"""

    def __init__(
        self,
        trump_card: Optional[Card],
        trump: Suit,
        player_bids: dict[str, int],
        player_scores: dict[str, int],
        next_player_lookup: dict[str, str],
        starting_player: str,
    ) -> None:
        super().__init__()
        self.player_played_cards: dict[str, list[Card]] = dict()
        self.player_bids: dict[str, int] = player_bids
        self.player_tricks_won: dict[str, int] = dict()
        self.player_scores: dict[str, int] = player_scores
        self.trump_card: Card = trump_card
        self.turn: str = starting_player
        self.starting_player: str = starting_player
        self.next_player_lookup: dict[str, str] = next_player_lookup
        self.trump = trump
        self.num_players = len(self.player_scores)

    def card_played(self, player: str, card: Card) -> None:
        self.player_played_cards.setdefault(player, []).append(card)
        self.turn = self.next_player_lookup[player]

    def trick_won(self, player: str) -> None:
        self.player_tricks_won.setdefault(player, 0)
        self.player_tricks_won[player] += 1
        self.turn = player

    def update_scores(self) -> None:
        for player in self.player_scores:
            self.player_scores[player] += self.score_for_round(player)

    def score_for_round(self, player: str) -> int:
        player_estimate: int = self.player_bids[player]
        tricks_won: int = self.player_tricks_won.setdefault(player, 0)
        if player_estimate == tricks_won:
            return 20 + 10 * tricks_won

        return -10 * abs(player_estimate - tricks_won)
