import random
from typing import Optional

from WizardAI.Card import build_shuffled_deck
from WizardAI.Board import Board
from WizardAI.Card import Card, CardType, Suit
from WizardAI.Player import Player
from WizardAI.Trick import Trick

CARDS_IN_DECK = 60


class Game:
    def __init__(self, players: list[Player]) -> None:
        super().__init__()
        assert len(players) > 2, "Cannot play Wizard with less than 2 people"
        self.board: Optional[Board] = None
        self.players: dict[str, Player] = {player.name: player for player in players}
        self.player_scores: dict[str, int] = {player.name: 0 for player in players}
        self.dealer: str = players[0].name
        self.next_player_lookup: dict[str, str] = {
            player.name: players[(i + 1) % len(players)].name
            for i, player in enumerate(players)
        }
        self.tricks: list[Trick] = list()

    def play_round(self, num_cards: int) -> None:
        # shuffle
        deck: list[Card] = build_shuffled_deck()
        first_player = self.next_player_lookup[self.dealer]

        player_hands: dict[str, list[Card]] = dict()

        # deal hands
        player_name: str = first_player
        for i in range(len(self.players)):
            hand: list[Card] = deck[i * num_cards : (i + 1) * num_cards]
            player_hands[player_name] = hand
            self.players[player_name].deal_hand(hand)
            print(
                f"round {num_cards}, dealing hand to player {player_name} - hand={','.join(str(card) for card in hand)}"
                f", hand_size = {len(hand)}"
            )
            if len(hand) != num_cards:
                print(
                    f"something went wrong while dealing the cards to {player_name} - hand size = {len(hand)}, "
                    f"expected hand size = {num_cards}!"
                )
                exit(1)
            player_name = self.next_player_lookup[player_name]

        # choose trump (if applicable)
        trump_card: Optional[Card] = None
        trump: Suit = Suit.NONE
        if num_cards * len(self.players) < len(deck):
            trump_card: Card = deck[num_cards * len(self.players)]
            if trump_card.card_type == CardType.WIZARD:
                trump = self.players[self.dealer].choose_trump()
            else:
                trump = trump_card.suit

        print(f"Trump card for this round is {trump_card}, trump suit = {trump}")

        bids: dict[str, int] = dict()
        board: Board = Board(
            trump_card,
            trump,
            bids,
            self.player_scores,
            self.next_player_lookup,
            first_player,
        )

        # gather bids
        player_name = first_player
        for i in range(len(self.players)):
            self.players[player_name].set_board(board)
            bid = self.players[player_name].calculate_bid(bids)
            bids[player_name] = bid
            player_name = self.next_player_lookup[player_name]

        print(f"Round {num_cards}, trump={trump_card}/{trump} - bids: {bids}")
        # play tricks
        trick: Trick = Trick(trump)
        for i in range(num_cards):
            trick: Trick = Trick(trump)
            print(f"Round {num_cards}, Trick {i} - {trick}")
            for j in range(len(self.players)):
                player_name: str = board.turn
                turn = board.turn
                hand_size = len(self.players[turn].hand)
                print(
                    f"round {num_cards}, player {board.turn} - hand={','.join(str(card) for card in self.players[board.turn].hand)}"
                )
                card: Card = self.players[board.turn].choose_card(trick)
                hand_size2 = len(self.players[turn].hand)
                if hand_size != hand_size2 + 1:
                    print(hand_size, hand_size2)
                    exit()
                if card not in player_hands[player_name]:
                    print(f"{player_name} played an unplayable card!! {card}")
                trick.play_card(player_name, card)
                board.card_played(player_name, card)
                print(f"Round {num_cards}, Trick {i} - {trick}")

            board.trick_won(trick.winner_player)

            for player_name, player in self.players.items():
                player.trick_outcome(trick)

        self.tricks.append(trick)

        # score
        board.update_scores()
        print(f"Bids: {board.player_bids}")
        print(f"Tricks won: {board.player_tricks_won}")
        print(self.player_scores)

    def play_game(self) -> None:
        for i in range(CARDS_IN_DECK // len(self.players)):
            print(f"Round {i + 1}")
            self.play_round(i + 1)
