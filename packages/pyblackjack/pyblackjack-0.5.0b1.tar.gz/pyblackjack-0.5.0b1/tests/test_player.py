# pylint: disable=wrong-import-order
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=no-member
# pylint: disable=protected-access

from typing import Sequence, cast
import pytest

from pyblackjack import objects
from pyblackjack.objects import Hand, Player
from conftest import MockShoe, get_cards

@pytest.fixture
def player():
    ret = Player()
    ret.hands.append(Hand(bet=0))
    return ret

# # # # # # # # # # TESTS # # # # # # # # # #

def test_id():
    _id = Player._id
    for _ in range(6):
        Player()
    assert Player._id == _id + 6

@pytest.mark.parametrize('chips,bet,expected', [
    (1000, 500, True),
    (500, 1000, False),
    (1000, 1000, True),
    (1000, 1001, False)
])
def test_check_bet(player: Player, chips: int, bet: int, expected: bool):
    player.chips = chips
    player.bet = bet
    assert player.check_bet() is expected

@pytest.mark.parametrize('cards,expected', [
    ((8, 5), False),
    ((2, 2), True),
    ((11, 11), True),
    ((10, 13), False),
    ((7, 7, 2), False)
])
def test_check_split(player: Player, cards: Sequence[int], expected: bool):
    player.active_hand.cards = get_cards(cards)
    assert player.check_split() is expected


def test_split(player: Player, mock_shoe):
    shoe = cast(MockShoe, objects.SHOE)
    shoe.set_next(4)
    player.active_hand.cards = get_cards([8, 8])
    player.active_hand.bet = 100
    player.bet = 100
    player.chips = 900
    player.split()
    assert player.active_hand.cards == get_cards([8, 4])
    assert len(player.hands) == 2
    assert player.hands[1].cards == get_cards([8])
    assert player.chips == 800
    assert player.bet == 100
    assert player.hands[0].bet == 100
    assert player.hands[1].bet == 100

@pytest.mark.parametrize('cards,expected', [
    ((8, 4), False),
    ((2, 2), False),
    ((4, 5), True),
    ((5, 6), True),
    ((2, 6), False),
    ((4, 6, 5), False),
    ((2, 4, 5), False)
])
def test_check_double(player: Player, cards: Sequence[int], expected: bool):
    player.active_hand.cards = get_cards(cards)
    assert player.check_double() is expected


def test_double_down(player: Player, mock_shoe):
    shoe = cast(MockShoe, objects.SHOE)
    shoe.set_next(7)
    player.active_hand.cards = get_cards([8, 3])
    player.chips = 900
    player.bet = 100
    player.active_hand.bet = 100
    player.double_down()
    assert player.active_hand.cards == get_cards([8, 3, 7])
    assert player.chips == 800
    assert player.bet == 100
    assert player.active_hand.bet == 200

@pytest.mark.parametrize('bet,expected', [
    (100, 950),
    (25, 912)
])
def test_surrender(player: Player, bet: int, expected: int):
    player.chips = 900
    player.bet = bet
    player.surrender()
    assert player.chips == expected

@pytest.mark.parametrize('bet,price,chips', [
    (100, 50, 850),
    (25, 12, 888)
])
def test_buy_insurance(player: Player, bet: int, price: int, chips: int):
    player.chips = 900
    player.bet = bet
    player.buy_insurance()
    assert player.insurance == price
    assert player.chips == chips

def test_reset(player: Player):
    player.insurance = 25
    player.reset()
    assert player._active_hand == 0
    assert player.insurance is None
