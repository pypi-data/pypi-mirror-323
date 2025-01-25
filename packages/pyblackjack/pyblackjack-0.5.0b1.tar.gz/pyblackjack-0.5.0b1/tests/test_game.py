# pylint: disable=wrong-import-order
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=no-member
# pylint: disable=protected-access

import pytest
from io import StringIO
import sys

from pyblackjack.game import Game
from pyblackjack.objects import SHOE, Hand, Player
from conftest import get_cards

def test_init_1() -> None:
    Player._id = 0
    players = ['Adam', 'Bob', 'Charlie', 'Diane']
    game = Game(players, 4000, 4, False)
    assert SHOE.decks == 4
    assert game.dealer.soft_stand == 17
    assert len(game.players) == 4
    assert len(game.active_players) == 0
    for i, player in enumerate(game.players):
        if players[i] is None:
            assert player.name == f'Player {i + 1}'
        else:
            assert player.name == players[i]
        assert player.chips == 4000

def test_init_defaults() -> None:
    Player._id = 0
    game = Game()
    assert SHOE.decks == 6
    assert game.dealer.soft_stand == 18
    assert len(game.players) == 1
    assert len(game.active_players) == 0
    assert game.players[0].name == 'Player 1'
    assert game.players[0].chips == 1000

@pytest.mark.parametrize('chips,input_value,xbet,xchips,xactive,xplaying', [
    (1000, '100\n', 100, 900, True, True),
    (1000, '0\n', 0, 1000, False, True),
    (1000, 'q\n', None, 1000, False, False),
    (0, '', None, 0, False, False)
])
def test_get_bet(
    monkeypatch,
    chips: int,
    input_value: str,
    xbet: int | None,
    xchips: int,
    xactive: bool,
    xplaying: bool,
) -> None:
    game = Game(players=['Test'], chips=chips)
    player = game.players[0]
    with monkeypatch.context() as m:
        m.setattr(sys, 'stdin', StringIO(input_value))
        game.get_bet(player)
    if xbet is not None:
        assert player.bet == xbet
    assert player.chips == xchips
    assert (player in game.active_players) is xactive
    assert (player in game.players) is xplaying

def test_deal_cards() -> None:
    game = Game(players=['a', 'b', 'c', 'd'])
    game.active_players = game.players.copy()
    starting_cards = len(SHOE.cards)
    for player in game.active_players:
        player.hands.append(Hand(bet=0))
    game.deal_cards()
    assert len(SHOE.cards) == starting_cards - 10
    for player in game.active_players:
        assert len(player.active_hand.cards) == 2
    assert len(game.dealer.cards) == 2

def test_print_hands(capfd) -> None:
    game = Game(players=['Alice', 'Bob', 'Carol'])
    game.active_players = game.players.copy()
    game.active_players[0].hands.append(Hand(bet=0))
    game.active_players[1].hands.append(Hand(bet=0))
    game.active_players[2].hands.append(Hand(bet=0))
    game.active_players[0].active_hand.cards = get_cards([4, 8])
    game.active_players[1].active_hand.cards = get_cards([1, 12])
    game.active_players[2].active_hand.cards = get_cards([3, 3])
    game.dealer.cards = get_cards([5, 11])
    game.print_hands()
    output = capfd.readouterr().out
    assert output == """\
Dealer: [] J
Alice: 4 8 (12)
Bob: A Q (21)
Carol: 3 3 (6)
"""
