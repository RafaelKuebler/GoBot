import pytest
from gobot.go.go import *
from gobot.go.exceptions import *

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class TestGridPosition:
    def test_free(self):
        grid_pos = GridPosition()
        assert grid_pos.free

    def test_occupied(self):
        grid_pos = GridPosition()
        grid_pos.color = "white"
        assert not grid_pos.free


class TestGoGame:
    @staticmethod
    def coord(x: int, y: int) -> str:
        return f"{chr(ord('a') + x)}{y + 1}"

    def test_new_game(self):
        sizes = [(9, 9), (13, 13), (19, 19)]
        for size in sizes:
            x, y = size
            game = GoGame(x, y)
            assert game.size_x == x
            assert game.size_y == y
            assert game.last_stone_placed is None
            for row in game.board:
                for grid_pos in row:
                    assert grid_pos.free

    def test_wrong_size(self):
        with pytest.raises(InvalidBoardSizeException):
            GoGame(15, 2)

    def test_place_stone(self):
        game = GoGame(9, 9)
        coords = [(0, 0), (4, 1), (4, 4)]
        for x, y in coords:
            game.place_stone(self.coord(x, y), "black")
            assert not game.board[x][y].free
            assert (x, y) in game.board[x][y].group
            assert len(game.board[x][y].group) == 1
            assert game.board[x][y].color == "black"

    def test_place_stone_invalid_coord(self):
        game = GoGame(9, 9)
        coords = ['x9', 'y22', 'o2', 'a30', 'test']
        for coord in coords:
            with pytest.raises(InvalidCoordinateException):
                game.place_stone(coord, "black")

    def test_place_stone_taken_coord(self):
        game = GoGame(9, 9)
        game.place_stone(self.coord(3, 3), "white")
        with pytest.raises(CoordOccupiedException):
            game.place_stone(self.coord(3, 3), "black")

    def test_last_stone_placed(self):
        game = GoGame(9, 9)
        coords = [(0, 0), (4, 6), (2, 4)]
        for x, y in coords:
            game.place_stone(self.coord(x, y), "black")
            assert game.last_stone_placed == (x, y)

    def test_merge_groups(self):
        game = GoGame(9, 9)
        coords = {(3, 3), (3, 5), (3, 4)}
        for coord in coords:
            game.place_stone(self.coord(*coord), "white")

        for x, y in coords:
            assert game.board[x][y].group == coords

    def test_capture_single(self):
        game = GoGame(9, 9)
        game.place_stone(self.coord(5, 5), "white")
        game.place_stone(self.coord(5, 4), "black")
        game.place_stone(self.coord(5, 6), "black")
        game.place_stone(self.coord(4, 5), "black")
        game.place_stone(self.coord(6, 5), "black")
        assert game.board[5][5].free

    def test_capture_group(self) -> None:
        game = GoGame(9, 9)
        game.place_stone(self.coord(5, 5), "white")
        game.place_stone(self.coord(5, 6), "white")
        game.place_stone(self.coord(5, 4), "black")
        game.place_stone(self.coord(5, 7), "black")
        game.place_stone(self.coord(4, 5), "black")
        game.place_stone(self.coord(4, 6), "black")
        game.place_stone(self.coord(6, 5), "black")
        game.place_stone(self.coord(6, 6), "black")
        assert game.board[5][5].free
        assert game.board[5][6].free

    def test_self_capture(self) -> None:
        game = GoGame(9, 9)
        game.place_stone(self.coord(5, 5), "white")
        game.place_stone(self.coord(5, 4), "black")
        game.place_stone(self.coord(5, 7), "black")
        game.place_stone(self.coord(4, 5), "black")
        game.place_stone(self.coord(4, 6), "black")
        game.place_stone(self.coord(6, 5), "black")
        game.place_stone(self.coord(6, 6), "black")
        with pytest.raises(SelfCaptureException):
            game.place_stone(self.coord(5, 6), "white")

    def test_ko(self):
        game = GoGame(9, 9)
        game.place_stone(self.coord(5, 5), "white")
        game.place_stone(self.coord(7, 5), "white")
        game.place_stone(self.coord(6, 4), "white")
        game.place_stone(self.coord(6, 6), "white")
        game.place_stone(self.coord(5, 6), "black")
        game.place_stone(self.coord(5, 4), "black")
        game.place_stone(self.coord(4, 5), "black")
        game.place_stone(self.coord(6, 5), "black")
        assert game.board[5][5].free

        with pytest.raises(KoException):
            game.place_stone(self.coord(5, 5), "white")

    def test_ko2(self):
        game = GoGame(9, 9)
        game.place_stone(self.coord(0, 0), "white")
        game.place_stone(self.coord(2, 0), "white")
        game.place_stone(self.coord(1, 1), "white")
        game.place_stone(self.coord(0, 1), "black")
        game.place_stone(self.coord(1, 0), "black")
        assert game.board[0][0].free

        with pytest.raises(KoException):
            game.place_stone(self.coord(0, 0), "white")
