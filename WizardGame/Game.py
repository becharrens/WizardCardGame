import random
from typing import Optional

from WizardGame.Board import Board
from WizardGame.Card import Card, CardType, Suit
from WizardGame.Player import Player
from WizardGame.PlayerBid import PlayerBid
from WizardGame.Trick import Trick

CARDS_IN_DECK = 60


def get_shuffled_deck() -> list[Card]:
    deck: list[Card] = list(Card(CardType(card_type), Suit(suit))
                            for card_type in CardType.numbers
                            for suit in Suit.all_suits)

    for i in range(4):
        deck.append(Card(CardType.WIZARD, Suit.NONE, wizard_index=i))
        deck.append(Card(CardType.JESTER, Suit.NONE, jester_index=i))

    random.shuffle(deck)

    return deck


class Game:
    def __init__(self, players: list[Player]) -> None:
        super().__init__()
        assert len(players) > 2, "Cannot play Wizard with less than 2 people"
        self.board: Optional[Board] = None
        self.players: dict[str, Player] = {player.name: player for player in players}
        self.scores: dict[str, int] = {player.name: 0 for player in players}
        self.dealer: str = players[0].name
        self.next_player_lookup: dict[str, str] = {player.name: players[(i + 1) % len(players)].name for i, player in
                                                   enumerate(players)}
        self.tricks: list[Trick] = list()

    def play_round(self, num_cards: int) -> None:
        # shuffle
        deck: list[Card] = get_shuffled_deck()
        first_player = self.next_player_lookup[self.dealer]

        # deal hands
        player_name: str = first_player
        for i in range(len(self.players)):
            hand: set[Card] = set(deck[i * num_cards: (i + 1) * num_cards])
            self.players[player_name].deal_hand(hand)
            print(
                f"round {num_cards}, dealing hand to player {player_name} - hand={','.join(str(card) for card in hand)}, hand_size = {len(hand)}")
            if len(hand) != num_cards:
                print("something went wrong!")
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

        bids: dict[str, PlayerBid] = dict()
        board: Board = Board(trump_card, trump, bids, self.scores, self.next_player_lookup, first_player)

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
                print(f"round {num_cards}, player {board.turn} - hand={','.join(str(card) for card in self.players[board.turn].hand)}")
                card: Card = self.players[board.turn].choose_card(trick)
                hand_size2 = len(self.players[turn].hand)
                if hand_size != hand_size2 + 1:
                    print(hand_size, hand_size2)
                    exit()
                trick.play_card(player_name, card)
                board.card_played(player_name, card)
                print(f"Round {num_cards}, Trick {i} - {trick}")

            board.trick_won(trick.winner_player)

        self.tricks.append(trick)

        # score
        board.update_scores()
        print(self.scores)

    def play_game(self) -> None:
        for i in range(CARDS_IN_DECK // len(self.players)):
            print(f"Round {i + 1}")
            self.play_round(i + 1)
