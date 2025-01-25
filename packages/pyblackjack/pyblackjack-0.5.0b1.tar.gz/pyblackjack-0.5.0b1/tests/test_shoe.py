# pylint: disable=wrong-import-order
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=no-member
# pylint: disable=protected-access

import pytest

from pyblackjack.objects import Shoe, CARDSET

@pytest.fixture(scope='module', params=range(1, 9))
def shoe(request):
    return Shoe(decks=request.param)

# # # # # # # # # # TESTS # # # # # # # # # #

def test_shoe_size(shoe: Shoe):
    assert len(shoe.cards) == shoe.decks * 52


def test_cut_position(shoe: Shoe):
    cut = shoe.decks * 52 // (2 if shoe.decks == 1 else 4)
    assert cut - shoe.decks * 4 <= shoe.cut <= cut + shoe.decks * 4


def test_deck_composition(shoe: Shoe):
    ranks = [card.rank for card in shoe.cards]
    for card in CARDSET:
        assert ranks.count(card.rank) == shoe.decks * 4


def test_deal(shoe: Shoe):
    topcard = shoe.cards[-1]
    dealt = shoe.deal()
    assert len(shoe.cards) == shoe.decks * 52 - 1
    assert dealt.rank == topcard.rank
    assert ([card.rank for card in shoe.cards].count(dealt.rank)
            == shoe.decks * 4 - 1)


def test_cut_detection(shoe: Shoe):
    shoe.cards = shoe.cards[:shoe.cut + 2]
    assert not shoe.time_to_shuffle
    shoe.deal()
    assert not shoe.time_to_shuffle
    shoe.deal()
    assert shoe.time_to_shuffle
    shoe.deal()
    assert shoe.time_to_shuffle


def test_shuffle(shoe: Shoe):
    shoe.new()
    test_shoe_size(shoe)
    test_cut_position(shoe)
    test_deck_composition(shoe)
