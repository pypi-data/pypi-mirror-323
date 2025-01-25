# pylint: disable=wrong-import-order
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=no-member
# pylint: disable=protected-access

from typing import Sequence
import pytest

from pyblackjack import objects
from pyblackjack.objects import Dealer
from conftest import get_cards

class MockShoe:
    def __init__(self):
        self.hits = 0
        self.iter = None

    def set_next(self, cards):
        self.iter = iter(get_cards(cards))

    def deal(self):
        self.hits += 1
        return next(self.iter)

# # # # # # # # # # TESTS # # # # # # # # # #

@pytest.mark.parametrize('hit_soft_17,expected', [
    (True, 18),
    (False, 17)
])
def test_hit_soft_17(hit_soft_17, expected):
    dealer = Dealer(hit_soft_17)
    assert dealer.soft_stand == expected

@pytest.mark.parametrize('cards,expected', [
    ((8, 5), False),
    ((1, 7), False),
    ((12, 1), True),
    ((5, 1), True),
    ((5, 4, 7, 1), False)
])
def test_check_insurance(cards, expected):
    dealer = Dealer()
    dealer.cards = get_cards(cards)
    assert dealer.check_insurance() is expected

@pytest.mark.parametrize('hit_soft_17,hand,deck,hits', [
    (True, (8, 5), (7, 3, 8, 5), 1),
    (True, (1, 7), (3, 4, 7, 10), 0),
    (True, (1, 2), (4, 1, 5, 7), 2),
    (False, (1, 2), (4, 1, 5, 7), 1),
    (True, (5, 1), (12, 11, 4, 6), 2),
    (True, (8, 8), (1, 2, 3, 4), 1)
])
def test_play_hand(
    monkeypatch,
    hit_soft_17: bool,
    hand: Sequence[int],
    deck: Sequence[int],
    hits: int,
):
    shoe = MockShoe()
    monkeypatch.setattr(objects, 'SHOE', shoe)
    dealer = Dealer(hit_soft_17)
    dealer.cards = get_cards(hand)
    shoe.set_next(deck)
    dealer.play_hand()
    assert shoe.hits == hits
