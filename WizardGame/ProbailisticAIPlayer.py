import random
from typing import Iterable, Optional, FrozenSet

from WizardGame.Board import Board
from WizardGame.Card import Suit, Card, CardType, compare_cards, build_deck
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
        self.player_suit_exhausted: bool = False

    def any_suit_exhausted(self) -> bool:
        for suits_left in self.player_suits_left.values():
            if len(suits_left) < len(Suit.all_suits):
                return True
        return False

    def set_board(self, board: Board) -> None:
        super().set_board(board)
        self.player_suits_left: dict[str, set[Suit]] = {
            player: {Suit(suit) for suit in Suit.all_suits}
            for player in board.player_scores
        }
        self.player_suit_exhausted = False

    def update_player_suits_left(self, trick: Trick) -> None:
        for player, card in trick.cards.items():
            if (
                trick.suit_to_follow in Suit.all_suits
                and card.suit != Suit.NONE
                and card.suit != trick.suit_to_follow
            ):
                if trick.suit_to_follow in self.player_suits_left[player]:
                    self.player_suits_left[player].remove(trick.suit_to_follow)

    def select_card(self, trick: Trick, cards_to_play: set[Card]) -> Card:
        self.player_suit_exhausted = self.any_suit_exhausted()
        if self.player_suit_exhausted:
            self.update_player_suits_left(trick)

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
                self.probability_of_winning_trick(
                    card,
                    trick,
                    all_cards_seen,
                ),
            )
            for card in cards_to_play
        ]

        if trick.winner_card is None:
            card_chances_in_new_trick: list[(Card, float)] = card_chances
        else:
            card_chances_in_new_trick: list[(Card, float)] = [
                (
                    card,
                    self.probability_of_winning_trick(
                        card,
                        Trick(trick.trump),
                        all_cards_seen,
                    ),
                )
                for card in cards_to_play
            ]

        print(f"{self.name}: card chances of winning: {card_chances}")

        if tricks_left_to_win == 0:
            card_chances_in_new_trick: list[(Card, float)] = [
                (card, 1 - p) for card, p in card_chances_in_new_trick
            ]
            card_chances: list[(Card, float)] = [
                (card, 1 - p) for card, p in card_chances
            ]

        # TODO: consider more factors here, such as, if you are always going to lose, be smart when choosing
        #       which card to discard
        max_chance: float = -1.0
        max_card: Optional[Card] = None
        for card, chance in card_chances:
            if chance > max_chance:
                max_chance = chance
                max_card = card

        if max_chance == 0.0:
            card_chances_in_new_trick: list[(Card, float)] = [
                (card, 1 - p) for card, p in card_chances_in_new_trick
            ]
            print(f"{self.name} - Choosing card based on absolute card values")
            max_chance: float = -1.0
            max_card: Optional[Card] = None
            for card, chance in card_chances_in_new_trick:
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
        # TODO:
        cards_left_per_suit: dict[Suit, int] = dict()
        for suit in Suit.all_suits:
            s: Suit = Suit(suit)
            for card_type in CardType.numbers:
                if Card.index(CardType(card_type), s, 0, 0) not in all_cards_seen:
                    cards_left_per_suit[s] = cards_left_per_suit.setdefault(s, 0) + 1

        cards_remaining: float = float(NUM_CARDS - len(all_cards_seen))

        for card in self.hand:
            probability: float = self.uniform_probability_of_card_winning(
                card, None, self.board.trump, all_cards_seen, 0
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
                    card, None, trump_suit, all_cards_seen, 0
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
        winning_card: Optional[Card],
        trump_suit: Suit,
        cards_seen: set[int],
        cards_played_in_trick: int,
    ) -> float:
        """
        Probability of a card winning if it were played first

        :param card: card to calculate probability for
        :param winning_card: current winning card in the trick
        :param trump_suit: suit of the trump card / chosen by the dealer if trump card is a wizard
        :param cards_seen: set of indices of cards seen so far in the round. Includes own hand + trump
        :param cards_played_in_trick: number of cards played in the trick so far
                                      (assumes current player hasn't played yet)
        """
        # card loses against current best
        if (
            winning_card is not None
            and compare_cards(winning_card, card, trump_suit) > 0
        ):
            return 0.0

        if card.card_type == CardType.WIZARD:
            return 1.0

        if card.card_type == CardType.JESTER:
            # Not real probability, does not account for all jokers case
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
        # if self.player_suit_exhausted:
        #     return self.probability_of_card_winning_with_player_info(
        #         card,
        #         trick,
        #         cards_seen,
        #         len(trick.cards),
        #     )
        #
        return self.estimate_probability_of_winning_with_card(card, trick, cards_seen)

    # TODO: Remove duplication
    def probability_of_card_winning_with_player_info(
        self,
        card: Card,
        trick: Trick,
        cards_seen: set[int],
        cards_played_in_trick: int,
    ) -> float:
        if (
            trick.winner_card is not None
            and compare_cards(trick.winner_card, card, trick.trump) > 0
        ):
            return 0.0

        if card.card_type == CardType.WIZARD:
            return 1.0

        if card.card_type == CardType.JESTER:
            # Not real probability, does not account for all jokers case
            return 0.0

        if (
            trick.suit_to_follow in Suit.all_suits
            and card.suit != trick.suit_to_follow
            and card.suit != trick.trump
        ):
            return 0.0

        cards_which_lose: int = 0

        cards_which_lose_per_suit: dict[Suit, int] = {
            Suit(suit): 0 for suit in Suit.values
        }

        # same suit
        card_index: int = Card.index(
            CardType.ONE, card.suit, jester_index=0, wizard_index=0
        )
        for i in range(card.card_type - 1):
            if card_index + i not in cards_seen:
                cards_which_lose_per_suit[card.suit] += 1
                cards_which_lose += 1

        # jester
        for i in range(NUM_JESTERS):
            card_index = Card.index(
                CardType.JESTER, Suit.NONE, jester_index=i, wizard_index=0
            )
            if card_index + i not in cards_seen:
                cards_which_lose_per_suit[Suit.NONE] += 1
                cards_which_lose += 1

        suits_which_lose: Iterable[Suit] = (
            Suit(suit)
            for suit in Suit.all_suits
            if suit != card.suit and suit != trick.trump
        )

        # non-same suit
        for suit in suits_which_lose:
            card_index = Card.index(CardType.ONE, suit, jester_index=0, wizard_index=0)
            for i in range(CARDS_PER_SUIT):
                if card_index + i not in cards_seen:
                    cards_which_lose_per_suit[suit] += 1
                    cards_which_lose += 1

        if cards_which_lose == 0:
            return 0.0

        cards_left: int = NUM_CARDS - len(cards_seen)

        cards_left_in_trick: int = self.num_players - cards_played_in_trick - 1

        if cards_which_lose < cards_left_in_trick:
            return 0.0

        players_left = {
            player
            for player in self.board.player_scores
            if player not in trick.cards and player != self.name
        }

        if len(players_left) > cards_which_lose:
            return 0.0

        return self.probability_of_players_having_losing_cards(
            cards_which_lose_per_suit, players_left, cards_left, 1.0
        )

    def probability_of_players_having_losing_cards(
        self,
        losing_cards_per_suit: dict[Suit, int],
        players_left: set[str],
        cards_left: int,
        probability: float,
    ) -> float:
        if len(players_left) == 0:
            return probability

        player: str = players_left.pop()
        can_play_losing_cards = False
        player_probability: float = 0.0
        for suit, num_cards in tuple(losing_cards_per_suit.items()):
            if suit in self.player_suits_left[player] and num_cards > 0:
                can_play_losing_cards = True
                losing_cards_per_suit[suit] -= 1

                player_probability += (
                    float(num_cards)
                    / float(cards_left)
                    * self.probability_of_players_having_losing_cards(
                        losing_cards_per_suit, players_left, cards_left - 1, 1.0
                    )
                )

                losing_cards_per_suit[suit] += 1

        if not can_play_losing_cards:
            return 0.0

        players_left.add(player)
        return probability * player_probability

    def estimate_probability_of_winning_with_card(
        self, card: Card, trick: Trick, cards_seen: set[int]
    ) -> float:
        players_left: set[str] = {
            player
            for player in self.board.player_scores
            if player not in trick.cards and player != self.name
        }
        if (
            trick.winner_card is not None
            and compare_cards(trick.winner_card, card, trick.trump) > 0
        ):
            return 0.0

        if card.card_type == CardType.WIZARD:
            return 1.0

        player_probabilities: dict[FrozenSet, float] = dict()
        probability = 1.0
        for player in players_left:
            suits_left = frozenset(self.player_suits_left[player])
            if suits_left in player_probabilities:
                player_losing_probability: float = player_probabilities[suits_left]
            else:
                player_losing_probability: float = (
                    self.simulate_player_losing_probability(
                        suits_left,
                        card,
                        len(self.hand),
                        trick,
                        cards_seen,
                        iterations=1000,
                    )
                )
            probability *= player_losing_probability
        return probability

    def simulate_player_losing_probability(
        self,
        suits_left: frozenset[Suit],
        card_to_beat: Card,
        num_cards: int,
        trick: Trick,
        cards_seen: set[int],
        iterations: int = 1000,
    ) -> float:
        deck: list[Card] = [
            card
            for card in build_deck()
            if hash(card) not in cards_seen and card.suit in suits_left
        ]
        for i in range(NUM_JESTERS):
            wizard: Card = Card(CardType.WIZARD, Suit.NONE, wizard_index=i)
            if hash(wizard) not in cards_seen:
                deck.append(wizard)
            jester: Card = Card(CardType.JESTER, Suit.NONE, jester_index=i)
            if hash(jester) not in cards_seen:
                deck.append(jester)

        if len(deck) < num_cards:
            return 0.0

        num_hands: int = 0
        probability_of_winning: float = 0.0
        can_play_anything = (
            trick.is_wizard_played
            or (trick.suit_to_follow == Suit.NONE or trick.suit_to_follow is None)
            and card_to_beat.suit == Suit.NONE
        )
        if can_play_anything:
            suits_to_play: set[Suit] = {Suit(suit) for suit in Suit.values}
        else:
            suits_to_play: set[Suit] = (
                {card_to_beat.suit, Suit.NONE}
                if trick.suit_to_follow == Suit.NONE or trick.suit_to_follow is None
                else {trick.suit_to_follow, Suit.NONE}
            )
        for i in range(iterations):
            random.shuffle(deck)
            for j in range(len(deck) // num_cards):
                num_hands += 1
                special_playable_cards: int = 0
                playable_cards: int = 0
                losing_cards: int = 0
                losing_cards_in_hand: int = 0
                for k in range(num_cards):
                    card: Card = deck[j * num_cards + k]
                    if card.suit in suits_to_play:
                        playable_cards += 1

                    if card.suit == Suit.NONE:
                        special_playable_cards += 1

                    if compare_cards(card_to_beat, card, trick.trump) > 0:
                        losing_cards_in_hand += 1
                        if card.suit in suits_to_play:
                            losing_cards += 1

                if playable_cards == special_playable_cards:
                    playable_cards = num_cards
                    losing_cards = losing_cards_in_hand

                # Uniform probability
                probability_of_winning += float(losing_cards) / float(playable_cards)

        return float(probability_of_winning) / float(num_hands)

    # def simulate_probability_of_remaining_players_losing(
    #     self,
    #     players_left: set[str],
    #     suits_left: frozenset[Suit],
    #     card_to_beat: Card,
    #     num_cards: int,
    #     trick: Trick,
    #     cards_seen: set[int],
    #     iterations: int = 1000,
    # ) -> float:
    #     deck: set[Card] = {
    #         card
    #         for card in build_deck()
    #         if hash(card) not in cards_seen
    #     }
    #     for i in range(NUM_JESTERS):
    #         wizard: Card = Card(CardType.WIZARD, Suit.NONE, wizard_index=i)
    #         if hash(wizard) not in cards_seen:
    #             deck.add(wizard)
    #         jester: Card = Card(CardType.JESTER, Suit.NONE, jester_index=i)
    #         if hash(jester) not in cards_seen:
    #             deck.add(jester)
    #
    #     if len(deck) < num_cards:
    #         print("WARNING - there are too few cards left")
    #         return 0.0
    #
    #     probability_of_winning: float = 0.0
    #     can_play_anything = (
    #         trick.is_wizard_played
    #         or (trick.suit_to_follow == Suit.NONE or trick.suit_to_follow is None)
    #         and card_to_beat.suit == Suit.NONE
    #     )
    #     if can_play_anything:
    #         suits_to_play: set[Suit] = {Suit(suit) for suit in Suit.values}
    #     else:
    #         suits_to_play: set[Suit] = (
    #             {card_to_beat.suit, Suit.NONE}
    #             if trick.suit_to_follow == Suit.NONE or trick.suit_to_follow is None
    #             else {trick.suit_to_follow, Suit.NONE}
    #         )
    #
    #     for i in range(iterations):
    #         random.shuffle(deck)
    #         for (j, player in players_left:
    #             special_playable_cards: int = 0
    #             playable_cards: int = 0
    #             losing_cards: int = 0
    #             losing_cards_in_hand: int = 0
    #             for k in range(num_cards):
    #                 card: Card = deck[j * num_cards + k]
    #                 if card.suit in suits_to_play:
    #                     playable_cards += 1
    #
    #                 if card.suit == Suit.NONE:
    #                     special_playable_cards += 1
    #
    #                 if compare_cards(card_to_beat, card, trick.trump) > 0:
    #                     losing_cards_in_hand += 1
    #                     if card.suit in suits_to_play:
    #                         losing_cards += 1
    #
    #             if playable_cards == special_playable_cards:
    #                 playable_cards = num_cards
    #                 losing_cards = losing_cards_in_hand
    #
    #             # Uniform probability
    #             probability_of_winning += float(losing_cards) / float(playable_cards)
    #
    #     return float(probability_of_winning) / float(num_hands)

    def generate_hand(
        self, hand_size: int, suits_left: frozenset[Suit], deck: set[Card]
    ):
        if len(deck) == hand_size:
            return set(deck)

        available_cards = tuple(card for card in deck if card.suit in suits_left)
        if len(available_cards) < hand_size:
            raise Exception(
                f"There are not enough cards to build a hand -  deck= {deck}, available cards={available_cards}, "
                f"suits_left={suits_left}"
            )
        hand: set[Card] = set(random.sample(available_cards, hand_size))
        deck -= hand
        return hand
