from typing import Optional

from WizardAI.Card import (
    Card,
    Suit,
    compare_cards,
    CardType,
    build_shuffled_deck,
    build_deck,
    playable_cards,
)
from WizardAI.Player import Player
from WizardAI.Trick import Trick


def get_new_suit_to_follow(
    played_card: Card,
    current_winning_card: Optional[Card],
    current_suit_to_follow: Optional[Suit],
) -> Optional[Suit]:
    """Should only get called if the played card wins against what is already played, if anything"""
    if played_card.card_type == CardType.WIZARD:
        if current_suit_to_follow == Suit.NONE:
            return None
        else:
            return current_suit_to_follow

    if (
        current_suit_to_follow is None and current_winning_card is None
    ) or current_suit_to_follow == Suit.NONE:
        return played_card.suit

    return current_suit_to_follow


class MonteCarloPlayer(Player):
    def __init__(
        self, name: str, num_players: int, branch_factor: int, num_iterations: int
    ) -> None:
        super().__init__(name, num_players)
        self.branch_factor: int = branch_factor
        self.num_iterations: int = num_iterations
        self.missing_suits: dict[str, set[Suit]] = dict()
        self.wins_estimate: int = -1

    def select_card(self, trick: Trick, cards_to_play: list[Card]) -> Card:
        simulator: MonteCarloSimulator = MonteCarloSimulator(
            self.name,
            self.hand,
            self.board.player_tricks_won,
            self.board.trump_card.suit,
            self.board.trump_card,
            trick.winner_card,
            trick.winner_player,
            trick.suit_to_follow,
            self.board.turn,
            dict(),
            dict(),
            self.board.next_player_lookup,
            self.branch_factor,
            self.num_iterations,
            self.wins_estimate,
        )
        return simulator.choose_card(cards_to_play)

    def choose_trump(self) -> Suit:
        simulator: MonteCarloSimulator = MonteCarloSimulator(
            self.name,
            self.hand,
            self.board.player_tricks_won,
            self.board.trump_card.suit,
            self.board.trump_card,
            None,
            None,
            None,
            self.board.turn,
            dict(),
            dict(),
            self.board.next_player_lookup,
            self.branch_factor,
            self.num_iterations,
            None,
        )
        return simulator.choose_trump()

    def select_bid(self, bids: dict[str, int]) -> int:
        simulator: MonteCarloSimulator = MonteCarloSimulator(
            self.name,
            self.hand,
            self.board.player_tricks_won,
            self.board.trump_card.suit,
            self.board.trump_card,
            None,
            None,
            None,
            self.board.turn,
            dict(),
            dict(),
            self.board.next_player_lookup,
            self.branch_factor,
            self.num_iterations,
            self.wins_estimate,
        )

        self.wins_estimate = simulator.estimate_winnings()
        return self.wins_estimate

    def trick_outcome(self, trick: Trick) -> None:
        for player, card in trick.cards.items():
            if (
                trick.suit_to_follow is not None
                and card.suit != Suit.NONE
                and card.suit != trick.suit_to_follow
            ):
                self.missing_suits.setdefault(player, set()).add(trick.suit_to_follow)


