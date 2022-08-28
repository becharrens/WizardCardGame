import random
from enum import IntEnum
from typing import Optional


class CardType(IntEnum):
    JESTER = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    ELEVEN = 11
    TWELVE = 12
    THIRTEEN = 13
    WIZARD = 14

    _ignore_ = ["values", "numbers"]
    values: list[int] = list()
    numbers: list[int] = list()

    def __str__(self) -> str:
        match self.name:
            case "WIZARD":
                return "Z"
            case "JESTER":
                return "N"
            case _:
                return str(self.value)


CardType.values = list(card_type for card_type in CardType)
CardType.numbers = CardType.values[1 : len(CardType.values) - 1]


class Suit(IntEnum):
    BLUE = 0
    GREEN = 1
    RED = 2
    YELLOW = 3
    NONE = 4

    _ignore_ = ["values", "all_suits"]
    values: list[int] = list()
    all_suits: list[int] = list()

    def __str__(self) -> str:
        if self.name == "NONE":
            return ""
        return self.name[0]


Suit.values = list(suit for suit in Suit)
Suit.all_suits = Suit.values[:-1]


class Card:
    wizard_index = 0
    jester_index = 0

    def __init__(
        self,
        card_type: CardType,
        suit: Suit,
        wizard_index: int = 0,
        jester_index: int = 0,
    ) -> None:
        super().__init__()
        self.card_type = card_type
        self.suit = suit
        self.wizard_index = wizard_index
        self.jester_index = jester_index

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Card) and hash(self) == hash(o)

    def __hash__(self) -> int:
        return Card.index(
            self.card_type, self.suit, self.jester_index, self.wizard_index
        )

    @staticmethod
    def index(
        card_type: CardType, suit: Suit, jester_index: int, wizard_index: int
    ) -> int:
        """
        Index for all cards of same suit are adjacent
        blue: 1 - 13
        green: 14 - 26
        red: 27 - 39
        yellow: 40 - 52
        jesters: 53 - 56
        wizards: 57 - 60
        :return: index of card
        """
        if card_type == CardType.JESTER:
            return suit * len(CardType.numbers) + jester_index + 1

        if card_type == CardType.WIZARD:
            return (
                suit * (len(CardType.numbers)) + len(Suit.all_suits) + wizard_index + 1
            )

        return suit * (len(CardType.numbers)) + card_type

    def __str__(self) -> str:
        return f"{self.card_type}{self.suit}"

    def __repr__(self):
        if self.card_type == CardType.WIZARD:
            return f"{self.card_type}{self.suit} i={self.wizard_index}"
        if self.card_type == CardType.JESTER:
            return f"{self.card_type}{self.suit} i={self.jester_index}"
        return f"{self.card_type}{self.suit}"


def card_from_string(card_str: str) -> Card:
    card_str = card_str.upper()
    match card_str:
        case "Z":
            return Card(CardType.WIZARD, Suit.NONE)
        case "N":
            return Card(CardType.JESTER, Suit.NONE)
        case _:
            try:
                card_type_str, suit_str = card_str[:-1], card_str[-1:]
                card_type: CardType = CardType(int(card_type_str))
            except (TypeError, IndexError, ValueError):
                raise InvalidCardException(f"Card {card_str} is not a valid card!")

            match suit_str:
                case "Y":
                    suit: Suit = Suit.YELLOW
                case "B":
                    suit: Suit = Suit.BLUE
                case "G":
                    suit: Suit = Suit.GREEN
                case "R":
                    suit: Suit = Suit.RED
                case _:
                    raise InvalidCardException(f"Card {card_str} is not a valid card!")
            return Card(card_type, suit)


def suit_from_string(suit_str: str) -> Suit:
    match suit_str.upper():
        case "Y":
            return Suit.YELLOW
        case "B":
            return Suit.BLUE
        case "G":
            return Suit.GREEN
        case "R":
            return Suit.RED
        case _:
            raise InvalidSuitException(f"{suit_str} is not a valid suit!")


def compare_cards(card1: Optional[Card], card2: Optional[Card], trump: Suit) -> int:
    """
    :param card1: first card to compare
    :param card2: second card to compare
    :param trump: trump suit for the round
    :return: 1 if card1 wins against card2, -1 if card1 loses card2 when card1 is played first
    """
    if card1 == card2:
        return 0

    if card1 is None:
        return -1

    if card2 is None:
        return 1

    match (card1.card_type, card2.card_type):
        case (CardType.WIZARD, _):
            return 1
        case (_, CardType.WIZARD):
            return -1
        case (CardType.JESTER, card_type2):
            return 1 if card_type2 == CardType.JESTER else -1
        case (_, CardType.JESTER):
            return 1

    match (card1.suit, card2.suit):
        case (suit1, suit2) if suit1 == suit2:
            return 1 if card1.card_type >= card2.card_type else -1
        case (suit1, suit2) if suit1 == trump or suit2 != trump:
            return 1
        case (_, _):
            return -1


def build_deck() -> list[Card]:
    deck: list[Card] = list(
        Card(CardType(card_type), Suit(suit))
        for suit in Suit.all_suits
        for card_type in CardType.numbers
    )

    for i in range(4):
        deck.append(Card(CardType.WIZARD, Suit.NONE, wizard_index=i))
        deck.append(Card(CardType.JESTER, Suit.NONE, jester_index=i))

    return deck


def build_shuffled_deck() -> list[Card]:
    deck: list[Card] = build_deck()

    random.shuffle(deck)

    return deck


def playable_cards(hand: list[Card], suit_to_follow: Optional[Suit]) -> list[Card]:
    cards: set[Card] = set(
        card
        for card in hand
        if card.suit == suit_to_follow and suit_to_follow != Suit.NONE
    )

    if len(cards) == 0:
        return list(hand)
    else:
        return list(cards.union({card for card in hand if card.suit == Suit.NONE}))


class InvalidSuitException(Exception):
    pass


class InvalidCardException(Exception):
    pass
