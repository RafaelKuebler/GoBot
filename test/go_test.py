#!/usr/bin/python
# coding: utf-8

from src.go import Stone, Group, Board, GoGame, Color


class TestStone:
    pass


class TestGroup:
    pass


class TestBoard:
    def test_size(self):
        sizes = [(9, 9), (13, 13), (19, 19)]
        for size in sizes:
            x, y = size
            board = Board(x, y)
            assert board.size_x == x
            assert board.size_y == y

    def test_stones(self):
        sizes = [(9, 9), (13, 13), (19, 19)]
        for size in sizes:
            x, y = size
            board = Board(x, y)
            assert len(board.stones) == x
            for row in board.stones:
                assert len(row) == y

    def test_last_stone_placed(self):
        board = Board(9, 9)
        assert board.last_stone_placed is None


class TestGoGame:
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