class MonteCarloSimulator:
    def __init__(
        self,
        name: str,
        hand: list[Card],
        tricks_won: dict[str, int],
        trump_suit: Suit,
        trump_card: Optional[Card],
        current_winning_card: Optional[Card],
        current_winner: Optional[str],
        suit_to_follow: Optional[Suit],
        starting_player: str,
        played_cards: dict[str, list[Card]],
        missing_suits: dict[str, set[Suit]],
        next_player_lookup: dict[str, str],
        branch_factor: int,
        num_iterations: int,
        wins_estimate: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.current_winner: Optional[str] = current_winner
        self.hand: list[Card] = hand
        # Player order
        self.next_player_lookup: dict[str, str] = next_player_lookup
        # If trump_card.card_type == CardType.WIZARD, need to set trump suit manually for simulations
        self.current_winning_card: Optional[Card] = current_winning_card
        self.suit_to_follow: Optional[Suit] = suit_to_follow
        # If there is no trump, trump suit should be Suit.NONE
        self.trump_suit: Suit = trump_suit
        self.trump_card: Optional[Card] = trump_card
        self.name: str = name
        self.branch_factor: int = branch_factor
        self.num_iterations: int = num_iterations
        self.starting_player: str = starting_player
        self.played_cards: dict[str, list[Card]] = played_cards
        self.all_played_cards: set[Card] = {
            card for player_cards in played_cards.values() for card in player_cards
        }
        self.missing_suits: dict[str, set[Suit]] = missing_suits
        self.wins_estimate: Optional[int] = wins_estimate
        self.tricks_won: dict[str, int] = dict(tricks_won)

    def simulate_number_of_wins_with_starting_hands(
        self,
        current_player: str,
        tricks_won: dict[str, int],
        player_hands: dict[str, list[Card]],
        current_winner: Optional[str],
        winning_card: Optional[Card],
        suit_to_follow: Optional[Suit],
        winning_freq: dict[int, int],
        cards_played: int,
    ) -> None:
        reset_tricks_won: bool = False
        prev_winner: str = current_winner
        if cards_played > 0 and cards_played % len(player_hands) == 0:
            # print(f"Current player: {current_player} - end of trick: {player_hands}")

            tricks_won.setdefault(current_winner, 0)
            tricks_won[current_winner] += 1
            current_player = current_winner
            current_winner = None
            winning_card = None
            suit_to_follow = None
            reset_tricks_won = True

            if len(player_hands[current_player]) == 0:
                tricks_won_by_player: int = tricks_won.setdefault(self.name, 0)
                winning_freq.setdefault(tricks_won_by_player, 0)
                winning_freq[tricks_won_by_player] += 1
                tricks_won[prev_winner] -= 1
                # print(
                #     f"Current player: {current_player} - before returning: {player_hands}"
                # )

                return

        player_hand: list[Card] = player_hands[current_player]
        cards: list[Card] = playable_cards(player_hand, suit_to_follow)
        next_player: str = self.next_player_lookup[current_player]
        for i in range(min(self.branch_factor, len(cards))):
            card: Card = cards[i]
            new_hand: list[Card] = [c for c in player_hand if c != card]
            # print(
            #     f"Current player: {current_player} - before: {player_hands}, {player_hand}"
            # )
            player_hands[current_player] = new_hand
            # print(f"Current player: {current_player} - after: {player_hands}")
            if compare_cards(winning_card, card, self.trump_suit) < 0:
                next_suit_to_follow: Optional[Suit] = get_new_suit_to_follow(
                    card, winning_card, suit_to_follow
                )
                self.simulate_number_of_wins_with_starting_hands(
                    next_player,
                    tricks_won,
                    player_hands,
                    current_player,
                    card,
                    next_suit_to_follow,
                    winning_freq,
                    cards_played + 1,
                )
            else:
                self.simulate_number_of_wins_with_starting_hands(
                    next_player,
                    tricks_won,
                    player_hands,
                    current_winner,
                    winning_card,
                    suit_to_follow,
                    winning_freq,
                    cards_played + 1,
                )

        # print(
        #     f"Current player: {current_player} - restoring before: {player_hands}, {player_hand}"
        # )
        player_hands[current_player] = player_hand
        # print(
        #     f"Current player: {current_player} - restoring after: {player_hands}, {player_hand}"
        # )
        if reset_tricks_won:
            tricks_won[prev_winner] -= 1

    def estimate_winnings(self) -> int:
        winning_freq: dict[int, int] = dict()
        for i in range(self.num_iterations):
            hands: dict[str, list[Card]] = self.generate_hands_without_constraints(
                self.get_starting_hand_sizes()
            )
            self.simulate_number_of_wins_with_starting_hands(
                self.starting_player, dict(), hands, None, None, None, winning_freq, 0
            )

        max_freq: int = -1
        best_estimate: int = 0
        for tricks_won, freq in winning_freq.items():
            if max_freq < freq:
                max_freq = freq
                best_estimate = tricks_won

        # Set wins estimate
        self.wins_estimate = best_estimate
        return best_estimate

    def choose_trump(self) -> Suit:
        best_suit: Suit = Suit.NONE
        max_freq: int = -1
        for suit in Suit.all_suits:
            win_frequencies: dict[int, int] = dict()
            for i in range(self.num_iterations):
                hands: dict[str, list[Card]] = self.generate_hands_without_constraints(
                    self.get_starting_hand_sizes()
                )

                # Set the chosen trump suit
                self.trump_suit = suit
                self.simulate_number_of_wins_with_starting_hands(
                    self.starting_player,
                    dict(),
                    hands,
                    None,
                    None,
                    None,
                    win_frequencies,
                    0,
                )

            # TODO: Revise - should this be in terms of max score or just max freq
            for tricks_won, freq in win_frequencies.items():
                if max_freq < freq:
                    max_freq = freq
                    best_suit = Suit(suit)

        # Set the trump suit for the simulation
        self.trump_suit = best_suit
        return best_suit

    def choose_card(self, cards_to_play: list[Card]) -> Card:
        # Assume it is simulated player's turn
        hands: dict[str, list[Card]] = self.generate_hands_with_constraints(
            max_tries=10
        )
        hand_sizes: dict[str, int] = self.get_hand_sizes()
        # Count card which is about to be played
        cards_played: int = self.get_cards_played(hand_sizes) + 1
        next_player: str = self.next_player_lookup[self.name]

        best_outcome: int = -1000
        best_frequency: int = -1
        chosen_card: Card = cards_to_play[0]
        for card in cards_to_play:
            new_hand: list[Card] = [c for c in self.hand if c != card]
            hands[self.name] = new_hand
            winning_freq: dict[int, int] = dict()
            if compare_cards(self.current_winning_card, card, self.trump_suit) < 0:
                next_suit_to_follow: Optional[Suit] = get_new_suit_to_follow(
                    card, self.current_winning_card, self.suit_to_follow
                )

                self.simulate_number_of_wins_with_starting_hands(
                    next_player,
                    self.tricks_won,
                    hands,
                    self.name,
                    card,
                    next_suit_to_follow,
                    winning_freq,
                    cards_played,
                )
            else:
                self.simulate_number_of_wins_with_starting_hands(
                    next_player,
                    self.tricks_won,
                    hands,
                    self.current_winner,
                    self.current_winning_card,
                    self.suit_to_follow,
                    winning_freq,
                    cards_played,
                )

            assert (
                self.wins_estimate is not None
            ), "we should have calculated a wins estimate before starting to play!"

            if self.wins_estimate in winning_freq:
                estimated_freq: int = winning_freq[self.wins_estimate]
                if best_outcome != self.wins_estimate:
                    best_frequency = estimated_freq
                    best_outcome = self.wins_estimate
                    chosen_card = card
                else:
                    if estimated_freq > best_frequency:
                        chosen_card = card
                        best_frequency = estimated_freq
            elif best_outcome != self.wins_estimate:
                current_diff: int = abs(best_outcome - self.wins_estimate)
                for outcome, freq in winning_freq.items():
                    diff: int = abs(best_outcome - outcome)
                    if diff < current_diff:
                        best_outcome = outcome
                        best_frequency = freq
                        chosen_card = card
                    elif diff == current_diff and freq > best_frequency:
                        best_frequency = freq
                        chosen_card = card

        return chosen_card

    def generate_hands_without_constraints(
        self, hand_sizes: dict[str, int]
    ) -> dict[str, list[Card]]:
        all_cards: list[Card] = [
            card
            for card in build_shuffled_deck()
            if card not in self.hand
            and card != self.trump_card
            and card not in self.all_played_cards
        ]

        start_idx = 0
        hands: dict[str, list[Card]] = dict()
        for player in self.next_player_lookup.keys():
            if player != self.name:
                hand_size: int = hand_sizes[player]
                hand: list[Card] = all_cards[start_idx : start_idx + hand_size]
                start_idx += hand_size
                hands[player] = hand

        hands[self.name] = self.hand
        return hands

    def generate_hands_with_constraints(self, max_tries=10):
        hand_sizes: dict[str, int] = self.get_hand_sizes()
        tries: int = 0
        success: bool = False
        while tries < max_tries:
            tries += 1
            all_cards: set[Card] = {
                card
                for card in build_deck()
                if card not in self.hand
                and card != self.trump_card
                and card not in self.all_played_cards
            }

            hands: dict[str, list[Card]] = dict()

            for player in self.next_player_lookup.keys():
                if player != self.name:
                    hand_size: int = hand_sizes[player]
                    possible_cards: set[Card] = {
                        card
                        for card in all_cards
                        if player not in self.missing_suits
                        or card.suit not in self.missing_suits[player]
                    }
                    if len(possible_cards) < hand_sizes[player]:
                        break

                    hand: list[Card] = [possible_cards.pop() for _ in range(hand_size)]
                    all_cards.difference_update(hand)

                    hands[player] = hand

            if success:
                hands[self.name] = self.hand
                return hands

        return self.generate_hands_without_constraints(hand_sizes)

    def get_hand_sizes(self) -> dict[str, int]:
        hand_size: int = len(self.hand) - 1
        current_player: str = self.starting_player
        hand_sizes: dict[str, int] = dict()
        for i in range(len(self.next_player_lookup)):
            if current_player == self.name:
                hand_size += 1

            hand_sizes[current_player] = hand_size
            current_player = self.next_player_lookup[current_player]

        return hand_sizes

    def get_cards_played(self, hand_sizes: dict[str, int]) -> int:
        cards_played: int = 0
        # Assumes that the method gets called before simulated player plays
        max_hand_size = hand_sizes[self.name]
        for player, hand_size in hand_sizes.items():
            if hand_size < max_hand_size:
                cards_played += 1
        return cards_played

    def get_starting_hand_sizes(self) -> dict[str, int]:
        return {player: len(self.hand) for player in self.next_player_lookup}

    def debug_valid_hand(
        self, hand: list[Card], new_hand: list[Card], expected_hand: set[Card]
    ):
        return len(set(hand).intersection(expected_hand)) == len(hand) or len(
            set(new_hand).intersection(expected_hand)
        ) == len(hand)
