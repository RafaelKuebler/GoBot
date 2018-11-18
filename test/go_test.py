#!/usr/bin/python
# coding: utf-8

from go.go import Stone, Group, Board, GoGame, Color


class TestStone:
    pass


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
        board = Board()
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

    # TODO: test many board sizes
    # TODO: test place stone
    # TODO: test calculate result
    # TODO: test mark stone
