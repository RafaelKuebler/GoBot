from enum import Enum
from . import settings
from .exceptions import *

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class Color(Enum):
    WHITE = "white"
    BLACK = "black"


class Stone:
    def __init__(self, x, y, color, board):
        self.coord = (x, y)
        self.color = color
        self.board = board

        self.group = Group(self.color)
        self.group.stones.add(self)
        self._check_ko()
        self.merge_group()

        self.capture_neighbors()
        self.board.stones[x][y] = self
        self._check_self_capture()
        self.board.last_stone_placed = self

    @property
    def neighbors(self):
        x, y = self.coord
        neighbors = []
        if x > 0:
            neighbors.append((x - 1, y))
        if x < self.board.size_x - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < self.board.size_y - 1:
            neighbors.append((x, y + 1))
        return neighbors

    @property
    def liberties(self):
        liberties = []
        for x, y in self.neighbors:
            if self.board.stones[x][y] is None:
                liberties.append((x, y))
        return liberties

    @property
    def adjacent_groups(self):
        adjacent_groups = set()
        for x, y in self.neighbors:
            if self.board.stones[x][y] is not None:
                adjacent_groups.add(self.board.stones[x][y].group)
        return adjacent_groups

    def capture_neighbors(self):
        stones = []
        for group in self.adjacent_groups:
            if group.color != self.color and len(group.liberties)-1 == 0:
                group.capture()
                stones.append(list(group.stones))

        if len(stones) == 1 and len(stones[0]) == 1:
            self.board.last_captured_single_stone = stones[0][0]
        else:
            self.board.last_captured_single_stone = None

    def capture(self):
        x, y = self.coord
        self.board.stones[x][y] = None

    def merge_group(self):
        for adj_group in self.adjacent_groups:
            if adj_group.color == self.color:
                self.group.merge(adj_group)

    def _check_ko(self):
        """
        Conditions:
        - Last round exactly one stone was captured
        - The newly placed stone would capture exactly one stone
        - The stone that would be captured is the last placed stone
        """

        if self.board.last_captured_single_stone is None:
            return

        single_threatened_neighbor = None

        for group in self.adjacent_groups:
            if group.color != self.color and len(group.liberties)-1 == 0 and group.size == 1:
                more_than_one_target = single_threatened_neighbor is not None
                if more_than_one_target:
                    return
                single_threatened_neighbor = list(group.stones)[0]

        if self.board.last_stone_placed == single_threatened_neighbor:
            raise KoException(settings.error_ko)

    def _check_self_capture(self):
        if not self.group.liberties:
            self.capture()
            self.group.stones.remove(self)
            raise SelfCaptureException(settings.error_self_capture)

    def __repr__(self):
        return "({}: {})".format(self.color, self.coord)


class Group:
    def __init__(self, color):
        self.stones = set()
        self.color = color

    @property
    def liberties(self):
        liberties = []
        for stone in self.stones:
            liberties.extend(stone.liberties)
        return set(liberties)

    @property
    def size(self):
        return len(self.stones)

    def merge(self, group):
        for stone in group.stones:
            stone.group = self
            self.stones.add(stone)

    def capture(self):
        for stone in self.stones:
            stone.capture()

    def __repr__(self):
        return "({}: {})".format(self.color, self.stones)


class Board:
    def __init__(self, size_x=9, size_y=9):
        self.size_x = size_x
        self.size_y = size_y
        self.stones = self._init_stones(self.size_x, self.size_y)
        self.last_stone_placed = None
        self.last_captured_single_stone = None

    @staticmethod
    def _init_stones(size_x, size_y):
        stones = []
        for _ in range(size_x):
            inner_stones = []
            for _ in range(size_y):
                inner_stones.append(None)
            stones.append(inner_stones)
        return stones


class GoGame:
    def __init__(self, board_x=9, board_y=9):
        self._check_board_size(board_x, board_y)
        self.board = Board(board_x, board_y)

    def place_stone(self, coord, color):
        self._check_stone_coord(coord)
        x, y = self._transform_coord(coord)
        self._check_pos_taken(x, y)
        Stone(x, y, color, self.board)

    def calculate_result(self):
        # TODO: Calculate the territory of each player
        raise NotImplementedError

    @staticmethod
    def _transform_coord(coord):
        # TODO: implement notation as in https://senseis.xmp.net/?Coordinates
        letter = ord(coord[0]) - ord('a')
        number = int(coord[1]) - 1
        return letter, number

    @staticmethod
    def _check_board_size(size_x, size_y):
        if (size_x, size_y) not in [(9, 9), (13, 13), (19, 19)]:
            raise InvalidBoardSizeException(settings.error_invalid_size)

    def _check_stone_coord(self, coord):
        if not coord[1:].isdigit():
            raise InvalidCoordinateException(settings.error_invalid_coords)

        x_in_range = ord('a') <= ord(coord[0]) < ord('a') + self.board.size_x
        y_in_range = 1 <= int(coord[1:]) <= self.board.size_y
        if not x_in_range or not y_in_range:
            raise InvalidCoordinateException(settings.error_invalid_coords)

    def _check_pos_taken(self, x, y):
        if self.board.stones[x][y] is not None:
            raise CoordOccupiedException(settings.error_coord_occupied)
