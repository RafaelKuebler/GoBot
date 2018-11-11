from enum import Enum
from exceptions import CoordOccupiedException, InexistentGameException

__author__ = "Rafael Kuebler da Silva <rafael_kuebler@yahoo.es>"
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


class GoGame:
    def __init__(self):
        self.groups = []
        self.cur_color = Color.BLACK
        self.size_x = 9
        self.size_y = 9
        self.players = (None, None)
        self.board = []

        for _ in range(self.size_x):
            for _ in range(self.size_y):
                self.board.append(None)

    def place_stone(self, coords):
        x, y = self.transform_coords(coords)
        if self.board[x][y] is not None:  # if coord is taken
            raise CoordOccupiedException()

        # TODO: add "Ko" rule

        #self.capture_neighbors(coords)
        # TODO: calculate group
        group = None
        self.board[x][y] = Stone(coords, self.cur_color, group)
        return f"Placed stone on {coords}"

    def capture_neighbors(self, coords):
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


    @staticmethod
    def transform_coords(self, coords):
        return (1,1)

    def turn(self):
        if self.cur_color == Color.BLACK:
            self.cur_color = self.cur_color.WHITE
            return self.cur_color
        else:
            self.cur_color = Color.BLACK
            return Color.WHITE
