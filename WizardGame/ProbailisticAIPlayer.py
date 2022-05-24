from typing import Iterable, Optional

from WizardGame.Board import Board
from WizardGame.Card import Suit, Card, CardType, compare_cards
from WizardGame.Constants import CARDS_PER_SUIT, NUM_CARDS, NUM_JESTERS
from WizardGame.Player import Player
from WizardGame.PlayerBid import PlayerBid
from WizardGame.Trick import Trick

TRICK_WIN_THRESHOLD: float = 0.5


# TODO: Possibilities to consider
# All/only jesters round
class ProbabilisticAIPlayer(Player):
    def __init__(self, name: str, num_players: int) -> None:
        super().__init__(name, num_players)
        self.player_suits_left: dict[str, set[Suit]] = dict()

    def set_board(self, board: Board) -> None:
        super().set_board(board)
        self.player_suits_left: dict[str, set[Suit]] = {
            player: {Suit(suit) for suit in Suit.all_suits}
            for player in board.player_scores
        }

    def select_card(self, trick: Trick, cards_to_play: set[Card]) -> Card:
        bid: PlayerBid = self.board.player_bids[self.name]
        tricks_left_to_win: int = min(
            len(self.hand), max(0, bid.expected_wins - bid.wins)
        )
        all_cards_seen: set[int] = self.board.played_cards | set(
            hash(card) for card in self.hand
        )

        card_chances: list[(Card, float)] = [
            (
                card,
                self.uniform_probability_of_card_winning(
                    card,
                    trick.suit_to_follow,
                    trick.trump,
                    all_cards_seen,
                    len(trick.cards),
                    trick.is_wizard_played,
                ),
            )
            for card in cards_to_play
        ]

        if tricks_left_to_win == 0:
            min_chance: float = 1.1
            min_card: Optional[Card] = None
            for card, chance in card_chances:
                if chance < min_chance:
                    min_chance = chance
                    min_card = card
            return min_card

        else:
            max_chance: float = -1.0
            max_card: Optional[Card] = None
            for card, chance in card_chances:
                if chance > max_chance:
                    max_chance = chance
                    max_card = card
            return max_card

    def select_bid(self, bids: dict[str, PlayerBid]) -> int:
        num_bids: int = 0
        print(f"player {self.name} hand win probabilities:")
        all_cards_seen: set[int] = (
            set(hash(card) for card in self.hand) | self.board.played_cards
        )
        for card in self.hand:
            probability: float = self.uniform_probability_of_card_winning(
                card, card.suit, self.board.trump, all_cards_seen, 0, False
            )
            print(f"{card} => {probability}")
            if probability > TRICK_WIN_THRESHOLD:
                num_bids += 1
        return num_bids

    def choose_trump(self) -> Suit:
        expected_card_wins_by_suit: dict[Suit, int] = dict()
        card_win_chances_by_suit: dict[Suit, float] = dict()

        max_wins: int = -1
        max_winning_chances: float = 0.0

        # beginning of round - trump card must be a wizard and
        random_wizard: Card = Card(
            CardType.WIZARD, Suit.NONE, wizard_index=0, jester_index=0
        )

        all_cards_seen: set[int] = set(hash(card) for card in self.hand).union(
            {hash(random_wizard)}
        )
        for suit in Suit.all_suits:
            trump_suit: Suit = Suit(suit)
            expected_card_wins_by_suit[trump_suit] = 0
            card_win_chances_by_suit[trump_suit] = 0.0
            for card in self.hand:
                winning_chance: float = self.uniform_probability_of_card_winning(
                    card, card.suit, trump_suit, all_cards_seen, 0, False
                )
                if winning_chance > TRICK_WIN_THRESHOLD:
                    expected_card_wins_by_suit[trump_suit] += 1
                card_win_chances_by_suit[trump_suit] += winning_chance

            max_wins = max(max_wins, expected_card_wins_by_suit[trump_suit])
            max_winning_chances = max(
                max_winning_chances, card_win_chances_by_suit[trump_suit]
            )

        winning_suits: list[Suit] = [
            suit
            for suit, expected_wins in expected_card_wins_by_suit.items()
            if expected_wins == max_wins
        ]

        if len(winning_suits) == 1:
            return winning_suits[0]

        winning_suit: list[Suit] = [
            suit
            for suit, winning_chance in card_win_chances_by_suit.items()
            if winning_chance == max_winning_chances
        ]

        return winning_suit[0]

    def uniform_probability_of_card_winning(
        self,
        card: Card,
        suit_to_follow: Optional[Suit],
        trump_suit: Suit,
        cards_seen: set[int],
        cards_played_in_trick: int,
        is_wizard_played: bool,
    ) -> float:
        """
        Probability of a card winning if it were played first

        :param is_wizard_played: has a wizard been played
        :param cards_played_in_trick: number of cards played in the trick so far
                                      (assumes current player hasn't played yet)
        :param card: card to calculate probability for
        :param suit_to_follow: suit of the first non-Jester card played, if any, unless it was a wizard,
                               in which case there is none
        :param trump_suit: suit of the trump card / chosen by the dealer if trump card is a wizard
        :param cards_seen: set of indices of cards seen so far in the round. Includes own hand + trump
        """
        if is_wizard_played:
            return 0.0

        if card.card_type == CardType.WIZARD:
            return 1.0

        if card.card_type == CardType.JESTER:
            # Not real probability, does not account for all jokers case
            return 0.0

        if (
            suit_to_follow in Suit.all_suits
            and card.suit != suit_to_follow
            and card.suit != trump_suit
        ):
            return 0.0

        cards_which_lose: int = 0
        suits_which_lose: Iterable[Suit] = (
            Suit(suit)
            for suit in Suit.all_suits
            if suit != card.suit and suit != trump_suit
        )

        # same suit
        card_index: int = Card.index(
            CardType.ONE, card.suit, jester_index=0, wizard_index=0
        )
        for i in range(card.card_type - 1):
            if card_index + i not in cards_seen:
                cards_which_lose += 1

        # non-same suit
        for suit in suits_which_lose:
            card_index = Card.index(CardType.ONE, suit, jester_index=0, wizard_index=0)
            for i in range(CARDS_PER_SUIT):
                if card_index + i not in cards_seen:
                    cards_which_lose += 1

        # jester
        for i in range(NUM_JESTERS):
            card_index = Card.index(
                CardType.JESTER, Suit.NONE, jester_index=i, wizard_index=0
            )
            if card_index + i not in cards_seen:
                cards_which_lose += 1

        if cards_which_lose == 0:
            return 0.0

        cards_left: int = NUM_CARDS - len(cards_seen)

        probability: float = 1.0
        cards_left_in_trick: int = self.num_players - cards_played_in_trick - 1

        if cards_which_lose < cards_left_in_trick:
            return 0.0

        for i in range(cards_left_in_trick):
            probability *= float(cards_which_lose) / float(cards_left)
            cards_which_lose -= 1
            cards_left -= 1

        return probability

    def probability_of_winning_trick(
        self, card: Card, trick: Trick, cards_seen: set[int]
    ) -> float:
        if trick.winner_card is None:
            return self.uniform_probability_of_card_winning(
                card,
                card.suit,
                trick.trump,
                cards_seen,
                len(trick.cards),
                trick.is_wizard_played,
            )

        if compare_cards(trick.winner_card, card, trick.trump) > 0:
            return 0.0

        return self.uniform_probability_of_card_winning(
            card,
            trick.suit_to_follow,
            trick.trump,
            cards_seen,
            len(trick.cards),
            trick.is_wizard_played,
        )
