#!/usr/bin/python
# coding: utf-8

from enum import Enum
import exceptions

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class Color(Enum):
    WHITE = "white"
    BLACK = "black"


class Stone:
    def __init__(self, x, y, color, board):
        self.coords = (x, y)
        self.color = color
        self.board = board
        self.board.stones[x][y] = self
        self.group = self.search_group()
        self.capture_neighbors()
        self.check_self_capture()
        self.board.last_stone_placed = self

    @property
    def neighbors(self):
        x, y = self.coords
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
    def adjacent_groups(self):
        adjacent_groups = set()
        for x, y in self.neighbors:
            if self.board.stones[x][y] is not None:
                adjacent_groups.add(self.board.stones[x][y].group)
        return adjacent_groups

    def capture_neighbors(self):
        for group in self.adjacent_groups:
            if group.color != self.color and not group.liberties:
                group.capture()

    @property
    def liberties(self):
        liberties = []
        for x, y in self.neighbors:
            if self.board.stones[x][y] is None:
                liberties.append((x, y))
        return liberties

    def capture(self):
        x, y = self.coords
        self.board.stones[x][y] = None

    def search_group(self):
        adjacent_groups = self.adjacent_groups
        group = Group(self.color)
        group.stones.add(self)
        for adj_group in adjacent_groups:
            if adj_group.color == self.color:
                group.merge(adj_group)
        return group

    def check_self_capture(self):
        if not self.group.liberties:
            self.capture()
            self.group.stones.remove(self)
            exceptions.check_self_capture()

    def __repr__(self):
        return "({}: {})".format(self.color, self.coords)


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
    def __init__(self, board_x, board_y):
        self.cur_color = Color.BLACK
        # TODO: Allow user to choose board size
        self.board = Board(board_x, board_y)

    def place_stone(self, coords):
        exceptions.check_stone_coords(coords, self.board)
        x, y = self.transform_coords(coords)
        exceptions.check_pos_taken(x, y, self.board)
        # TODO: Implement Ko rule
        Stone(x, y, self.cur_color, self.board)

    def change_turn(self):
        if self.cur_color == Color.BLACK:
            self.cur_color = Color.WHITE
        else:
            self.cur_color = Color.BLACK

    def mark_stone(self, coords):
        # TODO: Allow players to mark stones
        pass

    def calculate_result(self):
        # TODO: Calculate the territory of each player
        return 0, 0

    @staticmethod
    def transform_coords(coords):
        # TODO: implement notation as in https://senseis.xmp.net/?Coordinates
        letter = ord(coords[0]) - ord('a')
        number = int(coords[1]) - 1
        return letter, number
