from enum import Enum
import exceptions

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class Color(Enum):
    WHITE = 0,
    BLACK = 1


class Stone:
    def __init__(self, coords, color, group):
        self.coords = coords
        self.color = color
        self.group = group


class Group:
    def __init__(self):
        self.stones = []


class Board:
    def __init__(self):
        self.size_x = 9
        self.size_y = 9
        self.stones = []

        for _ in range(self.size_x):
            for _ in range(self.size_y):
                self.stones.append(None)


class GoGame:
    def __init__(self):
        self.groups = []
        self.cur_color = Color.BLACK
        self.players = (None, None)
        self.board = Board()

    def place_stone(self, coords):
        exceptions.sanitize_stone_position(coords, self.board)
        x, y = self.transform_coords(coords)

        # TODO: "Ko" rule
        # TODO: capture neighbor groups without liberties
        # TODO: calculate group
        group = None
        self.board[x][y] = Stone(coords, self.cur_color, group)

    def capture_neighbors(self, coords):
        # TODO
        return
        groups = []
        for neighbor in self.neighbors(coords):
            groups.append(neighbor.group)

    def neighbors(self, coords):
        x, y = coords
        neighbors = []
        if x > 0:
            neighbors.append((x - 1, y))
        if x < self.size_x - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < self.size_y - 1:
            neighbors.append((x, y + 1))
        return neighbors

    def turn(self):
        if self.cur_color == Color.BLACK:
            self.cur_color = self.cur_color.WHITE
            return self.cur_color
        else:
            self.cur_color = Color.BLACK
            return Color.WHITE

    @staticmethod
    def transform_coords(coords):
        letter = ord(coords[0]) - ord('a')
        number = coords[1] - 1
        return letter, number
