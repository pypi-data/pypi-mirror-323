from collections import Counter
import random
from typing import ClassVar, Final, Iterator, no_type_check


class Card(int):
    '''An individual playing card. Subclass of int for simplicity.'''

    rank: str

    def __new__(cls, rank: str) -> 'Card':
        value: int
        if rank == 'A':
            value = 1
        elif rank in 'JQK':
            value = 10
        elif rank == '[]':
            value = 0
        else:
            value = int(rank)
        self: Card = super().__new__(cls, value)
        self.rank = rank
        return self

    def __str__(self) -> str:
        return str(self.rank)


CARDSET = [
    Card('A'),
    Card('2'),
    Card('3'),
    Card('4'),
    Card('5'),
    Card('6'),
    Card('7'),
    Card('8'),
    Card('9'),
    Card('10'),
    Card('J'),
    Card('Q'),
    Card('K'),
]

DECK: Final[list[Card]] = CARDSET * 4

FACEDOWN_CARD: Final[Card] = Card('[]')

class Shoe:
    def __init__(self, *, decks: int = 6):
        self.decks: int = decks
        self.cards: list[Card] = []
        self.cut: int = 0
        self.new()

    def deal(self) -> Card:
        return self.cards.pop()

    @property
    def time_to_shuffle(self) -> bool:
        return len(self.cards) <= self.cut

    def new(self) -> None:
        self.cards = DECK * self.decks
        random.shuffle(self.cards)
        if self.decks == 1:
            self.cut = len(self.cards) // 2
        else:
            self.cut = len(self.cards) // 4
        self.cut += random.randint(self.decks * -4, self.decks * 4)

    def __getstate__(self) -> tuple[int, dict[str, int], int]:
        counter = Counter(card.rank for card in self.cards)
        return (self.decks, dict(counter), self.cut)

    def __setstate__(self, state: tuple[int, dict[str, int], int]) -> None:
        decks, counter, cut = state
        self.decks = decks
        self.cut = cut
        self.cards = []
        for rank, count in counter.items():
            self.cards.extend([Card(rank)] * count)
        random.shuffle(self.cards)

SHOE: Final[Shoe] = Shoe()

class Hand:
    def __init__(self, *, bet: int) -> None:
        self.cards: list[Card] = []
        self.bet: int = bet

    def hard_total(self) -> int:
        return sum(self.cards)

    def soft_total(self) -> int | None:
        total = self.hard_total()
        if total > 11 or 1 not in self.cards:
            return None
        return total + 10

    def total(self) -> int:
        return self.soft_total() or self.hard_total()

    def print_hand(self, downcard: bool = False)-> str:
        cards: list[Card] = self.cards[:]
        if downcard:
            cards[0] = FACEDOWN_CARD
        cardtext: str = ' '.join(str(card) for card in cards)
        if downcard:
            return cardtext
        else:
            return f'{cardtext} ({self.total()})'

    def check_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.total() == 21

    def check_bust(self) -> bool:
        return self.hard_total() > 21

    def hit(self) -> None:
        self.cards.append(SHOE.deal())

    def reset(self) -> None:
        self.cards = []


class Dealer(Hand):
    def __init__(self, hit_soft_17: bool = True):
        super().__init__(bet=0)
        self.hard_stand: Final[int] = 17
        self.soft_stand: Final[int] = 18 if hit_soft_17 else 17

    def check_insurance(self) -> bool:
        return self.cards[1] == 1

    def play_hand(self) -> None:
        while True:
            soft_total: int | None = self.soft_total()
            if ((soft_total and soft_total >= self.soft_stand)
                    or self.hard_total() >= self.hard_stand):
                break
            self.hit()

    def __getstate__(self) -> int:
        return self.soft_stand

    @no_type_check
    def __setstate__(self, state: int) -> None:
        super().__init__(bet=0)
        self.hard_stand = 17
        self.soft_stand = state


class Player:
    _id: ClassVar[int] = 0

    def __init__(
        self,
        name: str | None = None,
        chips: int = 1000,
    ):
        self.__class__._id += 1
        self.id: Final[int] = self.__class__._id
        self.name: Final[str] = f'Player {self.id}' if name is None else name
        self.chips: int = chips
        self.bet: int = 0
        self.insurance: int | None = None
        self.hands: list[Hand] = []
        self._active_hand: int = 0

    def __iter__(self) -> Iterator[tuple[int, Hand]]:
        while self._active_hand < len(self.hands):
            yield (self._active_hand + 1, self.active_hand)
            self._active_hand += 1
        # cleanup
        self._active_hand = 0

    def get_name(self) -> str:
        if self.is_split():
            return f'{self.name} (hand {self._active_hand + 1})'
        else:
            return self.name

    @property
    def active_hand(self) -> Hand:
        return self.hands[self._active_hand]

    def is_split(self) -> bool:
        return len(self.hands) > 1

    def check_bet(self) -> bool:
        return self.chips >= self.bet

    def check_blackjack(self) -> bool:
        return not self.is_split() and self.active_hand.check_blackjack()

    def hit(self) -> None:
        self.active_hand.hit()

    def check_split(self) -> bool:
        hand: Hand = self.active_hand
        return (len(hand.cards) == 2 and
                hand.cards[0].rank == hand.cards[1].rank)

    def split(self) -> None:
        self.chips -= self.bet
        new_hand = Hand(bet=self.bet)
        new_hand.cards.append(self.active_hand.cards.pop())
        self.hands.append(new_hand)
        self.active_hand.hit()

    def check_double(self) -> bool:
        return (len(self.active_hand.cards) == 2 and
                9 <= self.active_hand.total() <= 11)

    def double_down(self) -> None:
        self.chips -= self.active_hand.bet
        self.active_hand.bet *= 2
        self.active_hand.hit()

    def surrender(self) -> None:
        self.chips += self.bet // 2

    def buy_insurance(self) -> None:
        price: int = self.bet // 2
        self.chips -= price
        self.insurance = price

    def reset(self) -> None:
        self._active_hand = 0
        self.insurance = None

    def __getstate__(self) -> tuple[str, int]:
        return (self.name, self.chips)

    @no_type_check
    def __setstate__(self, state: tuple[str, int]) -> None:
        self.__init__(*state)
