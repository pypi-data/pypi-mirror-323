# pylint: disable=wrong-import-order
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=no-member
# pylint: disable=protected-access

from typing import Sequence, cast
import pytest

from pyblackjack import objects
from pyblackjack.objects import Hand

from conftest import MockShoe, get_cards

@pytest.fixture
def hand():
    return Hand(bet=0)

# # # # # # # # # # TESTS # # # # # # # # # #

@pytest.mark.parametrize('cards,expected', [
    ((8, 5), 13),
    ((2, 7), 9),
    ((12, 1), 11),
    ((5, 4, 7, 11), 26)
])
def test_hard_total(hand: Hand, cards: Sequence[int], expected: int):
    hand.cards = get_cards(cards)
    assert hand.hard_total() == expected

@pytest.mark.parametrize('cards,expected', [
    ((8, 5), None),
    ((1, 7), 18),
    ((12, 1), 21),
    ((5, 4, 7, 1), None)
])
def test_soft_total(hand: Hand, cards: Sequence[int], expected: int | None):
    hand.cards = get_cards(cards)
    assert hand.soft_total() == expected

@pytest.mark.parametrize('cards,expected', [
    ((8, 5), 13),
    ((1, 7), 18),
    ((12, 1), 21),
    ((5, 4, 7, 1), 17)
])
def test_total(hand: Hand, cards: Sequence[int], expected: int):
    hand.cards = get_cards(cards)
    assert hand.total() == expected

@pytest.mark.parametrize('cards,expected', [
    ((8, 5), '8 5 (13)'),
    ((1, 7), 'A 7 (18)'),
    ((12, 1), 'Q A (21)'),
    ((11, 13), 'J K (20)'),
    ((5, 4, 7, 11), '5 4 7 J (26)')
])
def test_print_hand(hand: Hand, cards: Sequence[int], expected: str):
    hand.cards = get_cards(cards)
    assert hand.print_hand() == expected

@pytest.mark.parametrize('cards,expected', [
    ((8, 5), '[] 5'),
    ((12, 1), '[] A'),
    ((11, 13), '[] K'),
    ((5, 4, 7, 11), '[] 4 7 J')
])
def test_print_hand_with_downcard(hand: Hand, cards: Sequence[int],
                                  expected: str):
    hand.cards = get_cards(cards)
    assert hand.print_hand(downcard=True) == expected

@pytest.mark.parametrize('cards,expected', [
    ((8, 5), False),
    ((12, 1), True),
    ((1, 11), True),
    ((6, 8, 7), False)
])
def test_check_blackjack(hand: Hand, cards: Sequence[int], expected: bool):
    hand.cards = get_cards(cards)
    assert hand.check_blackjack() is expected

@pytest.mark.parametrize('cards,expected', [
    ((8, 5), False),
    ((5, 4, 7, 1), False),
    ((5, 4, 7, 6), True),
    ((6, 8, 7), False)
])
def test_check_bust(hand: Hand, cards: Sequence[int], expected: bool):
    hand.cards = get_cards(cards)
    assert hand.check_bust() is expected

def test_hit(hand: Hand, mock_shoe):
    SHOE = cast(MockShoe, objects.SHOE)
    SHOE.set_next(5)
    n = len(hand.cards)
    hand.hit()
    assert len(hand.cards) == n + 1
    assert hand.cards[-1] == 5
    SHOE.set_next(12)
    n = len(hand.cards)
    hand.hit()
    assert len(hand.cards) == n + 1
    assert hand.cards[-1] == 10
    assert hand.cards[-1].rank == 'Q'

def test_reset(hand: Hand):
    hand.cards = get_cards([4, 9, 8])
    assert len(hand.cards) != 0
    hand.reset()
    assert len(hand.cards) == 0
