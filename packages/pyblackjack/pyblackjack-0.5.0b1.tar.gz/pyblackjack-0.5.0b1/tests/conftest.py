# pylint: disable=wrong-import-order
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=no-member
# pylint: disable=protected-access

import pytest

from pyblackjack import objects
from pyblackjack.objects import CARDSET, Shoe

class MockShoe(Shoe):
    def __init__(self, decks=6):
        super().__init__(decks=decks)
        self.next = None

    def set_next(self, n):
        self.next = CARDSET[n - 1]

    def deal(self):
        return self.next

@pytest.fixture
def mock_shoe(monkeypatch, request):
    shoe = MockShoe()
    monkeypatch.setattr(objects, "SHOE", shoe)

def get_cards(cards):
    return [CARDSET[n - 1] for n in cards]
