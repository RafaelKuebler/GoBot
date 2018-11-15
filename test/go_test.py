#!/usr/bin/python
# coding: utf-8

from src.go import GoGame, Color


class TestGoGame:
    def test_init(self):
        game = GoGame()
        assert game is not None

    def test_first_player_black(self):
        game = GoGame()
        assert game.cur_color == Color.BLACK

    def test_board(self):
        game = GoGame()
        assert game.board is not None

    def test_change_turn(self):
        game = GoGame()
        game.change_turn()
        assert game.cur_color == Color.WHITE
        game.change_turn()
        assert game.cur_color == Color.BLACK

    def test_transform_coords(self):
        game = GoGame()
        coords = ['a1', 'e2', 'e5']
        expected = [(0, 0), (4, 1), (4, 4)]
        for i in range(len(coords)):
            transformed = game.transform_coords(coords[i])
            assert transformed == expected[i]

    # TODO: test place stone
    # TODO: test calculate result
    # TODO: test mark stone
