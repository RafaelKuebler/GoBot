#!/usr/bin/python
# coding: utf-8

import pytest
import sys
sys.path.append('../')
from go.go import Stone, Group, Board, GoGame, Color
from exceptions import SelfCaptureException


class TestStone:
    def test_color(self):
        colors = [Color.BLACK, Color.WHITE]
        for color in colors:
            stone = Stone(5, 5, color, Board())
            assert stone.color == color

    def test_coords(self):
        stone = Stone(5, 5, Color.BLACK, Board())
        assert stone.coords == (5, 5)

    def test_stone_on_board(self):
        board = Board()
        stone = Stone(5, 5, Color.WHITE, board)
        assert board.stones[5][5] == stone

    def test_capture_single(self):
        board = Board()
        Stone(5, 5, Color.WHITE, board)
        Stone(5, 4, Color.BLACK, board)
        Stone(5, 6, Color.BLACK, board)
        Stone(4, 5, Color.BLACK, board)
        Stone(6, 5, Color.BLACK, board)
        assert board.stones[5][5] is None

    def test_capture_group(self):
        board = Board()
        Stone(5, 5, Color.WHITE, board)
        Stone(5, 6, Color.WHITE, board)
        Stone(5, 4, Color.BLACK, board)
        Stone(5, 7, Color.BLACK, board)
        Stone(4, 5, Color.BLACK, board)
        Stone(4, 6, Color.BLACK, board)
        Stone(6, 5, Color.BLACK, board)
        Stone(6, 6, Color.BLACK, board)
        assert board.stones[5][5] is None
        assert board.stones[5][6] is None

    def test_self_capture(self):
        with pytest.raises(SelfCaptureException):
            board = Board()
            Stone(5, 5, Color.WHITE, board)
            Stone(5, 4, Color.BLACK, board)
            Stone(5, 7, Color.BLACK, board)
            Stone(4, 5, Color.BLACK, board)
            Stone(4, 6, Color.BLACK, board)
            Stone(6, 5, Color.BLACK, board)
            Stone(6, 6, Color.BLACK, board)
            Stone(5, 6, Color.WHITE, board)

    def test_neighbors(self):
        stone = Stone(5, 5, Color.WHITE, Board())
        neighbors = {(4, 5), (6, 5), (5, 4), (5, 6)}
        assert neighbors.issubset(stone.neighbors)

    def test_neighbors_border(self):
        stone = Stone(0, 0, Color.WHITE, Board())
        neighbors = {(1, 0), (0, 1)}
        assert neighbors.issubset(stone.neighbors)


class TestGroup:
    def test_color(self):
        colors = [Color.WHITE, Color.BLACK]
        for color in colors:
            group = Group(color)
            assert group.color == color

    def test_stones(self):
        colors = [Color.WHITE, Color.BLACK]
        for color in colors:
            group = Group(color)
            assert not group.stones

    def test_add_to_group(self):
        board = Board()
        stone1 = Stone(5, 5, Color.WHITE, board)
        stone2 = Stone(5, 6, Color.WHITE, board)
        assert stone1.group == stone2.group

    def test_combine_groups(self):
        board = Board()
        color = Color.WHITE
        stone1 = Stone(5, 5, color, board)
        stone2 = Stone(5, 7, color, board)
        stone3 = Stone(5, 6, color, board)
        assert stone1.group == stone2.group == stone3.group

    def test_capture(self):
        board = Board()
        color = Color.WHITE
        stone1 = Stone(5, 5, color, board)
        Stone(5, 6, color, board)
        Stone(6, 5, color, board)
        stone1.group.capture()
        assert board.stones[5][5] is None
        assert board.stones[5][6] is None
        assert board.stones[6][5] is None

    def test_liberties_single_stone(self):
        board = Board()
        color = Color.WHITE
        stone = Stone(5, 5, color, board)
        liberties = {(4, 5), (6, 5), (5, 4), (5, 6)}
        group_liberties = stone.group.liberties
        assert liberties.issubset(group_liberties)

    def test_liberties_more_than_1_stones(self):
        board = Board()
        color = Color.WHITE
        stone = Stone(5, 5, color, board)
        Stone(5, 6, color, board)
        Stone(6, 5, color, board)
        liberties = {(5, 4), (6, 4), (7, 5), (6, 6), (5, 7), (4, 6), (4, 5)}
        group_liberties = stone.group.liberties
        assert liberties.issubset(group_liberties)


class TestBoard:
    def test_sizes(self):
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
        board = Board()
        assert board.last_stone_placed is None


class TestGoGame:
    def test_first_player_black(self):
        game = GoGame()
        assert game.cur_color == Color.BLACK

    def test_board(self):
        game = GoGame()
        assert game.board is not None

    def test_board_sizes(self):
        sizes = [(9, 9), (13, 13), (19, 19)]
        for size in sizes:
            x, y = size
            game = GoGame(x, y)
            assert game.board.size_x == x
            assert game.board.size_y == y

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
